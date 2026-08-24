from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ProgressStep(StrEnum):
    VALIDATING_INPUT = "VALIDATING_INPUT"
    IDENTIFYING_SONG = "IDENTIFYING_SONG"
    SONG_IDENTIFIED = "SONG_IDENTIFIED"
    SEARCHING_LYRICS = "SEARCHING_LYRICS"
    LYRICS_SOURCE_FOUND = "LYRICS_SOURCE_FOUND"
    FETCHING_LYRICS = "FETCHING_LYRICS"
    PARSING_LYRICS = "PARSING_LYRICS"
    MATCHING_LYRIC = "MATCHING_LYRIC"
    CONTINUATION_FOUND = "CONTINUATION_FOUND"


class ProgressEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    step: ProgressStep
    song: str | None = None
    artist: str | None = None
