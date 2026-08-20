from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.core.worker import RequestWorker
from frontend.modules.statistics.view import StatisticsView

class StatisticsPresenter(QObject):
    def __init__(self, view: StatisticsView):
        super().__init__()
        self.view = view
        
        # Subscribe to bookings updates and auth notifications
        event_bus.subscribe("bookings_updated", self.load_statistics)
        event_bus.subscribe("user_logged_in", self.on_user_logged_in)
        
        # Initial load
        self.load_statistics()

    def on_user_logged_in(self, user_profile: dict):
        self.load_statistics()

    def load_statistics(self):
        # Fetch statistics asynchronously to avoid freezing UI thread
        self.worker = RequestWorker(api_client.get_statistics)
        self.worker.finished.connect(self.on_stats_loaded)
        self.worker.start()

    def on_stats_loaded(self, result):
        stats, status = result
        if status == 200:
            avg_prices = stats.get("avg_prices", [])
            volume = stats.get("booking_volume", [])
            self.view.update_charts(avg_prices, volume)
        else:
            self.view.update_charts([], [])
