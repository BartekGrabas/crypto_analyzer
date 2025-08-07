import importlib
import pytest


@pytest.fixture
def app_state(monkeypatch):
    from PyQt6 import QtCore

    class DummySignal:
        def __init__(self, *args, **kwargs):
            self._slots = []

        def connect(self, func):
            self._slots.append(func)

        def emit(self, *args, **kwargs):
            for slot in self._slots:
                slot(*args, **kwargs)

    monkeypatch.setattr(QtCore, "QObject", object)
    monkeypatch.setattr(QtCore, "pyqtSignal", lambda *a, **k: DummySignal())
    import crypto_analyzer.models.app_state as module
    importlib.reload(module)
    AppState = module.AppState
    AppState._instance = None
    state = AppState()
    yield state
    AppState._instance = None
    importlib.reload(module)


def test_update_indicator_emits_signal(app_state):
    received = []
    app_state.indicatorConfigChanged.connect(lambda: received.append(True))

    app_state.update_indicator("sma_fast", True, period=5)

    assert app_state.active_indicators["sma_fast"]["enabled"] is True
    assert received == [True]


def test_get_enabled_indicators(app_state):
    app_state.update_indicator("sma_fast", True, period=5)
    app_state.update_indicator("sma_slow", False)

    enabled = app_state.get_enabled_indicators()

    assert "sma_fast" in enabled
    assert "sma_slow" not in enabled

