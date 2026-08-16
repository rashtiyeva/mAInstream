from pydantic import ValidationError

from app.clients.genius_client import GeniusClient
from app.core.exceptions import GeniusResponseException
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.models.dto.genius_search_response import GeniusSearchResponse
from app.providers.base_provider import BaseProvider


class GeniusProvider(BaseProvider):

    def __init__(self, client: GeniusClient) -> None:
        self._client = client

    async def find_song(
        self,
        song: Song,
    ) -> SongSource | None:
        query = f"{song.title} {song.artist}"

        response = await self._client.search(query)

        try:
            data = GeniusSearchResponse.model_validate(
                response.json()
            )
        except (ValueError, ValidationError) as ex:
            raise GeniusResponseException(
                "Genius returned an invalid response."
            ) from ex

        for hit in data.response.hits:
            result = hit.result

            if self._matches_song(
                song=song,
                title=result.title,
                artist=result.primary_artist.name,
            ):
                return SongSource(
                    song=song,
                    url=result.url,
                )

        return None

    @staticmethod
    def _matches_song(
        song: Song,
        title: str,
        artist: str,
    ) -> bool:
        return (
            GeniusProvider._normalize(song.title)
            == GeniusProvider._normalize(title)
            and GeniusProvider._normalize(song.artist)
            == GeniusProvider._normalize(artist)
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.lower().split())