from pydantic import BaseModel

from app.models.domain.song import Song


class SongSource(BaseModel):
    song: Song
    url: str