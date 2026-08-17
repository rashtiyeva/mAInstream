
from app.core.exceptions import LyricNotFoundException
from app.services.lyric_line_classifier import LyricLineClassifier
from app.services.lyric_matcher import LyricMatcher


class NextLineService:
    """
    Finds the next meaningful lyric line after
    the user's lyric.
    """

    def __init__(
        self,
        lyric_matcher: LyricMatcher,
        lyric_line_classifier: LyricLineClassifier,
    ):
        self._lyric_matcher = lyric_matcher
        self._lyric_line_classifier = lyric_line_classifier

    def find_next_line(
        self,
        lyrics: list[str],
        user_lyric: str,
    ) -> str:

        match_end = self._lyric_matcher.find_match_end(
            lyrics=lyrics,
            user_lyric=user_lyric,
        )

        if match_end is None:
            raise LyricNotFoundException(
                "Unable to find the provided lyric "
                "in the song."
            )

        for index in range(
            match_end + 1,
            len(lyrics),
        ):
            line = lyrics[index].strip()

            if not line:
                continue

            if self._lyric_line_classifier.is_vocal_only(
                line
            ):
                continue

            # IMPORTANT:
            # Return the ORIGINAL Genius line.
            #
            # Do not return a normalized version.
            return line

        raise LyricNotFoundException(
            "No continuation found after the "
            "provided lyric."
        )