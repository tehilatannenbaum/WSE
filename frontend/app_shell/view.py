from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class AppShellView(QMainWindow):
    nav_changed = Signal(str)  # Emits selected tab name
    logout_clicked = Signal()

    def __init__(self, auth_widget: QWidget, search_widget: QWidget, details_widget: QWidget, booking_widget: QWidget, stats_widget: QWidget, ai_widget: QWidget):
        super().__init__()
        self.auth_widget = auth_widget
        self.search_widget = search_widget
        self.details_widget = details_widget
        self.booking_widget = booking_widget
        self.stats_widget = stats_widget
        self.ai_widget = ai_widget
        
        self.setWindowTitle("Flight Booking & Travel Assistant")
        self.resize(1100, 750)
        self.init_ui()

    def init_ui(self):
        # 1. Main outer central stacked widget (Index 0: Auth, Index 1: Main App)
        self.outer_stack = QStackedWidget()
        self.setCentralWidget(self.outer_stack)

        # Outer Index 0: Auth Screen
        self.outer_stack.addWidget(self.auth_widget)

        # Outer Index 1: Main App Screen (Sidebar + Content stack)
        self.app_widget = QWidget()
        app_layout = QHBoxLayout(self.app_widget)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)

        # Sidebar Frame
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(10, 30, 10, 30)
        sidebar_layout.setSpacing(10)

        # App Brand Logo/Label
        brand_label = QLabel("✈️ TravelGateway")
        brand_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 20px; padding-left: 10px;")
        sidebar_layout.addWidget(brand_label)

        # User profile badge
        self.user_badge = QLabel("Guest User")
        self.user_badge.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold; margin-bottom: 10px; padding-left: 10px;")
        sidebar_layout.addWidget(self.user_badge)

        # Navigation buttons
        self.nav_buttons = {}
        tabs = [
            ("Search", "🔍 Search Flights"),
            ("Details", "📋 Flight Details"),
            ("Bookings", "✈️ My Bookings"),
            ("Statistics", "📊 Analytics Charts"),
            ("AI Advisor", "🤖 AI Travel Advisor")
        ]

        for tab_id, tab_text in tabs:
            btn = QPushButton(tab_text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tab_id: self.on_nav_clicked(t))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[tab_id] = btn

        # Default select Search
        self.nav_buttons["Search"].setChecked(True)

        sidebar_layout.addStretch()

        # Logout Button at bottom
        self.logout_btn = QPushButton("🚪 Log Out")
        self.logout_btn.setObjectName("navButton")
        self.logout_btn.setStyleSheet("color: #ef4444;")
        self.logout_btn.clicked.connect(self.logout_clicked.emit)
        sidebar_layout.addWidget(self.logout_btn)

        app_layout.addWidget(self.sidebar_frame)

        # Inner Content Stack for tabs
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("mainContent")
        self.content_stack.addWidget(self.search_widget)   # Index 0
        self.content_stack.addWidget(self.details_widget)  # Index 1
        self.content_stack.addWidget(self.booking_widget)  # Index 2
        self.content_stack.addWidget(self.stats_widget)    # Index 3
        self.content_stack.addWidget(self.ai_widget)       # Index 4

        app_layout.addWidget(self.content_stack)

        self.outer_stack.addWidget(self.app_widget)
        self.outer_stack.setCurrentIndex(0) # Start in Auth

    def on_nav_clicked(self, tab_id: str):
        # Uncheck other buttons
        for tid, btn in self.nav_buttons.items():
            btn.setChecked(tid == tab_id)
        self.nav_changed.emit(tab_id)

    # Public View API
    def show_auth_screen(self):
        self.outer_stack.setCurrentIndex(0)

    def show_app_screen(self):
        self.outer_stack.setCurrentIndex(1)

    def set_user_profile(self, username: str):
        self.user_badge.setText(f"👤 {username}")

    def select_tab(self, tab_id: str):
        # Update sidebar button states
        for tid, btn in self.nav_buttons.items():
            btn.setChecked(tid == tab_id)

        # Switch stack index
        indices = {"Search": 0, "Details": 1, "Bookings": 2, "Statistics": 3, "AI Advisor": 4}
        if tab_id in indices:
            self.content_stack.setCurrentIndex(indices[tab_id])
