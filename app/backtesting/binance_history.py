"""Historical Binance kline downloader for backtesting."""

from datetime import datetime

import httpx
import pandas as pd

from app.core.config import Settings, get_settings


class BinanceHistoryClient:
    """Fetch historical klines from Binance REST API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "5m",
        limit: int = 1000,
        start_time: datetime | None = None,
    ) -> pd.DataFrame:
        """Download klines into a DataFrame compatible with IndicatorEngine."""
        params: dict[str, str | int] = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        async with httpx.AsyncClient(base_url=self.settings.binance_rest_base, timeout=15) as client:
            response = await client.get("/api/v3/klines", params=params)
            response.raise_for_status()
        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ]
        df = pd.DataFrame(response.json(), columns=columns)
        numeric_columns = ["open", "high", "low", "close", "volume"]
        df[numeric_columns] = df[numeric_columns].astype(float)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
        return df.set_index("open_time")
