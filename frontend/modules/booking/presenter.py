from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.modules.booking.view import BookingView

class BookingPresenter(QObject):
    def __init__(self, view: BookingView):
        super().__init__()
        self.view = view
        
        self.view.book_submitted.connect(self.handle_booking_submission)
        self.view.cancel_clicked.connect(self.handle_booking_cancellation)
        
        # Subscribe to relevant system events
        event_bus.subscribe("user_logged_in", self.on_user_logged_in)
        event_bus.subscribe("initiate_booking", self.on_initiate_booking)

    def on_user_logged_in(self, user_profile: dict):
        # Refresh history when user logs in
        self.load_history()

    def on_initiate_booking(self, flight_id: int):
        # Prefill form
        flight, status = api_client.get_flight_details(flight_id)
        if status == 200:
            self.view.set_prefilled_flight(flight)
            # Switch central stack index to booking module
            event_bus.emit("navigate_to_tab", "Bookings")
        else:
            self.view.set_status("Failed to prefill flight data.", is_error=True)

    def load_history(self):
        bookings, status = api_client.get_my_orders()
        if status == 200:
            self.view.update_history(bookings)
        else:
            self.view.set_table_status("Failed to load booking history.", is_error=True)

    def handle_booking_submission(self):
        flight_id = self.view.flight_id
        passenger_name = self.view.get_passenger_name()
        passport_number = self.view.get_passport_number()

        if not passenger_name or not passport_number:
            self.view.set_status("Please fill in passenger name and passport number.", is_error=True)
            return

        self.view.set_status("Submitting booking...")
        
        res, status = api_client.book_flight(flight_id, passenger_name, passport_number)
        if status == 201:
            self.view.set_status("Booking confirmed successfully!")
            self.view.clear_form()
            # Refresh logs
            self.load_history()
            # Notify other modules that bookings were updated (e.g. stats chart)
            event_bus.emit("bookings_updated")
        else:
            err_msg = res.get("detail", "Failed to book flight. The flight might be sold out.")
            self.view.set_status(err_msg, is_error=True)

    def handle_booking_cancellation(self, booking_id: str):
        self.view.set_table_status("Processing cancellation...")
        
        res, status = api_client.cancel_booking(booking_id)
        if status == 200:
            self.view.set_table_status("Booking cancelled successfully!")
            self.load_history()
            event_bus.emit("bookings_updated")
        else:
            err_msg = res.get("detail", "Failed to cancel booking.")
            self.view.set_table_status(err_msg, is_error=True)
