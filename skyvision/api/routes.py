from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from skyvision.core.config import settings
from skyvision.db.models import AlertORM
from skyvision.db.session import check_database, check_redis, get_session
from skyvision.schemas.api import AlertResponse, HealthResponse, ReadinessResponse

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.env)


@router.get("/ready", response_model=ReadinessResponse)
async def ready() -> ReadinessResponse:
    checks: dict[str, str] = {}
    try:
        await check_database()
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = "failed"
        raise HTTPException(status_code=503, detail={"checks": checks}) from exc
    try:
        await check_redis()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = "failed"
        raise HTTPException(status_code=503, detail={"checks": checks}) from exc
    return ReadinessResponse(status="ready", checks=checks)


@router.get("/alerts", response_model=list[AlertResponse])
async def alerts(session: SessionDep, limit: int = 50) -> list[AlertResponse]:
    result = await session.execute(
        select(AlertORM).order_by(desc(AlertORM.created_at)).limit(min(limit, 250))
    )
    return [AlertResponse.model_validate(a, from_attributes=True) for a in result.scalars()]
