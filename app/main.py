"""FastAPI backend starter for the AI-powered crypto scalping assistant."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import candle_store, router
from app.core.config import get_settings
from app.data.binance_ws import BinanceKlineWebSocket

settings = get_settings()
stream = BinanceKlineWebSocket(settings)
stream.subscribe(candle_store.upsert)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, ARG001 - FastAPI lifespan signature
    """Start and stop background market data streaming."""
    import asyncio

    task = asyncio.create_task(stream.start())
    try:
        yield
    finally:
        stream.stop()
        task.cancel()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Suggestions-only AI crypto scalping assistant. It never executes real trades.",
    lifespan=lifespan,
)
app.include_router(router, prefix="/api")
