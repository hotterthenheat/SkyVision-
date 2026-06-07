from datetime import UTC, datetime, time

import httpx

from skyvision.clients.http import request_json
from skyvision.models import OptionContract


class TradierClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.tradier.com/v1",
        *,
        timeout_seconds: float = 20.0,
        retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=timeout_seconds,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def expirations(self, symbol: str) -> list[str]:
        payload = await request_json(
            self._client,
            "GET",
            f"{self.base_url}/markets/options/expirations",
            provider="tradier",
            retries=self.retries,
            params={"symbol": symbol, "includeAllRoots": "true"},
        )
        dates = payload.get("expirations", {}).get("date", [])
        return dates if isinstance(dates, list) else [dates]

    async def chain(self, symbol: str, expiration: str) -> list[OptionContract]:
        payload = await request_json(
            self._client,
            "GET",
            f"{self.base_url}/markets/options/chains",
            provider="tradier",
            retries=self.retries,
            params={"symbol": symbol, "expiration": expiration, "greeks": "true"},
        )
        raw = payload.get("options", {}).get("option", []) or []
        if isinstance(raw, dict):
            raw = [raw]
        contracts = []
        for option in raw:
            greeks = option.get("greeks") or {}
            contracts.append(
                OptionContract(
                    symbol=option["symbol"],
                    underlying=symbol,
                    expiration=_parse_expiration(option["expiration_date"]),
                    strike=float(option["strike"]),
                    option_type=str(option["option_type"]).lower(),
                    bid=float(option.get("bid") or 0),
                    ask=float(option.get("ask") or 0),
                    last=float(option["last"]) if option.get("last") else None,
                    volume=int(option.get("volume") or 0),
                    open_interest=int(option.get("open_interest") or 0),
                    delta=float(greeks.get("delta") or 0),
                    gamma=_optional_float(greeks.get("gamma")),
                    theta=_optional_float(greeks.get("theta")),
                    vega=_optional_float(greeks.get("vega")),
                    implied_volatility=_normalize_iv(_optional_float(greeks.get("mid_iv"))),
                )
            )
        return contracts


def _parse_expiration(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return datetime.combine(parsed.date(), time(21, 0), tzinfo=UTC)
    return parsed.astimezone(UTC)


def _optional_float(value) -> float | None:
    return float(value) if value not in (None, "") else None


def _normalize_iv(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 100 if value > 3 else value
