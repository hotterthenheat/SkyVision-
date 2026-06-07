from collections.abc import Sequence
from datetime import UTC, datetime

from skyvision.models import Direction, OptionContract


class OptionSelector:
    def __init__(self, min_oi: int, min_volume: int, max_spread_pct: float) -> None:
        self.min_oi = min_oi
        self.min_volume = min_volume
        self.max_spread_pct = max_spread_pct

    def select(
        self, contracts: Sequence[OptionContract], direction: Direction
    ) -> OptionContract | None:
        desired = "call" if direction == Direction.BULLISH else "put"
        candidates = [
            c
            for c in contracts
            if c.option_type.lower() == desired
            and c.open_interest >= self.min_oi
            and c.volume >= self.min_volume
            and c.spread_pct <= self.max_spread_pct
            and 0.30 <= abs(c.delta) <= 0.60
            and c.ask > c.bid > 0
        ]
        if not candidates:
            return None
        now = datetime.now(UTC)

        def rank(c: OptionContract) -> tuple[float, float, float, float, float]:
            dte = max((c.expiration - now).days, 0)
            expiry_score = 1 / (1 + abs(dte - 7))
            delta_score = 1 - abs(abs(c.delta) - 0.45) / 0.15
            spread_score = 1 - c.spread_pct / self.max_spread_pct
            liquidity = min(c.volume / max(self.min_volume, 1), 5) + min(
                c.open_interest / max(self.min_oi, 1), 5
            )
            return (liquidity, c.open_interest, c.volume, delta_score, spread_score + expiry_score)

        return max(candidates, key=rank)
