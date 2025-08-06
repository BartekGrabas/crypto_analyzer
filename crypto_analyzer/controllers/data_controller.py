"""Kontroler odpowiedzialny za pobieranie danych z Binance.

Zarządza strumieniami WebSocket oraz zapytaniami REST i przekazuje
zaktualizowane dane do stanu aplikacji oraz widoków.
"""

from __future__ import annotations

import logging
import threading
from typing import List, Optional

from ..models.binance_client import BinanceClient
from ..models.database import Database
from ..models.app_state import AppState, MarketFrame
from ..config import config

logger = logging.getLogger(__name__)


class DataController:
    """Obsługuje komunikację z API Binance."""

    def __init__(self) -> None:
        self.app_state = AppState()
        self.client = BinanceClient(
            api_key=config.binance.api_key,
            api_secret=config.binance.api_secret,
            testnet=config.binance.testnet,
        )

        self.db = Database(config.database.db_path)
        self.db.create_table(
            """
            CREATE TABLE IF NOT EXISTS klines (
                timestamp INTEGER PRIMARY KEY,
                symbol TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                interval TEXT
            )
            """
        )

        self._kline_socket: Optional[str] = None
        self._depth_socket: Optional[str] = None
        self._last_orderbook: dict = {}
        self._lock = threading.Lock()

        self.symbol = self.app_state.current_symbol
        self.interval = self.app_state.current_interval

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start_streaming(self) -> None:
        """Uruchamia strumienie danych."""
        self.stop_streaming()

        try:
            self._load_initial_data()
        except Exception as exc:  # pragma: no cover - logowanie błędów
            logger.error("Nie udało się pobrać danych początkowych: %s", exc)
            self.app_state.emit_error(str(exc))
            return

        self._kline_socket = self.client.start_kline_socket(
            symbol=self.symbol.lower(),
            interval=self.interval,
            callback=self._handle_kline,
        )
        self._depth_socket = self.client.start_depth_socket(
            symbol=self.symbol.lower(),
            callback=self._handle_depth,
        )

        self.app_state.set_connection_status(True)

    def stop_streaming(self) -> None:
        """Zatrzymuje wszystkie aktywne strumienie."""
        try:
            self.client.stop()
        except Exception as exc:  # pragma: no cover - logowanie błędów
            logger.warning("Błąd podczas zatrzymywania strumienia: %s", exc)

        self.app_state.set_connection_status(False)

    def change_symbol_interval(self, symbol: str, interval: str) -> None:
        """Zmienia symbol/interwał i restartuje strumienie."""
        with self._lock:
            self.symbol = symbol
            self.interval = interval
        self.start_streaming()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_initial_data(self) -> None:
        """Pobiera historię świec przez REST i aktualizuje AppState."""
        klines = self.client.get_klines(
            symbol=self.symbol.upper(),
            interval=self.interval,
            limit=500,
        )

        for kline in klines:
            frame = self._kline_to_market_frame(kline)
            self.app_state.update_market_data(frame)
            self._save_frame(frame)

    def _kline_to_market_frame(self, kline: List) -> MarketFrame:
        """Konwertuje kline na strukturę MarketFrame."""
        return MarketFrame(
            timestamp=int(kline[0]),
            symbol=self.symbol.upper(),
            open_price=float(kline[1]),
            high_price=float(kline[2]),
            low_price=float(kline[3]),
            close_price=float(kline[4]),
            volume=float(kline[5]),
            interval=self.interval,
            bids=self._last_orderbook.get("bids", []),
            asks=self._last_orderbook.get("asks", []),
        )

    def _save_frame(self, frame: MarketFrame) -> None:
        """Zapisuje ramkę rynku w bazie danych."""
        try:
            self.db.insert(
                "klines",
                {
                    "timestamp": frame.timestamp,
                    "symbol": frame.symbol,
                    "open": frame.open_price,
                    "high": frame.high_price,
                    "low": frame.low_price,
                    "close": frame.close_price,
                    "volume": frame.volume,
                    "interval": frame.interval,
                },
                replace=True,
            )
        except Exception as exc:  # pragma: no cover - logowanie błędów
            logger.warning("Błąd zapisu do bazy danych: %s", exc)

    def _handle_kline(self, msg: dict) -> None:
        """Obsługuje wiadomości kline z WebSocket."""
        try:
            kline = msg.get("k")
            if not kline or not kline.get("x"):
                return  # interesują nas tylko zakończone świece

            frame = MarketFrame(
                timestamp=int(kline["t"]),
                symbol=kline["s"],
                open_price=float(kline["o"]),
                high_price=float(kline["h"]),
                low_price=float(kline["l"]),
                close_price=float(kline["c"]),
                volume=float(kline["v"]),
                interval=kline["i"],
                bids=self._last_orderbook.get("bids", []),
                asks=self._last_orderbook.get("asks", []),
            )
            self.app_state.update_market_data(frame)
            self._save_frame(frame)
        except Exception as exc:  # pragma: no cover - logowanie błędów
            logger.error("Błąd przetwarzania kline: %s", exc)

    def _handle_depth(self, msg: dict) -> None:
        """Obsługuje aktualizacje order book."""
        try:
            bids = [(float(p), float(q)) for p, q in msg.get("b", [])]
            asks = [(float(p), float(q)) for p, q in msg.get("a", [])]
            self._last_orderbook = {"bids": bids, "asks": asks}
        except Exception as exc:  # pragma: no cover - logowanie błędów
            logger.error("Błąd przetwarzania order book: %s", exc)
