import pytest

from app.core.exceptions import (
    ContinuationNotFoundException,
    LyricNotFoundException,
)
from app.services.next_line_service import NextLineService


@pytest.fixture
def service() -> NextLineService:
    return NextLineService()


@pytest.fixture
def lyrics() -> str:
    return (
        "In another life\n"
        "I would be your girl\n"
        "We keep all our promises\n"
        "Be us against the world"
    )


@pytest.mark.parametrize(
    ("user_lyric", "expected"),
    [
        (
            "In another life",
            "I would be your girl",
        ),
        (
            "IN ANOTHER LIFE",
            "I would be your girl",
        ),
        (
            "In AnoTher Life",
            "I would be your girl",
        ),
        (
            "In   another   life",
            "I would be your girl",
        ),
    ],
)
def test_find_next_line_returns_next_line_for_complete_lyric(
    service: NextLineService,
    lyrics: str,
    user_lyric: str,
    expected: str,
) -> None:
    result = service.find_next_line(
        lyrics=lyrics,
        user_lyric=user_lyric,
    )

    assert result == expected


def test_find_next_line_returns_remaining_text_and_next_line_for_partial_lyric(
    service: NextLineService,
    lyrics: str,
) -> None:
    result = service.find_next_line(
        lyrics=lyrics,
        user_lyric="In another",
    )

    assert result == "life...\n\nI would be your girl"


def test_partial_match_returns_line_remainder_and_next_line(
    service: NextLineService,
) -> None:
    lyrics = (
        "'Cause the players gonna play, play, play, play, play\n"
        "And the haters gonna hate, hate, hate, hate, hate"
    )

    result = service.find_next_line(
        lyrics=lyrics,
        user_lyric="the players gonna play",
    )

    assert result == (
        "play, play, play, play...\n\n"
        "And the haters gonna hate, hate, hate, hate, hate"
    )


def test_aggressive_partial_match_preserves_original_remainder(
    service: NextLineService,
) -> None:
    lyrics = (
        "I remember it all too well\n"
        "Wind in my hair, I was there"
    )

    result = service.find_next_line(
        lyrics=lyrics,
        user_lyric="'I remember it all too",
    )

    assert result == "well...\n\nWind in my hair, I was there"


@pytest.mark.parametrize(
    "user_input",
    [
        "Shake It Off",
        "shake it off",
        "SHAKE IT OFF",
    ],
)
def test_song_title_returns_first_lyric_line(
    service: NextLineService,
    user_input: str,
) -> None:
    lyrics = (
        "I stay out too late\n"
        "Got nothin' in my brain\n"
        "I shake it off, I shake it off"
    )

    result = service.find_next_line(
        lyrics=lyrics,
        user_lyric=user_input,
        song_title="Shake It Off",
    )

    assert result == "I stay out too late"


def test_find_next_line_raises_when_lyric_is_not_found(
    service: NextLineService,
    lyrics: str,
) -> None:
    with pytest.raises(
        LyricNotFoundException,
        match="Unable to find the provided lyric in the song.",
    ):
        service.find_next_line(
            lyrics=lyrics,
            user_lyric="Something completely different",
        )


@pytest.mark.parametrize(
    "user_lyric",
    [
        "",
        "   ",
    ],
)
def test_find_next_line_raises_when_user_lyric_is_empty(
    service: NextLineService,
    lyrics: str,
    user_lyric: str,
) -> None:
    with pytest.raises(
        LyricNotFoundException,
        match="Lyric input is empty.",
    ):
        service.find_next_line(
            lyrics=lyrics,
            user_lyric=user_lyric,
        )


@pytest.mark.parametrize(
    "lyrics",
    [
        "",
        "   ",
    ],
)
def test_find_next_line_raises_when_lyrics_are_empty(
    service: NextLineService,
    lyrics: str,
) -> None:
    with pytest.raises(
        LyricNotFoundException,
        match="Song lyrics are empty.",
    ):
        service.find_next_line(
            lyrics=lyrics,
            user_lyric="In another",
        )


def test_find_next_line_raises_when_complete_lyric_is_last_line(
    service: NextLineService,
) -> None:
    lyrics = (
        "First line\n"
        "Last line"
    )

    with pytest.raises(
        ContinuationNotFoundException,
        match="There is no next line for the provided lyric.",
    ):
        service.find_next_line(
            lyrics=lyrics,
            user_lyric="Last line",
        )
