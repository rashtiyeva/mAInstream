from fastapi import APIRouter, Depends

from app.dependencies.services import get_song_identifier_service
from app.models.dto.request import LyricContinuationRequest
from app.models.dto.response import LyricContinuationResponse
from app.services.song_identifier_service import SongIdentifierService

router = APIRouter(prefix="/lyrics", tags=["Lyrics"])


@router.post("/identify", response_model=LyricContinuationResponse)
async def identify_song(
    request: LyricContinuationRequest,
    service: SongIdentifierService = Depends(get_song_identifier_service),
):
    song = await service.identify_song(request.lyric)

    return LyricContinuationResponse(
        song=song.title,
        artist=song.artist,
        next_line="",
    )