from PySide6.QtCore import QThread, Signal, QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.modules.details.view import DetailsView

# Simple QThread to fetch weather asynchronously to prevent UI lag
class WeatherWorker(QThread):
    finished = Signal(dict)

    def __init__(self, destination: str):
        super().__init__()
        self.destination = destination

    def run(self):
        weather, status_code = api_client.get_weather(self.destination)
        self.finished.emit(weather)

class DetailsPresenter(QObject):
    def __init__(self, view: DetailsView):
        super().__init__()
        self.view = view
        self.view.book_clicked.connect(self.handle_book)
        
        # Subscribe to global flight selection events
        event_bus.subscribe("flight_selected", self.on_flight_selected)

    def on_flight_selected(self, flight: dict):
        # Update view fields
        self.view.set_flight_data(flight)
        self.view.show_weather_loading()
        
        # Fetch weather in background thread to avoid freezing UI
        self.worker = WeatherWorker(flight["destination"])
        self.worker.finished.connect(self.view.set_weather_data)
        self.worker.start()

    def handle_book(self, flight_id: int):
        # Notify globally that the user wishes to book this flight
        # This will trigger navigation to the Booking tab with this flight pre-selected
        event_bus.emit("initiate_booking", flight_id)
