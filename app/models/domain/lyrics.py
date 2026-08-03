from pydantic import BaseModel

from app.models.domain.song import Song


class Lyrics(BaseModel):
    song: Song
    lines: list[str]