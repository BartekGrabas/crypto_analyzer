"""
Singleton do zarządzania stanem aplikacji
"""

import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from PyQt6.QtCore import QObject, pyqtSignal

@dataclass
class MarketFrame:
    """Struktura danych reprezentująca ramkę rynkową"""
    timestamp: int
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    interval: str
    
    # Order book data
    bids: list = field(default_factory=list)  # [(price, quantity), ...]
    asks: list = field(default_factory=list)  # [(price, quantity), ...]

class AppState(QObject):
    """
    Singleton zarządzający stanem aplikacji
    """
    
    # Sygnały Qt
    dataUpdated = pyqtSignal(MarketFrame)
    connectionStatusChanged = pyqtSignal(bool)  # True = connected, False = disconnected
    errorOccurred = pyqtSignal(str)  # Komunikat błędu
    themeChanged = pyqtSignal(str)  # 'light' lub 'dark'
    indicatorConfigChanged = pyqtSignal()  # Zmiana konfiguracji wskaźników
    
    _instance: Optional['AppState'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self.__dict__.get('_initialized', False):
            return

        super().__init__()
        self._initialized = True
        
        # Stan aplikacji
        self.current_symbol: str = "BTCUSDT"
        self.current_interval: str = "1m"
        self.current_theme: str = "dark"
        self.is_connected: bool = False
        
        # Aktywne wskaźniki
        self.active_indicators: Dict[str, Dict[str, Any]] = {
            'sma_fast': {'enabled': False, 'period': 9},
            'sma_slow': {'enabled': False, 'period': 21},
            'bollinger_bands': {'enabled': False, 'period': 20, 'std_dev': 2},
            'keltner_channels': {'enabled': False, 'period': 20, 'atr_mult': 2}
        }
        
        # Ostatnie dane rynkowe
        self.latest_market_frame: Optional[MarketFrame] = None
        
        # Historia świec (cache)
        self.candle_history: list = []
        self.max_history_size: int = 1000
    
    def update_market_data(self, market_frame: MarketFrame):
        """Aktualizuje dane rynkowe i emituje sygnał"""
        self.latest_market_frame = market_frame
        
        # Aktualizuj historię świec
        self._update_candle_history(market_frame)
        
        # Emituj sygnał
        self.dataUpdated.emit(market_frame)
    
    def _update_candle_history(self, market_frame: MarketFrame):
        """Aktualizuje historię świec"""
        # Sprawdź czy to nowa świeca czy aktualizacja istniejącej
        if (self.candle_history and 
            self.candle_history[-1]['timestamp'] == market_frame.timestamp):
            # Aktualizuj ostatnią świecę
            self.candle_history[-1] = self._market_frame_to_dict(market_frame)
        else:
            # Dodaj nową świecę
            self.candle_history.append(self._market_frame_to_dict(market_frame))
            
            # Usuń stare świece jeśli przekroczono limit
            if len(self.candle_history) > self.max_history_size:
                self.candle_history.pop(0)
    
    def _market_frame_to_dict(self, market_frame: MarketFrame) -> dict:
        """Konwertuje MarketFrame do słownika"""
        return {
            'timestamp': market_frame.timestamp,
            'open': market_frame.open_price,
            'high': market_frame.high_price,
            'low': market_frame.low_price,
            'close': market_frame.close_price,
            'volume': market_frame.volume
        }
    
    def set_symbol_interval(self, symbol: str, interval: str):
        """Ustawia aktualny symbol i interwał"""
        if symbol != self.current_symbol or interval != self.current_interval:
            self.current_symbol = symbol
            self.current_interval = interval
            # Wyczyść historię przy zmianie symbolu/interwału
            self.candle_history.clear()
    
    def set_connection_status(self, connected: bool):
        """Ustawia status połączenia"""
        if self.is_connected != connected:
            self.is_connected = connected
            self.connectionStatusChanged.emit(connected)
    
    def emit_error(self, error_message: str):
        """Emituje sygnał błędu"""
        self.errorOccurred.emit(error_message)
    
    def set_theme(self, theme: str):
        """Ustawia motyw aplikacji"""
        if theme in ['light', 'dark'] and theme != self.current_theme:
            self.current_theme = theme
            self.themeChanged.emit(theme)
    
    def update_indicator(self, indicator_name: str, enabled: bool, **params):
        """Aktualizuje konfigurację wskaźnika"""
        if indicator_name in self.active_indicators:
            self.active_indicators[indicator_name]['enabled'] = enabled
            self.active_indicators[indicator_name].update(params)
            self.indicatorConfigChanged.emit()
    
    def get_enabled_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Zwraca listę włączonych wskaźników"""
        return {
            name: config
            for name, config in self.active_indicators.items()
            if config["enabled"]
        }

