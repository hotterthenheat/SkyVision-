import asyncio
import logging
from collections.abc import Mapping
from typing import Any

import httpx

log = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


class ProviderRequestError(RuntimeError):
    def __init__(self, provider: str, message: str) -> None:
        super().__init__(f"{provider}: {message}")
        self.provider = provider


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    provider: str,
    retries: int,
    params: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    attempts = max(retries, 1)
    for attempt in range(1, attempts + 1):
        try:
            response = await client.request(method, url, params=params)
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < attempts:
                await _sleep_before_retry(attempt, provider, response.status_code)
                continue
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ProviderRequestError(provider, "expected JSON object response")
            return payload
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            last_error = exc
            if attempt >= attempts:
                break
            await _sleep_before_retry(attempt, provider, None)
    raise ProviderRequestError(provider, str(last_error)) from last_error


async def _sleep_before_retry(attempt: int, provider: str, status_code: int | None) -> None:
    delay = min(2 ** (attempt - 1), 10)
    log.warning(
        "provider_request_retry",
        extra={
            "provider": provider,
            "attempt": attempt,
            "status_code": status_code,
            "delay": delay,
        },
    )
    await asyncio.sleep(delay)
