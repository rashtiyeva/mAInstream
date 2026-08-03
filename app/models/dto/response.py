from pydantic import BaseModel


class LyricContinuationResponse(BaseModel):
    song: str
    artist: str
    next_line: str