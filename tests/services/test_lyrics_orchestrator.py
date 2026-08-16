from unittest.mock import AsyncMock, Mock

import pytest

from app.core.exceptions import (
    GeniusApiException,
    SongNotFoundException,
)
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.models.dto.lyric_continuation_response import (
    LyricContinuationResponse,
)
from app.services.lyrics_orchestrator import LyricsOrchestrator
from app.services.lyrics_provider_service import LyricsProviderService
from app.services.next_line_service import NextLineService
from app.services.song_identifier_service import SongIdentifierService


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
def orchestrator(
    song_identifier_service: Mock,
    lyrics_provider_service: Mock,
    genius_client: Mock,
    lyrics_parser: Mock,
    next_line_service: Mock,
) -> LyricsOrchestrator:
    return LyricsOrchestrator(
        song_identifier_service=song_identifier_service,
        lyrics_provider_service=lyrics_provider_service,
        genius_client=genius_client,
        lyrics_parser=lyrics_parser,
        next_line_service=next_line_service,
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
    )


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