"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the scalping assistant."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "TradeAnalyzer AI Scalping Assistant"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://tradeanalyzer:tradeanalyzer@localhost:5432/tradeanalyzer"
    binance_ws_base: str = "wss://stream.binance.com:9443/ws"
    binance_rest_base: str = "https://api.binance.com"
    symbol: str = "btcusdt"
    timeframes: str = "1m,3m,5m,15m"
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    voice_alerts_enabled: bool = True
    screen_monitor_enabled: bool = False
    max_candles_per_timeframe: int = Field(default=500, ge=100, le=5000)

    @property
    def timeframe_list(self) -> list[str]:
        """Configured Binance kline intervals."""
        return [item.strip() for item in self.timeframes.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()
