import pytest
from crypto_analyzer.models.binance_client import BinanceClient


@pytest.fixture
def client_with_mocks(mocker):
    client_cls = mocker.patch('crypto_analyzer.models.binance_client.Client')
    twm_cls = mocker.patch('crypto_analyzer.models.binance_client.ThreadedWebsocketManager')
    client_instance = client_cls.return_value
    twm_instance = twm_cls.return_value
    bc = BinanceClient('key', 'secret', testnet=True)
    return bc, client_instance, twm_instance


def test_get_klines(client_with_mocks):
    bc, client_instance, _ = client_with_mocks
    client_instance.get_klines.return_value = ['data']

    result = bc.get_klines('BTCUSDT', '1m', limit=10)

    client_instance.get_klines.assert_called_once_with(symbol='BTCUSDT', interval='1m', limit=10)
    assert result == ['data']


def test_start_kline_socket(client_with_mocks):
    bc, _, twm_instance = client_with_mocks
    callback = lambda x: x

    bc.start_kline_socket('BTCUSDT', '1m', callback)

    twm_instance.start.assert_called_once()
    twm_instance.start_kline_socket.assert_called_once_with(symbol='BTCUSDT', interval='1m', callback=callback)
    assert bc._twm is twm_instance


def test_start_depth_socket(client_with_mocks):
    bc, _, twm_instance = client_with_mocks
    callback = lambda x: x

    bc.start_depth_socket('BTCUSDT', callback)

    twm_instance.start.assert_called_once()
    twm_instance.start_depth_socket.assert_called_once_with(symbol='BTCUSDT', callback=callback)
    assert bc._twm is twm_instance


def test_stop(client_with_mocks):
    bc, _, twm_instance = client_with_mocks
    callback = lambda x: x

    bc.start_kline_socket('BTCUSDT', '1m', callback)
    bc.stop()

    twm_instance.stop.assert_called_once()
    assert bc._twm is None
