from fastapi import Depends

from app.clients.openai_client import OpenAIClient
from app.dependencies.clients import get_openai_client
from app.services.song_identifier_service import SongIdentifierService


def get_song_identifier_service(
    client: OpenAIClient = Depends(get_openai_client),
) -> SongIdentifierService:
    return SongIdentifierService(client)