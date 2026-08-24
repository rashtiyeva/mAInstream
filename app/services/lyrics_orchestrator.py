import logging

from app.clients.genius_client import GeniusClient
from app.core.exceptions import (
    LyricTooGenericException,
    SongNotFoundException,
)
from app.models.dto.lyric_continuation_response import (
    LyricContinuationResponse,
)
from app.models.dto.progress_event import ProgressEvent, ProgressStep
from app.parsers.genius_lyrics_parser import GeniusLyricsParser
from app.services.lyric_input_validator import LyricInputValidator
from app.services.lyrics_provider_service import LyricsProviderService
from app.services.next_line_service import NextLineService
from app.services.progress_reporter import (
    NoOpProgressReporter,
    ProgressReporter,
)
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
        lyric_input_validator: LyricInputValidator,
    ) -> None:
        self._song_identifier_service = song_identifier_service
        self._lyrics_provider_service = lyrics_provider_service
        self._genius_client = genius_client
        self._lyrics_parser = lyrics_parser
        self._next_line_service = next_line_service
        self._lyric_input_validator = lyric_input_validator

    async def get_continuation(
        self,
        lyric: str,
        progress_reporter: ProgressReporter | None = None,
    ) -> LyricContinuationResponse:
        reporter = progress_reporter or NoOpProgressReporter()
        logger.info("Starting lyric continuation.")

        await reporter.report(
            ProgressEvent(step=ProgressStep.VALIDATING_INPUT)
        )
        input_is_too_generic = (
            self._lyric_input_validator.is_too_generic(lyric)
        )

        await reporter.report(
            ProgressEvent(step=ProgressStep.IDENTIFYING_SONG)
        )
        try:
            song = await self._song_identifier_service.identify_song(lyric)
        except SongNotFoundException as exception:
            if input_is_too_generic:
                raise LyricTooGenericException(
                    "The provided lyric is too short to identify reliably."
                ) from exception

            raise

        logger.info(
            "Song identified: %s - %s",
            song.title,
            song.artist,
        )

        await reporter.report(
            ProgressEvent(
                step=ProgressStep.SONG_IDENTIFIED,
                song=song.title,
                artist=song.artist,
            )
        )

        await reporter.report(
            ProgressEvent(step=ProgressStep.SEARCHING_LYRICS)
        )

        source = await self._lyrics_provider_service.find_song_source(
            song,
        )

        logger.info("Lyrics source found.")

        await reporter.report(
            ProgressEvent(step=ProgressStep.LYRICS_SOURCE_FOUND)
        )

        await reporter.report(
            ProgressEvent(step=ProgressStep.FETCHING_LYRICS)
        )

        page = await self._genius_client.get_page(source.url)

        logger.info("Genius page retrieved.")

        await reporter.report(
            ProgressEvent(step=ProgressStep.PARSING_LYRICS)
        )

        lyrics = self._lyrics_parser.parse(page.text)

        logger.info("Genius lyrics parsed successfully.")

        await reporter.report(
            ProgressEvent(step=ProgressStep.MATCHING_LYRIC)
        )

        continuation = self._next_line_service.find_next_line(
            lyrics=lyrics,
            user_lyric=lyric,
            song_title=song.title,
        )

        logger.info("Lyric continuation found.")

        await reporter.report(
            ProgressEvent(step=ProgressStep.CONTINUATION_FOUND)
        )

        return LyricContinuationResponse(
            song=song.title,
            artist=song.artist,
            continuation=continuation,
        )
