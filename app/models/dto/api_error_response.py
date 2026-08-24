from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ApiErrorCode(StrEnum):
    INVALID_REQUEST = "INVALID_REQUEST"
    LYRIC_TOO_GENERIC = "LYRIC_TOO_GENERIC"
    SONG_NOT_FOUND = "SONG_NOT_FOUND"
    LYRICS_NOT_FOUND = "LYRICS_NOT_FOUND"
    LYRIC_NOT_FOUND = "LYRIC_NOT_FOUND"
    CONTINUATION_NOT_FOUND = "CONTINUATION_NOT_FOUND"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: ApiErrorCode
    message: str
