from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.error_handling import register_exception_handlers
from app.api.lyrics_controller import router as lyrics_router
from app.core.logging_config import configure_logging
from app.dependencies.clients import close_clients

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await close_clients()


app = FastAPI(
    title="Mainstream",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(lyrics_router)


@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "running"}
