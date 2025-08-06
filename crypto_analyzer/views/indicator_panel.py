"""Simple placeholder widget for indicator controls."""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class IndicatorPanel(QWidget):
    """Placeholder indicator panel widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Indicator panel placeholder"))

