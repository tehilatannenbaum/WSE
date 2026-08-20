import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core elements
from frontend.core.api_client import api_client

# Import Microfrontends Views & Presenters
from frontend.modules.auth.view import AuthView
from frontend.modules.auth.presenter import AuthPresenter

from frontend.modules.search.view import SearchView
from frontend.modules.search.presenter import SearchPresenter

from frontend.modules.details.view import DetailsView
from frontend.modules.details.presenter import DetailsPresenter

from frontend.modules.booking.view import BookingView
from frontend.modules.booking.presenter import BookingPresenter

from frontend.modules.statistics.view import StatisticsView
from frontend.modules.statistics.presenter import StatisticsPresenter

from frontend.modules.ai_advisor.view import AIAdvisorView
from frontend.modules.ai_advisor.presenter import AIAdvisorPresenter

# Import App Shell
from frontend.app_shell.view import AppShellView
from frontend.app_shell.presenter import AppShellPresenter

def load_stylesheet(app: QApplication):
    qss_file_path = os.path.join(os.path.dirname(__file__), "core", "style.qss")
    if os.path.exists(qss_file_path):
        with open(qss_file_path, "r", encoding="utf-8") as f:
            stylesheet_content = f.read()
            app.setStyleSheet(stylesheet_content)
    else:
        print(f"Warning: Stylesheet not found at {qss_file_path}")

def main():
    # Initialize PySide Application
    app = QApplication(sys.argv)
    
    # Apply global premium theme styles
    load_stylesheet(app)

    # 1. Instantiate Views
    auth_view = AuthView()
    search_view = SearchView()
    details_view = DetailsView()
    booking_view = BookingView()
    stats_view = StatisticsView()
    ai_view = AIAdvisorView()

    # 2. Instantiate Presenters to bind business logic to the Views
    auth_presenter = AuthPresenter(auth_view)
    search_presenter = SearchPresenter(search_view)
    details_presenter = DetailsPresenter(details_view)
    booking_presenter = BookingPresenter(booking_view)
    stats_presenter = StatisticsPresenter(stats_view)
    ai_presenter = AIAdvisorPresenter(ai_view)

    # 3. Assemble and initialize the App Shell
    shell_view = AppShellView(
        auth_widget=auth_view,
        search_widget=search_view,
        details_widget=details_view,
        booking_widget=booking_view,
        stats_widget=stats_view,
        ai_widget=ai_view
    )
    shell_presenter = AppShellPresenter(shell_view)

    # Show application shell
    shell_view.show()
    
    # Run PySide Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
