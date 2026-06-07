from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from skyvision.db.base import Base


class CandleORM(Base):
    __tablename__ = "candles"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    timeframe: Mapped[str] = mapped_column(String(8), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    vwap: Mapped[float | None] = mapped_column(Float)
    __table_args__ = (UniqueConstraint("symbol", "timeframe", "timestamp"),)


class OptionSnapshotORM(Base):
    __tablename__ = "option_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(64), index=True)
    underlying: Mapped[str] = mapped_column(String(16), index=True)
    expiration: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    strike: Mapped[float] = mapped_column(Float)
    option_type: Mapped[str] = mapped_column(String(8))
    bid: Mapped[float] = mapped_column(Float)
    ask: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)
    open_interest: Mapped[int] = mapped_column(Integer)
    greeks: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class AlertORM(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    direction: Mapped[str] = mapped_column(String(8), index=True)
    score: Mapped[int] = mapped_column(Integer, index=True)
    grade: Mapped[str] = mapped_column(String(8))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updates: Mapped[list["TradeUpdateORM"]] = relationship(back_populates="alert")


class TradeUpdateORM(Base):
    __tablename__ = "trade_updates"
    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True)
    event: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    alert: Mapped[AlertORM] = relationship(back_populates="updates")


Index("ix_candles_symbol_tf_ts", CandleORM.symbol, CandleORM.timeframe, CandleORM.timestamp)
