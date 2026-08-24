import pytest

from app.core.exceptions import LyricsNotFoundException
from app.parsers.genius_lyrics_parser import GeniusLyricsParser


def test_parse_returns_lyrics_from_genius_html():
    html = """
    <html>
        <body>
            <div data-lyrics-container="true">
                Yesterday
                <br/>
                All my troubles seemed so far away
                <br/>
                Now I need a place to hide away
            </div>
        </body>
    </html>
    """

    parser = GeniusLyricsParser()

    result = parser.parse(html)

    assert result == (
        "Yesterday\n"
        "All my troubles seemed so far away\n"
        "Now I need a place to hide away"
    )


def test_parse_combines_multiple_lyrics_containers():
    html = """
    <html>
        <body>
            <div data-lyrics-container="true">
                First verse
                <br/>
                First line
            </div>

            <div data-lyrics-container="true">
                Second verse
                <br/>
                Second line
            </div>
        </body>
    </html>
    """

    parser = GeniusLyricsParser()

    result = parser.parse(html)

    assert result == (
        "First verse\n"
        "First line\n"
        "Second verse\n"
        "Second line"
    )


def test_parse_raises_when_html_is_empty():
    parser = GeniusLyricsParser()

    with pytest.raises(
        LyricsNotFoundException,
        match="Genius page HTML is empty.",
    ):
        parser.parse("")


def test_parse_raises_when_lyrics_are_not_found():
    html = """
    <html>
        <body>
            <div>No lyrics here</div>
        </body>
    </html>
    """

    parser = GeniusLyricsParser()

    with pytest.raises(
        LyricsNotFoundException,
        match="Lyrics were not found on the Genius page.",
    ):
        parser.parse(html)


def test_parse_ignores_empty_lines():
    html = """
    <div data-lyrics-container="true">
        First line
        <br/>
        <br/>
        Second line
    </div>
    """

    parser = GeniusLyricsParser()

    result = parser.parse(html)

    assert result == "First line\nSecond line"


def test_parse_removes_genius_preamble_before_first_section_header():
    html = """
    <div data-lyrics-container="true">
        Español<br/>
        Português<br/>
        A description of the song that is not part of its lyrics.<br/>
        [Verse 1]<br/>
        First lyric line<br/>
        Second lyric line
    </div>
    """

    result = GeniusLyricsParser().parse(html)

    assert result == "First lyric line\nSecond lyric line"


def test_parse_preserves_valid_headerless_lyrics():
    html = """
    <div data-lyrics-container="true">
        First lyric line<br/>
        Second lyric line
    </div>
    """

    result = GeniusLyricsParser().parse(html)

    assert result == "First lyric line\nSecond lyric line"
