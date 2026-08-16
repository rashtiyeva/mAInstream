from app.core.exceptions import LyricNotFoundException


class NextLineService:
    """
    Finds the continuation of a user's lyric input
    within the full song lyrics.
    """

    def find_next_line(
        self,
        lyrics: str,
        user_lyric: str,
    ) -> str:
        if not lyrics or not lyrics.strip():
            raise LyricNotFoundException(
                "Song lyrics are empty."
            )

        if not user_lyric or not user_lyric.strip():
            raise LyricNotFoundException(
                "Lyric input is empty."
            )

        lines = self._split_lines(lyrics)
        user_input = self._normalize_for_matching(user_lyric)

        for index, line in enumerate(lines):
            normalized_line = self._normalize_for_matching(line)

            if user_input == normalized_line:
                return self._get_next_line(lines, index)

            if normalized_line.startswith(user_input + " "):
                remainder = line[len(user_lyric.strip()):].strip()

                return self._build_partial_continuation(
                    remainder=remainder,
                    next_line=self._get_next_line(lines, index),
                )

        raise LyricNotFoundException(
            "Unable to find the provided lyric in the song."
        )

    @staticmethod
    def _split_lines(lyrics: str) -> list[str]:
        return [
            line.strip()
            for line in lyrics.splitlines()
            if line.strip()
        ]

    @staticmethod
    def _normalize_for_matching(value: str) -> str:
        return " ".join(value.lower().split())

    @staticmethod
    def _get_next_line(
        lines: list[str],
        index: int,
    ) -> str:
        next_index = index + 1

        if next_index >= len(lines):
            raise LyricNotFoundException(
                "There is no next line for the provided lyric."
            )

        return lines[next_index]

    @staticmethod
    def _build_partial_continuation(
        remainder: str,
        next_line: str,
    ) -> str:
        if not remainder:
            return next_line

        return f"...{remainder}\n\n{next_line}"