from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.modules.auth.view import AuthView

class AuthPresenter:
    def __init__(self, view: AuthView):
        self.view = view
        # Bind view signals to presenter slots
        self.view.login_clicked.connect(self.handle_login)
        self.view.register_clicked.connect(self.handle_register)

    def handle_login(self):
        username = self.view.get_login_username()
        password = self.view.get_login_password()

        if not username or not password:
            self.view.set_login_error("Please enter both username and password.")
            return

        self.view.clear_status()
        
        # Call API Client
        res, status_code = api_client.login(username, password)
        if status_code == 200:
            # Login successful, fetch profile
            profile, prof_status = api_client.get_profile()
            if prof_status == 200:
                self.view.clear_inputs()
                # Notify application that user has authenticated
                event_bus.emit("user_logged_in", profile)
            else:
                self.view.set_login_error("Failed to retrieve user profile.")
        else:
            err_msg = res.get("detail", "Incorrect username or password.")
            self.view.set_login_error(err_msg)

    def handle_register(self):
        username = self.view.get_reg_username()
        email = self.view.get_reg_email()
        password = self.view.get_reg_password()

        if not username or not password:
            self.view.set_reg_error("Please enter a username and password.")
            return

        if len(password) < 4:
            self.view.set_reg_error("Password must be at least 4 characters.")
            return

        self.view.clear_status()
        
        # Call API Client
        res, status_code = api_client.register(username, password, email)
        if status_code == 201:
            self.view.set_reg_success("Registration successful! You can now log in.")
            # Switch back to login form after a short delay or let user click
            self.view.login_user_input.setText(username)
            self.view.login_pass_input.clear()
            self.view.show_login_layout()
        else:
            err_msg = res.get("detail", "Username already exists or invalid data.")
            self.view.set_reg_error(err_msg)
