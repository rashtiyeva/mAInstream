from typing import Annotated

from fastapi import Depends

from app.clients.genius_client import GeniusClient
from app.clients.openai_client import OpenAIClient
from app.dependencies.clients import (
    get_genius_client,
    get_openai_client,
)
from app.parsers.genius_lyrics_parser import GeniusLyricsParser
from app.providers.genius_provider import GeniusProvider
from app.services.lyrics_orchestrator import LyricsOrchestrator
from app.services.lyrics_provider_service import LyricsProviderService
from app.services.next_line_service import NextLineService
from app.services.song_identifier_service import SongIdentifierService


def get_song_identifier_service(
    client: Annotated[
        OpenAIClient,
        Depends(get_openai_client),
    ],
) -> SongIdentifierService:
    return SongIdentifierService(client)


def get_genius_provider(
    client: Annotated[
        GeniusClient,
        Depends(get_genius_client),
    ],
) -> GeniusProvider:
    return GeniusProvider(client)


def get_lyrics_provider_service(
    genius_provider: Annotated[
        GeniusProvider,
        Depends(get_genius_provider),
    ],
) -> LyricsProviderService:
    return LyricsProviderService(genius_provider)


def get_lyrics_parser() -> GeniusLyricsParser:
    return GeniusLyricsParser()


def get_next_line_service() -> NextLineService:
    return NextLineService()


def get_lyrics_orchestrator(
    song_identifier_service: Annotated[
        SongIdentifierService,
        Depends(get_song_identifier_service),
    ],
    lyrics_provider_service: Annotated[
        LyricsProviderService,
        Depends(get_lyrics_provider_service),
    ],
    genius_client: Annotated[
        GeniusClient,
        Depends(get_genius_client),
    ],
    lyrics_parser: Annotated[
        GeniusLyricsParser,
        Depends(get_lyrics_parser),
    ],
    next_line_service: Annotated[
        NextLineService,
        Depends(get_next_line_service),
    ],
) -> LyricsOrchestrator:
    return LyricsOrchestrator(
        song_identifier_service=song_identifier_service,
        lyrics_provider_service=lyrics_provider_service,
        genius_client=genius_client,
        lyrics_parser=lyrics_parser,
        next_line_service=next_line_service,
    )