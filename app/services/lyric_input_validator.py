import logging

from app.core.constants import MIN_LYRIC_WORDS
from app.services.lyric_normalizer import LyricNormalizer

logger = logging.getLogger(__name__)


class LyricInputValidator:
    """Classify whether lyric input lacks enough identification context."""

    def __init__(self, min_words: int = MIN_LYRIC_WORDS) -> None:
        if min_words < 1:
            raise ValueError("min_words must be at least 1.")

        self._min_words = min_words

    def is_too_generic(self, lyric: str) -> bool:
        word_count = self.count_meaningful_words(lyric)
        is_too_generic = word_count < self._min_words
        logger.debug(
            "INPUT VALIDATION | meaningful_words=%d | minimum=%d | "
            "too_generic=%s",
            word_count,
            self._min_words,
            is_too_generic,
        )
        return is_too_generic

    @staticmethod
    def count_meaningful_words(lyric: str) -> int:
        normalized = LyricNormalizer.aggressive(lyric)
        return len(normalized.split()) if normalized else 0
