from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class Direction(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass(slots=True)
class Candle:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float | None = None


@dataclass(slots=True)
class Trade:
    symbol: str
    timestamp: datetime
    price: float
    size: int
    exchange: int | None = None


@dataclass(slots=True)
class OptionContract:
    symbol: str
    underlying: str
    expiration: datetime
    strike: float
    option_type: str
    bid: float
    ask: float
    last: float | None
    volume: int
    open_interest: int
    delta: float
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    implied_volatility: float | None = None

    @property
    def mid(self) -> float:
        return round((self.bid + self.ask) / 2, 4)

    @property
    def spread_pct(self) -> float:
        return (self.ask - self.bid) / self.mid if self.mid > 0 else 1.0


@dataclass(slots=True)
class StructureState:
    swing_highs: list[tuple[datetime, float]]
    swing_lows: list[tuple[datetime, float]]
    trend: str
    bos: bool
    mss: bool
    higher_high: bool
    higher_low: bool
    lower_high: bool
    lower_low: bool


@dataclass(slots=True)
class Signal:
    symbol: str
    direction: Direction
    score: int
    grade: str
    rsi_1m: float
    rsi_5m: float
    vwap_status: str
    rvol: float
    volume_status: str
    structure: StructureState
    entry: float
    targets: list[float]
    invalidation: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
