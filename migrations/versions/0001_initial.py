"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-07
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("grade", sa.String(8), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_alerts_symbol"), "alerts", ["symbol"])
    op.create_index(op.f("ix_alerts_direction"), "alerts", ["direction"])
    op.create_index(op.f("ix_alerts_score"), "alerts", ["score"])
    op.create_index(op.f("ix_alerts_status"), "alerts", ["status"])
    op.create_index(op.f("ix_alerts_created_at"), "alerts", ["created_at"])
    op.create_table(
        "candles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("timeframe", sa.String(8), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("vwap", sa.Float()),
        sa.UniqueConstraint("symbol", "timeframe", "timestamp"),
    )
    op.create_index("ix_candles_symbol_tf_ts", "candles", ["symbol", "timeframe", "timestamp"])
    op.create_index(op.f("ix_candles_symbol"), "candles", ["symbol"])
    op.create_index(op.f("ix_candles_timeframe"), "candles", ["timeframe"])
    op.create_index(op.f("ix_candles_timestamp"), "candles", ["timestamp"])
    op.create_table(
        "option_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(64), nullable=False),
        sa.Column("underlying", sa.String(16), nullable=False),
        sa.Column("expiration", sa.DateTime(timezone=True), nullable=False),
        sa.Column("strike", sa.Float(), nullable=False),
        sa.Column("option_type", sa.String(8), nullable=False),
        sa.Column("bid", sa.Float(), nullable=False),
        sa.Column("ask", sa.Float(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column("open_interest", sa.Integer(), nullable=False),
        sa.Column("greeks", sa.JSON(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    for col in ("symbol", "underlying", "expiration", "timestamp"):
        op.create_index(op.f(f"ix_option_snapshots_{col}"), "option_snapshots", [col])
    op.create_table(
        "trade_updates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("event", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_trade_updates_alert_id"), "trade_updates", ["alert_id"])


def downgrade() -> None:
    op.drop_table("trade_updates")
    op.drop_table("option_snapshots")
    op.drop_table("candles")
    op.drop_table("alerts")
