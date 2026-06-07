import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from skyvision.api import router
from skyvision.core.config import settings
from skyvision.core.logging import configure_logging

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    settings.validate_api()
    log.info("skyvision_api_started", extra={"environment": settings.env})
    yield
    log.info("skyvision_api_stopped")


app = FastAPI(title="SkyVision", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/api")
