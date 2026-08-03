from pydantic import BaseModel, Field


class LyricContinuationRequest(BaseModel):
    lyric: str = Field(
        min_length=3,
        max_length=300,
        description="A lyric snippet provided by the user.",
    )