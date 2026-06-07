# SkyVision Production Engineering Audit

Date: 2026-06-07  
Target platform: Render

## Issues found

1. Render `DATABASE_URL` was not supported because the app only read `SKYVISION_DATABASE_URL`.
2. Render PostgreSQL URLs commonly use `postgres://` or `postgresql://`, but SQLAlchemy asyncpg requires `postgresql+asyncpg://`.
3. Render Redis/Key Value URLs were not supported unless copied into `SKYVISION_REDIS_URL`.
4. Startup validation did not fail fast for missing API, scanner, or Discord configuration.
5. The API only had a liveness endpoint; it did not expose readiness checks for PostgreSQL and Redis.
6. The Docker image did not copy Alembic files, migrations, or scripts, which would break Render pre-deploy migrations.
7. The Docker command hard-coded port `8000` and did not honor Render's `$PORT` contract.
8. There was no Render Blueprint describing the production services, managed PostgreSQL, Redis-compatible Key Value service, pre-deploy migration, or health check.
9. Provider HTTP clients did not retry retryable network, rate-limit, or 5xx failures.
10. Provider timestamps from Polygon REST were naive datetimes instead of UTC-aware datetimes.
11. Polygon WebSocket handling had no reconnect loop, backoff, or authentication-failure handling.
12. Scanner and Discord workers did not consistently validate their required configuration at startup.
13. Scanner shutdown was not signal-aware and could wait for the full sleep interval during Render restarts.
14. Discord worker did not close Redis cleanly on shutdown.
15. Discord worker did not isolate alert polling errors, so transient failures could stop alert delivery.
16. Discord worker Redis de-duplication used `setnx` plus a separate expire call, which is not atomic.
17. Persisted alert payloads included dataclasses, enums, and datetimes that are not JSON-serializable by SQLAlchemy's JSON column.
18. Orchestrator commits did not roll back on database errors.
19. Tradier implied volatility values were not normalized when providers return percentages instead of decimals.
20. Tradier expiration parsing treated date-only expirations as midnight instead of a market-close UTC timestamp.
21. Indicator VWAP raised an implicit `IndexError` on empty input instead of a clear error.
22. RSI returned `100` for a flat market because average loss was zero, even when average gain was also zero.
23. Trade monitoring recalculated market structure multiple times for the same candle set.
24. Test coverage was too thin for market structure, JSON serialization, Render URL normalization, and WebSocket parsing.
25. The pytest configuration did not enforce the requested 90% coverage threshold.
26. README lacked Render-specific services, environment variables, and architecture guidance.

## Fixes applied

1. Added `AliasChoices` support for both prefixed and Render-native `DATABASE_URL` and `REDIS_URL`.
2. Added database URL normalization from `postgres://` and `postgresql://` to `postgresql+asyncpg://`.
3. Added API, scanner, and Discord startup validation methods.
4. Added `/api/ready` readiness endpoint that checks PostgreSQL and Redis.
5. Hardened SQLAlchemy engine settings with pre-ping, pool recycle, and bounded overflow.
6. Updated Dockerfile to copy Alembic/migration files and honor `${PORT:-8000}`.
7. Added `render.yaml` with web, scanner worker, Discord worker, PostgreSQL, and Redis-compatible Key Value services.
8. Added provider HTTP retry helper with sanitized structured logging.
9. Updated Polygon, Tradier, and ThetaData clients to use retrying JSON requests.
10. Made Polygon REST timestamps UTC-aware.
11. Added Polygon WebSocket reconnect/backoff logic and auth-failure handling.
12. Added graceful SIGINT/SIGTERM handling for the scanner worker.
13. Added Redis cleanup, poller cancellation, atomic Redis de-duplication, and polling error isolation for Discord.
14. Added JSON-safe serialization for signals, contracts, projections, datetimes, and enums before persistence.
15. Added database rollback on alert persistence failures.
16. Normalized Tradier implied volatility and expiration timestamps.
17. Improved RSI and VWAP edge-case behavior.
18. Reduced duplicate market-structure calculations in trade monitoring.
19. Added tests for market structure, JSON serialization, Render URL normalization, and WebSocket parsing.
20. Added `pytest-cov` and configured `--cov-fail-under=90`.
21. Expanded README with Render deployment instructions, required services, required environment variables, and recommended architecture.

