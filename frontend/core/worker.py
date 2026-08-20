from PySide6.QtCore import QThread, Signal

class RequestWorker(QThread):
    """
    A generic QThread worker to execute synchronous HTTP requests in the background.
    Emits a tuple (response_data, status_code) upon completion.
    """
    finished = Signal(tuple)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            res = self.func(*self.args, **self.kwargs)
            if isinstance(res, tuple):
                self.finished.emit(res)
            else:
                self.finished.emit((res, 200))
        except Exception as e:
            self.finished.emit(({"detail": str(e)}, 500))
