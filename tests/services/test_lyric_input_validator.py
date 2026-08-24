import pytest
from app.services.lyric_input_validator import LyricInputValidator


@pytest.mark.parametrize(
    ("lyric", "expected_count"),
    [
        ("hello", 1),
        ("shake it", 2),
        ("hello!!!", 1),
        ("'shake   it?'", 2),
        ("making the bed", 3),
        ("  making   the\tbed  ", 3),
        ("Привет, мой мир!", 3),
    ],
)
def test_count_meaningful_words(lyric: str, expected_count: int) -> None:
    assert LyricInputValidator.count_meaningful_words(lyric) == expected_count


@pytest.mark.parametrize("lyric", ["hello", "shake it", "hello!!!", "'shake it?'"])
def test_classifies_fewer_than_three_words_as_too_generic(lyric: str) -> None:
    assert LyricInputValidator().is_too_generic(lyric) is True


@pytest.mark.parametrize("lyric", ["making the bed", "i stay out too late"])
def test_three_or_more_words_are_not_too_generic(lyric: str) -> None:
    assert LyricInputValidator().is_too_generic(lyric) is False
