from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout, QAbstractItemView
from PySide6.QtCore import Qt, Signal

class BookingView(QWidget):
    book_submitted = Signal()
    cancel_clicked = Signal(str)  # Emits booking ID to cancel

    def __init__(self):
        super().__init__()
        self.flight_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Flight Reservations")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        # Horizontal layout splitting Form (left) and Bookings history (right)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # 1. Booking Form (Left Panel)
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_frame.setFixedWidth(350)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        form_title = QLabel("BOOK A NEW FLIGHT")
        form_title.setObjectName("sectionHeader")
        form_layout.addWidget(form_title)

        # Flight preview panel
        self.flight_preview_frame = QFrame()
        self.flight_preview_frame.setStyleSheet("background-color: #1e293b; border-radius: 6px; border: 1px solid #334155;")
        preview_layout = QGridLayout(self.flight_preview_frame)
        preview_layout.addWidget(QLabel("Selected Flight:"), 0, 0)
        self.flight_num_lbl = QLabel("None")
        self.flight_num_lbl.setStyleSheet("font-weight: bold; color: #38bdf8;")
        preview_layout.addWidget(self.flight_num_lbl, 0, 1)
        
        preview_layout.addWidget(QLabel("Route:"), 1, 0)
        self.route_lbl = QLabel("-")
        self.route_lbl.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(self.route_lbl, 1, 1)

        preview_layout.addWidget(QLabel("Price:"), 2, 0)
        self.price_lbl = QLabel("-")
        preview_layout.addWidget(self.price_lbl, 2, 1)
        form_layout.addWidget(self.flight_preview_frame)

        # Input fields
        self.passenger_input = QLineEdit()
        self.passenger_input.setPlaceholderText("Passenger Full Name")
        form_layout.addWidget(self.passenger_input)

        self.passport_input = QLineEdit()
        self.passport_input.setPlaceholderText("Passport Number")
        form_layout.addWidget(self.passport_input)

        self.status_lbl = QLabel("")
        self.status_lbl.setWordWrap(True)
        form_layout.addWidget(self.status_lbl)

        self.submit_btn = QPushButton("Confirm Booking")
        self.submit_btn.setMinimumHeight(35)
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(self.book_submitted.emit)
        form_layout.addWidget(self.submit_btn)

        form_layout.addStretch()
        split_layout.addWidget(form_frame)

        # 2. My Bookings History Table (Right Panel)
        history_frame = QFrame()
        history_frame.setObjectName("card")
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(20, 20, 20, 20)
        history_layout.setSpacing(15)

        history_title = QLabel("MY RESERVATION HISTORY")
        history_title.setObjectName("sectionHeader")
        history_layout.addWidget(history_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Flight", "Route", "Passenger", "Passport", "Status", "Booked Date"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.itemSelectionChanged.connect(self.handle_selection_changed)
        history_layout.addWidget(self.history_table)

        # Action bar under table
        table_action_layout = QHBoxLayout()
        self.table_status_lbl = QLabel("")
        table_action_layout.addWidget(self.table_status_lbl)
        table_action_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel Selected Ticket")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.emit_cancel_clicked)
        table_action_layout.addWidget(self.cancel_btn)

        history_layout.addLayout(table_action_layout)
        split_layout.addWidget(history_frame)

        layout.addLayout(split_layout)

        # Local booking ID mapping for table rows
        self.booking_ids = []

    def set_prefilled_flight(self, flight: dict):
        self.flight_id = flight["id"]
        self.flight_num_lbl.setText(flight["flight_number"])
        self.route_lbl.setText(f"{flight['origin']} ➔ {flight['destination']}")
        self.price_lbl.setText(f"${flight['price']:.2f}")
        self.submit_btn.setEnabled(True)
        self.status_lbl.setText("")

    def get_passenger_name(self) -> str:
        return self.passenger_input.text().strip()

    def get_passport_number(self) -> str:
        return self.passport_input.text().strip()

    def set_status(self, text: str, is_error: bool = False):
        if is_error:
            self.status_lbl.setObjectName("errorLabel")
            self.status_lbl.setStyleSheet("color: #f87171;")
        else:
            self.status_lbl.setObjectName("successLabel")
            self.status_lbl.setStyleSheet("color: #4ade80;")
        self.status_lbl.setText(text)

    def set_table_status(self, text: str, is_error: bool = False):
        if is_error:
            self.table_status_lbl.setObjectName("errorLabel")
            self.table_status_lbl.setStyleSheet("color: #f87171;")
        else:
            self.table_status_lbl.setObjectName("successLabel")
            self.table_status_lbl.setStyleSheet("color: #4ade80;")
        self.table_status_lbl.setText(text)

    def clear_form(self):
        self.flight_id = None
        self.flight_num_lbl.setText("None")
        self.route_lbl.setText("-")
        self.price_lbl.setText("-")
        self.passenger_input.clear()
        self.passport_input.clear()
        self.submit_btn.setEnabled(False)

    def update_history(self, bookings: list[dict]):
        self.history_table.setRowCount(0)
        self.booking_ids = []
        self.cancel_btn.setEnabled(False)

        self.history_table.setRowCount(len(bookings))
        for row, booking in enumerate(bookings):
            self.booking_ids.append(booking["id"])
            
            self.history_table.setItem(row, 0, QTableWidgetItem(booking["flight_number"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"{booking['origin']} -> {booking['destination']}"))
            self.history_table.setItem(row, 2, QTableWidgetItem(booking["passenger_name"]))
            self.history_table.setItem(row, 3, QTableWidgetItem(booking["passport_number"]))
            
            # Highlight status
            status_item = QTableWidgetItem(booking["status"])
            if booking["status"] == "Cancelled":
                status_item.setForeground(Qt.red)
            else:
                status_item.setForeground(Qt.green)
            self.history_table.setItem(row, 4, status_item)

            # Date
            date_str = booking.get("created_at", "")
            if date_str:
                # Format to short date
                date_str = date_str.split("T")[0]
            self.history_table.setItem(row, 5, QTableWidgetItem(date_str))

    def handle_selection_changed(self):
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            self.cancel_btn.setEnabled(False)
            return

        row_idx = selected_rows[0].row()
        # Enable cancellation only for active bookings
        status_text = self.history_table.item(row_idx, 4).text()
        self.cancel_btn.setEnabled(status_text == "Active")

    def emit_cancel_clicked(self):
        selected_rows = self.history_table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            booking_id = self.booking_ids[row_idx]
            self.cancel_clicked.emit(booking_id)
