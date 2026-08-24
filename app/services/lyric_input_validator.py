from app.core.constants import MIN_LYRIC_WORDS
from app.services.lyric_normalizer import LyricNormalizer


class LyricInputValidator:
    """Classify whether lyric input lacks enough identification context."""

    def __init__(self, min_words: int = MIN_LYRIC_WORDS) -> None:
        if min_words < 1:
            raise ValueError("min_words must be at least 1.")

        self._min_words = min_words

    def is_too_generic(self, lyric: str) -> bool:
        return self.count_meaningful_words(lyric) < self._min_words

    @staticmethod
    def count_meaningful_words(lyric: str) -> int:
        normalized = LyricNormalizer.aggressive(lyric)
        return len(normalized.split()) if normalized else 0
