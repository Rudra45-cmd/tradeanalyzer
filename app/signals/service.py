"""Multi-timeframe signal generation service."""

from app.ai.prediction_engine import XGBoostPredictionEngine
from app.core.schemas import PredictionDirection, RiskLevel, Signal, SignalAction
from app.data.candle_store import CandleStore
from app.indicators.engine import IndicatorEngine
from app.risk.manager import RiskManager


class SignalService:
    """Combines indicators, AI prediction, and no-trade filters."""

    def __init__(
        self,
        candle_store: CandleStore,
        indicators: IndicatorEngine | None = None,
        predictor: XGBoostPredictionEngine | None = None,
        risk_manager: RiskManager | None = None,
    ) -> None:
        self.candle_store = candle_store
        self.indicators = indicators or IndicatorEngine()
        self.predictor = predictor or XGBoostPredictionEngine()
        self.risk_manager = risk_manager or RiskManager()

    def latest_signal(self, symbol: str = "BTCUSDT") -> Signal:
        """Generate the latest scalping signal from 15m trend and 5m entry data."""
        trend_frame = self.indicators.calculate(self.candle_store.frame("15m"), "15m")
        entry_timeframe = self._select_entry_timeframe()
        entry_frame = self.indicators.calculate(self.candle_store.frame(entry_timeframe), entry_timeframe)

        if trend_frame.empty or entry_frame.empty or len(entry_frame) < 50:
            return self._no_trade(symbol, entry_timeframe, "Waiting for enough candles to analyze market structure.")

        latest_entry = entry_frame.iloc[-1]
        no_trade_reason = self._detect_no_trade(latest_entry)
        if no_trade_reason:
            return self._no_trade(symbol, entry_timeframe, no_trade_reason)

        trend_direction = self._trend_direction(trend_frame.iloc[-1])
        prediction = self.predictor.predict(entry_frame, entry_timeframe)
        if not self._confirmed_by_trend(prediction.direction, trend_direction):
            return self._no_trade(symbol, entry_timeframe, "AI direction is not aligned with 15m trend confirmation.")

        action = SignalAction.BUY if prediction.direction == PredictionDirection.UP else SignalAction.SELL
        trade_plan = self.risk_manager.build_plan(
            prediction.direction,
            entry_price=float(latest_entry["close"]),
            atr=float(latest_entry.get("atr", 0) or 0),
        )
        return Signal(
            action=action,
            symbol=symbol.upper(),
            timeframe=entry_timeframe,
            trend_direction=trend_direction,
            confidence=prediction.confidence,
            risk_level=prediction.risk_level,
            reason="High-probability scalp setup aligned with trend, momentum, and volume.",
            prediction=prediction,
            trade_plan=trade_plan,
        )

    def _select_entry_timeframe(self) -> str:
        """Choose 1m/3m/5m based on ATR percentage; default to 5m."""
        frame = self.indicators.calculate(self.candle_store.frame("5m"), "5m")
        if frame.empty:
            return "5m"
        latest = frame.iloc[-1]
        atr_percent = float(latest.get("atr", 0) or 0) / float(latest.get("close", 1) or 1)
        if atr_percent >= 0.008:
            return "1m"
        if atr_percent >= 0.004:
            return "3m"
        return "5m"

    @staticmethod
    def _trend_direction(row) -> str:  # noqa: ANN001 - pandas Series
        if row["ema_20"] > row["ema_50"] and row["close"] > row["vwap"]:
            return "BULLISH"
        if row["ema_20"] < row["ema_50"] and row["close"] < row["vwap"]:
            return "BEARISH"
        return "SIDEWAYS"

    @staticmethod
    def _confirmed_by_trend(direction: PredictionDirection, trend_direction: str) -> bool:
        return (direction == PredictionDirection.UP and trend_direction == "BULLISH") or (
            direction == PredictionDirection.DOWN and trend_direction == "BEARISH"
        )

    @staticmethod
    def _detect_no_trade(row) -> str | None:  # noqa: ANN001 - pandas Series
        volume_ratio = float(row.get("volume_ratio", 0) or 0)
        atr = float(row.get("atr", 0) or 0)
        close = float(row.get("close", 1) or 1)
        rsi = float(row.get("rsi", 50) or 50)
        macd_histogram = abs(float(row.get("macd_histogram", 0) or 0))

        if volume_ratio < 0.75:
            return "Low volume detected; avoiding weak liquidity scalp."
        if atr / close < 0.0015:
            return "Sideways/low-volatility market detected."
        if 45 <= rsi <= 55 and macd_histogram < atr * 0.03:
            return "Weak momentum detected; no edge for scalp entry."
        if volume_ratio > 1.8 and abs(float(row["close"]) - float(row["vwap"])) < atr * 0.15:
            return "Possible fake breakout: volume spike without clean VWAP displacement."
        return None

    @staticmethod
    def _no_trade(symbol: str, timeframe: str, reason: str) -> Signal:
        return Signal(
            action=SignalAction.NO_TRADE,
            symbol=symbol.upper(),
            timeframe=timeframe,
            trend_direction="UNKNOWN",
            confidence=0.0,
            risk_level=RiskLevel.HIGH,
            reason=reason,
        )
