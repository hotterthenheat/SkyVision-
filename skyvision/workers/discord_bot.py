import asyncio
import logging
from contextlib import suppress

import discord
from redis.asyncio import Redis
from sqlalchemy import select

from skyvision.core.config import settings
from skyvision.core.logging import configure_logging
from skyvision.db.models import AlertORM
from skyvision.db.session import SessionLocal
from skyvision.services.discord_service import DiscordAlertFormatter

log = logging.getLogger(__name__)


class SkyVisionBot(discord.Client):
    async def setup_hook(self) -> None:
        settings.validate_discord()
        self.redis = Redis.from_url(
            settings.redis_url, decode_responses=True, socket_connect_timeout=5, socket_timeout=5
        )
        self.bg = asyncio.create_task(self.poll_alerts(), name="skyvision-discord-alert-poller")

    async def close(self) -> None:
        task = getattr(self, "bg", None)
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        redis = getattr(self, "redis", None)
        if redis:
            await redis.aclose()
        await super().close()

    async def poll_alerts(self) -> None:
        await self.wait_until_ready()
        channel = (
            self.get_channel(settings.discord_channel_id) if settings.discord_channel_id else None
        )
        if not isinstance(channel, discord.abc.Messageable):
            log.error(
                "discord_channel_not_found", extra={"channel_id": settings.discord_channel_id}
            )
            return
        while not self.is_closed():
            try:
                await self._send_pending_alerts(channel)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("discord_alert_poll_failed")
            await asyncio.sleep(15)

    async def _send_pending_alerts(self, channel: discord.abc.Messageable) -> None:
        async with SessionLocal() as session:
            result = await session.execute(
                select(AlertORM)
                .where(AlertORM.status == "open")
                .order_by(AlertORM.created_at.desc())
                .limit(25)
            )
            for alert in result.scalars():
                key = f"discord:alert:{alert.id}"
                if await self.redis.set(key, "sent", nx=True, ex=60 * 60 * 24 * 14):
                    await channel.send(
                        embed=DiscordAlertFormatter.embed_from_payload(alert.payload)
                    )
                    log.info(
                        "discord_alert_sent", extra={"alert_id": alert.id, "symbol": alert.symbol}
                    )


def run() -> None:
    configure_logging(settings.log_level)
    intents = discord.Intents.default()
    client = SkyVisionBot(intents=intents)
    client.run(settings.discord_bot_token)


if __name__ == "__main__":
    run()
