from datetime import UTC, datetime, timedelta

from skyvision.models import Candle
from skyvision.services.signal_engine import SignalEngine


def test_signal_engine_generates_ranked_signal():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    candles = []
    price = 100.0
    for i in range(80):
        price += [0.20, -0.08, 0.12, -0.04, 0.15][i % 5]
        volume = 5000 if i == 79 else 1000 + i * 5
        candles.append(
            Candle(
                "NVDA",
                base + timedelta(minutes=i),
                price - 0.04,
                price + 0.06,
                price - 0.06,
                price,
                volume,
                price - 0.3,
            )
        )
    signal = SignalEngine().analyze(candles)
    assert signal is not None
    assert signal.score >= 60
