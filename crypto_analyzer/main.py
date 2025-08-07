"""
Punkt wejścia aplikacji
"""

import sys
import logging
from pathlib import Path



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

def create_data_directory(path: str | Path = "data"):
    """Tworzy katalog dla bazy danych jeśli nie istnieje.

    Parameters
    ----------
    path: str | Path, optional
        Ścieżka do katalogu danych. Domyślnie ``"data"``.
    """
    data_dir = Path(path)
    data_dir.mkdir(exist_ok=True)

def main():
    """Główna funkcja aplikacji"""
    
    # Konfiguracja środowiska
    setup_logging()
    create_data_directory()

    # Importy lokalne wymagające PyQt6
    from PyQt6.QtWidgets import QApplication
    # Używamy bezwzględnych importów, aby skrypt można było uruchomić
    # również bez kontekstu pakietu (np. `python crypto_analyzer/main.py`).
    from crypto_analyzer.models.app_state import AppState
    from crypto_analyzer.views.main_window import MainWindow

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
