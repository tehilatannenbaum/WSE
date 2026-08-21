from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.core.worker import RequestWorker
from frontend.modules.search.view import SearchView

class SearchModel:
    def search_flights(self, origin=None, destination=None, date=None):
        return api_client.search_flights(origin, destination, date)

    def get_flight_details(self, flight_id: int):
        return api_client.get_flight_details(flight_id)

class SearchPresenter(QObject):
    def __init__(self, view: SearchView):
        super().__init__()
        self.view = view
        self.model = SearchModel()
        self._active_workers = set()

        self.view.search_clicked.connect(self.perform_search)
        self.view.view_details_clicked.connect(self.handle_view_details)
        # Load default search on initialize
        self.perform_search()

    def _start_worker(self, attr_name: str, func, *args, on_completed, **kwargs):
        if hasattr(self, attr_name):
            old_worker = getattr(self, attr_name)
            if old_worker and old_worker.isRunning():
                return None
        
        worker = RequestWorker(func, *args, **kwargs)
        setattr(self, attr_name, worker)
        self._active_workers.add(worker)
        
        worker.finished.connect(lambda res: self._active_workers.discard(worker))
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(on_completed)
        worker.start()
        return worker

    def perform_search(self):
        self.view.search_btn.setEnabled(False)
        self.view.set_status("Searching flights...")
        
        origin = self.view.get_origin()
        destination = self.view.get_destination()
        date = self.view.get_date()

        self._start_worker(
            "_search_worker",
            self.model.search_flights,
            origin=origin if origin else None,
            destination=destination if destination else None,
            date=date if date else None,
            on_completed=self.on_search_completed
        )

    def on_search_completed(self, result):
        flights, status_code = result
        self.view.search_btn.setEnabled(True)
        if status_code == 200:
            self.view.update_results(flights)
        else:
            self.view.update_results([])
            self.view.set_status("Failed to retrieve flights.", is_error=True)

    def handle_view_details(self, flight_id: int):
        self.view.set_status("Loading details...")
        self._start_worker(
            "_detail_worker",
            self.model.get_flight_details,
            flight_id,
            on_completed=self.on_details_completed
        )

    def on_details_completed(self, result):
        flight, status_code = result
        if status_code == 200:
            self.view.set_status("")
            event_bus.emit("flight_selected", flight)
        else:
            self.view.set_status("Failed to load flight details.", is_error=True)
