from pydantic import BaseModel


class Song(BaseModel):
    title: str
    artist: str