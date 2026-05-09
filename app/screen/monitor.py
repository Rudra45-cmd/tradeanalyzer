"""Optional TradingView screen analysis using screenshots, OpenCV, and OCR."""

from dataclasses import dataclass

import cv2
import numpy as np
import pyautogui
import pytesseract


@dataclass(slots=True)
class ScreenAnalysis:
    """Detected TradingView metadata from screen OCR."""

    pair_name: str | None
    timeframe: str | None
    candle_count_estimate: int


class TradingViewScreenMonitor:
    """Reads chart metadata from the desktop screen; disabled by default."""

    def analyze_screen(self) -> ScreenAnalysis:
        """Capture the screen and estimate pair, timeframe, and candle count."""
        screenshot = np.array(pyautogui.screenshot())
        gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        text = pytesseract.image_to_string(gray).upper()
        pair = self._detect_pair(text)
        timeframe = self._detect_timeframe(text)
        edges = cv2.Canny(gray, 80, 160)
        candle_count = int(np.count_nonzero(edges) / 5000)
        return ScreenAnalysis(pair_name=pair, timeframe=timeframe, candle_count_estimate=candle_count)

    @staticmethod
    def _detect_pair(text: str) -> str | None:
        for token in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
            if token in text.replace("/", ""):
                return token
        return None

    @staticmethod
    def _detect_timeframe(text: str) -> str | None:
        for token in ("1M", "3M", "5M", "15M"):
            if token in text:
                return token.lower()
        return None
