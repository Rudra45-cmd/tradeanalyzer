"""XGBoost-powered prediction engine for scalping signals."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from app.core.schemas import PredictionDirection, PredictionResult, RiskLevel

LABELS = [PredictionDirection.DOWN, PredictionDirection.NO_TRADE, PredictionDirection.UP]


class XGBoostPredictionEngine:
    """Wraps an XGBoost classifier and conservative fallback rules.

    The production model can be trained offline with historical Binance candles.
    Until a model is fitted, this engine falls back to deterministic indicator
    scoring so the rest of the assistant remains usable during development.
    """

    feature_columns = [
        "ema_9",
        "ema_20",
        "ema_50",
        "rsi",
        "macd",
        "macd_signal",
        "macd_histogram",
        "atr",
        "vwap",
        "volume_ratio",
        "close",
    ]

    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model = XGBClassifier(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            tree_method="hist",
        )
        self.is_trained = False
        if model_path and Path(model_path).exists():
            self.model.load_model(model_path)
            self.is_trained = True

    def predict(self, feature_frame: pd.DataFrame, suggested_timeframe: str) -> PredictionResult:
        """Predict UP, DOWN, or NO TRADE from the latest feature row."""
        if feature_frame.empty:
            return PredictionResult(
                direction=PredictionDirection.NO_TRADE,
                confidence=0.0,
                suggested_timeframe=suggested_timeframe,
                risk_level=RiskLevel.HIGH,
            )

        latest = feature_frame.iloc[-1]
        features = self._extract_features(latest)
        if self.is_trained:
            probability = self.model.predict_proba(pd.DataFrame([features]))[0]
            label_index = int(np.argmax(probability))
            direction = LABELS[label_index]
            confidence = float(probability[label_index])
        else:
            direction, confidence = self._fallback_prediction(latest)

        return PredictionResult(
            direction=direction,
            confidence=confidence,
            suggested_timeframe=suggested_timeframe,
            risk_level=self._risk_level(latest, confidence),
            features=features,
        )

    def train(self, training_frame: pd.DataFrame, target_column: str = "target") -> None:
        """Train the model with engineered features and integer labels."""
        training_frame = training_frame.dropna(subset=self.feature_columns + [target_column])
        self.model.fit(training_frame[self.feature_columns], training_frame[target_column])
        self.is_trained = True

    def save(self, path: str | Path) -> None:
        """Persist the fitted XGBoost model."""
        self.model.save_model(path)

    def _extract_features(self, row: pd.Series) -> dict[str, float]:
        return {column: float(row.get(column, 0.0) or 0.0) for column in self.feature_columns}

    @staticmethod
    def _fallback_prediction(row: pd.Series) -> tuple[PredictionDirection, float]:
        ema_9 = float(row.get("ema_9", 0) or 0)
        ema_20 = float(row.get("ema_20", 0) or 0)
        ema_50 = float(row.get("ema_50", 0) or 0)
        rsi = float(row.get("rsi", 50) or 50)
        macd_histogram = float(row.get("macd_histogram", 0) or 0)
        volume_ratio = float(row.get("volume_ratio", 1) or 1)

        bullish = ema_9 > ema_20 > ema_50 and 52 <= rsi <= 72 and macd_histogram > 0 and volume_ratio >= 1.1
        bearish = ema_9 < ema_20 < ema_50 and 28 <= rsi <= 48 and macd_histogram < 0 and volume_ratio >= 1.1
        if bullish:
            return PredictionDirection.UP, min(0.9, 0.58 + (volume_ratio - 1) * 0.12)
        if bearish:
            return PredictionDirection.DOWN, min(0.9, 0.58 + (volume_ratio - 1) * 0.12)
        return PredictionDirection.NO_TRADE, 0.55

    @staticmethod
    def _risk_level(row: pd.Series, confidence: float) -> RiskLevel:
        atr = float(row.get("atr", 0) or 0)
        close = float(row.get("close", 1) or 1)
        atr_percent = atr / close if close else 0
        if confidence >= 0.75 and atr_percent < 0.006:
            return RiskLevel.LOW
        if confidence >= 0.62 and atr_percent < 0.012:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH
