"""Controller responsible for calculating technical indicators."""
from __future__ import annotations

from typing import Dict

import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

from models.models.app_state import AppState


class IndicatorController(QObject):
    """Calculates and updates technical indicators.

    The controller listens for new market data emitted by :class:`AppState`.
    When data arrives it calculates enabled indicators (e.g. SMA, Bollinger
    Bands) based on the candle history stored in ``AppState`` and emits a
    signal with the results. Views can connect to :attr:`indicatorUpdated` to
    receive new indicator values.
    """

    indicatorUpdated = pyqtSignal(str, dict)

    def __init__(self, app_state: AppState | None = None) -> None:
        super().__init__()
        self.app_state = app_state or AppState()
        # Recalculate indicators whenever new market data is available
        self.app_state.dataUpdated.connect(self._on_market_frame)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------
    def _on_market_frame(self, _frame) -> None:
        """Handle new market data coming from :class:`AppState`.

        Parameters
        ----------
        _frame: MarketFrame
            Incoming market frame (unused, data is taken from ``AppState``).
        """
        indicators = self.app_state.get_enabled_indicators()
        if not indicators or not self.app_state.candle_history:
            return

        data = pd.DataFrame(self.app_state.candle_history)
        if data.empty:
            return

        for name, cfg in indicators.items():
            try:
                if name.startswith("sma"):
                    period = int(cfg.get("period", 14))
                    value = self._calculate_sma(data, period)
                    if value is not None:
                        self.indicatorUpdated.emit(name, {"period": period, "value": value})
                elif name == "bollinger_bands":
                    period = int(cfg.get("period", 20))
                    std = float(cfg.get("std_dev", 2))
                    bands = self._calculate_bollinger_bands(data, period, std)
                    if bands:
                        self.indicatorUpdated.emit(name, bands)
                elif name == "keltner_channels":
                    period = int(cfg.get("period", 20))
                    atr_mult = float(cfg.get("atr_mult", 2))
                    channels = self._calculate_keltner_channels(data, period, atr_mult)
                    if channels:
                        self.indicatorUpdated.emit(name, channels)
            except Exception:
                # Indicator calculation errors should not stop the controller
                continue

    # ------------------------------------------------------------------
    # Indicator calculations
    # ------------------------------------------------------------------
    @staticmethod
    def _calculate_sma(df: pd.DataFrame, period: int) -> float | None:
        """Return the latest Simple Moving Average value."""
        if len(df) < period:
            return None
        sma = df["close"].rolling(window=period).mean()
        result = sma.iloc[-1]
        return float(result) if pd.notna(result) else None

    @staticmethod
    def _calculate_bollinger_bands(df: pd.DataFrame, period: int, std_dev: float) -> Dict[str, float] | None:
        """Return latest Bollinger Bands values."""
        if len(df) < period:
            return None
        rolling = df["close"].rolling(window=period)
        mean = rolling.mean().iloc[-1]
        std = rolling.std().iloc[-1]
        if pd.isna(mean) or pd.isna(std):
            return None
        upper = float(mean + std_dev * std)
        lower = float(mean - std_dev * std)
        return {"upper": upper, "middle": float(mean), "lower": lower}

    @staticmethod
    def _calculate_keltner_channels(df: pd.DataFrame, period: int, atr_mult: float) -> Dict[str, float] | None:
        """Return latest Keltner Channels values."""
        if len(df) < period:
            return None

        ema = df["close"].ewm(span=period, adjust=False).mean()
        tr1 = df["high"] - df["low"]
        tr2 = (df["high"] - df["close"].shift()).abs()
        tr3 = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        middle = ema.iloc[-1]
        atr_val = atr.iloc[-1]
        if pd.isna(middle) or pd.isna(atr_val):
            return None

        upper = float(middle + atr_mult * atr_val)
        lower = float(middle - atr_mult * atr_val)
        return {"upper": upper, "middle": float(middle), "lower": lower}
