import asyncio
import logging
import signal
from datetime import UTC, datetime, timedelta

from skyvision.clients import PolygonClient, TradierClient
from skyvision.core.config import settings
from skyvision.core.logging import configure_logging
from skyvision.db.session import SessionLocal
from skyvision.services.orchestrator import AnalysisOrchestrator

log = logging.getLogger("skyvision.worker")


async def run_scanner(stop_event: asyncio.Event) -> None:
    settings.validate_scanner()
    polygon = PolygonClient(
        settings.polygon_api_key,
        settings.polygon_base_url,
        timeout_seconds=settings.request_timeout_seconds,
        retries=settings.request_retries,
    )
    tradier = TradierClient(
        settings.tradier_api_key,
        settings.tradier_base_url,
        timeout_seconds=settings.request_timeout_seconds,
        retries=settings.request_retries,
    )
    orchestrator = AnalysisOrchestrator(settings)
    try:
        while not stop_event.is_set():
            end = datetime.now(UTC).date().isoformat()
            start = (datetime.now(UTC) - timedelta(days=3)).date().isoformat()
            async with SessionLocal() as session:
                for symbol in settings.symbols:
                    if stop_event.is_set():
                        break
                    try:
                        result = await orchestrator.analyze_symbol(
                            symbol, polygon, tradier, session, start, end
                        )
                        if result:
                            log.info("alert_generated", extra={"symbol": symbol})
                    except Exception:
                        log.exception("analysis_failed", extra={"symbol": symbol})
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=settings.scan_interval_seconds)
            except TimeoutError:
                continue
    finally:
        await polygon.close()
        await tradier.close()


def _install_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)


async def main() -> None:
    configure_logging(settings.log_level)
    stop_event = asyncio.Event()
    _install_signal_handlers(stop_event)
    log.info("skyvision_scanner_started", extra={"symbols": settings.symbols})
    await run_scanner(stop_event)
    log.info("skyvision_scanner_stopped")


if __name__ == "__main__":
    asyncio.run(main())
