import re

from bs4 import BeautifulSoup


class GeniusLyricsParser:
    """
    Parses lyrics from a Genius song page and returns clean lyrics.
    """

    LYRICS_CONTAINER_SELECTOR = 'div[data-lyrics-container="true"]'

    SECTION_HEADER_PATTERN = re.compile(
        r"^\s*\[[^\]]+\]\s*$"
    )

    def parse(self, html: str) -> str:
        if not html or not html.strip():
            raise ValueError("Genius page HTML is empty.")

        soup = BeautifulSoup(html, "html.parser")

        containers = soup.select(self.LYRICS_CONTAINER_SELECTOR)

        if not containers:
            raise ValueError(
                "Lyrics were not found on the Genius page."
            )

        lyrics = "\n".join(
            container.get_text("\n", strip=True)
            for container in containers
        )

        lyrics = self._clean_lyrics(lyrics)

        if not lyrics:
            raise ValueError(
                "Lyrics were not found on the Genius page."
            )

        return lyrics

    @classmethod
    def _clean_lyrics(cls, lyrics: str) -> str:
        lines = []

        for line in lyrics.splitlines():
            line = line.strip()

            if not line:
                continue

            if cls._is_section_header(line):
                continue

            # Keep the actual lyric text intact.
            lines.append(line)

        return "\n".join(lines)

    @classmethod
    def _is_section_header(cls, line: str) -> bool:
        return bool(cls.SECTION_HEADER_PATTERN.fullmatch(line))