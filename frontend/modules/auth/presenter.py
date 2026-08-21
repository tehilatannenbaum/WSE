from PySide6.QtCore import QObject
from frontend.core.api_client import api_client
from frontend.core.event_bus import event_bus
from frontend.core.worker import RequestWorker
from frontend.modules.auth.view import AuthView

class AuthPresenter(QObject):
    def __init__(self, view: AuthView):
        super().__init__()
        self.view = view
        self._active_workers = set()

        # Bind view signals to presenter slots
        self.view.login_clicked.connect(self.handle_login)
        self.view.register_clicked.connect(self.handle_register)

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

    def handle_login(self):
        username = self.view.get_login_username()
        password = self.view.get_login_password()

        if not username or not password:
            self.view.set_login_error("Please enter both username and password.")
            return

        self.view.clear_status()
        self.view.login_btn.setEnabled(False)
        self.view.login_btn.setText("Signing In...")
        
        self._start_worker(
            "_login_worker",
            api_client.login,
            username,
            password,
            on_completed=self.on_login_completed
        )

    def on_login_completed(self, result):
        res, status_code = result
        if status_code == 200:
            # Login successful, fetch profile in background too
            self._start_worker(
                "_profile_worker",
                api_client.get_profile,
                on_completed=self.on_profile_completed
            )
        else:
            self.view.login_btn.setEnabled(True)
            self.view.login_btn.setText("Sign In")
            err_msg = res.get("detail", "Incorrect username or password.")
            self.view.set_login_error(err_msg)

    def on_profile_completed(self, result):
        profile, prof_status = result
        self.view.login_btn.setEnabled(True)
        self.view.login_btn.setText("Sign In")
        if prof_status == 200:
            self.view.clear_inputs()
            # Notify application that user has authenticated
            event_bus.emit("user_logged_in", profile)
        else:
            self.view.set_login_error("Failed to retrieve user profile.")

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
        self.view.register_btn.setEnabled(False)
        self.view.register_btn.setText("Creating Account...")
        
        self._start_worker(
            "_reg_worker",
            api_client.register,
            username,
            password,
            email,
            on_completed=self.on_register_completed
        )

    def on_register_completed(self, result):
        res, status_code = result
        self.view.register_btn.setEnabled(True)
        self.view.register_btn.setText("Create Account")
        
        username = self.view.get_reg_username()
        
        if status_code == 201:
            self.view.set_reg_success("Registration successful! You can now log in.")
            # Switch back to login form
            self.view.login_user_input.setText(username)
            self.view.login_pass_input.clear()
            self.view.show_login_layout()
        else:
            err_msg = res.get("detail", "Username already exists or invalid data.")
            self.view.set_reg_error(err_msg)
