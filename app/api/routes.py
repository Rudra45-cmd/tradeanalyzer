"""FastAPI routes for health, signals, indicators, and safety metadata."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.schemas import Signal
from app.data.candle_store import CandleStore
from app.db.repository import SignalRepository
from app.db.session import get_session
from app.indicators.engine import IndicatorEngine
from app.signals.service import SignalService

router = APIRouter()
candle_store = CandleStore(maxlen=get_settings().max_candles_per_timeframe)
indicator_engine = IndicatorEngine()
signal_service = SignalService(candle_store=candle_store, indicators=indicator_engine)


@router.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, str | list[str]]:
    """Return service health and configured timeframes."""
    return {"status": "ok", "app": settings.app_name, "timeframes": settings.timeframe_list}


@router.get("/safety")
async def safety() -> dict[str, str]:
    """Explicitly state that the assistant never executes real trades."""
    return {"mode": "suggestions_only", "message": "No automated order execution is implemented."}


@router.get("/signals/latest", response_model=Signal)
async def latest_signal(settings: Settings = Depends(get_settings)) -> Signal:
    """Return the latest generated assistant signal."""
    return signal_service.latest_signal(settings.symbol.upper())


@router.post("/signals/save")
async def save_latest_signal(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    """Persist the latest generated signal in PostgreSQL."""
    signal = signal_service.latest_signal(settings.symbol.upper())
    record = await SignalRepository(session).add_signal(signal)
    return {"id": record.id}


@router.get("/indicators/{timeframe}")
async def indicators(timeframe: str) -> dict[str, object]:
    """Return the latest indicator snapshot for a timeframe."""
    snapshot = indicator_engine.latest_snapshot(candle_store.frame(timeframe), timeframe)
    return snapshot.model_dump() if snapshot else {"timeframe": timeframe, "message": "No candles available yet"}
