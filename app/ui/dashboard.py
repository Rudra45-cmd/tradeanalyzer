"""Modern dark-themed PyQt5 dashboard starter."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QListWidget, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg


class Dashboard(QMainWindow):
    """Desktop dashboard for live chart, prediction, confidence, and history."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TradeAnalyzer AI Scalping Assistant")
        self.setMinimumSize(1100, 720)
        pg.setConfigOption("background", "#0f172a")
        pg.setConfigOption("foreground", "#e2e8f0")

        container = QWidget()
        layout = QVBoxLayout(container)
        self.prediction_label = QLabel("Prediction: NO TRADE")
        self.prediction_label.setAlignment(Qt.AlignCenter)
        self.prediction_label.setStyleSheet("font-size: 28px; color: #38bdf8; padding: 16px;")
        self.chart = pg.PlotWidget(title="BTCUSDT Live Chart")
        self.history = QListWidget()
        layout.addWidget(self.prediction_label)
        layout.addWidget(self.chart, stretch=3)
        layout.addWidget(QLabel("Signal History"))
        layout.addWidget(self.history, stretch=1)
        self.setCentralWidget(container)
        self.setStyleSheet("QMainWindow, QWidget { background: #020617; color: #e2e8f0; }")

    def update_prediction(self, text: str) -> None:
        """Update the headline prediction label and append signal history."""
        self.prediction_label.setText(text)
        self.history.insertItem(0, text)


def run_dashboard() -> None:
    """Run the PyQt5 dashboard."""
    app = QApplication([])
    dashboard = Dashboard()
    dashboard.show()
    app.exec_()
