import json

import pytest
from websockets.exceptions import WebSocketException

from skyvision.clients.polygon_stream import PolygonStreamClient


def test_polygon_stream_parses_trade_message() -> None:
    trades = PolygonStreamClient._parse_message(
        json.dumps([{"ev": "T", "sym": "SPY", "t": 1760000000000, "p": 500.1, "s": 10}])
    )
    assert len(trades) == 1
    assert trades[0].symbol == "SPY"
    assert trades[0].price == 500.1


def test_polygon_stream_raises_on_auth_failure() -> None:
    with pytest.raises(WebSocketException):
        PolygonStreamClient._parse_message(json.dumps([{"status": "auth_failed"}]))
