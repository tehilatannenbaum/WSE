from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.modules.search.view import SearchView

class SearchPresenter:
    def __init__(self, view: SearchView):
        self.view = view
        self.view.search_clicked.connect(self.perform_search)
        self.view.view_details_clicked.connect(self.handle_view_details)
        # Load default search on initialize
        self.perform_search()

    def perform_search(self):
        origin = self.view.get_origin()
        destination = self.view.get_destination()

        flights, status_code = api_client.search_flights(
            origin=origin if origin else None,
            destination=destination if destination else None
        )
        self.view.update_results(flights)

    def handle_view_details(self, flight_id: int):
        # Fetch details
        flight, status_code = api_client.get_flight_details(flight_id)
        if status_code == 200:
            # Emit globally to notify shell to navigate to Details tab and show this flight
            event_bus.emit("flight_selected", flight)
        else:
            self.view.set_status("Failed to load flight details.", is_error=True)
class SearchModel:
    pass
