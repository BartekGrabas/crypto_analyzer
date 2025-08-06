"""
Główne okno aplikacji
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                            QToolBar, QComboBox, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from ..models.app_state import AppState
from ..controllers.data_controller import DataController
from .chart_view import ChartView
from .indicator_panel import IndicatorPanel
from .orderbook_heatmap import OrderBookHeatmap
from ..config import config

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Główne okno aplikacji"""
    
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.data_controller = DataController()
        
        self.setWindowTitle("Crypto Market Analyzer")
        self.setGeometry(100, 100, 1400, 800)
        
        self.setup_ui()
        self.setup_connections()
        self.load_theme(self.app_state.current_theme)
        
        # Start połączenia z danymi
        self.data_controller.start_streaming()
    
    def setup_ui(self):
        """Inicjalizacja interfejsu użytkownika"""
        
        # Główny widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Główny layout
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        self.create_toolbar()
        
        # Splitter dla głównych paneli
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Lewy panel - wskaźniki
        self.indicator_panel = IndicatorPanel()
        self.indicator_panel.setMaximumWidth(250)
        splitter.addWidget(self.indicator_panel)
        
        # Centralny widget - wykres
        chart_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Wykres świecowy
        self.chart_view = ChartView()
        chart_splitter.addWidget(self.chart_view)
        
        # Heat-mapa order book (prawa strona wykresu)
        self.orderbook_heatmap = OrderBookHeatmap()
        self.orderbook_heatmap.setMaximumWidth(100)
        chart_splitter.addWidget(self.orderbook_heatmap)
        
        # Proporcje dla chart_splitter
        chart_splitter.setSizes([800, 100])
        
        splitter.addWidget(chart_splitter)
        
        # Proporcje dla głównego splitter
        splitter.setSizes([250, 900])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Łączenie z Binance...")
    
    def create_toolbar(self):
        """Tworzy toolbar z kontrolkami"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Symbol selector
        toolbar.addWidget(QLabel("Symbol:"))
        self.symbol_combo = QComboBox()
        self.symbol_combo.setEditable(True)
        self.symbol_combo.addItems(config.get_popular_symbols())
        self.symbol_combo.setCurrentText(config.chart.default_symbol)
        toolbar.addWidget(self.symbol_combo)
        
        toolbar.addSeparator()
        
        # Interval buttons
        toolbar.addWidget(QLabel("Interwał:"))
        intervals = ['1m', '5m', '15m', '1h', '1d']
        self.interval_buttons = []
        
        for interval in intervals:
            btn = QPushButton(interval)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=interval: self.set_interval(i))
            self.interval_buttons.append(btn)
            toolbar.addWidget(btn)
        
        # Ustaw domyślny interwał
        self.interval_buttons[0].setChecked(True)  # 1m
        
        toolbar.addSeparator()
        
        # Theme toggle
        self.theme_button = QPushButton("🌙")  # Moon icon for dark mode
        self.theme_button.setToolTip("Przełącz motyw")
        self.theme_button.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_button)
    
    def setup_connections(self):
        """Konfiguruje połączenia sygnałów"""
        
        # App state signals
        self.app_state.dataUpdated.connect(self.on_data_updated)
        self.app_state.connectionStatusChanged.connect(self.on_connection_changed)
        self.app_state.errorOccurred.connect(self.on_error)
        self.app_state.themeChanged.connect(self.load_theme)
        
        # Symbol change
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
    
    def set_interval(self, interval: str):
        """Ustawia interwał i aktualizuje przyciski"""
        # Odznacz wszystkie przyciski
        for btn in self.interval_buttons:
            btn.setChecked(False)
        
        # Zaznacz wybrany
        for btn in self.interval_buttons:
            if btn.text() == interval:
                btn.setChecked(True)
                break
        
        # Aktualizuj dane
        symbol = self.symbol_combo.currentText()
        self.app_state.set_symbol_interval(symbol, interval)
        self.data_controller.change_symbol_interval(symbol, interval)
    
    def on_symbol_changed(self, symbol: str):
        """Obsługuje zmianę symbolu"""
        current_interval = self.get_current_interval()
        self.app_state.set_symbol_interval(symbol, current_interval)
        self.data_controller.change_symbol_interval(symbol, current_interval)
    
    def get_current_interval(self) -> str:
        """Zwraca aktualny interwał"""
        for btn in self.interval_buttons:
            if btn.isChecked():
                return btn.text()
        return '1m'
    
    def toggle_theme(self):
        """Przełącza motyw aplikacji"""
        current_theme = self.app_state.current_theme
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        self.app_state.set_theme(new_theme)
    
    def load_theme(self, theme: str):
        """Ładuje motyw aplikacji"""
        try:
            skins_dir = Path(__file__).resolve().parent.parent / "resources" / "skins"
            if theme == 'dark':
                self.theme_button.setText("☀️")  # Sun icon for light mode
                style_file = skins_dir / "dark.qss"
            else:
                self.theme_button.setText("🌙")  # Moon icon for dark mode
                style_file = skins_dir / "light.qss"

            try:
                self.setStyleSheet(style_file.read_text())
            except FileNotFoundError:
                logger.warning(f"Nie znaleziono pliku stylu: {style_file}")

        except Exception as e:
            logger.error(f"Błąd podczas ładowania motywu: {e}")
    
    def on_data_updated(self, market_frame):
        """Obsługuje aktualizację danych rynkowych"""
        # Aktualizuj status bar
        self.status_bar.showMessage(
            f"Połączony - {market_frame.symbol} | "
            f"Cena: {market_frame.close_price:.8f} | "
            f"Wolumen: {market_frame.volume:.2f}"
        )
    
    def on_connection_changed(self, connected: bool):
        """Obsługuje zmianę statusu połączenia"""
        if connected:
            self.status_bar.showMessage("Połączony z Binance")
        else:
            self.status_bar.showMessage("Brak połączenia z Binance")
    
    def on_error(self, error_message: str):
        """Obsługuje błędy"""
        logger.error(f"Błąd aplikacji: {error_message}")
        QMessageBox.warning(self, "Błąd", error_message)
    
    def closeEvent(self, event):
        """Obsługuje zamknięcie aplikacji"""
        # Zatrzymaj streaming danych
        self.data_controller.stop_streaming()
        event.accept()
