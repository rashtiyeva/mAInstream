
import re


class LyricLineClassifier:
    """
    Classifies complete lyric lines.

    A line is considered vocal-only only when every meaningful token
    in the entire line belongs to the configured vocal vocabulary.

    Examples:
        "Yeah" -> True
        "Oh-ooh" -> True
        "Whoa!" -> True
        "I remember you said yeah" -> False
    """

    _VOCAL_WORDS = {
        "ah",
        "aha",
        "ahh",
        "ahhh",
        "ha",
        "hmm",
        "hm",
        "mmm",
        "mm",
        "oh",
        "ooh",
        "oohh",
        "oooh",
        "uh",
        "uhh",
        "woo",
        "woah",
        "whoa",
        "yeah",
        "yea",
        "yep",
    }

    _SEPARATOR_PATTERN = re.compile(
        r"[\s\-–—,'’.!?…]+"
    )

    def is_vocal_only(
        self,
        line: str,
    ) -> bool:

        normalized = self._normalize(line)

        if not normalized:
            return False

        words = self._SEPARATOR_PATTERN.split(
            normalized
        )

        words = [
            word
            for word in words
            if word
        ]

        return bool(words) and all(
            word in self._VOCAL_WORDS
            for word in words
        )

    @staticmethod
    def _normalize(
        line: str,
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            line.strip().lower(),
        )
