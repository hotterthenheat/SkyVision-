import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from skyvision.models import Trade

log = logging.getLogger(__name__)


class PolygonStreamClient:
    def __init__(
        self,
        api_key: str,
        url: str = "wss://socket.polygon.io/stocks",
        *,
        reconnect_min_seconds: float = 1.0,
        reconnect_max_seconds: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.url = url
        self.reconnect_min_seconds = reconnect_min_seconds
        self.reconnect_max_seconds = reconnect_max_seconds

    async def trades(
        self, symbols: list[str], stop_event: asyncio.Event | None = None
    ) -> AsyncIterator[Trade]:
        if not symbols:
            return
        backoff = self.reconnect_min_seconds
        while not (stop_event and stop_event.is_set()):
            try:
                async with websockets.connect(
                    self.url, ping_interval=20, ping_timeout=20, close_timeout=10
                ) as ws:
                    await ws.send(json.dumps({"action": "auth", "params": self.api_key}))
                    await ws.send(
                        json.dumps(
                            {"action": "subscribe", "params": ",".join(f"T.{s}" for s in symbols)}
                        )
                    )
                    backoff = self.reconnect_min_seconds
                    async for message in ws:
                        if stop_event and stop_event.is_set():
                            break
                        for trade in self._parse_message(message):
                            yield trade
            except asyncio.CancelledError:
                raise
            except (ConnectionClosed, WebSocketException, OSError, json.JSONDecodeError) as exc:
                log.warning("polygon_websocket_disconnected", extra={"error": str(exc)})
            if stop_event and stop_event.is_set():
                break
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, self.reconnect_max_seconds)

    @staticmethod
    def _parse_message(message: str) -> list[Trade]:
        payload = json.loads(message)
        if isinstance(payload, dict):
            payload = [payload]
        trades: list[Trade] = []
        for event in payload:
            if event.get("ev") != "T":
                if event.get("status") == "auth_failed":
                    raise WebSocketException("Polygon authentication failed")
                continue
            trades.append(
                Trade(
                    symbol=event["sym"],
                    timestamp=datetime.fromtimestamp(event["t"] / 1000, tz=UTC),
                    price=float(event["p"]),
                    size=int(event["s"]),
                    exchange=event.get("x"),
                )
            )
        return trades
