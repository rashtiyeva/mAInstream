import logging
import re
import unicodedata


logger = logging.getLogger(__name__)


class LyricNormalizer:
    """
    Creates a normalized representation of lyric text
    for deterministic comparison.

    The original lyric text is never modified.

    Normalization:
    - Unicode normalization
    - apostrophe normalization
    - lowercase
    - leading/trailing whitespace removal
    - repeated whitespace collapse

    Punctuation is intentionally preserved.
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
        if not text:
            return ""

        text = unicodedata.normalize(
            "NFKC",
            text,
        )

        text = cls._normalize_apostrophes(
            text
        )

        text = text.lower().strip()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    @classmethod
    def normalize_lines(
        cls,
        lines: list[str],
    ) -> list[str]:
        return [
            cls.normalize(line)
            for line in lines
        ]

    @staticmethod
    def aggressive(text: str) -> str:
        """Normalize text for punctuation-insensitive comparison.

        Punctuation is deleted rather than replaced, so punctuation inside a
        word does not split that word. Unicode letters, combining marks,
        numbers, and whitespace are retained.
        """

        if not text:
            return ""

        normalized = unicodedata.normalize("NFKC", text).lower()
        characters: list[str] = []

        for character in normalized:
            category = unicodedata.category(character)

            if category[0] in {"L", "M", "N"}:
                characters.append(character)
            elif character.isspace():
                characters.append(" ")

        return re.sub(r"\s+", " ", "".join(characters)).strip()

    @classmethod
    def aggressive_lines(
        cls,
        lines: list[str],
    ) -> list[str]:
        return [
            cls.aggressive(line)
            for line in lines
        ]

    @classmethod
    def _normalize_apostrophes(
        cls,
        text: str,
    ) -> str:
        for source, replacement in cls._APOSTROPHES.items():
            text = text.replace(
                source,
                replacement,
            )

        return text

    @classmethod
    def normalize_user_lyric(cls, text: str) -> str:
        """Normalize user input while logging every transformation step."""

        logger.debug("USER LYRIC NORMALIZATION | input=%r", text)

        if not text:
            logger.debug(
                "USER LYRIC NORMALIZATION | result='' (input is empty)"
            )
            return ""

        unicode_normalized = unicodedata.normalize("NFKC", text)
        logger.debug(
            "USER LYRIC NORMALIZATION | after_unicode_nfkc=%r | changed=%s",
            unicode_normalized,
            unicode_normalized != text,
        )

        apostrophes_normalized = cls._normalize_apostrophes(
            unicode_normalized
        )
        logger.debug(
            "USER LYRIC NORMALIZATION | after_apostrophes=%r | changed=%s",
            apostrophes_normalized,
            apostrophes_normalized != unicode_normalized,
        )

        lowercased = apostrophes_normalized.lower()
        logger.debug(
            "USER LYRIC NORMALIZATION | after_lowercase=%r | changed=%s",
            lowercased,
            lowercased != apostrophes_normalized,
        )

        stripped = lowercased.strip()
        logger.debug(
            "USER LYRIC NORMALIZATION | after_strip=%r | changed=%s",
            stripped,
            stripped != lowercased,
        )

        whitespace_collapsed = re.sub(r"\s+", " ", stripped)
        logger.debug(
            "USER LYRIC NORMALIZATION | after_whitespace_collapse=%r "
            "| changed=%s",
            whitespace_collapsed,
            whitespace_collapsed != stripped,
        )
        logger.debug(
            "USER LYRIC NORMALIZATION | result=%r",
            whitespace_collapsed,
        )

        return whitespace_collapsed
