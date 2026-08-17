
import re
import unicodedata


class LyricNormalizer:
    """
    Creates comparable representations of lyrics.

    The original lyric text is never modified.

    Normalization is intentionally divided into two levels:

    1. standard normalization
       - lowercase
       - Unicode normalization
       - apostrophe normalization
       - whitespace normalization

    2. aggressive normalization
       - standard normalization
       - remove punctuation
       - remove apostrophes
       - collapse whitespace
    """

    _APOSTROPHES = {
        "’": "'",
        "‘": "'",
        "`": "'",
        "´": "'",
        "ʼ": "'",
        "ʹ": "'",
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Standard normalization.

        Example:

            "  IT’S   The   Climb!  "
                ->
            "it's the climb!"
        """

        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)

        text = cls._normalize_apostrophes(text)

        text = text.lower().strip()

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def aggressive(cls, text: str) -> str:
        """
        Aggressive normalization for fuzzy textual comparison.

        Example:

            "It's THE climb!"
                ->
            "its the climb"

            "Its   the-climb"
                ->
            "its the climb"
        """

        text = cls.normalize(text)

        if not text:
            return ""

        # Remove apostrophes completely.
        #
        # "it's" -> "its"
        text = text.replace("'", "")

        # Convert every remaining non-word character
        # into whitespace.
        text = re.sub(
            r"[^\w\s]",
            " ",
            text,
        )

        # Collapse whitespace again after punctuation removal.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @classmethod
    def normalize_lines(
        cls,
        lyrics: list[str],
    ) -> list[str]:
        """
        Standard-normalizes a list of lyric lines.
        """

        return [
            cls.normalize(line)
            for line in lyrics
        ]

    @classmethod
    def aggressive_lines(
        cls,
        lyrics: list[str],
    ) -> list[str]:
        """
        Aggressively normalizes a list of lyric lines.
        """

        return [
            cls.aggressive(line)
            for line in lyrics
        ]

    @classmethod
    def _normalize_apostrophes(
        cls,
        text: str,
    ) -> str:
        for source, replacement in cls._APOSTROPHES.items():
            text = text.replace(source, replacement)

        return text
