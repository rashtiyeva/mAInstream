from app.services.lyric_normalizer import LyricNormalizer


def test_normalize_lowercases_text():
    result = LyricNormalizer.normalize(
        "IT'S THE CLIMB"
    )

    assert result == "it's the climb"


def test_normalize_collapses_whitespace():
    result = LyricNormalizer.normalize(
        "  It's    the   climb  "
    )

    assert result == "it's the climb"


def test_normalize_apostrophe():
    result = LyricNormalizer.normalize(
        "It’s the climb"
    )

    assert result == "it's the climb"


def test_normalize_preserves_punctuation():
    result = LyricNormalizer.normalize(
        "It's the climb!"
    )

    assert result == "it's the climb!"


def test_normalize_empty_string():
    result = LyricNormalizer.normalize("")

    assert result == ""


def test_aggressive_normalization_removes_apostrophes_inside_words():
    assert LyricNormalizer.aggressive("It's the climb") == "its the climb"
    assert LyricNormalizer.aggressive("I’m still standing") == "im still standing"


def test_aggressive_normalization_removes_surrounding_punctuation():
    assert (
        LyricNormalizer.aggressive("'I remember it all too")
        == "i remember it all too"
    )
    assert LyricNormalizer.aggressive("Hello, baby!") == "hello baby"


def test_aggressive_normalization_preserves_unicode_letters_and_numbers():
    assert (
        LyricNormalizer.aggressive("  Привет, 世界! 123  ")
        == "привет 世界 123"
    )
