from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt, Signal

class SearchView(QWidget):
    search_clicked = Signal()
    view_details_clicked = Signal(int)  # Emits selected flight ID

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title
        title_label = QLabel("Search Flight Schedules")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Explore and book your next journey")
        subtitle_label.setObjectName("subtitle")
        layout.addWidget(subtitle_label)

        # Search Controls Row
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.origin_input = QLineEdit()
        self.origin_input.setPlaceholderText("Origin (e.g. Tel Aviv)")
        search_row.addWidget(self.origin_input)

        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Destination (e.g. Paris)")
        search_row.addWidget(self.dest_input)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_clicked.emit)
        search_row.addWidget(self.search_btn)
        
        layout.addLayout(search_row)

        # Table for Results
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Flight No", "Origin", "Destination", "Departure Time", "Price", "Seats Left"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.itemSelectionChanged.connect(self.handle_selection_changed)
        layout.addWidget(self.results_table)

        # Bottom Actions Row
        actions_row = QHBoxLayout()
        self.status_label = QLabel("")
        actions_row.addWidget(self.status_label)
        
        actions_row.addStretch()
        
        self.details_btn = QPushButton("View Flight Details")
        self.details_btn.setEnabled(False)
        self.details_btn.clicked.connect(self.emit_view_details)
        actions_row.addWidget(self.details_btn)

        layout.addLayout(actions_row)
        
        # Flight ID mapping based on row index
        self.flight_ids = []

    def get_origin(self) -> str:
        return self.origin_input.text().strip()

    def get_destination(self) -> str:
        return self.dest_input.text().strip()

    def set_status(self, text: str, is_error: bool = False):
        if is_error:
            self.status_label.setObjectName("errorLabel")
            self.status_label.setStyleSheet("color: #f87171;")
        else:
            self.status_label.setObjectName("successLabel")
            self.status_label.setStyleSheet("color: #4ade80;")
        self.status_label.setText(text)

    def update_results(self, flights: list[dict]):
        self.results_table.setRowCount(0)
        self.flight_ids = []
        self.details_btn.setEnabled(False)
        
        if not flights:
            self.set_status("No flights found matching your search.", is_error=True)
            return

        self.set_status(f"Found {len(flights)} flights.", is_error=False)
        self.results_table.setRowCount(len(flights))

        for row, flight in enumerate(flights):
            self.flight_ids.append(flight["id"])
            
            # Populate columns
            self.results_table.setItem(row, 0, QTableWidgetItem(str(flight["flight_number"])))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(flight["origin"])))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(flight["destination"])))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(flight["departure_time"])))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"${flight['price']:.2f}"))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(flight["available_seats"])))

    def handle_selection_changed(self):
        selected_rows = self.results_table.selectionModel().selectedRows()
        self.details_btn.setEnabled(len(selected_rows) > 0)

    def emit_view_details(self):
        selected_rows = self.results_table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            flight_id = self.flight_ids[row_idx]
            self.view_details_clicked.emit(flight_id)
