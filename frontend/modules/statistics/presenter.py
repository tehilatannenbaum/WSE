from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.core.worker import RequestWorker
from frontend.modules.statistics.view import StatisticsView

class StatisticsPresenter(QObject):
    def __init__(self, view: StatisticsView):
        super().__init__()
        self.view = view
        self._active_workers = set()
        
        # Subscribe to bookings updates and auth notifications
        event_bus.subscribe("bookings_updated", self.load_statistics)
        event_bus.subscribe("user_logged_in", self.on_user_logged_in)
        
        # Initial load
        self.load_statistics()

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

    def on_user_logged_in(self, user_profile: dict):
        self.load_statistics()

    def load_statistics(self):
        # Fetch statistics asynchronously to avoid freezing UI thread
        self._start_worker(
            "_stats_worker",
            api_client.get_statistics,
            on_completed=self.on_stats_loaded
        )

    def on_stats_loaded(self, result):
        stats, status = result
        if status == 200:
            avg_prices = stats.get("avg_prices", [])
            volume = stats.get("booking_volume", [])
            self.view.update_charts(avg_prices, volume)
        else:
            self.view.update_charts([], [])
