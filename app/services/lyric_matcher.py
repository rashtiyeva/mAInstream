
import re


class LyricMatcher:
    """
    Finds the position of user-provided lyrics inside song lyrics.

    Matching priority:

    1. Exact match.
    2. Normalized match.
    3. Punctuation-agnostic match.

    AI matching is intentionally not handled here.
    It will be added later as a fallback.

    The original lyrics are never modified.
    """

    def find_match(
        self,
        lyrics: list[str],
        user_lyric: str,
    ) -> int | None:
        if not lyrics or not user_lyric.strip():
            return None

        user_lines = self._prepare_user_lines(user_lyric)

        if not user_lines:
            return None

        # ---------------------------------------------------------
        # 1. Exact match
        # ---------------------------------------------------------

        match = self._find_exact_match(
            lyrics=lyrics,
            user_lyric=user_lyric,
        )

        if match is not None:
            return match

        # ---------------------------------------------------------
        # 2. Normalized match
        # ---------------------------------------------------------

        match = self._find_normalized_match(
            lyrics=lyrics,
            user_lines=user_lines,
        )

        if match is not None:
            return match

        # ---------------------------------------------------------
        # 3. Punctuation-agnostic match
        # ---------------------------------------------------------

        return self._find_punctuation_agnostic_match(
            lyrics=lyrics,
            user_lyric=user_lyric,
        )

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

        user_lines = self._prepare_user_lines(
            user_lyric
        )

        return start_index + len(user_lines) - 1

    # =============================================================
    # EXACT MATCHING
    # =============================================================

    def _find_exact_match(
        self,
        lyrics: list[str],
        user_lyric: str,
    ) -> int | None:
        user_lines = [
            line.strip()
            for line in user_lyric.splitlines()
            if line.strip()
        ]

        if not user_lines:
            return None

        # Single-line input.
        if len(user_lines) == 1:
            user_line = user_lines[0]

            for index, lyric in enumerate(lyrics):
                if lyric.strip() == user_line:
                    return index

            return None

        # Multi-line input.
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

    # =============================================================
    # NORMALIZED MATCHING
    # =============================================================

    def _find_normalized_match(
        self,
        lyrics: list[str],
        user_lines: list[str],
    ) -> int | None:
        normalized_lyrics = [
            self._normalize(line)
            for line in lyrics
        ]

        # Single-line input.
        if len(user_lines) == 1:
            user_line = user_lines[0]

            for index, lyric in enumerate(
                normalized_lyrics
            ):
                if lyric == user_line:
                    return index

            return None

        # Multi-line input.
        for start in range(
            len(normalized_lyrics) - len(user_lines) + 1
        ):
            candidate = normalized_lyrics[
                start:start + len(user_lines)
            ]

            if candidate == user_lines:
                return start

        return None

    # =============================================================
    # PUNCTUATION-AGNOSTIC MATCHING
    # =============================================================

    def _find_punctuation_agnostic_match(
        self,
        lyrics: list[str],
        user_lyric: str,
    ) -> int | None:
        user_lines = [
            line
            for line in user_lyric.splitlines()
            if line.strip()
        ]

        if not user_lines:
            return None

        # ---------------------------------------------------------
        # Single-line input
        # ---------------------------------------------------------

        if len(user_lines) == 1:
            user_variants = self._punctuation_agnostic_variants(
                user_lines[0]
            )

            for index, lyric in enumerate(lyrics):
                lyric_variants = (
                    self._punctuation_agnostic_variants(lyric)
                )

                if user_variants.intersection(
                    lyric_variants
                ):
                    return index

            return None

        # ---------------------------------------------------------
        # Multi-line input
        # ---------------------------------------------------------

        user_variants_per_line = [
            self._punctuation_agnostic_variants(line)
            for line in user_lines
        ]

        for start in range(
            len(lyrics) - len(user_lines) + 1
        ):
            candidate_lyrics = lyrics[
                start:start + len(user_lines)
            ]

            if self._multi_line_variants_match(
                candidate_lyrics,
                user_variants_per_line,
            ):
                return start

        return None

    def _multi_line_variants_match(
        self,
        lyrics: list[str],
        user_variants_per_line: list[set[str]],
    ) -> bool:
        for lyric, user_variants in zip(
            lyrics,
            user_variants_per_line,
        ):
            lyric_variants = (
                self._punctuation_agnostic_variants(lyric)
            )

            if not user_variants.intersection(
                lyric_variants
            ):
                return False

        return True

    # =============================================================
    # PUNCTUATION-AGNOSTIC VARIANTS
    # =============================================================

    @classmethod
    def _punctuation_agnostic_variants(
        cls,
        text: str,
    ) -> set[str]:
        """
        Returns punctuation-agnostic representations.

        Apostrophes are treated specially.

        Examples:

            "It's the climb"
                ->
            {
                "its the climb",
                "it s the climb",
            }

            "Its the climb"
                ->
            {
                "its the climb",
            }

            "It s the climb"
                ->
            {
                "it s the climb",
            }

        Other punctuation is converted to whitespace.
        """

        text = cls._normalize(text)

        if not text:
            return set()

        # Variant 1:
        # Remove apostrophes completely.
        #
        # "it's" -> "its"
        without_apostrophe = text.replace("'", "")

        without_apostrophe = re.sub(
            r"[^\w\s]",
            " ",
            without_apostrophe,
        )

        without_apostrophe = re.sub(
            r"\s+",
            " ",
            without_apostrophe,
        ).strip()

        variants = {
            without_apostrophe,
        }

        # Variant 2:
        # Treat apostrophe as a word separator.
        #
        # "it's" -> "it s"
        #
        # We do this separately because the user may type
        # "it s" instead of "it's".
        with_apostrophe_as_separator = re.sub(
            r"'",
            " ",
            text,
        )

        with_apostrophe_as_separator = re.sub(
            r"[^\w\s]",
            " ",
            with_apostrophe_as_separator,
        )

        with_apostrophe_as_separator = re.sub(
            r"\s+",
            " ",
            with_apostrophe_as_separator,
        ).strip()

        if with_apostrophe_as_separator:
            variants.add(
                with_apostrophe_as_separator
            )

        return variants

    # =============================================================
    # PREPARATION
    # =============================================================

    @staticmethod
    def _prepare_user_lines(
        user_lyric: str,
    ) -> list[str]:
        return [
            LyricMatcher._normalize(line)
            for line in user_lyric.splitlines()
            if line.strip()
        ]

    # =============================================================
    # NORMALIZATION
    # =============================================================

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        """
        Performs normalization without removing punctuation.

        Examples:

            "IT'S   THE   CLIMB"
                ->
            "it's the climb"

            "It's THE climb!"
                ->
            "it's the climb!"
        """

        text = text.lower().strip()

        text = LyricMatcher._normalize_apostrophes(
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def _normalize_apostrophes(
        text: str,
    ) -> str:
        """
        Converts different apostrophe characters
        into the standard ASCII apostrophe.
        """

        return (
            text
            .replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
        )
