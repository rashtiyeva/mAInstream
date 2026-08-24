import logging
import re

from app.services.lyric_normalizer import LyricNormalizer


logger = logging.getLogger(__name__)


class LyricMatcher:
    """
    Finds the position of user-provided lyrics
    inside parsed song lyrics.

    Matching priority:

    1. Exact match.
    2. Normalized match.
    3. Normalized partial-line match at word boundaries.
    4. Aggressively normalized partial-line match at word boundaries.

    More tolerant matching strategies will be
    added later as fallbacks.

    The original lyrics are never modified.
    """

    def find_match(
        self,
        lyrics: list[str],
        user_lyric: str,
    ) -> int | None:
        logger.debug(
            "LYRIC MATCH | started | song_lines=%d | user_input=%r",
            len(lyrics),
            user_lyric,
        )

        if not lyrics or not user_lyric.strip():
            logger.info(
                "LYRIC MATCH | found=false | reason=empty_input_or_lyrics"
            )
            return None

        user_lines = self._prepare_original_user_lines(
            user_lyric
        )

        if not user_lines:
            logger.info(
                "LYRIC MATCH | found=false | reason=no_user_lines"
            )
            return None

        logger.debug("LYRIC MATCH | prepared_user_lines=%r", user_lines)
        normalized_user_lines = [
            LyricNormalizer.normalize_user_lyric(line)
            for line in user_lines
        ]

        match = self._find_exact_match(
            lyrics=lyrics,
            user_lines=user_lines,
        )

        if match is not None:
            logger.info(
                "LYRIC MATCH | found=true | strategy=exact | "
                "start_index=%d | matched_lines=%d",
                match,
                len(user_lines),
            )
            return match

        logger.debug("LYRIC MATCH | exact match not found")

        normalized_match = self._find_normalized_match(
            lyrics=lyrics,
            normalized_user_lines=normalized_user_lines,
        )

        if normalized_match is None:
            logger.debug("LYRIC MATCH | normalized whole-line match not found")
        else:
            logger.info(
                "LYRIC MATCH | found=true | strategy=normalized | "
                "start_index=%d | matched_lines=%d",
                normalized_match,
                len(user_lines),
            )
            return normalized_match

        partial_match = self._find_normalized_partial_match(
            lyrics=lyrics,
            normalized_user_lines=normalized_user_lines,
        )

        if partial_match is not None:
            logger.info(
                "LYRIC MATCH | found=true | strategy=normalized_partial | "
                "start_index=%d | matched_lines=%d",
                partial_match,
                len(user_lines),
            )
            return partial_match

        aggressive_partial_match = (
            self._find_aggressive_normalized_partial_match(
                lyrics=lyrics,
                user_lines=user_lines,
            )
        )

        if aggressive_partial_match is not None:
            logger.info(
                "LYRIC MATCH | found=true | "
                "strategy=aggressive_normalized_partial | "
                "start_index=%d | matched_lines=%d",
                aggressive_partial_match,
                len(user_lines),
            )
            return aggressive_partial_match

        logger.info(
            "LYRIC MATCH | found=false | "
            "strategies=exact,normalized,normalized_partial,"
            "aggressive_normalized_partial"
        )
        return None

    def find_match_end(
        self,
        lyrics: list[str],
        user_lyric: str,
    ) -> int | None:
        start_index = self.find_match(
            lyrics=lyrics,
            user_lyric=user_lyric,
        )

        if start_index is None:
            return None

        user_lines = self._prepare_original_user_lines(
            user_lyric
        )

        return start_index + len(user_lines) - 1

    # =========================================================
    # EXACT MATCH
    # =========================================================

    @staticmethod
    def _find_exact_match(
        lyrics: list[str],
        user_lines: list[str],
    ) -> int | None:
        if len(user_lines) == 1:
            user_line = user_lines[0]

            for index, lyric in enumerate(lyrics):
                if lyric.strip() == user_line:
                    return index

            return None

        for start in range(
            len(lyrics) - len(user_lines) + 1
        ):
            candidate = [
                line.strip()
                for line in lyrics[
                    start:start + len(user_lines)
                ]
            ]

            if candidate == user_lines:
                return start

        return None

    # =========================================================
    # NORMALIZED MATCH
    # =========================================================

    @staticmethod
    def _find_normalized_match(
        lyrics: list[str],
        normalized_user_lines: list[str],
    ) -> int | None:
        normalized_lyrics = (
            LyricNormalizer.normalize_lines(
                lyrics
            )
        )

        logger.debug(
            "LYRIC MATCH | normalized_user_lines=%r",
            normalized_user_lines,
        )

        if len(normalized_user_lines) == 1:
            user_line = normalized_user_lines[0]

            for index, lyric in enumerate(
                normalized_lyrics
            ):
                if lyric == user_line:
                    return index

            return None

        for start in range(
            len(normalized_lyrics)
            - len(normalized_user_lines)
            + 1
        ):
            candidate = normalized_lyrics[
                start:start + len(
                    normalized_user_lines
                )
            ]

            if candidate == normalized_user_lines:
                return start

        return None

    # =========================================================
    # NORMALIZED PARTIAL MATCH
    # =========================================================

    @staticmethod
    def _find_normalized_partial_match(
        lyrics: list[str],
        normalized_user_lines: list[str],
    ) -> int | None:
        """Find user fragments bounded by complete words in lyric lines."""

        normalized_lyrics = LyricNormalizer.normalize_lines(lyrics)

        if not normalized_user_lines:
            return None

        patterns = [
            LyricMatcher._compile_partial_pattern(user_line)
            for user_line in normalized_user_lines
            if user_line
        ]

        if len(patterns) != len(normalized_user_lines):
            return None

        for start in range(
            len(normalized_lyrics) - len(patterns) + 1
        ):
            candidate = normalized_lyrics[
                start:start + len(patterns)
            ]

            if all(
                pattern.search(line)
                for pattern, line in zip(patterns, candidate)
            ):
                return start

        return None

    @classmethod
    def find_normalized_partial_remainder(
        cls,
        lyric_line: str,
        user_line: str,
    ) -> str | None:
        """Return the untouched text following a boundary-safe partial match."""

        normalized_lyric = LyricNormalizer.normalize(lyric_line)
        normalized_user = LyricNormalizer.normalize(user_line)

        if not normalized_lyric or not normalized_user:
            return None

        match = cls._compile_partial_pattern(normalized_user).search(
            normalized_lyric
        )

        if match is None:
            return None

        original_end = cls._map_normalized_end_to_original(
            original=lyric_line,
            normalized_end=match.end(),
            aggressive=False,
        )

        # Separating punctuation belongs to the matched fragment, not to the
        # continuation. Punctuation inside the remaining lyric is preserved.
        return re.sub(
            r"^[\s,;:.!?…\-–—]+",
            "",
            lyric_line[original_end:],
        ).strip()

    @classmethod
    def find_partial_remainder(
        cls,
        lyric_line: str,
        user_line: str,
    ) -> str | None:
        """Return a remainder for normal or aggressive partial matching."""

        normal_remainder = cls.find_normalized_partial_remainder(
            lyric_line=lyric_line,
            user_line=user_line,
        )

        if normal_remainder is not None:
            return normal_remainder

        aggressive_lyric = LyricNormalizer.aggressive(lyric_line)
        aggressive_user = LyricNormalizer.aggressive(user_line)

        if not aggressive_lyric or not aggressive_user:
            return None

        match = cls._compile_partial_pattern(aggressive_user).search(
            aggressive_lyric
        )

        if match is None:
            return None

        original_end = cls._map_normalized_end_to_original(
            original=lyric_line,
            normalized_end=match.end(),
            aggressive=True,
        )

        return re.sub(
            r"^[\s,;:.!?…\-–—]+",
            "",
            lyric_line[original_end:],
        ).strip()

    @staticmethod
    def _compile_partial_pattern(normalized_user_line: str) -> re.Pattern[str]:
        return re.compile(
            rf"(?<!\w){re.escape(normalized_user_line)}(?!\w)"
        )

    @staticmethod
    def _map_normalized_end_to_original(
        original: str,
        normalized_end: int,
        aggressive: bool,
    ) -> int:
        """Map a normalized end offset back to the original lyric line."""

        for original_end in range(1, len(original) + 1):
            normalizer = (
                LyricNormalizer.aggressive
                if aggressive
                else LyricNormalizer.normalize
            )
            normalized_prefix = normalizer(original[:original_end])

            if len(normalized_prefix) >= normalized_end:
                return original_end

        return len(original)

    @staticmethod
    def _find_aggressive_normalized_partial_match(
        lyrics: list[str],
        user_lines: list[str],
    ) -> int | None:
        aggressive_lyrics = LyricNormalizer.aggressive_lines(lyrics)
        aggressive_user_lines = LyricNormalizer.aggressive_lines(user_lines)

        if not aggressive_user_lines or any(
            not line for line in aggressive_user_lines
        ):
            return None

        patterns = [
            LyricMatcher._compile_partial_pattern(line)
            for line in aggressive_user_lines
        ]

        for start in range(
            len(aggressive_lyrics) - len(patterns) + 1
        ):
            candidate = aggressive_lyrics[
                start:start + len(patterns)
            ]

            if all(
                pattern.search(line)
                for pattern, line in zip(patterns, candidate)
            ):
                return start

        return None

    # =========================================================
    # PREPARATION
    # =========================================================

    @staticmethod
    def _prepare_original_user_lines(
        user_lyric: str,
    ) -> list[str]:
        return [
            line.strip()
            for line in user_lyric.splitlines()
            if line.strip()
        ]
