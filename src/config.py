"""
Konfiguracja aplikacji - klucze API, ustawienia domyślne
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BinanceConfig:
    """Konfiguracja połączenia z Binance"""
    api_key: str = ""  # Ustaw w zmiennych środowiskowych
    api_secret: str = ""  # Ustaw w zmiennych środowiskowych
    testnet: bool = False
    base_url: str = "https://api.binance.com"
    ws_base_url: str = "wss://stream.binance.com:9443/ws/"

@dataclass
class DatabaseConfig:
    """Konfiguracja bazy danych"""
    db_path: str = "data/crypto_analyzer.db"
    echo: bool = False  # SQLAlchemy echo dla debugowania

@dataclass
class ChartConfig:
    """Konfiguracja wykresów"""
    default_symbol: str = "BTCUSDT"
    default_interval: str = "1m"
    max_candles: int = 1000
    update_interval: int = 1000  # ms
    
    # Kolory dla motywów
    colors_light: Dict[str, str] = None
    colors_dark: Dict[str, str] = None
    
    def __post_init__(self):
        if self.colors_light is None:
            self.colors_light = {
                'up': '#26A69A',
                'down': '#EF5350',
                'background': '#FFFFFF',
                'grid': '#E0E0E0',
                'text': '#000000'
            }
        
        if self.colors_dark is None:
            self.colors_dark = {
                'up': '#4CAF50',
                'down': '#F44336',
                'background': '#1E1E1E',
                'grid': '#404040',
                'text': '#FFFFFF'
            }

class AppConfig:
    """Główna konfiguracja aplikacji"""
    
    def __init__(self):
        self.binance = BinanceConfig(
            api_key=os.getenv('BINANCE_API_KEY', ''),
            api_secret=os.getenv('BINANCE_API_SECRET', '')
        )
        self.database = DatabaseConfig()
        self.chart = ChartConfig()
        
    def get_available_intervals(self) -> list:
        """Zwraca dostępne interwały dla Binance"""
        return ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    
    def get_popular_symbols(self) -> list:
        """Zwraca popularne pary handlowe"""
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT'
        ]

# Singleton instancja
config = AppConfig()