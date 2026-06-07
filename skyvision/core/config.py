from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SKYVISION_", env_file=".env", extra="ignore")

    env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: str = Field(
        default="postgresql+asyncpg://skyvision:skyvision@localhost:5432/skyvision",
        validation_alias=AliasChoices("SKYVISION_DATABASE_URL", "DATABASE_URL"),
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("SKYVISION_REDIS_URL", "REDIS_URL"),
    )
    polygon_api_key: str = ""
    polygon_base_url: str = "https://api.polygon.io"
    polygon_ws_url: str = "wss://socket.polygon.io/stocks"
    tradier_api_key: str = ""
    tradier_base_url: str = "https://api.tradier.com/v1"
    thetadata_username: str = ""
    thetadata_password: str = ""
    thetadata_base_url: str = "http://localhost:25510/v2"
    discord_bot_token: str = ""
    discord_channel_id: int | None = None
    symbols: list[str] = Field(default_factory=lambda: ["SPY", "QQQ"])
    risk_free_rate: float = 0.045
    min_open_interest: int = 250
    min_option_volume: int = 100
    max_spread_pct: float = 0.12
    alert_score_threshold: int = 80
    scan_interval_seconds: int = 60
    request_timeout_seconds: float = 20.0
    request_retries: int = 3
    websocket_reconnect_min_seconds: float = 1.0
    websocket_reconnect_max_seconds: float = 60.0

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("symbols", mode="before")
    @classmethod
    def parse_symbols(cls, value):
        if isinstance(value, str):
            return [s.strip().upper() for s in value.split(",") if s.strip()]
        return value

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    def validate_api(self) -> None:
        missing = []
        if not self.database_url:
            missing.append("DATABASE_URL or SKYVISION_DATABASE_URL")
        if not self.redis_url:
            missing.append("REDIS_URL or SKYVISION_REDIS_URL")
        if missing:
            raise RuntimeError(f"Missing required API configuration: {', '.join(missing)}")

    def validate_scanner(self) -> None:
        self.validate_api()
        missing = []
        if not self.polygon_api_key:
            missing.append("SKYVISION_POLYGON_API_KEY")
        if not self.tradier_api_key:
            missing.append("SKYVISION_TRADIER_API_KEY")
        if not self.symbols:
            missing.append("SKYVISION_SYMBOLS")
        if missing:
            raise RuntimeError(f"Missing required scanner configuration: {', '.join(missing)}")

    def validate_discord(self) -> None:
        self.validate_api()
        missing = []
        if not self.discord_bot_token:
            missing.append("SKYVISION_DISCORD_BOT_TOKEN")
        if not self.discord_channel_id:
            missing.append("SKYVISION_DISCORD_CHANNEL_ID")
        if missing:
            raise RuntimeError(f"Missing required Discord configuration: {', '.join(missing)}")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
