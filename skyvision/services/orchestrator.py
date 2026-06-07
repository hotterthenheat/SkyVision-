import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from skyvision.clients import PolygonClient, TradierClient
from skyvision.core.config import Settings
from skyvision.db.models import AlertORM
from skyvision.models import OptionContract, Signal
from skyvision.services.options_selector import OptionSelector
from skyvision.services.pricing import Projection, projected_values
from skyvision.services.serialization import json_safe
from skyvision.services.signal_engine import SignalEngine

log = logging.getLogger(__name__)


class AnalysisOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.signal_engine = SignalEngine()
        self.selector = OptionSelector(
            settings.min_open_interest, settings.min_option_volume, settings.max_spread_pct
        )

    async def analyze_symbol(
        self,
        symbol: str,
        polygon: PolygonClient,
        tradier: TradierClient,
        session: AsyncSession,
        from_date: str,
        to_date: str,
    ) -> tuple[Signal, OptionContract | None, list[Projection]] | None:
        candles = await polygon.candles(symbol, 1, from_date, to_date)
        signal = self.signal_engine.analyze(candles)
        if not signal or signal.score < self.settings.alert_score_threshold:
            return None

        expirations = await tradier.expirations(symbol)
        contracts: list[OptionContract] = []
        for expiration in expirations[:4]:
            try:
                contracts.extend(await tradier.chain(symbol, expiration))
            except Exception:
                log.exception(
                    "tradier_chain_failed", extra={"symbol": symbol, "expiration": expiration}
                )

        contract = self.selector.select(contracts, signal.direction)
        projections: list[Projection] = []
        if contract:
            years = max(
                (contract.expiration - datetime.now(UTC)).total_seconds() / (365 * 24 * 3600),
                1 / 365,
            )
            projections = projected_values(
                contract, signal.entry, years, self.settings.risk_free_rate
            )

        payload = json_safe({"signal": signal, "contract": contract, "projections": projections})
        try:
            session.add(
                AlertORM(
                    symbol=symbol,
                    direction=signal.direction.value,
                    score=signal.score,
                    grade=signal.grade,
                    payload=payload,
                    status="open",
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return signal, contract, projections
