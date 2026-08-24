from unittest.mock import AsyncMock, Mock

import pytest

from app.core.exceptions import (
    GeniusApiException,
    LyricTooGenericException,
    SongNotFoundException,
)
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.models.dto.lyric_continuation_response import (
    LyricContinuationResponse,
)
from app.models.dto.progress_event import ProgressEvent, ProgressStep
from app.services.lyrics_orchestrator import LyricsOrchestrator
from app.services.lyric_input_validator import LyricInputValidator
from app.services.lyrics_provider_service import LyricsProviderService
from app.services.next_line_service import NextLineService
from app.services.song_identifier_service import SongIdentifierService


class CollectingProgressReporter:
    def __init__(self) -> None:
        self.events: list[ProgressEvent] = []

    async def report(self, event: ProgressEvent) -> None:
        self.events.append(event)


@pytest.fixture
def song_identifier_service() -> Mock:
    service = Mock(spec=SongIdentifierService)
    service.identify_song = AsyncMock()
    return service


@pytest.fixture
def lyrics_provider_service() -> Mock:
    service = Mock(spec=LyricsProviderService)
    service.find_song_source = AsyncMock()
    return service


@pytest.fixture
def genius_client() -> Mock:
    client = Mock()
    client.get_page = AsyncMock()
    return client


@pytest.fixture
def lyrics_parser() -> Mock:
    return Mock()


@pytest.fixture
def next_line_service() -> Mock:
    service = Mock(spec=NextLineService)
    service.find_next_line.return_value = "I will be your girl"
    return service


@pytest.fixture
def lyric_input_validator() -> Mock:
    validator = Mock(spec=LyricInputValidator)
    validator.is_too_generic.return_value = False
    return validator


@pytest.fixture
def orchestrator(
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    lyric_input_validator: Mock,
) -> LyricsOrchestrator:
    return LyricsOrchestrator(
        song_identifier_service=song_identifier_service,
        lyrics_provider_service=lyrics_provider_service,
        genius_client=genius_client,
        lyrics_parser=lyrics_parser,
        next_line_service=next_line_service,
        lyric_input_validator=lyric_input_validator,
    )


@pytest.fixture
def song() -> Song:
    return Song(
        title="Another Life",
        artist="Example Artist",
    )


@pytest.fixture
def song_source(song: Song) -> SongSource:
    return SongSource(
        song=song,
        url="https://genius.com/example-lyrics",
    )


@pytest.fixture
def genius_response() -> Mock:
    response = Mock()
    response.text = "<html>lyrics</html>"
    return response


@pytest.fixture
def clean_lyrics() -> str:
    return "In another life\nI will be your girl"


@pytest.fixture
def lyric() -> str:
    return "In another life"


@pytest.mark.asyncio
async def test_get_continuation_returns_response(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    song: Song,
    song_source: SongSource,
    genius_response: Mock,
    clean_lyrics: str,
    lyric: str,
) -> None:
    expected_continuation = "I will be your girl"

    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.return_value = genius_response
    lyrics_parser.parse.return_value = clean_lyrics
    next_line_service.find_next_line.return_value = expected_continuation

    result = await orchestrator.get_continuation(lyric)

    assert result == LyricContinuationResponse(
        song=song.title,
        artist=song.artist,
        continuation=expected_continuation,
    )


