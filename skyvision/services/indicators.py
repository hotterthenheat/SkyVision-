from collections.abc import Sequence
from statistics import mean

from skyvision.models import Candle


def rsi(values: Sequence[float], period: int = 14) -> float:
    if len(values) < period + 1:
        return 50.0
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[-period - 1 : -1], values[-period:], strict=True):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    if avg_loss == 0 and avg_gain == 0:
        return 50.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def vwap(candles: Sequence[Candle]) -> float:
    if not candles:
        raise ValueError("VWAP requires at least one candle")
    pv = sum(((c.high + c.low + c.close) / 3) * c.volume for c in candles)
    vol = sum(c.volume for c in candles)
    return round(pv / vol, 4) if vol else candles[-1].close


def relative_volume(candles: Sequence[Candle], lookback: int = 20) -> float:
    if len(candles) < 2:
        return 1.0
    baseline = candles[-lookback - 1 : -1]
    avg = mean([c.volume for c in baseline]) if baseline else candles[-1].volume
    return round(candles[-1].volume / avg, 2) if avg else 1.0


def aggregate_candles(candles: Sequence[Candle], minutes: int) -> list[Candle]:
    if minutes <= 1:
        return list(candles)
    out: list[Candle] = []
    for index in range(0, len(candles), minutes):
        chunk = candles[index : index + minutes]
        if len(chunk) < minutes:
            continue
        out.append(
            Candle(
                symbol=chunk[0].symbol,
                timestamp=chunk[-1].timestamp,
                open=chunk[0].open,
                high=max(c.high for c in chunk),
                low=min(c.low for c in chunk),
                close=chunk[-1].close,
                volume=sum(c.volume for c in chunk),
                vwap=vwap(chunk),
            )
        )
    return out
