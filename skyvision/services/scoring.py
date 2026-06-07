from dataclasses import dataclass

from skyvision.models import Direction, StructureState


@dataclass(frozen=True, slots=True)
class ScoreInput:
    direction: Direction
    rsi_1m: float
    rsi_5m: float
    price: float
    vwap: float
    rvol: float
    volume_expanding: bool
    structure: StructureState
    trend_aligned: bool
    stretched: bool


def grade(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "IGNORE"


def score_setup(data: ScoreInput) -> tuple[int, str]:
    if data.stretched:
        return 0, "IGNORE"
    score = 0
    bullish = data.direction == Direction.BULLISH
    if (bullish and data.rsi_1m > 55) or (not bullish and data.rsi_1m < 45):
        score += 15
    if (bullish and data.rsi_5m > 52) or (not bullish and data.rsi_5m < 48):
        score += 15
    if (bullish and data.price > data.vwap) or (not bullish and data.price < data.vwap):
        score += 15
    if data.rvol >= 1.5:
        score += 15
    elif data.rvol >= 1.2:
        score += 8
    if data.volume_expanding:
        score += 10
    if data.trend_aligned:
        score += 15
    if data.structure.bos:
        score += 10
    if data.structure.mss:
        score += 5
    score = min(score, 100)
    return score, grade(score)
