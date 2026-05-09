"""Offline pyttsx3 voice alerts."""

import pyttsx3

from app.core.schemas import Signal, SignalAction


class VoiceAssistant:
    """Speaks high-confidence manual signal alerts."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.engine = pyttsx3.init() if enabled else None

    def announce(self, signal: Signal) -> None:
        """Speak a concise signal summary."""
        if not self.enabled or not self.engine or signal.action == SignalAction.NO_TRADE:
            return
        direction = "bullish" if signal.action == SignalAction.BUY else "bearish"
        self.engine.say(f"Strong {direction} momentum detected. Suggested scalp {signal.action.value}.")
        self.engine.runAndWait()
