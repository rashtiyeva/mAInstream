from fastapi import FastAPI

from app.api.lyrics_controller import router as lyrics_router
from app.core.logging_config import configure_logging

configure_logging()


app = FastAPI(
    title="Mainstream",
    version="1.0.0",
)

app.include_router(lyrics_router)


@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "running"}