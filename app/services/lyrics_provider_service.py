import logging

from app.core.exceptions import LyricsNotFoundException
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.providers.genius_provider import GeniusProvider

logger = logging.getLogger(__name__)


class LyricsProviderService:
    """
    Service responsible for finding a song source.
    """

    def __init__(self, genius_provider: GeniusProvider) -> None:
        self._genius_provider = genius_provider

    async def find_song_source(self, song: Song) -> SongSource:
        logger.debug(
            "LYRICS PROVIDER | find_source | started | song=%r | artist=%r",
            song.title,
            song.artist,
        )
        source = await self._genius_provider.find_song(song)

        if source is None:
            logger.info("LYRICS PROVIDER | find_source | not_found")
            raise LyricsNotFoundException(
                "Unable to find the song on Genius."
            )

        logger.debug("LYRICS PROVIDER | find_source | completed")
        return source
