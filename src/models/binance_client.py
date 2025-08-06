"""Wrapper for Binance REST and WebSocket clients."""

from __future__ import annotations

from typing import Callable, Optional

from binance.client import Client
from binance import ThreadedWebsocketManager


class BinanceClient:
    """Simple wrapper around python-binance to unify access."""

    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False) -> None:
        self._client = Client(api_key=api_key, api_secret=api_secret, testnet=testnet)
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
        self._twm: Optional[ThreadedWebsocketManager] = None

    # ------------------------------------------------------------------
    # REST methods
    # ------------------------------------------------------------------
    def get_klines(self, symbol: str, interval: str, limit: int = 500):
        """Fetch kline/candlestick data."""
        return self._client.get_klines(symbol=symbol, interval=interval, limit=limit)

    # ------------------------------------------------------------------
    # WebSocket methods
    # ------------------------------------------------------------------
    def _ensure_twm(self) -> None:
        if self._twm is None:
            self._twm = ThreadedWebsocketManager(
                api_key=self._api_key,
                api_secret=self._api_secret,
                testnet=self._testnet,
            )
            self._twm.start()

    def start_kline_socket(self, symbol: str, interval: str, callback: Callable):
        """Start a kline WebSocket stream."""
        self._ensure_twm()
        assert self._twm is not None
        return self._twm.start_kline_socket(symbol=symbol, interval=interval, callback=callback)

    def start_depth_socket(self, symbol: str, callback: Callable):
        """Start a depth WebSocket stream."""
        self._ensure_twm()
        assert self._twm is not None
        return self._twm.start_depth_socket(symbol=symbol, callback=callback)

    def stop(self) -> None:
        """Stop all active WebSocket streams."""
        if self._twm:
            self._twm.stop()
            self._twm = None
