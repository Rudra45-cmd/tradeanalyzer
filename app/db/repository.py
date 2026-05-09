"""Persistence helpers for generated signals."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import Signal
from app.db.models import AIPrediction, SignalHistory


class SignalRepository:
    """Stores and retrieves signal history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_signal(self, signal: Signal) -> SignalHistory:
        """Persist a generated signal and optional AI prediction."""
        record = SignalHistory(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            action=signal.action.value,
            confidence=signal.confidence,
            risk_level=signal.risk_level.value,
            trend_direction=signal.trend_direction,
            reason=signal.reason,
            trade_plan=signal.trade_plan.model_dump() if signal.trade_plan else None,
        )
        self.session.add(record)
        if signal.prediction:
            self.session.add(
                AIPrediction(
                    symbol=signal.symbol,
                    timeframe=signal.prediction.suggested_timeframe,
                    direction=signal.prediction.direction.value,
                    confidence=signal.prediction.confidence,
                    risk_level=signal.prediction.risk_level.value,
                    features=signal.prediction.features,
                )
            )
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def recent_signals(self, limit: int = 50) -> list[SignalHistory]:
        """Return recent signals newest first."""
        result = await self.session.scalars(select(SignalHistory).order_by(SignalHistory.created_at.desc()).limit(limit))
        return list(result)
