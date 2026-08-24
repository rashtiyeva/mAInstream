import logging

import pytest

from app.parsers.genius_lyrics_parser import GeniusLyricsParser
from app.services.lyric_matcher import LyricMatcher
from app.services.lyric_normalizer import LyricNormalizer


def messages_for(
    caplog: pytest.LogCaptureFixture,
    logger_name: str,
) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.name == logger_name
    ]


def test_parser_keeps_full_clean_lyrics_in_debug_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    html = (
        '<div data-lyrics-container="true">'
        "First lyric line<br/>Second lyric line"
        "</div>"
    )

    with caplog.at_level(
        logging.DEBUG,
        logger="app.parsers.genius_lyrics_parser",
    ):
        GeniusLyricsParser().parse(html)

    messages = messages_for(
        caplog,
        "app.parsers.genius_lyrics_parser",
    )

    assert any("full_clean_lyrics" in message for message in messages)
    assert any("First lyric line\nSecond lyric line" in message for message in messages)
    assert any("cleaning_summary" in message for message in messages)


def test_user_normalization_logs_input_and_final_result(
    caplog: pytest.LogCaptureFixture,
) -> None:
    user_input = "  IT’S   The Climb  "

    with caplog.at_level(
        logging.DEBUG,
        logger="app.services.lyric_normalizer",
    ):
        result = LyricNormalizer.normalize_user_lyric(user_input)

    messages = messages_for(
        caplog,
        "app.services.lyric_normalizer",
    )

    assert result == "it's the climb"
    assert any(repr(user_input) in message for message in messages)
    assert any("result=\"it's the climb\"" in message for message in messages)


def test_fuzzy_match_logs_strategy_score_and_index(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(
        logging.INFO,
        logger="app.services.lyric_matcher",
    ):
        result = LyricMatcher().find_match(
            lyrics=["It's the climb"],
            user_lyric="itss the climb",
        )

    messages = messages_for(
        caplog,
        "app.services.lyric_matcher",
    )

    assert result == 0
    assert any(
        "strategy=fuzzy" in message
        and "score=" in message
        and "index=0" in message
        for message in messages
    )
