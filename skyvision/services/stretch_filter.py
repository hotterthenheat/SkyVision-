from collections.abc import Sequence
from dataclasses import dataclass

from skyvision.models import Candle, Direction, StructureState


@dataclass(frozen=True, slots=True)
class StretchResult:
    rejected: bool
    reasons: list[str]


def evaluate_stretch(
    candles: Sequence[Candle],
    direction: Direction,
    rsi_1m: float,
    vwap_value: float,
    structure: StructureState,
) -> StretchResult:
    if not candles:
        return StretchResult(True, ["no candle data"])
    last = candles[-1]
    reasons: list[str] = []
    dist_vwap = abs(last.close - vwap_value) / vwap_value if vwap_value else 0
    if dist_vwap > 0.018:
        reasons.append(f"price {dist_vwap:.2%} from VWAP")
    if direction == Direction.BULLISH and rsi_1m >= 82:
        reasons.append("bullish RSI is extreme")
    if direction == Direction.BEARISH and rsi_1m <= 18:
        reasons.append("bearish RSI is extreme")
    if len(candles) >= 3:
        bodies = [abs(c.close - c.open) for c in candles[-3:]]
        ranges = [max(c.high - c.low, 1e-9) for c in candles[-3:]]
        if all(body / rng > 0.75 for body, rng in zip(bodies, ranges, strict=True)):
            reasons.append("three consecutive expansion candles")
    swings = structure.swing_lows if direction == Direction.BULLISH else structure.swing_highs
    if swings:
        swing_price = swings[-1][1]
        dist_swing = abs(last.close - swing_price) / last.close
        if dist_swing > 0.025:
            reasons.append(f"price {dist_swing:.2%} from latest swing")
    return StretchResult(bool(reasons), reasons)
