import logging

from app.clients.genius_client import GeniusClient
from app.models.dto.lyric_continuation_response import (
    LyricContinuationResponse,
)
from app.parsers.genius_lyrics_parser import GeniusLyricsParser
from app.services.lyrics_provider_service import LyricsProviderService
from app.services.next_line_service import NextLineService
from app.services.song_identifier_service import SongIdentifierService

logger = logging.getLogger(__name__)


class LyricsOrchestrator:

    def __init__(
        self,
        song_identifier_service: SongIdentifierService,
        lyrics_provider_service: LyricsProviderService,
        genius_client: GeniusClient,
        lyrics_parser: GeniusLyricsParser,
        next_line_service: NextLineService,
    ) -> None:
        self._song_identifier_service = song_identifier_service
        self._lyrics_provider_service = lyrics_provider_service
        self._genius_client = genius_client
        self._lyrics_parser = lyrics_parser
        self._next_line_service = next_line_service

    async def get_continuation(
        self,
        lyric: str,
    ) -> LyricContinuationResponse:
        logger.info("Starting lyric continuation.")

        song = await self._song_identifier_service.identify_song(lyric)

        logger.info(
            "Song identified: %s - %s",
            song.title,
            song.artist,
        )

        source = await self._lyrics_provider_service.find_song_source(
            song,
        )

        logger.info("Lyrics source found.")

        page = await self._genius_client.get_page(source.url)

        logger.info("Genius page retrieved.")

        lyrics = self._lyrics_parser.parse(page.text)

        logger.info("Genius lyrics parsed successfully.")

        continuation = self._next_line_service.find_next_line(
            lyrics=lyrics,
            user_lyric=lyric,
        )

        logger.info("Lyric continuation found.")

        return LyricContinuationResponse(
            song=song.title,
            artist=song.artist,
            continuation=continuation,
        )