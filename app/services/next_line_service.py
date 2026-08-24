import logging

from app.core.exceptions import (
    ContinuationNotFoundException,
    LyricNotFoundException,
)
from app.services.lyric_line_classifier import LyricLineClassifier
from app.services.lyric_matcher import LyricMatcher
from app.services.lyric_normalizer import LyricNormalizer


logger = logging.getLogger(__name__)


class NextLineService:
    """
    Finds the next meaningful lyric line
    after the user's matched lyric.

    Vocal-only continuation handling will
    be improved separately.
    """

    def __init__(
        self,
        lyric_matcher: LyricMatcher | None = None,
        lyric_line_classifier: LyricLineClassifier | None = None,
    ) -> None:
        self._lyric_matcher = lyric_matcher or LyricMatcher()
        self._lyric_line_classifier = (
            lyric_line_classifier or LyricLineClassifier()
        )

    def find_next_line(
        self,
        lyrics: str | list[str],
        user_lyric: str,
        song_title: str | None = None,
    ) -> str:
        lyric_lines = self._prepare_lyric_lines(lyrics)

        if not user_lyric or not user_lyric.strip():
            raise LyricNotFoundException("Lyric input is empty.")

        if not lyric_lines:
            raise LyricNotFoundException("Song lyrics are empty.")

        if self._is_song_title(
            user_lyric=user_lyric,
            song_title=song_title,
        ):
            first_line = self._find_next_meaningful_line(
                lyric_lines=lyric_lines,
                start_index=0,
            )

            if first_line is None:
                raise LyricNotFoundException("Song lyrics are empty.")

            logger.info(
                "NEXT LINE | user input matched song title; "
                "returning first lyric line"
            )
            return first_line

        logger.debug(
            "NEXT LINE | matching user lyric against %d parsed lines",
            len(lyric_lines),
        )

        match_end = (
            self._lyric_matcher.find_match_end(
                lyrics=lyric_lines,
                user_lyric=user_lyric,
            )
        )

        if match_end is None:
            raise LyricNotFoundException(
                "Unable to find the provided lyric "
                "in the song."
            )

        user_lines = [
            line.strip()
            for line in user_lyric.splitlines()
            if line.strip()
        ]

        if len(user_lines) == 1:
            matched_line = lyric_lines[match_end]
            is_whole_line_match = (
                LyricNormalizer.normalize(matched_line)
                == LyricNormalizer.normalize(user_lines[0])
            )

            if not is_whole_line_match:
                remainder = (
                    self._lyric_matcher
                    .find_partial_remainder(
                        lyric_line=matched_line,
                        user_line=user_lines[0],
                    )
                )

                if remainder:
                    next_line = self._find_next_meaningful_line(
                        lyric_lines=lyric_lines,
                        start_index=match_end + 1,
                    )

                    logger.info(
                        "NEXT LINE | returning partial-line remainder "
                        "and next line"
                    )

                    if next_line is None:
                        return remainder

                    return f"{remainder}...\n\n{next_line}"

        line = self._find_next_meaningful_line(
            lyric_lines=lyric_lines,
            start_index=match_end + 1,
        )

        if line is not None:
            return line

        raise ContinuationNotFoundException(
            "There is no next line for the provided lyric."
        )

    def _find_next_meaningful_line(
        self,
        lyric_lines: list[str],
        start_index: int,
    ) -> str | None:
        for line in lyric_lines[start_index:]:
            if not self._lyric_line_classifier.is_vocal_only(line):
                return line

        return None

    @staticmethod
    def _is_song_title(
        user_lyric: str,
        song_title: str | None,
    ) -> bool:
        if not song_title or not song_title.strip():
            return False

        return (
            LyricNormalizer.aggressive(user_lyric)
            == LyricNormalizer.aggressive(song_title)
        )

    @staticmethod
    def _prepare_lyric_lines(
        lyrics: str | list[str],
    ) -> list[str]:
        """Convert parser output into clean lines for deterministic matching."""

        source_lines = lyrics.splitlines() if isinstance(lyrics, str) else lyrics

        return [
            line.strip()
            for line in source_lines
            if line and line.strip()
        ]
