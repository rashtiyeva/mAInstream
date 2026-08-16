from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import GeniusResponseException
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.providers.genius_provider import GeniusProvider


@pytest.fixture
def song() -> Song:
    return Song(
        title="Yesterday",
        artist="The Beatles",
    )


@pytest.fixture
def genius_response() -> MagicMock:
    response = MagicMock()

    response.json.return_value = {
        "response": {
            "hits": [
                {
                    "result": {
                        "title": "Yesterday",
                        "url": "https://genius.com/The-beatles-yesterday-lyrics",
                        "primary_artist": {
                            "name": "The Beatles",
                        },
                    }
                }
            ]
        }
    }

    return response


@pytest.mark.asyncio
async def test_find_song_returns_matching_song(
    song: Song,
    genius_response: MagicMock,
) -> None:
    client = MagicMock()
    client.search = AsyncMock(return_value=genius_response)

    provider = GeniusProvider(client)

    result = await provider.find_song(song)

    assert result == SongSource(
        song=song,
        url="https://genius.com/The-beatles-yesterday-lyrics",
    )

    client.search.assert_awaited_once_with(
        "Yesterday The Beatles"
    )


@pytest.mark.asyncio
async def test_find_song_returns_none_when_song_not_found(
    song: Song,
) -> None:
    client = MagicMock()

    response = MagicMock()
    response.json.return_value = {
        "response": {
            "hits": [
                {
                    "result": {
                        "title": "Let It Be",
                        "url": "https://genius.com/The-beatles-let-it-be-lyrics",
                        "primary_artist": {
                            "name": "The Beatles",
                        },
                    }
                }
            ]
        }
    }

    client.search = AsyncMock(return_value=response)

    provider = GeniusProvider(client)

    result = await provider.find_song(song)

    assert result is None


@pytest.mark.asyncio
async def test_find_song_raises_when_response_is_invalid(
    song: Song,
) -> None:
    client = MagicMock()

    response = MagicMock()
    response.json.return_value = {
        "invalid": "response"
    }

    client.search = AsyncMock(return_value=response)

    provider = GeniusProvider(client)

    with pytest.raises(GeniusResponseException):
        await provider.find_song(song)


def test_matches_song_normalizes_case_and_whitespace() -> None:
    song = Song(
        title="Yesterday",
        artist="The Beatles",
    )

    result = GeniusProvider._matches_song(
        song=song,
        title="  YESTERDAY  ",
        artist="THE   BEATLES",
    )

    assert result is True