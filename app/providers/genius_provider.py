import logging

from pydantic import ValidationError

from app.clients.genius_client import GeniusClient
from app.core.exceptions import GeniusResponseException
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.models.dto.genius_search_response import GeniusSearchResponse
from app.providers.base_provider import BaseProvider


logger = logging.getLogger(__name__)


class GeniusProvider(BaseProvider):

    def __init__(self, client: GeniusClient) -> None:
        self._client = client

    async def find_song(
        self,
        song: Song,
    ) -> SongSource | None:
        query = f"{song.title} {song.artist}"
        logger.info(
            "GENIUS PROVIDER | find_song | started | song=%r | artist=%r",
            song.title,
            song.artist,
        )

        response = await self._client.search(query)

        try:
            data = GeniusSearchResponse.model_validate(
                response.json()
            )
        except (ValueError, ValidationError) as ex:
            raise GeniusResponseException(
                "Genius returned an invalid response."
            ) from ex

        logger.debug(
            "GENIUS PROVIDER | search_results=%d",
            len(data.response.hits),
        )

        for index, hit in enumerate(data.response.hits):
            result = hit.result
            logger.debug(
                "GENIUS PROVIDER | candidate | index=%d | title=%r | "
                "artist=%r",
                index,
                result.title,
                result.primary_artist.name,
            )

            if self._matches_song(
                song=song,
                title=result.title,
                artist=result.primary_artist.name,
            ):
                logger.info(
                    "GENIUS PROVIDER | find_song | matched | index=%d",
                    index,
                )
                return SongSource(
                    song=song,
                    url=result.url,
                )

        logger.info("GENIUS PROVIDER | find_song | no_match")
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
