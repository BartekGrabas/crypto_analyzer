"""
Punkt wejścia aplikacji
"""

import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Dodaj src do ścieżki
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dodaj katalog nadrzędny src do sys.path, aby umożliwić import modeli
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from views.main_window import MainWindow
from models.app_state import AppState

def setup_logging():
    """Konfiguracja logowania"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('crypto_analyzer.log')
        ]
    )

def create_data_directory():
    """Tworzy katalog dla bazy danych jeśli nie istnieje"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

def main():
    """Główna funkcja aplikacji"""
    
    # Konfiguracja środowiska
    setup_logging()
    create_data_directory()
    
    # Utworzenie aplikacji Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Crypto Market Analyzer")
    app.setApplicationVersion("1.0.0")
    
    # Inicjalizacja stanu aplikacji
    app_state = AppState()
    
    # Utworzenie głównego okna
    main_window = MainWindow()
    main_window.show()
    
    # Uruchomienie pętli zdarzeń
    sys.exit(app.exec())

if __name__ == "__main__":
    main()