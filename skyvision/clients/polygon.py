from datetime import UTC, datetime

import httpx

from skyvision.clients.http import request_json
from skyvision.models import Candle, Trade


class PolygonClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.polygon.io",
        *,
        timeout_seconds: float = 20.0,
        retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def candles(
        self, symbol: str, multiplier: int, from_date: str, to_date: str
    ) -> list[Candle]:
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/{multiplier}/minute/{from_date}/{to_date}"
        payload = await request_json(
            self._client,
            "GET",
            url,
            provider="polygon",
            retries=self.retries,
            params={"adjusted": "true", "sort": "asc", "apiKey": self.api_key},
        )
        return [
            Candle(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(x["t"] / 1000, tz=UTC),
                open=float(x["o"]),
                high=float(x["h"]),
                low=float(x["l"]),
                close=float(x["c"]),
                volume=float(x["v"]),
                vwap=float(x["vw"]) if x.get("vw") is not None else None,
            )
            for x in payload.get("results", [])
        ]

    async def trades(self, symbol: str, timestamp_gte: str | None = None) -> list[Trade]:
        params = {"apiKey": self.api_key, "order": "asc", "limit": 1000}
        if timestamp_gte:
            params["timestamp.gte"] = timestamp_gte
        payload = await request_json(
            self._client,
            "GET",
            f"{self.base_url}/v3/trades/{symbol}",
            provider="polygon",
            retries=self.retries,
            params=params,
        )
        return [
            Trade(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(x["sip_timestamp"] / 1_000_000_000, tz=UTC),
                price=float(x["price"]),
                size=int(x["size"]),
                exchange=x.get("exchange"),
            )
            for x in payload.get("results", [])
        ]
