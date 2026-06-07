import httpx

from skyvision.clients.http import request_json


class ThetaDataClient:
    def __init__(
        self,
        username: str,
        password: str,
        base_url: str,
        *,
        timeout_seconds: float = 60.0,
        retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        auth = (username, password) if username or password else None
        self._client = httpx.AsyncClient(auth=auth, timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def historical_greeks(
        self, root: str, exp: int, strike: int, right: str, start: str, end: str
    ) -> dict:
        return await request_json(
            self._client,
            "GET",
            f"{self.base_url}/hist/option/greeks",
            provider="thetadata",
            retries=self.retries,
            params=_historical_params(root, exp, strike, right, start, end),
        )

    async def historical_iv(
        self, root: str, exp: int, strike: int, right: str, start: str, end: str
    ) -> dict:
        return await request_json(
            self._client,
            "GET",
            f"{self.base_url}/hist/option/implied_volatility",
            provider="thetadata",
            retries=self.retries,
            params=_historical_params(root, exp, strike, right, start, end),
        )


def _historical_params(root: str, exp: int, strike: int, right: str, start: str, end: str) -> dict:
    return {
        "root": root,
        "exp": exp,
        "strike": strike,
        "right": right,
        "start_date": start,
        "end_date": end,
    }
