from collections.abc import Sequence

from skyvision.models import Candle, Direction, Signal
from skyvision.services.indicators import aggregate_candles, relative_volume, rsi, vwap
from skyvision.services.scoring import ScoreInput, score_setup
from skyvision.services.stretch_filter import evaluate_stretch
from skyvision.services.structure import analyze_structure


class SignalEngine:
    def analyze(self, candles_1m: Sequence[Candle]) -> Signal | None:
        if len(candles_1m) < 30:
            return None
        closes_1m = [c.close for c in candles_1m]
        candles_5m = aggregate_candles(candles_1m, 5)
        rsi_1m = rsi(closes_1m)
        rsi_5m = rsi([c.close for c in candles_5m])
        current_vwap = candles_1m[-1].vwap or vwap(candles_1m[-60:])
        rvol = relative_volume(candles_1m)
        structure = analyze_structure(candles_1m)
        last = candles_1m[-1]
        direction = (
            Direction.BULLISH if last.close >= current_vwap and rsi_1m >= 50 else Direction.BEARISH
        )
        trend_aligned = (direction == Direction.BULLISH and structure.trend == "uptrend") or (
            direction == Direction.BEARISH and structure.trend == "downtrend"
        )
        volume_expanding = len(candles_1m) >= 2 and candles_1m[-1].volume > candles_1m[-2].volume
        stretch = evaluate_stretch(candles_1m, direction, rsi_1m, current_vwap, structure)
        score, setup_grade = score_setup(
            ScoreInput(
                direction,
                rsi_1m,
                rsi_5m,
                last.close,
                current_vwap,
                rvol,
                volume_expanding,
                structure,
                trend_aligned,
                stretch.rejected,
            )
        )
        if score < 60:
            return None
        if direction == Direction.BULLISH:
            targets = [round(last.close * m, 2) for m in (1.0025, 1.005, 1.01)]
            invalidation = f"Lose VWAP {current_vwap:.2f} or break latest swing low"
            vwap_status = "above VWAP"
        else:
            targets = [round(last.close * m, 2) for m in (0.9975, 0.995, 0.99)]
            invalidation = f"Reclaim VWAP {current_vwap:.2f} or break latest swing high"
            vwap_status = "below VWAP"
        return Signal(
            last.symbol,
            direction,
            score,
            setup_grade,
            rsi_1m,
            rsi_5m,
            vwap_status,
            rvol,
            "expanding" if volume_expanding else "normal",
            structure,
            last.close,
            targets,
            invalidation,
        )
