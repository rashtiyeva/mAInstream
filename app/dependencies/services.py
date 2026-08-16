from typing import Annotated

from fastapi import Depends

from app.clients.genius_client import GeniusClient
from app.clients.openai_client import OpenAIClient
from app.dependencies.clients import (
    get_genius_client,
    get_openai_client,
)
from app.providers.genius_provider import GeniusProvider
from app.services.lyrics_provider_service import LyricsProviderService
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