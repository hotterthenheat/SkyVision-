from datetime import UTC, datetime, timedelta

from skyvision.models import Candle
from skyvision.services.structure import analyze_structure


def candle(i: int, high: float, low: float, close: float) -> Candle:
    return Candle(
        symbol="SPY",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
        vwap=100,
    )


def test_structure_detects_break_of_structure() -> None:
    candles = [
        candle(0, 100, 99, 99.5),
        candle(1, 103, 100, 102),
        candle(2, 101, 98, 99),
        candle(3, 104, 101, 103),
        candle(4, 102, 100, 101),
        candle(5, 105, 102, 104),
        candle(6, 103, 101, 102),
        candle(7, 106, 103, 105),
        candle(8, 104, 102, 103),
        candle(9, 108, 104, 107),
    ]
    state = analyze_structure(candles)
    assert state.bos is True
    assert state.higher_high is True


def test_structure_detects_market_structure_shift() -> None:
    candles = [
        candle(0, 100, 95, 96),
        candle(1, 98, 93, 94),
        candle(2, 99, 94, 98),
        candle(3, 97, 92, 93),
        candle(4, 98, 93, 97),
        candle(5, 96, 91, 92),
        candle(6, 99, 94, 98),
        candle(7, 101, 96, 100),
    ]
    state = analyze_structure(candles)
    assert state.mss is True
