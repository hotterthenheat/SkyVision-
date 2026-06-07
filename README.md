# SkyVision

SkyVision is a production-ready Python 3.12 options intelligence platform for real-time market scanning, options-chain ranking, Black-Scholes repricing, Discord alerting, and post-alert trade monitoring.

> Security note: never commit live API keys or Discord bot tokens. Put them in Render environment variables. Rotate any credentials that have been pasted into chat, terminals, logs, or tickets.

## Features

- **Polygon** REST and WebSocket market data clients for real-time trades plus aggregates, 1-minute candles, 5-minute aggregation, VWAP, volume, and trades.
- **Tradier** options chain client for bid/ask, Greeks, open interest, and volume.
- **ThetaData** client for historical options, Greeks, IV, and backtesting datasets.
- Signal engine using 1m RSI momentum shifts, 5m RSI confirmation, VWAP alignment, RVOL, volume expansion, trend alignment, and market structure.
- Market structure detection for MSS, BOS, swing highs/lows, HH, HL, LH, and LL.
- Stretch filter rejecting overextended setups by VWAP distance, extreme RSI, candle expansion, and swing distance.
- 0-100 scoring with A+/A/B/C grades; production alerts are persisted only at configured thresholds.
- Options contract selector with liquidity, OI, volume, delta quality, spread quality, and near-expiration ranking.
- Black-Scholes projections for +0.25%, +0.50%, +0.75%, +1.00%, +1.50%, and +2.00% setup-direction moves.
- FastAPI HTTP API, PostgreSQL persistence, Redis de-duplication, Render-compatible Docker deployment, Alembic migrations, and pytest coverage configuration.

## Render production deployment

This repository includes `render.yaml` for a Render Blueprint deployment.

### Required Render services

1. **PostgreSQL**: `skyvision-postgres`
2. **Render Key Value (Redis-compatible)**: `skyvision-redis`
3. **Web Service**: `skyvision-api`
   - Docker command: `uvicorn skyvision.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/api/health`
   - Pre-deploy command: `alembic upgrade head`
4. **Background Worker**: `skyvision-scanner`
   - Docker command: `python -m skyvision.workers.realtime`
5. **Background Worker**: `skyvision-discord`
   - Docker command: `python -m skyvision.workers.discord_bot`

### Required Render environment variables

Render will inject `DATABASE_URL` and `REDIS_URL` from the managed services. SkyVision normalizes Render's `postgres://` URLs to SQLAlchemy's asyncpg format at startup.

Set these manually in Render:

- `SKYVISION_ENV=production`
- `SKYVISION_LOG_LEVEL=INFO`
- `SKYVISION_SYMBOLS=AAPL,MSFT,NVDA,SPY,QQQ`
- `SKYVISION_POLYGON_API_KEY`
- `SKYVISION_TRADIER_API_KEY`
- `SKYVISION_DISCORD_BOT_TOKEN`
- `SKYVISION_DISCORD_CHANNEL_ID`

Optional tuning variables:

- `SKYVISION_ALERT_SCORE_THRESHOLD=80`
- `SKYVISION_SCAN_INTERVAL_SECONDS=60`
- `SKYVISION_REQUEST_TIMEOUT_SECONDS=20`
- `SKYVISION_REQUEST_RETRIES=3`
- `SKYVISION_MIN_OPEN_INTEREST=250`
- `SKYVISION_MIN_OPTION_VOLUME=100`
- `SKYVISION_MAX_SPREAD_PCT=0.12`
- `SKYVISION_THETADATA_USERNAME`
- `SKYVISION_THETADATA_PASSWORD`
- `SKYVISION_THETADATA_BASE_URL`

### Recommended Render architecture

- Keep the API, scanner, and Discord bot as separate Render services so deploys, restarts, and scaling are isolated.
- Use a single managed PostgreSQL database for alerts, candles, option snapshots, and monitor updates.
- Use Render Key Value/managed Redis for Discord de-duplication and future low-latency coordination.
- Run Alembic only as the API service pre-deploy command to avoid concurrent worker migrations.
- Scale the scanner horizontally only after adding symbol partitioning; otherwise multiple scanners may generate duplicate alerts.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
```

## API

```bash
curl https://<render-service>.onrender.com/api/health
curl https://<render-service>.onrender.com/api/ready
curl https://<render-service>.onrender.com/api/alerts
```

## Architecture

```text
skyvision/
  api/              FastAPI routes and health/readiness checks
  clients/          Polygon, Tradier, ThetaData integrations with retries
  core/             configuration, startup validation, logging
  db/               SQLAlchemy models, sessions, health checks
  models/           domain dataclasses
  schemas/          API schemas
  services/         indicators, structure, scoring, options, pricing, Discord, monitoring
  workers/          real-time scanner and Discord worker
migrations/         Alembic schema migrations
tests/              unit and integration tests
```

## Database

Run migrations with:

```bash
alembic upgrade head
```

The initial schema stores candles, option snapshots, generated alerts, and trade-monitor updates.

## Operational workflow

1. `skyvision.workers.realtime` fetches recent Polygon candles per configured symbol.
2. The signal engine evaluates momentum, VWAP, RVOL, structure, trend, and stretch risk.
3. Qualified setups are scored and ignored below the configured alert threshold.
4. Tradier chains are scanned and ranked for the most liquid directional option contract.
5. Black-Scholes projections are generated and the alert is persisted to PostgreSQL.
6. `skyvision.workers.discord_bot` de-duplicates alerts through Redis and sends Discord embeds.
7. `TradeMonitor` can evaluate active alerts for target hits, VWAP loss/reclaim, structure breaks, RSI failure, and trend reversal.

## Testing

```bash
pytest
ruff check .
```

The pytest configuration enforces 90% coverage through `pytest-cov` when the development dependencies are installed.
