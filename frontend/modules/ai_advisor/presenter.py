from PySide6.QtCore import QThread, Signal, QObject
from frontend.core.api_client import api_client
from frontend.modules.ai_advisor.view import AIAdvisorView

class QueryWorker(QThread):
    finished = Signal(dict, int)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        res, status = api_client.ask_ai(self.query)
        self.finished.emit(res, status)

class AIAdvisorPresenter(QObject):
    def __init__(self, view: AIAdvisorView):
        super().__init__()
        self.view = view
        self.view.send_clicked.connect(self.send_query)

    def send_query(self):
        query = self.view.get_query()
        if not query:
            return

        self.view.append_user_message(query)
        self.view.clear_query()
        self.view.set_loading(True)

        # Launch request in background thread
        self.worker = QueryWorker(query)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response: dict, status_code: int):
        self.view.set_loading(False)
        
        answer = response.get("response", "No response received.")
        mode = response.get("mode", "Ollama")
        
        is_fallback = (mode == "Offline fallback" or status_code != 200)
        self.view.append_advisor_message(answer, is_fallback=is_fallback)
