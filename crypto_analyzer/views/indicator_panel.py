"""Panel providing basic indicator toggles."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel

from ..models.app_state import AppState


class IndicatorPanel(QWidget):
    """Allows enabling or disabling sample indicators."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.app_state = AppState()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Wskaźniki"))

        self.sma_fast = QCheckBox("SMA Fast (9)")
        self.sma_fast.toggled.connect(lambda s: self.app_state.update_indicator("sma_fast", s))
        layout.addWidget(self.sma_fast)

        self.sma_slow = QCheckBox("SMA Slow (21)")
        self.sma_slow.toggled.connect(lambda s: self.app_state.update_indicator("sma_slow", s))
        layout.addWidget(self.sma_slow)

        self.bb = QCheckBox("Bollinger Bands")
        self.bb.toggled.connect(lambda s: self.app_state.update_indicator("bollinger_bands", s))
        layout.addWidget(self.bb)

        layout.addStretch()

