from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PySide6.QtCore import Qt, Signal

class AIAdvisorView(QWidget):
    send_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title
        title_label = QLabel("AI Travel Advisor")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Ask questions about baggage limits, refunds, cancellations, and destination guides")
        subtitle_label.setObjectName("subtitle")
        layout.addWidget(subtitle_label)

        # Chat History Log
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setObjectName("chatHistory")
        layout.addWidget(self.chat_history)
        
        # Initial greeting
        self.append_system_message(
            "Hello! I am your Travel Assistant. Ask me anything about luggage allowances, "
            "cancellation fees, refund eligibility, or sightseeing highlights in Paris, Tokyo, London, and New York."
        )

        # Input Row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Type your travel question here... (e.g. Can I get a full refund?)")
        self.query_input.returnPressed.connect(self.send_clicked.emit)
        input_row.addWidget(self.query_input)

        self.send_btn = QPushButton("Ask Advisor")
        self.send_btn.clicked.connect(self.send_clicked.emit)
        input_row.addWidget(self.send_btn)

        layout.addLayout(input_row)

    def get_query(self) -> str:
        return self.query_input.text().strip()

    def clear_query(self):
        self.query_input.clear()

    def set_loading(self, is_loading: bool):
        self.send_btn.setEnabled(not is_loading)
        if is_loading:
            self.send_btn.setText("Consulting...")
            self.query_input.setEnabled(False)
        else:
            self.send_btn.setText("Ask Advisor")
            self.query_input.setEnabled(True)
            self.query_input.setFocus()

    def append_user_message(self, message: str):
        import html
        escaped = html.escape(message)
        formatted = f'<p style="color: #38bdf8; margin: 4px 0;"><b>👤 You:</b> {escaped}</p>'
        self.chat_history.append(formatted)

    def append_advisor_message(self, message: str, is_fallback: bool = False):
        import html
        color = "#10b981" if not is_fallback else "#f59e0b"
        prefix = "🤖 Advisor" if not is_fallback else "⚠️ Advisor (Offline database)"
        
        # Escape then replace newlines with HTML breaks
        escaped_message = html.escape(message).replace("\n", "<br>")
        formatted = f'<p style="color: {color}; margin: 8px 0;"><b>{prefix}:</b> {escaped_message}</p>'
        self.chat_history.append(formatted)

    def append_system_message(self, message: str):
        import html
        escaped = html.escape(message)
        formatted = f'<p style="color: #94a3b8; font-style: italic; margin: 4px 0;">💬 {escaped}</p>'
        self.chat_history.append(formatted)
