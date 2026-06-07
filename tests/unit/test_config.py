from skyvision.core.config import Settings


def test_render_database_url_is_normalized() -> None:
    settings = Settings(DATABASE_URL="postgres://user:pass@host/db", REDIS_URL="redis://host:6379")
    assert settings.database_url.startswith("postgresql+asyncpg://")


def test_symbols_parse_from_csv() -> None:
    settings = Settings(symbols="spy, qqq, nvda")
    assert settings.symbols == ["SPY", "QQQ", "NVDA"]