## Remaining risks

1. Provider API schemas can change; production should add contract tests against recorded Polygon, Tradier, and ThetaData payloads.
2. The scanner currently processes all symbols in one worker; horizontal scaling requires symbol partitioning or stronger alert-level idempotency.
3. Alerts are de-duplicated for Discord delivery, but signal generation itself can still create repeated alerts if the same setup remains valid across scans.
4. Render free/starter instances may sleep or have limited resources; production market scanning should use paid always-on workers.
5. Backtesting endpoints are client-ready but a full backtesting workflow and API are not yet exposed.
6. The signal model is deterministic and testable, but trading performance requires market validation and forward testing before capital deployment.
7. Full test execution was limited by the current environment's missing Python 3.12 development dependencies and blocked package installation.

## Production readiness score

**84/100**

The application is substantially more Render-ready after the audit: it has Render-native configuration, migration support, health/readiness checks, retries, WebSocket reconnection, graceful worker shutdown, safer JSON persistence, and broader tests. The score is not higher because duplicate alert suppression at generation time, full backtesting workflows, live provider contract tests, and horizontal scanner partitioning remain future production hardening items.

## Render deployment instructions

1. Push this repository to GitHub or GitLab.
2. In Render, create a new Blueprint and select this repository.
3. Confirm Render detects `render.yaml` at the repository root.
4. Create or confirm the managed services:
   - `skyvision-postgres`
   - `skyvision-redis`
   - `skyvision-api`
   - `skyvision-scanner`
   - `skyvision-discord`
5. Set all secret environment variables in the Render dashboard; do not commit them.
6. Deploy the Blueprint. The API service runs `alembic upgrade head` before deployment.
7. Confirm `https://<skyvision-api>.onrender.com/api/health` returns `status=ok`.
8. Confirm `https://<skyvision-api>.onrender.com/api/ready` returns database and Redis checks as `ok`.
9. Watch scanner and Discord worker logs for startup validation and provider connectivity.

## Required Render services

- Render PostgreSQL database: `skyvision-postgres`
- Render Key Value / Redis-compatible service: `skyvision-redis`
- Render Web Service: `skyvision-api`
- Render Background Worker: `skyvision-scanner`
- Render Background Worker: `skyvision-discord`

## Required Render environment variables

Render-managed:

- `DATABASE_URL`
- `REDIS_URL`

User-managed:

- `SKYVISION_ENV=production`
- `SKYVISION_LOG_LEVEL=INFO`
- `SKYVISION_SYMBOLS`
- `SKYVISION_POLYGON_API_KEY`
- `SKYVISION_TRADIER_API_KEY`
- `SKYVISION_DISCORD_BOT_TOKEN`
- `SKYVISION_DISCORD_CHANNEL_ID`

Optional:

- `SKYVISION_THETADATA_USERNAME`
- `SKYVISION_THETADATA_PASSWORD`
- `SKYVISION_THETADATA_BASE_URL`
- `SKYVISION_ALERT_SCORE_THRESHOLD`
- `SKYVISION_SCAN_INTERVAL_SECONDS`
- `SKYVISION_REQUEST_TIMEOUT_SECONDS`
- `SKYVISION_REQUEST_RETRIES`
- `SKYVISION_MIN_OPEN_INTEREST`
- `SKYVISION_MIN_OPTION_VOLUME`
- `SKYVISION_MAX_SPREAD_PCT`

## Recommended Render architecture

- One web service for the API and health/readiness endpoints.
- One scanner background worker for market/provider polling and alert creation.
- One Discord background worker for alert delivery and Redis-backed de-duplication.
- One managed PostgreSQL database for durable state.
- One Render Key Value/Redis-compatible instance for de-duplication and future coordination.
- API pre-deploy migration only; workers should depend on the already migrated database.
- Add symbol partitioning before scaling scanner worker replicas beyond one.
