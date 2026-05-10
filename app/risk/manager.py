"""Risk management calculations for manual trade plans."""

from app.core.schemas import PredictionDirection, TradePlan


class RiskManager:
    """Calculates entry, stop loss, take profit, and reward/risk."""

    def __init__(self, atr_stop_multiplier: float = 1.2, atr_target_multiplier: float = 2.0) -> None:
        self.atr_stop_multiplier = atr_stop_multiplier
        self.atr_target_multiplier = atr_target_multiplier

    def build_plan(self, direction: PredictionDirection, entry_price: float, atr: float) -> TradePlan | None:
        """Create a scalp plan for UP/DOWN predictions; return None for NO TRADE."""
        if direction == PredictionDirection.NO_TRADE or atr <= 0:
            return None

        stop_distance = atr * self.atr_stop_multiplier
        target_distance = atr * self.atr_target_multiplier
        if direction == PredictionDirection.UP:
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + target_distance
        else:
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - target_distance

        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        return TradePlan(
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=round(reward / risk, 2) if risk else 0.0,
        )
