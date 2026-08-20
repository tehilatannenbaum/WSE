from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
from PySide6.QtCore import Qt, Signal

class DetailsView(QWidget):
    book_clicked = Signal(int)  # Emits flight ID to book

    def __init__(self):
        super().__init__()
        self.flight_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title
        title_label = QLabel("Flight & Destination Details")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Check flight specifications and live destination weather forecast")
        subtitle_label.setObjectName("subtitle")
        layout.addWidget(subtitle_label)

        # Main content card
        self.main_card = QFrame()
        self.main_card.setObjectName("card")
        card_layout = QVBoxLayout(self.main_card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)

        # Flight Details Section
        flight_sec_label = QLabel("FLIGHT SPECIFICATIONS")
        flight_sec_label.setObjectName("sectionHeader")
        card_layout.addWidget(flight_sec_label)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("Flight Number:"), 0, 0)
        self.flight_num_lbl = QLabel("-")
        self.flight_num_lbl.setStyleSheet("font-weight: bold; color: #ffffff;")
        grid.addWidget(self.flight_num_lbl, 0, 1)

        grid.addWidget(QLabel("Route:"), 1, 0)
        self.route_lbl = QLabel("-")
        self.route_lbl.setStyleSheet("font-weight: bold; color: #ffffff;")
        grid.addWidget(self.route_lbl, 1, 1)

        grid.addWidget(QLabel("Departure Time:"), 2, 0)
        self.departure_lbl = QLabel("-")
        self.departure_lbl.setStyleSheet("font-weight: bold; color: #ffffff;")
        grid.addWidget(self.departure_lbl, 2, 1)

        grid.addWidget(QLabel("Price per Ticket:"), 3, 0)
        self.price_lbl = QLabel("-")
        self.price_lbl.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 16px;")
        grid.addWidget(self.price_lbl, 3, 1)

        grid.addWidget(QLabel("Seats Remaining:"), 4, 0)
        self.seats_lbl = QLabel("-")
        self.seats_lbl.setStyleSheet("font-weight: bold; color: #ffffff;")
        grid.addWidget(self.seats_lbl, 4, 1)

        card_layout.addLayout(grid)

        # Separator Line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet("background-color: #232d3f;")
        card_layout.addWidget(sep)

        # Live Weather Section
        weather_sec_label = QLabel("LIVE DESTINATION WEATHER (Open-Meteo API)")
        weather_sec_label.setObjectName("sectionHeader")
        card_layout.addWidget(weather_sec_label)

        weather_grid = QGridLayout()
        weather_grid.setSpacing(15)

        weather_grid.addWidget(QLabel("Current Temperature:"), 0, 0)
        self.temp_lbl = QLabel("Loading weather...")
        self.temp_lbl.setStyleSheet("font-weight: bold; color: #f59e0b; font-size: 16px;")
        weather_grid.addWidget(self.temp_lbl, 0, 1)

        weather_grid.addWidget(QLabel("Conditions:"), 1, 0)
        self.cond_lbl = QLabel("-")
        self.cond_lbl.setStyleSheet("font-weight: bold; color: #ffffff;")
        weather_grid.addWidget(self.cond_lbl, 1, 1)

        weather_grid.addWidget(QLabel("Wind Speed:"), 2, 0)
        self.wind_lbl = QLabel("-")
        self.wind_lbl.setStyleSheet("font-weight: bold; color: #ffffff;")
        weather_grid.addWidget(self.wind_lbl, 2, 1)

        card_layout.addLayout(weather_grid)
        card_layout.addSpacing(10)

        # Action Buttons
        self.book_btn = QPushButton("Book This Flight Now")
        self.book_btn.setMinimumHeight(40)
        self.book_btn.clicked.connect(self.handle_book_clicked)
        card_layout.addWidget(self.book_btn)

        layout.addWidget(self.main_card)
        layout.addStretch()

        # Disable main card until a flight is loaded
        self.main_card.setVisible(False)
        self.placeholder_lbl = QLabel("Select a flight from the Search tab to view details.")
        self.placeholder_lbl.setAlignment(Qt.AlignCenter)
        self.placeholder_lbl.setStyleSheet("color: #64748b; font-size: 14px;")
        layout.addWidget(self.placeholder_lbl)

    def set_flight_data(self, flight: dict):
        self.flight_id = flight["id"]
        self.flight_num_lbl.setText(flight["flight_number"])
        self.route_lbl.setText(f"{flight['origin']} ➔ {flight['destination']}")
        self.departure_lbl.setText(flight["departure_time"])
        self.price_lbl.setText(f"${flight['price']:.2f}")
        self.seats_lbl.setText(str(flight["available_seats"]))
        
        self.placeholder_lbl.setVisible(False)
        self.main_card.setVisible(True)
        self.book_btn.setEnabled(flight["available_seats"] > 0)
        if flight["available_seats"] <= 0:
            self.book_btn.setText("Flight Sold Out")
        else:
            self.book_btn.setText("Book This Flight Now")

    def set_weather_data(self, weather: dict):
        temp = weather.get("temperature", 0.0)
        cond = weather.get("conditions", "Unknown")
        wind = weather.get("windspeed", 0.0)
        
        self.temp_lbl.setText(f"{temp}°C")
        self.cond_lbl.setText(cond)
        self.wind_lbl.setText(f"{wind} km/h")

    def show_weather_loading(self):
        self.temp_lbl.setText("Updating weather forecast...")
        self.cond_lbl.setText("-")
        self.wind_lbl.setText("-")

    def handle_book_clicked(self):
        if self.flight_id is not None:
            self.book_clicked.emit(self.flight_id)
