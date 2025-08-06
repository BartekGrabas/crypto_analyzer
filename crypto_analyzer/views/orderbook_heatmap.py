"""Simple placeholder widget for order book heatmap."""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class OrderBookHeatmap(QWidget):
    """Placeholder order book heatmap widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Order book heatmap placeholder"))


