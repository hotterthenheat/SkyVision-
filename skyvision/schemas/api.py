from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    direction: str
    score: int
    grade: str
    status: str
    created_at: datetime
    payload: dict


class BacktestRequest(BaseModel):
    symbol: str
    from_date: str
    to_date: str