@pytest.mark.asyncio
async def test_get_continuation_identifies_song_from_lyric(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    song: Song,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.return_value = song

    await orchestrator.get_continuation(lyric)

    song_identifier_service.identify_song.assert_awaited_once_with(
        lyric,
    )


@pytest.mark.asyncio
async def test_get_continuation_finds_source_for_identified_song(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    song: Song,
    song_source: SongSource,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source

    await orchestrator.get_continuation(lyric)

    lyrics_provider_service.find_song_source.assert_awaited_once_with(
        song,
    )


@pytest.mark.asyncio
async def test_get_continuation_retrieves_source_page(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    song: Song,
    song_source: SongSource,
    genius_response: Mock,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.return_value = genius_response

    await orchestrator.get_continuation(lyric)

    genius_client.get_page.assert_awaited_once_with(
        song_source.url,
    )


@pytest.mark.asyncio
async def test_get_continuation_parses_retrieved_html(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    song: Song,
    song_source: SongSource,
    genius_response: Mock,
    clean_lyrics: str,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.return_value = genius_response
    lyrics_parser.parse.return_value = clean_lyrics

    await orchestrator.get_continuation(lyric)

    lyrics_parser.parse.assert_called_once_with(
        genius_response.text,
    )


@pytest.mark.asyncio
async def test_get_continuation_finds_next_line_from_parsed_lyrics(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    song: Song,
    song_source: SongSource,
    genius_response: Mock,
    clean_lyrics: str,
    lyric: str,
) -> None:
    expected_continuation = "I will be your girl"

    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.return_value = genius_response
    lyrics_parser.parse.return_value = clean_lyrics
    next_line_service.find_next_line.return_value = expected_continuation

    await orchestrator.get_continuation(lyric)

    next_line_service.find_next_line.assert_called_once_with(
        lyrics=clean_lyrics,
        user_lyric=lyric,
        song_title=song.title,
    )


@pytest.mark.asyncio
async def test_short_input_is_attempted_and_allowed_when_song_is_identified(
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    song: Song,
    song_source: SongSource,
    genius_response: Mock,
    clean_lyrics: str,
) -> None:
    orchestrator = LyricsOrchestrator(
        song_identifier_service=song_identifier_service,
        lyrics_provider_service=lyrics_provider_service,
        genius_client=genius_client,
        lyrics_parser=lyrics_parser,
        next_line_service=next_line_service,
        lyric_input_validator=LyricInputValidator(),
    )
    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.return_value = genius_response
    lyrics_parser.parse.return_value = clean_lyrics

    result = await orchestrator.get_continuation("Euphoria")

    song_identifier_service.identify_song.assert_awaited_once_with("Euphoria")
    assert result.song == song.title


@pytest.mark.asyncio
async def test_failed_short_input_becomes_lyric_too_generic(
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
) -> None:
    orchestrator = LyricsOrchestrator(
        song_identifier_service=song_identifier_service,
        lyrics_provider_service=lyrics_provider_service,
        genius_client=genius_client,
        lyrics_parser=lyrics_parser,
        next_line_service=next_line_service,
        lyric_input_validator=LyricInputValidator(),
    )
    song_identifier_service.identify_song.side_effect = (
        SongNotFoundException("Unable to identify the song.")
    )

    with pytest.raises(LyricTooGenericException):
        await orchestrator.get_continuation("shake it")

    song_identifier_service.identify_song.assert_awaited_once_with("shake it")


@pytest.mark.asyncio
async def test_failed_long_input_remains_song_not_found(
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
) -> None:
    orchestrator = LyricsOrchestrator(
        song_identifier_service=song_identifier_service,
        lyrics_provider_service=lyrics_provider_service,
        genius_client=genius_client,
        lyrics_parser=lyrics_parser,
        next_line_service=next_line_service,
        lyric_input_validator=LyricInputValidator(),
    )
    song_identifier_service.identify_song.side_effect = (
        SongNotFoundException("Unable to identify the song.")
    )

    with pytest.raises(SongNotFoundException):
        await orchestrator.get_continuation(
            "this lyric is not recognizable"
        )


@pytest.mark.asyncio
async def test_get_continuation_reports_progress_in_logical_order(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    song: Song,
    song_source: SongSource,
    genius_response: Mock,
    clean_lyrics: str,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.return_value = genius_response
    lyrics_parser.parse.return_value = clean_lyrics
    reporter = CollectingProgressReporter()

    await orchestrator.get_continuation(
        lyric,
        progress_reporter=reporter,
    )

    assert [event.step for event in reporter.events] == [
        ProgressStep.VALIDATING_INPUT,
        ProgressStep.IDENTIFYING_SONG,
        ProgressStep.SONG_IDENTIFIED,
        ProgressStep.SEARCHING_LYRICS,
        ProgressStep.LYRICS_SOURCE_FOUND,
        ProgressStep.FETCHING_LYRICS,
        ProgressStep.PARSING_LYRICS,
        ProgressStep.MATCHING_LYRIC,
        ProgressStep.CONTINUATION_FOUND,
    ]
    assert reporter.events[2].song == song.title
    assert reporter.events[2].artist == song.artist


@pytest.mark.asyncio
async def test_get_continuation_propagates_song_not_found_exception(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.side_effect = (
        SongNotFoundException(
            "Unable to identify the song.",
        )
    )

    with pytest.raises(
        SongNotFoundException,
        match="Unable to identify the song.",
    ):
        await orchestrator.get_continuation(lyric)

    lyrics_provider_service.find_song_source.assert_not_awaited()
    genius_client.get_page.assert_not_awaited()
    lyrics_parser.parse.assert_not_called()
    next_line_service.find_next_line.assert_not_called()


@pytest.mark.asyncio
async def test_get_continuation_propagates_genius_api_exception(
    orchestrator: LyricsOrchestrator,
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
    song: Song,
    song_source: SongSource,
    lyric: str,
) -> None:
    song_identifier_service.identify_song.return_value = song
    lyrics_provider_service.find_song_source.return_value = song_source
    genius_client.get_page.side_effect = GeniusApiException(
        "Failed to communicate with Genius API.",
    )

    with pytest.raises(
        GeniusApiException,
        match="Failed to communicate with Genius API.",
    ):
        await orchestrator.get_continuation(lyric)

    lyrics_parser.parse.assert_not_called()
    next_line_service.find_next_line.assert_not_called()
