import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class GeniusLyricsParser:

    LYRICS_CONTAINER_SELECTOR = 'div[data-lyrics-container="true"]'

    SECTION_HEADER_PATTERN = re.compile(
        r"^\s*\[[^\]]+\]\s*$"
    )

    NON_LYRIC_PATTERNS = (
        re.compile(r"^\d+\s+Contributors?$", re.IGNORECASE),
        re.compile(r"^Translations?$", re.IGNORECASE),
        re.compile(r"^Read More$", re.IGNORECASE),
        re.compile(r"^.+ Lyrics$", re.IGNORECASE),
    )

    def parse(self, html: str) -> str:
        logger.info("Parsing Genius lyrics page.")

        if not html or not html.strip():
            logger.error("Genius page HTML is empty.")
            raise ValueError("Genius page HTML is empty.")

        soup = BeautifulSoup(html, "html.parser")

        containers = soup.select(
            self.LYRICS_CONTAINER_SELECTOR
        )

        logger.debug(
            "Found %d lyrics containers.",
            len(containers),
        )

        if not containers:
            logger.warning(
                "No lyrics containers found on Genius page."
            )
            raise ValueError(
                "Lyrics were not found on the Genius page."
            )

        raw_lyrics = "\n".join(
            container.get_text("\n", strip=True)
            for container in containers
        )

        logger.debug(
            "RAW GENIUS LYRICS:\n%s",
            raw_lyrics,
        )

        lyrics = self._clean_lyrics(raw_lyrics)

        logger.debug(
            "CLEANED GENIUS LYRICS:\n%s",
            lyrics,
        )

        if not lyrics:
            logger.warning(
                "Lyrics became empty after cleaning."
            )
            raise ValueError(
                "Lyrics were not found on the Genius page."
            )

        logger.info(
            "Successfully parsed Genius lyrics (%d characters).",
            len(lyrics),
        )

        return lyrics

    @classmethod
    def _clean_lyrics(cls, lyrics: str) -> str:
        lines = []

        removed_empty_lines = 0
        removed_section_headers = 0
        removed_page_metadata = 0

        lyrics_started = False

        for line in lyrics.splitlines():
            line = line.strip()

            if not line:
                removed_empty_lines += 1
                continue

            if cls._is_section_header(line):
                lyrics_started = True
                removed_section_headers += 1
                continue

            if not lyrics_started:
                removed_page_metadata += 1
                continue

            if cls._is_page_metadata(line):
                removed_page_metadata += 1
                continue

            lines.append(line)

        logger.debug(
            "Lyrics cleaned: %d lines kept, "
            "%d empty lines removed, "
            "%d section headers removed, "
            "%d page metadata lines removed.",
            len(lines),
            removed_empty_lines,
            removed_section_headers,
            removed_page_metadata,
        )

        return "\n".join(lines)

    @classmethod
    def _is_section_header(cls, line: str) -> bool:
        return bool(
            cls.SECTION_HEADER_PATTERN.fullmatch(line)
        )

    @classmethod
    def _is_page_metadata(cls, line: str) -> bool:
        return any(
            pattern.fullmatch(line)
            for pattern in cls.NON_LYRIC_PATTERNS
        )