"""Simple vectorized backtesting scaffold for signal rules."""

import pandas as pd

from app.indicators.engine import IndicatorEngine


class BacktestEngine:
    """Backtests indicator-based scalp entries against historical candles."""

    def __init__(self, indicators: IndicatorEngine | None = None) -> None:
        self.indicators = indicators or IndicatorEngine()

    def run(self, candles: pd.DataFrame, timeframe: str = "5m") -> dict[str, float]:
        """Run a conservative EMA/MACD momentum backtest summary."""
        frame = self.indicators.calculate(candles, timeframe).dropna()
        if frame.empty:
            return {"trades": 0, "win_rate": 0.0, "average_return": 0.0}

        long_entries = (frame["ema_9"] > frame["ema_20"]) & (frame["macd_histogram"] > 0) & (frame["volume_ratio"] > 1)
        forward_return = frame["close"].shift(-3) / frame["close"] - 1
        trade_returns = forward_return[long_entries].dropna()
        if trade_returns.empty:
            return {"trades": 0, "win_rate": 0.0, "average_return": 0.0}
        return {
            "trades": float(len(trade_returns)),
            "win_rate": float((trade_returns > 0).mean()),
            "average_return": float(trade_returns.mean()),
        }
