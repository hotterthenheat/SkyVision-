from datetime import UTC, datetime, timedelta

from skyvision.models import Direction, OptionContract
from skyvision.services.options_selector import OptionSelector
from skyvision.services.pricing import black_scholes, projected_values


def contract(delta=0.45, bid=1.0, ask=1.1, vol=500, oi=1000):
    return OptionContract(
        "SPY260101C00500000",
        "SPY",
        datetime.now(UTC) + timedelta(days=7),
        500,
        "call",
        bid,
        ask,
        None,
        vol,
        oi,
        delta,
        implied_volatility=0.25,
    )


def test_black_scholes_positive():
    assert black_scholes(500, 500, 7 / 365, 0.04, 0.25, "call") > 0


def test_projection_count():
    assert len(projected_values(contract(), 500, 7 / 365, 0.04)) == 6


def test_selector_prefers_liquid_contract():
    selector = OptionSelector(250, 100, 0.12)
    best = selector.select(
        [contract(vol=100, oi=250), contract(vol=1000, oi=2000)], Direction.BULLISH
    )
    assert best is not None
    assert best.volume == 1000
