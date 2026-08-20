from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QLineSeries
from PySide6.QtCore import Qt

class StatisticsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title
        title_label = QLabel("Travel Analytics & Booking Trends")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Visualize average ticket pricing and monthly volume trends")
        subtitle_label.setObjectName("subtitle")
        layout.addWidget(subtitle_label)

        # Layout for charts (side-by-side)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # 1. Bar Chart Container
        self.bar_chart = QChart()
        self.bar_chart.setTitle("Average Ticket Price by Destination ($)")
        self.bar_chart.setTheme(QChart.ChartThemeDark)
        self.bar_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.bar_chart_view = QChartView(self.bar_chart)
        self.bar_chart_view.setRenderHint(QPainter.Antialiasing)
        self.bar_chart_view.setStyleSheet("background-color: #161925; border-radius: 10px; border: 1px solid #232d3f;")
        charts_layout.addWidget(self.bar_chart_view)

        # 2. Line Chart Container
        self.line_chart = QChart()
        self.line_chart.setTitle("Active Bookings Frequency by Month")
        self.line_chart.setTheme(QChart.ChartThemeDark)
        self.line_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.line_chart_view = QChartView(self.line_chart)
        self.line_chart_view.setRenderHint(QPainter.Antialiasing)
        self.line_chart_view.setStyleSheet("background-color: #161925; border-radius: 10px; border: 1px solid #232d3f;")
        charts_layout.addWidget(self.line_chart_view)

        # Info Label for Empty State
        self.info_label = QLabel("No active bookings registered yet. Chart will populate after reservations are made.")
        self.info_label.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold; background-color: #1e293b; padding: 8px; border-radius: 5px; border: 1px solid #334155;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        self.info_label.hide()

        layout.addLayout(charts_layout)
        
        # Style titles
        title_font = QFont("Segoe UI", 12, QFont.Bold)
        self.bar_chart.setTitleFont(title_font)
        self.line_chart.setTitleFont(title_font)
        
        self.bar_chart.setBackgroundVisible(False)
        self.line_chart.setBackgroundVisible(False)

    def update_charts(self, avg_prices: list[dict], volume: list[dict]):
        # Check for empty booking volume state
        total_bookings = sum(item["count"] for item in volume)
        if total_bookings == 0:
            self.info_label.show()
        else:
            self.info_label.hide()
        # Clear existing series & axes
        self.bar_chart.removeAllSeries()
        for axis in list(self.bar_chart.axes()):
            self.bar_chart.removeAxis(axis)
            
        self.line_chart.removeAllSeries()
        for axis in list(self.line_chart.axes()):
            self.line_chart.removeAxis(axis)

        # ==========================================
        # 1. Update Bar Chart
        # ==========================================
        bar_set = QBarSet("Average Price")
        bar_set.setColor(QColor("#4f46e5")) # Sleek Indigo
        
        categories = []
        max_price = 0.0
        
        for item in avg_prices:
            categories.append(item["destination"])
            bar_set.append(item["avg_price"])
            if item["avg_price"] > max_price:
                max_price = item["avg_price"]
                
        bar_series = QBarSeries()
        bar_series.append(bar_set)
        self.bar_chart.addSeries(bar_series)
        
        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.bar_chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max_price * 1.15 if max_price > 0 else 100)
        axis_y.setLabelFormat("$%d")
        self.bar_chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        # ==========================================
        # 2. Update Line Chart
        # ==========================================
        line_series = QLineSeries()
        line_series.setName("Monthly Reservations")
        line_series.setColor(QColor("#06b6d4")) # Bright Cyan
        
        line_categories = []
        max_count = 0
        
        for i, item in enumerate(volume):
            line_categories.append(item["month"])
            line_series.append(i, item["count"])
            if item["count"] > max_count:
                max_count = item["count"]
                
        self.line_chart.addSeries(line_series)
        
        # Line Chart Axes
        axis_line_x = QBarCategoryAxis()
        axis_line_x.append(line_categories)
        self.line_chart.addAxis(axis_line_x, Qt.AlignBottom)
        line_series.attachAxis(axis_line_x)
        
        axis_line_y = QValueAxis()
        axis_line_y.setRange(0, max_count + 5 if max_count > 0 else 10)
        axis_line_y.setLabelFormat("%d")
        self.line_chart.addAxis(axis_line_y, Qt.AlignLeft)
        line_series.attachAxis(axis_line_y)
