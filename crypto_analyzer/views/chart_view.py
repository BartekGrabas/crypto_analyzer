"""Candlestick chart widget with optional technical indicators."""

from __future__ import annotations

import pandas as pd
import mplfinance as mpf
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from ..models.app_state import AppState
from ..config import config


class ChartView(QWidget):
    """Displays market data as a candlestick chart."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.app_state = AppState()

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        # React to state changes
        self.app_state.dataUpdated.connect(self._on_data)
        self.app_state.themeChanged.connect(lambda _t: self.plot())
        self.app_state.indicatorConfigChanged.connect(self.plot)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------
    def _on_data(self, _frame) -> None:
        """Replot chart when new market data arrives."""
        self.plot()

    # ------------------------------------------------------------------
    # Plotting helpers
    # ------------------------------------------------------------------
    def _get_style(self):
        theme = self.app_state.current_theme
        colors = config.chart.colors_dark if theme == "dark" else config.chart.colors_light
        mc = mpf.make_marketcolors(up=colors["up"], down=colors["down"])
        return mpf.make_mpf_style(
            marketcolors=mc,
            facecolor=colors["background"],
            edgecolor=colors["grid"],
            gridcolor=colors["grid"],
            rc={
                "axes.labelcolor": colors["text"],
                "axes.edgecolor": colors["text"],
                "xtick.color": colors["text"],
                "ytick.color": colors["text"],
            },
        )

    def plot(self) -> None:
        """Render candlestick chart with active indicators."""
        data = self.app_state.candle_history
        if not data:
            return

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        apds = []
        indicators = self.app_state.get_enabled_indicators()
        if "sma_fast" in indicators:
            period = indicators["sma_fast"].get("period", 9)
            df["sma_fast"] = df["close"].rolling(period).mean()
            apds.append(mpf.make_addplot(df["sma_fast"]))
        if "sma_slow" in indicators:
            period = indicators["sma_slow"].get("period", 21)
            df["sma_slow"] = df["close"].rolling(period).mean()
            apds.append(mpf.make_addplot(df["sma_slow"]))
        if "bollinger_bands" in indicators:
            period = indicators["bollinger_bands"].get("period", 20)
            std_dev = indicators["bollinger_bands"].get("std_dev", 2)
            ma = df["close"].rolling(period).mean()
            std = df["close"].rolling(period).std()
            df["bb_upper"] = ma + std_dev * std
            df["bb_lower"] = ma - std_dev * std
            apds.append(mpf.make_addplot(df["bb_upper"], color="grey"))
            apds.append(mpf.make_addplot(df["bb_lower"], color="grey"))

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        mpf.plot(
            df,
            type="candle",
            ax=ax,
            style=self._get_style(),
            addplot=apds,
            xrotation=15,
            warn_too_much_data=10000,
        )
        self.canvas.draw()

