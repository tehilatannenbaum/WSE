from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.app_shell.view import AppShellView

class AppShellPresenter(QObject):
    def __init__(self, view: AppShellView):
        super().__init__()
        self.view = view
        
        # Connect signals
        self.view.nav_changed.connect(self.handle_navigation)
        self.view.logout_clicked.connect(self.handle_logout)
        
        # Subscribe to global events
        event_bus.subscribe("user_logged_in", self.on_user_login)
        event_bus.subscribe("navigate_to_tab", self.on_navigate_request)
        event_bus.subscribe("flight_selected", self.on_flight_selected)

    def on_user_login(self, user_profile: dict):
        username = user_profile.get("username", "User")
        self.view.set_user_profile(username)
        # Show main interface
        self.view.show_app_screen()
        # Navigate to search by default
        self.handle_navigation("Search")

    def on_navigate_request(self, tab_id: str):
        self.view.select_tab(tab_id)

    def on_flight_selected(self, flight: dict):
        # Auto-switch to flight details when a flight is clicked in search
        self.view.select_tab("Details")

    def handle_navigation(self, tab_id: str):
        self.view.select_tab(tab_id)

    def handle_logout(self):
        api_client.clear_token()
        self.view.show_auth_screen()
