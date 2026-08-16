from pydantic import BaseModel


class GeniusArtist(BaseModel):
    name: str


class GeniusResult(BaseModel):
    title: str
    url: str
    primary_artist: GeniusArtist


class GeniusHit(BaseModel):
    result: GeniusResult


class GeniusSearchResponseData(BaseModel):
    hits: list[GeniusHit]


class GeniusSearchResponse(BaseModel):
    response: GeniusSearchResponseData