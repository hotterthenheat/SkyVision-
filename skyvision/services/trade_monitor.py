from skyvision.models import Candle, Direction, Signal
from skyvision.services.indicators import rsi
from skyvision.services.structure import analyze_structure


class TradeMonitor:
    def evaluate(self, signal: Signal, candles: list[Candle]) -> list[str]:
        if not candles:
            return []
        events: list[str] = []
        last = candles[-1]
        structure = analyze_structure(candles)
        current_rsi = rsi([c.close for c in candles])
        if signal.direction == Direction.BULLISH:
            if any(last.high >= target for target in signal.targets):
                events.append("target hit")
            if last.vwap and last.close < last.vwap:
                events.append("VWAP lost")
            if structure.lower_low:
                events.append("market structure breaks")
            if current_rsi < 50:
                events.append("RSI confirmation fails")
            if structure.trend == "downtrend":
                events.append("trend reverses")
        else:
            if any(last.low <= target for target in signal.targets):
                events.append("target hit")
            if last.vwap and last.close > last.vwap:
                events.append("VWAP reclaimed")
            if structure.higher_high:
                events.append("market structure breaks")
            if current_rsi > 50:
                events.append("RSI confirmation fails")
            if structure.trend == "uptrend":
                events.append("trend reverses")
        return events
