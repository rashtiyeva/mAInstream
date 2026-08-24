from pydantic import BaseModel, Field


class LyricContinuationRequest(BaseModel):
    lyric: str = Field(
        max_length=300,
        description="A lyric snippet provided by the user.",
    )
