from datetime import UTC, datetime, timedelta

from skyvision.models import Candle
from skyvision.services.indicators import aggregate_candles, relative_volume, rsi, vwap


def candles(n=30):
    base = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        Candle(
            "SPY",
            base + timedelta(minutes=i),
            100 + i * 0.1,
            101 + i * 0.1,
            99 + i * 0.1,
            100.5 + i * 0.1,
            1000 + i * 10,
        )
        for i in range(n)
    ]


def test_rsi_uptrend_high():
    assert rsi([c.close for c in candles(20)]) > 90


def test_vwap_and_rvol():
    cs = candles(30)
    assert vwap(cs) > 100
    assert relative_volume(cs) > 1


def test_aggregate_candles():
    agg = aggregate_candles(candles(10), 5)
    assert len(agg) == 2
    assert agg[0].open == 100
