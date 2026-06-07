from collections.abc import Sequence

from skyvision.models import Candle, StructureState


def find_swings(candles: Sequence[Candle], width: int = 2) -> tuple[list[tuple], list[tuple]]:
    highs, lows = [], []
    if len(candles) < width * 2 + 1:
        return highs, lows
    for i in range(width, len(candles) - width):
        window = candles[i - width : i + width + 1]
        c = candles[i]
        if c.high == max(x.high for x in window):
            highs.append((c.timestamp, c.high))
        if c.low == min(x.low for x in window):
            lows.append((c.timestamp, c.low))
    return highs, lows


def analyze_structure(candles: Sequence[Candle]) -> StructureState:
    highs, lows = find_swings(candles)
    hh = len(highs) >= 2 and highs[-1][1] > highs[-2][1]
    lh = len(highs) >= 2 and highs[-1][1] < highs[-2][1]
    hl = len(lows) >= 2 and lows[-1][1] > lows[-2][1]
    ll = len(lows) >= 2 and lows[-1][1] < lows[-2][1]
    trend = "range"
    if hh and hl:
        trend = "uptrend"
    elif lh and ll:
        trend = "downtrend"
    last = candles[-1] if candles else None
    bos = bool(
        last and ((highs and last.close > highs[-1][1]) or (lows and last.close < lows[-1][1]))
    )
    mss = bool(
        (trend == "uptrend" and lows and last and last.close < lows[-1][1])
        or (trend == "downtrend" and highs and last and last.close > highs[-1][1])
    )
    return StructureState(highs[-8:], lows[-8:], trend, bos, mss, hh, hl, lh, ll)
