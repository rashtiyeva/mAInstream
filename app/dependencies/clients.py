from functools import lru_cache

from app.clients.genius_client import GeniusClient
from app.clients.openai_client import OpenAIClient


@lru_cache
def get_openai_client() -> OpenAIClient:
    return OpenAIClient()

@lru_cache
def get_genius_client() -> GeniusClient:
    return GeniusClient()