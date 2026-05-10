"""Shared domain schemas used by the API, services, and UI."""

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class SignalAction(StrEnum):
    """Supported assistant actions. This app never executes trades."""

    BUY = "BUY"
    SELL = "SELL"
    NO_TRADE = "NO TRADE"


class PredictionDirection(StrEnum):
    """AI classifier labels."""

    UP = "UP"
    DOWN = "DOWN"
    NO_TRADE = "NO TRADE"


class RiskLevel(StrEnum):
    """Human-readable risk buckets."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Candle(BaseModel):
    """Normalized Binance candle/kline payload."""

    symbol: str
    timeframe: str
    open_time: datetime
    close_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_closed: bool = False


class IndicatorSnapshot(BaseModel):
    """Latest technical indicator values for a timeframe."""

    timeframe: str
    ema_9: float | None = None
    ema_20: float | None = None
    ema_50: float | None = None
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    atr: float | None = None
    vwap: float | None = None
    volume_ratio: float | None = None


class PredictionResult(BaseModel):
    """AI prediction response."""

    direction: PredictionDirection
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_timeframe: str
    risk_level: RiskLevel
    features: dict[str, float] = Field(default_factory=dict)


class TradePlan(BaseModel):
    """Suggested trade parameters for manual review."""

    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float


class Signal(BaseModel):
    """Complete assistant signal. Suggestions only; no order execution."""

    action: SignalAction
    symbol: str
    timeframe: str
    trend_direction: str
    confidence: float
    risk_level: RiskLevel
    reason: str
    prediction: PredictionResult | None = None
    trade_plan: TradePlan | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
