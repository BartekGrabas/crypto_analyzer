"""Simple placeholder widget for chart display."""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class ChartView(QWidget):
    """Placeholder chart widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Chart view placeholder"))

