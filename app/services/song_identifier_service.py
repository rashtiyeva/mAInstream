import logging

from app.clients.openai_client import OpenAIClient
from app.core.exceptions import SongNotFoundException
from app.models.domain.song import Song

logger = logging.getLogger(__name__)


class SongIdentifierService:

    def __init__(self, client: OpenAIClient):
        self._client = client

    async def identify_song(self, lyric: str) -> Song:
        logger.debug("SONG IDENTIFIER | identify | started")
        song = await self._client.identify_song(lyric)

        if not song.title or not song.artist:
            logger.info("SONG IDENTIFIER | identify | incomplete_result")
            raise SongNotFoundException(
                "Unable to identify the song."
            )

        logger.debug("SONG IDENTIFIER | identify | completed")
        return song
