from app.services.lyric_matcher import LyricMatcher


def test_exact_single_line_match():
    matcher = LyricMatcher()

    lyrics = [
        "I can almost see it",
        "That dream I'm dreaming",
        "There's a voice inside my head saying",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="That dream I'm dreaming",
    )

    assert result == 1


def test_normalized_case_insensitive_match():
    matcher = LyricMatcher()

    lyrics = [
        "I can almost see it",
        "It's the climb",
        "Keep on moving",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="IT'S THE CLIMB",
    )

    assert result == 1


def test_normalized_apostrophe_match():
    matcher = LyricMatcher()

    lyrics = [
        "I can almost see it",
        "It's the climb",
        "Keep on moving",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="It’s the climb",
    )

    assert result == 1


def test_normalized_whitespace_match():
    matcher = LyricMatcher()

    lyrics = [
        "I can almost see it",
        "It's the climb",
        "Keep on moving",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="  it's    the   climb  ",
    )

    assert result == 1


def test_aggressive_match_ignores_missing_apostrophe():
    matcher = LyricMatcher()

    lyrics = [
        "It's the climb",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="its the climb",
    )

    assert result == 0


def test_does_not_join_split_contraction_yet():
    matcher = LyricMatcher()

    lyrics = [
        "It's the climb",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="it s the climb",
    )

    assert result is None


def test_multi_line_exact_match():
    matcher = LyricMatcher()

    lyrics = [
        "I can almost see it",
        "That dream I'm dreaming",
        "But there's a voice inside my head",
        "You'll never reach it",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric=(
            "That dream I'm dreaming\n"
            "But there's a voice inside my head"
        ),
    )

    assert result == 1


def test_multi_line_normalized_match():
    matcher = LyricMatcher()

    lyrics = [
        "I can almost see it",
        "That dream I'm dreaming",
        "But there's a voice inside my head",
        "You'll never reach it",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric=(
            "THAT DREAM I'M DREAMING\n"
            "BUT THERE'S A VOICE INSIDE MY HEAD"
        ),
    )

    assert result == 1


def test_match_end_single_line():
    matcher = LyricMatcher()

    lyrics = [
        "First",
        "Second",
        "Third",
    ]

    result = matcher.find_match_end(
        lyrics=lyrics,
        user_lyric="Second",
    )

    assert result == 1


def test_match_end_multi_line():
    matcher = LyricMatcher()

    lyrics = [
        "First",
        "Second",
        "Third",
        "Fourth",
    ]

    result = matcher.find_match_end(
        lyrics=lyrics,
        user_lyric="Second\nThird",
    )

    assert result == 2


def test_no_match():
    matcher = LyricMatcher()

    lyrics = [
        "First",
        "Second",
        "Third",
    ]

    result = matcher.find_match(
        lyrics=lyrics,
        user_lyric="Something else",
    )

    assert result is None


def test_empty_lyrics():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=[],
        user_lyric="Something",
    )

    assert result is None


def test_empty_user_input():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["Something"],
        user_lyric="   ",
    )

    assert result is None


def test_normalized_partial_match_at_start_of_line():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["'Cause the players gonna play, play, play, play, play"],
        user_lyric="'cause the players gonna play",
    )

    assert result == 0


def test_normalized_partial_match_in_middle_of_line():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["Before the players gonna play after"],
        user_lyric="THE PLAYERS GONNA PLAY",
    )

    assert result == 0


def test_normalized_partial_match_at_end_of_line():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["It starts before the players gonna play"],
        user_lyric="the   players gonna play",
    )

    assert result == 0


def test_partial_match_does_not_match_inside_word():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["The players gonna play"],
        user_lyric="he",
    )

    assert result is None


def test_aggressive_normalized_partial_match_removes_punctuation():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["I remember it all too well"],
        user_lyric="'I remember it all too",
    )

    assert result == 0


def test_aggressive_partial_match_does_not_match_inside_word():
    matcher = LyricMatcher()

    result = matcher.find_match(
        lyrics=["The players gonna play"],
        user_lyric="'he'",
    )

    assert result is None
