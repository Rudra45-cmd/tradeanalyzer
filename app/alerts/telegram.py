"""Telegram alert integration for manual trade suggestions."""

from telegram import Bot

from app.core.config import Settings, get_settings
from app.core.schemas import Signal, SignalAction


class TelegramAlertService:
    """Sends trade suggestions to a configured Telegram chat."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._bot = Bot(self.settings.telegram_bot_token) if self.settings.telegram_bot_token else None

    async def send_signal(self, signal: Signal) -> None:
        """Send a formatted signal if Telegram is configured."""
        if not self._bot or not self.settings.telegram_chat_id or signal.action == SignalAction.NO_TRADE:
            return
        plan = signal.trade_plan
        plan_text = "No trade plan"
        if plan:
            plan_text = (
                f"Entry: {plan.entry_price:.2f}\nSL: {plan.stop_loss:.2f}\n"
                f"TP: {plan.take_profit:.2f}\nR/R: {plan.risk_reward_ratio:.2f}"
            )
        await self._bot.send_message(
            chat_id=self.settings.telegram_chat_id,
            text=(
                f"{signal.action.value} {signal.symbol} ({signal.timeframe})\n"
                f"Confidence: {signal.confidence:.0%}\nRisk: {signal.risk_level.value}\n"
                f"Trend: {signal.trend_direction}\n{plan_text}\n\n{signal.reason}\n\n"
                "Suggestion only. No automated trade was executed."
            ),
        )
