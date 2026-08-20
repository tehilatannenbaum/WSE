from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedLayout, QFrame
from PySide6.QtCore import Qt, Signal

class AuthView(QWidget):
    # Signals for Presenter to connect to
    login_clicked = Signal()
    register_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Stacked layout to toggle between Login & Register forms
        self.stacked_layout = QStackedLayout()
        self.setLayout(self.stacked_layout)

        # 1. Login Form Widget
        self.login_widget = QWidget()
        login_main_layout = QVBoxLayout(self.login_widget)
        login_main_layout.setAlignment(Qt.AlignCenter)

        # Login Card Frame for premium look
        login_card = QFrame()
        login_card.setObjectName("card")
        login_card.setFixedWidth(380)
        login_layout = QVBoxLayout(login_card)
        login_layout.setContentsMargins(30, 40, 30, 40)
        login_layout.setSpacing(15)

        # Title
        title_label = QLabel("Welcome Back")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(title_label)

        subtitle_label = QLabel("Sign in to your travel planner")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(subtitle_label)
        login_layout.addSpacing(10)

        # Inputs
        self.login_user_input = QLineEdit()
        self.login_user_input.setPlaceholderText("Username")
        login_layout.addWidget(self.login_user_input)

        self.login_pass_input = QLineEdit()
        self.login_pass_input.setPlaceholderText("Password")
        self.login_pass_input.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.login_pass_input)

        # Error/Success label
        self.login_status_label = QLabel("")
        self.login_status_label.setAlignment(Qt.AlignCenter)
        self.login_status_label.setWordWrap(True)
        login_layout.addWidget(self.login_status_label)

        # Buttons
        self.login_btn = QPushButton("Sign In")
        self.login_btn.clicked.connect(self.login_clicked.emit)
        login_layout.addWidget(self.login_btn)

        # Toggle to register
        toggle_layout = QHBoxLayout()
        toggle_layout.addWidget(QLabel("Don't have an account?"))
        self.go_to_register_btn = QPushButton("Sign Up")
        self.go_to_register_btn.setObjectName("secondaryButton")
        self.go_to_register_btn.clicked.connect(self.show_register_layout)
        toggle_layout.addWidget(self.go_to_register_btn)
        login_layout.addLayout(toggle_layout)

        login_main_layout.addWidget(login_card)
        self.stacked_layout.addWidget(self.login_widget)

        # 2. Register Form Widget
        self.register_widget = QWidget()
        reg_main_layout = QVBoxLayout(self.register_widget)
        reg_main_layout.setAlignment(Qt.AlignCenter)

        reg_card = QFrame()
        reg_card.setObjectName("card")
        reg_card.setFixedWidth(380)
        reg_layout = QVBoxLayout(reg_card)
        reg_layout.setContentsMargins(30, 40, 30, 40)
        reg_layout.setSpacing(15)

        # Title
        reg_title = QLabel("Create Account")
        reg_title.setObjectName("title")
        reg_title.setAlignment(Qt.AlignCenter)
        reg_layout.addWidget(reg_title)

        reg_subtitle = QLabel("Get started with your free account")
        reg_subtitle.setObjectName("subtitle")
        reg_subtitle.setAlignment(Qt.AlignCenter)
        reg_layout.addWidget(reg_subtitle)
        reg_layout.addSpacing(10)

        # Inputs
        self.reg_user_input = QLineEdit()
        self.reg_user_input.setPlaceholderText("Username")
        reg_layout.addWidget(self.reg_user_input)

        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("Email Address (Optional)")
        reg_layout.addWidget(self.reg_email_input)

        self.reg_pass_input = QLineEdit()
        self.reg_pass_input.setPlaceholderText("Password")
        self.reg_pass_input.setEchoMode(QLineEdit.Password)
        reg_layout.addWidget(self.reg_pass_input)

        # Status label
        self.reg_status_label = QLabel("")
        self.reg_status_label.setAlignment(Qt.AlignCenter)
        self.reg_status_label.setWordWrap(True)
        reg_layout.addWidget(self.reg_status_label)

        # Buttons
        self.register_btn = QPushButton("Create Account")
        self.register_btn.clicked.connect(self.register_clicked.emit)
        reg_layout.addWidget(self.register_btn)

        # Toggle to login
        toggle_layout2 = QHBoxLayout()
        toggle_layout2.addWidget(QLabel("Already have an account?"))
        self.go_to_login_btn = QPushButton("Sign In")
        self.go_to_login_btn.setObjectName("secondaryButton")
        self.go_to_login_btn.clicked.connect(self.show_login_layout)
        toggle_layout2.addWidget(self.go_to_login_btn)
        reg_layout.addLayout(toggle_layout2)

        reg_main_layout.addWidget(reg_card)
        self.stacked_layout.addWidget(self.register_widget)

    # Getters
    def get_login_username(self) -> str:
        return self.login_user_input.text().strip()

    def get_login_password(self) -> str:
        return self.login_pass_input.text()

    def get_reg_username(self) -> str:
        return self.reg_user_input.text().strip()

    def get_reg_email(self) -> str:
        return self.reg_email_input.text().strip()

    def get_reg_password(self) -> str:
        return self.reg_pass_input.text()

    # View manipulators
    def show_login_layout(self):
        self.clear_status()
        self.stacked_layout.setCurrentIndex(0)

    def show_register_layout(self):
        self.clear_status()
        self.stacked_layout.setCurrentIndex(1)

    def set_login_error(self, message: str):
        self.login_status_label.setObjectName("errorLabel")
        self.login_status_label.setStyleSheet("color: #f87171;")  # Force color refresh
        self.login_status_label.setText(message)

    def set_reg_error(self, message: str):
        self.reg_status_label.setObjectName("errorLabel")
        self.reg_status_label.setStyleSheet("color: #f87171;")
        self.reg_status_label.setText(message)

    def set_reg_success(self, message: str):
        self.reg_status_label.setObjectName("successLabel")
        self.reg_status_label.setStyleSheet("color: #4ade80;")
        self.reg_status_label.setText(message)

    def clear_status(self):
        self.login_status_label.setText("")
        self.reg_status_label.setText("")

    def clear_inputs(self):
        self.login_user_input.clear()
        self.login_pass_input.clear()
        self.reg_user_input.clear()
        self.reg_email_input.clear()
        self.reg_pass_input.clear()
