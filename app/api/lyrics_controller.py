from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.services import get_lyrics_orchestrator
from app.models.dto.request import LyricContinuationRequest
from app.models.dto.response import LyricContinuationResponse
from app.services.lyrics_orchestrator import LyricsOrchestrator

router = APIRouter(prefix="/lyrics", tags=["Lyrics"])


@router.post(
    "/identify",
    response_model=LyricContinuationResponse,
)
async def identify_song(
    request: LyricContinuationRequest,
    orchestrator: Annotated[
        LyricsOrchestrator,
        Depends(get_lyrics_orchestrator),
    ],
) -> LyricContinuationResponse:
    return await orchestrator.get_continuation(request.lyric)