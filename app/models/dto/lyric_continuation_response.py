from pydantic import BaseModel, ConfigDict


class LyricContinuationResponse(BaseModel):
    """Response returned by the lyric continuation endpoint."""

    model_config = ConfigDict(frozen=True)

    song: str
    artist: str
    continuation: str