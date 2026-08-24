import logging
import re
from collections.abc import Iterable

from bs4 import BeautifulSoup
from bs4.element import Tag

from app.core.exceptions import LyricsNotFoundException

logger = logging.getLogger(__name__)


class GeniusLyricsParser:

    LYRICS_CONTAINER_SELECTOR = 'div[data-lyrics-container="true"]'

    # Removes genuine structural headings while preserving possible lyrics or
    # stage directions such as "[Phone rings]" and "[Laughing]".
    SECTION_HEADER_PATTERN = re.compile(
        r"""
        ^\s*
        \[
        (?:
            intro
            | verse(?:\s+\d+)?
            | pre[-\s]?chorus(?:\s+\d+)?
            | chorus(?:\s+\d+)?
            | post[-\s]?chorus(?:\s+\d+)?
            | refrain(?:\s+\d+)?
            | hook(?:\s+\d+)?
            | bridge(?:\s+\d+)?
            | interlude(?:\s+\d+)?
            | outro
            | breakdown
            | instrumental(?:\s+break)?
            | solo
            | spoken(?:\s+word)?
            | sample
            | skit
        )
        (?:\s*:\s*[^\]]+)?
        \]\s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    NON_LYRIC_PATTERNS = (
        re.compile(r"^\d+\s+Contributors?$", re.IGNORECASE),
        re.compile(r"^Translations?$", re.IGNORECASE),
        re.compile(r"^Read More$", re.IGNORECASE),
        re.compile(r"^Embed$", re.IGNORECASE),
        re.compile(r"^Share URL$", re.IGNORECASE),
        re.compile(r"^Copy$", re.IGNORECASE),
        re.compile(r"^.+\s+Lyrics$", re.IGNORECASE),
    )

    # Genius sometimes attaches an Embed count to the final lyric line.
    TRAILING_EMBED_PATTERN = re.compile(
        r"\s*\d*Embed\s*$",
        re.IGNORECASE,
    )

    WHITESPACE_PATTERN = re.compile(r"[^\S\r\n]+")

    def parse(self, html: str) -> str:
        """Return newline-separated lyrics extracted from Genius HTML."""

        logger.info("Parsing Genius lyrics page.")

        if not html or not html.strip():
            raise LyricsNotFoundException("Genius page HTML is empty.")

        soup = BeautifulSoup(html, "html.parser")
        containers = soup.select(self.LYRICS_CONTAINER_SELECTOR)

        logger.debug("Found %d lyrics containers.", len(containers))

        if not containers:
            raise LyricsNotFoundException(
                "Lyrics were not found on the Genius page."
            )

        raw_lines = self._extract_lines(containers)
        raw_lines = self._remove_pre_lyrics_preamble(raw_lines)
        lyrics = self._clean_lines(raw_lines)

        if not lyrics:
            raise LyricsNotFoundException(
                "Lyrics were not found on the Genius page."
            )

        result = "\n".join(lyrics)

        logger.info(
            "Successfully parsed Genius lyrics (%d lines, %d characters).",
            len(lyrics),
            len(result),
        )
        logger.debug(
            "FULL CLEAN GENIUS LYRICS (%d lines):\n%s",
            len(lyrics),
            result,
        )

        return result

    @classmethod
    def _extract_lines(
        cls,
        containers: Iterable[Tag],
    ) -> list[str]:
        """Extract lines while respecting Genius <br> elements."""

        lines: list[str] = []

        for container in containers:
            text = container.get_text(
                separator="\n",
                strip=True,
            )
            lines.extend(text.splitlines())

        return lines

    @classmethod
    def _remove_pre_lyrics_preamble(
        cls,
        raw_lines: list[str],
    ) -> list[str]:
        """Discard Genius metadata before the first structural heading.

        Some Genius pages put translations and the song description inside
        the first lyrics container. When a recognized section heading exists,
        it is the most reliable boundary between that preamble and the lyrics.
        Headerless pages are returned unchanged.
        """

        for index, raw_line in enumerate(raw_lines):
            line = cls._normalize_line(raw_line)

            if cls._is_section_header(line):
                logger.debug(
                    "Removed %d pre-lyrics lines before first section header.",
                    index,
                )
                return raw_lines[index:]

        logger.debug(
            "No section header found; preserving headerless lyrics content."
        )
        return raw_lines

    @classmethod
    def _clean_lines(
        cls,
        raw_lines: Iterable[str],
    ) -> list[str]:
        cleaned_lines: list[str] = []

        for raw_line in raw_lines:
            line = cls._normalize_line(raw_line)

            if not line:
                continue

            if cls._is_section_header(line):
                continue

            if cls._is_page_metadata(line):
                continue

            line = cls.TRAILING_EMBED_PATTERN.sub("", line).strip()

            if not line:
                continue

            cleaned_lines.append(line)

        return cleaned_lines

    @classmethod
    def _normalize_line(cls, line: str) -> str:
        """Normalize HTML whitespace without altering lyric punctuation."""

        # Convert non-breaking spaces produced by HTML into ordinary spaces.
        line = line.replace("\xa0", " ")

        # Remove zero-width characters occasionally present in copied content.
        line = (
            line.replace("\u200b", "")
            .replace("\u200c", "")
            .replace("\u200d", "")
            .replace("\ufeff", "")
        )

        return cls.WHITESPACE_PATTERN.sub(" ", line).strip()

    @classmethod
    def _is_section_header(cls, line: str) -> bool:
        return bool(cls.SECTION_HEADER_PATTERN.fullmatch(line))

    @classmethod
    def _is_page_metadata(cls, line: str) -> bool:
        return any(
            pattern.fullmatch(line)
            for pattern in cls.NON_LYRIC_PATTERNS
        )
