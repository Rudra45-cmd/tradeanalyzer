"""Technical indicator engine for scalping decisions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.core.schemas import IndicatorSnapshot


class IndicatorEngine:
    """Calculates EMA, RSI, MACD, ATR, VWAP, and volume metrics."""

    def calculate(self, candles: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Return a copy of candles with indicator columns appended."""
        if candles.empty:
            return candles.copy()

        df = candles.copy()
        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        volume = df["volume"].astype(float)

        df["ema_9"] = close.ewm(span=9, adjust=False).mean()
        df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        df["ema_50"] = close.ewm(span=50, adjust=False).mean()
        df["rsi"] = self._rsi(close)
        macd, macd_signal, macd_histogram = self._macd(close)
        df["macd"] = macd
        df["macd_signal"] = macd_signal
        df["macd_histogram"] = macd_histogram
        df["atr"] = self._atr(high, low, close)
        df["vwap"] = self._vwap(high, low, close, volume)
        df["volume_sma_20"] = volume.rolling(20, min_periods=1).mean()
        df["volume_ratio"] = np.where(df["volume_sma_20"] > 0, volume / df["volume_sma_20"], 0.0)
        df["timeframe"] = timeframe
        return df

    def latest_snapshot(self, candles: pd.DataFrame, timeframe: str) -> IndicatorSnapshot | None:
        """Return the latest indicator snapshot for a timeframe."""
        calculated = self.calculate(candles, timeframe)
        if calculated.empty:
            return None
        latest = calculated.iloc[-1]
        return IndicatorSnapshot(
            timeframe=timeframe,
            ema_9=self._nullable(latest.get("ema_9")),
            ema_20=self._nullable(latest.get("ema_20")),
            ema_50=self._nullable(latest.get("ema_50")),
            rsi=self._nullable(latest.get("rsi")),
            macd=self._nullable(latest.get("macd")),
            macd_signal=self._nullable(latest.get("macd_signal")),
            macd_histogram=self._nullable(latest.get("macd_histogram")),
            atr=self._nullable(latest.get("atr")),
            vwap=self._nullable(latest.get("vwap")),
            volume_ratio=self._nullable(latest.get("volume_ratio")),
        )

    @staticmethod
    def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        average_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        average_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = average_gain / average_loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _macd(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal, macd - signal

    @staticmethod
    def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        previous_close = close.shift(1)
        true_range = pd.concat(
            [(high - low), (high - previous_close).abs(), (low - previous_close).abs()], axis=1
        ).max(axis=1)
        return true_range.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    @staticmethod
    def _vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        typical_price = (high + low + close) / 3
        cumulative_volume = volume.cumsum().replace(0, np.nan)
        return (typical_price * volume).cumsum() / cumulative_volume

    @staticmethod
    def _nullable(value: object) -> float | None:
        if value is None or pd.isna(value):
            return None
        return float(value)
