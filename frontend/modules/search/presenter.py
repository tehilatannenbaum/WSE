from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.core.worker import RequestWorker
from frontend.modules.search.view import SearchView

class SearchPresenter(QObject):
    def __init__(self, view: SearchView):
        super().__init__()
        self.view = view
        self.view.search_clicked.connect(self.perform_search)
        self.view.view_details_clicked.connect(self.handle_view_details)
        # Load default search on initialize
        self.perform_search()

    def perform_search(self):
        self.view.search_btn.setEnabled(False)
        self.view.set_status("Searching flights...")
        
        origin = self.view.get_origin()
        destination = self.view.get_destination()
        date = self.view.get_date()

        self.worker = RequestWorker(
            api_client.search_flights,
            origin=origin if origin else None,
            destination=destination if destination else None,
            date=date if date else None
        )
        self.worker.finished.connect(self.on_search_completed)
        self.worker.start()

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
        self.detail_worker = RequestWorker(api_client.get_flight_details, flight_id)
        self.detail_worker.finished.connect(self.on_details_completed)
        self.detail_worker.start()

    def on_details_completed(self, result):
        flight, status_code = result
        if status_code == 200:
            self.view.set_status("")
            event_bus.emit("flight_selected", flight)
        else:
            self.view.set_status("Failed to load flight details.", is_error=True)

class SearchModel:
    pass
