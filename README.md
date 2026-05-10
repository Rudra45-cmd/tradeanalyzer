# TradeAnalyzer AI Scalping Assistant

TradeAnalyzer is a Python 3.11 desktop + API starter for a personal, suggestions-only crypto scalping assistant. It analyzes live Binance BTCUSDT market data and can suggest `BUY`, `SELL`, or `NO TRADE` without placing real orders.

> Safety: this project intentionally contains no exchange order-execution code. Signals are manual suggestions only.

## Project Architecture

```text
tradeanalyzer/
├── app/
│   ├── ai/                 # XGBoost prediction engine and model training hooks
│   ├── alerts/             # Telegram signal alerts
│   ├── api/                # FastAPI routes and service wiring
│   ├── backtesting/        # Historical Binance data and backtest engine
│   ├── core/               # Settings and shared Pydantic schemas
│   ├── data/               # Binance WebSocket ingestion and candle store
│   ├── db/                 # PostgreSQL SQLAlchemy models and repositories
│   ├── indicators/         # EMA, RSI, MACD, ATR, VWAP, volume analysis
│   ├── risk/               # Entry, stop loss, take profit, R/R calculations
│   ├── screen/             # Optional OpenCV + OCR TradingView screen monitor
│   ├── signals/            # Multi-timeframe analysis and no-trade detection
│   ├── ui/                 # PyQt5 dark dashboard starter
│   └── voice/              # pyttsx3 voice assistant
├── scripts/                # Local entrypoints
├── tests/                  # Test suite placeholder
├── .env.example            # Environment variable template
└── requirements.txt        # Python dependencies
```

## Core Capabilities

- Binance WebSocket streaming for BTCUSDT candles on `1m`, `3m`, `5m`, and `15m` intervals.
- Multi-timeframe logic that uses `15m` trend confirmation and dynamically selects an entry timeframe from `1m`, `3m`, and `5m` based on volatility.
- Indicator engine for EMA 9/20/50, RSI, MACD, ATR, VWAP, and relative volume.
- XGBoost prediction engine returning direction, confidence, suggested timeframe, and risk level.
- No-trade filters for sideways markets, low volume, weak momentum, and fake breakout conditions.
- Risk manager for entry, stop loss, take profit, and risk/reward ratio.
- FastAPI backend starter, PostgreSQL persistence models, Telegram alerts, pyttsx3 voice alerts, PyQt5 UI, screen OCR scaffold, and historical backtesting scaffold.

## Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/run_api.py
```

Open the API at <http://localhost:8000/docs>.

## API Endpoints

- `GET /api/health` — service health and configured timeframes.
- `GET /api/safety` — confirms suggestions-only operation.
- `GET /api/signals/latest` — latest AI/manual-review signal.
- `POST /api/signals/save` — persist latest signal to PostgreSQL.
- `GET /api/indicators/{timeframe}` — latest indicator snapshot.

## Desktop Dashboard

```bash
python scripts/run_dashboard.py
```

The dashboard is a dark PyQt5 starter that displays a live chart area, prediction headline, and signal history panel.

## PostgreSQL

Set `DATABASE_URL` in `.env` to an async SQLAlchemy URL, for example:

```text
DATABASE_URL=postgresql+asyncpg://tradeanalyzer:tradeanalyzer@localhost:5432/tradeanalyzer
```

The models are defined in `app/db/models.py`. Add Alembic migrations before production use.

## Trading Safety

This assistant is for personal research and manual decision support. It does not execute trades, does not manage exchange API keys, and should not be treated as financial advice.
