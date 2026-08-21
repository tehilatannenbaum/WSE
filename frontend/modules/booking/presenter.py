from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.core.worker import RequestWorker
from frontend.modules.booking.view import BookingView

class BookingPresenter(QObject):
    def __init__(self, view: BookingView):
        super().__init__()
        self.view = view
        self._active_workers = set()
        
        self.view.book_submitted.connect(self.handle_booking_submission)
        self.view.cancel_clicked.connect(self.handle_booking_cancellation)
        
        # Subscribe to relevant system events
        event_bus.subscribe("user_logged_in", self.on_user_logged_in)
        event_bus.subscribe("initiate_booking", self.on_initiate_booking)
        event_bus.subscribe("bookings_updated", self.load_history)

    def _start_worker(self, attr_name: str, func, *args, on_completed, **kwargs):
        # Prevent starting same operation type simultaneously
        if hasattr(self, attr_name):
            old_worker = getattr(self, attr_name)
            if old_worker and old_worker.isRunning():
                return None
        
        worker = RequestWorker(func, *args, **kwargs)
        setattr(self, attr_name, worker)
        self._active_workers.add(worker)
        
        # Connect signals for cleanup and completion
        worker.finished.connect(lambda res: self._active_workers.discard(worker))
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(on_completed)
        worker.start()
        return worker

    def on_user_logged_in(self, user_profile: dict):
        self.load_history()

    def on_initiate_booking(self, flight_id: int):
        self.view.set_status("Loading flight data...")
        self._start_worker(
            "_prefill_worker",
            api_client.get_flight_details,
            flight_id,
            on_completed=self.on_prefill_completed
        )

    def on_prefill_completed(self, result):
        flight, status = result
        if status == 200:
            self.view.set_prefilled_flight(flight)
            event_bus.emit("navigate_to_tab", "Bookings")
        else:
            self.view.set_status("Failed to prefill flight data.", is_error=True)

    def load_history(self):
        self.view.set_table_status("Loading reservation history...")
        self._start_worker(
            "_history_worker",
            api_client.get_my_orders,
            on_completed=self.on_history_completed
        )

    def on_history_completed(self, result):
        bookings, status = result
        if status == 200:
            self.view.set_table_status("")
            self.view.update_history(bookings)
        else:
            self.view.set_table_status("Failed to load booking history.", is_error=True)

    def handle_booking_submission(self):
        flight_id = self.view.flight_id
        passenger_name = self.view.get_passenger_name()
        passport_number = self.view.get_passport_number()

        # Validate inputs
        if not passenger_name or not passport_number:
            self.view.set_status("Please fill in passenger name and passport number.", is_error=True)
            return

        # Name validation: letters and spaces only
        if len(passenger_name) < 2 or not all(c.isalpha() or c.isspace() for c in passenger_name):
            self.view.set_status("Invalid passenger name. Use only letters and spaces (min 2 chars).", is_error=True)
            return

        # Passport validation: alphanumeric only
        if len(passport_number) < 5 or not passport_number.isalnum():
            self.view.set_status("Invalid passport number. Must be at least 5 alphanumeric characters.", is_error=True)
            return

        self.view.set_status("Submitting booking...")
        self.view.submit_btn.setEnabled(False)
        self.view.submit_btn.setText("Booking...")
        
        self._start_worker(
            "_book_worker",
            api_client.book_flight,
            flight_id,
            passenger_name,
            passport_number,
            on_completed=self.on_booking_completed
        )

    def on_booking_completed(self, result):
        res, status = result
        self.view.submit_btn.setEnabled(True)
        self.view.submit_btn.setText("Confirm Booking")
        if status == 201:
            self.view.set_status("Booking confirmed successfully!")
            self.view.clear_form()
            # Only emitbookings_updated event, which triggers load_history automatically
            event_bus.emit("bookings_updated")
        else:
            err_msg = res.get("detail", "Failed to book flight. The flight might be sold out.")
            self.view.set_status(err_msg, is_error=True)

    def handle_booking_cancellation(self, booking_id: str):
        self.view.set_table_status("Processing cancellation...")
        self.view.cancel_btn.setEnabled(False)
        
        self._start_worker(
            "_cancel_worker",
            api_client.cancel_booking,
            booking_id,
            on_completed=self.on_cancellation_completed
        )

    def on_cancellation_completed(self, result):
        res, status = result
        if status == 200:
            self.view.set_table_status("Booking cancelled successfully!")
            # Only emit bookings_updated, which triggers load_history automatically
            event_bus.emit("bookings_updated")
        else:
            err_msg = res.get("detail", "Failed to cancel booking.")
            self.view.set_table_status(err_msg, is_error=True)
            # Restore Cancel button correctly if cancellation fails
            self.view.handle_selection_changed()
