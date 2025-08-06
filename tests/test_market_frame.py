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

    monkeypatch.setattr(QtCore, 'QObject', object)
    monkeypatch.setattr(QtCore, 'pyqtSignal', lambda *a, **k: DummySignal())
    import crypto_analyzer.models.app_state as module
    importlib.reload(module)
    AppState = module.AppState
    MarketFrame = module.MarketFrame
    AppState._instance = None
    state = AppState()
    yield state, MarketFrame
    AppState._instance = None
    importlib.reload(module)  # restore original for other tests


def make_frame(MarketFrame, ts: int, *, open_price=1.0, high_price=2.0, low_price=0.5, close_price=1.5, volume=100.0, symbol="BTCUSDT", interval="1m"):
    return MarketFrame(ts, symbol, open_price, high_price, low_price, close_price, volume, interval)


def test_update_market_data_sets_latest_and_emits_signal(app_state):
    state, MarketFrame = app_state
    received = []
    state.dataUpdated.connect(lambda frame: received.append(frame))

    frame = make_frame(MarketFrame, 1)
    state.update_market_data(frame)

    assert state.latest_market_frame is frame
    assert received == [frame]


def test_candle_history_updates_and_limits(app_state):
    state, MarketFrame = app_state
    state.max_history_size = 2

    frame1 = make_frame(MarketFrame, 1, close_price=10)
    frame2 = make_frame(MarketFrame, 1, close_price=20)
    frame3 = make_frame(MarketFrame, 2, close_price=30)
    frame4 = make_frame(MarketFrame, 3, close_price=40)

    state.update_market_data(frame1)
    assert len(state.candle_history) == 1
    assert state.candle_history[-1]["close"] == 10

    state.update_market_data(frame2)
    assert len(state.candle_history) == 1
    assert state.candle_history[-1]["close"] == 20

    state.update_market_data(frame3)
    assert len(state.candle_history) == 2
    assert [c["timestamp"] for c in state.candle_history] == [1, 2]

    state.update_market_data(frame4)
    assert len(state.candle_history) == 2
    assert [c["timestamp"] for c in state.candle_history] == [2, 3]
