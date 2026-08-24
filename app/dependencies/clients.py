import asyncio
import logging
from functools import lru_cache

from app.clients.genius_client import GeniusClient
from app.clients.openai_client import OpenAIClient


logger = logging.getLogger(__name__)


@lru_cache
def get_openai_client() -> OpenAIClient:
    return OpenAIClient()


@lru_cache
def get_genius_client() -> GeniusClient:
    return GeniusClient()


async def close_clients() -> None:
    """Close cached provider clients that were created by the application."""

    close_operations = []

    if get_openai_client.cache_info().currsize:
        close_operations.append(get_openai_client().close())

    if get_genius_client.cache_info().currsize:
        close_operations.append(get_genius_client().close())

    try:
        if close_operations:
            logger.info(
                "CLIENT LIFECYCLE | closing | clients=%d",
                len(close_operations),
            )
            await asyncio.gather(*close_operations)
    finally:
        get_openai_client.cache_clear()
        get_genius_client.cache_clear()
        logger.info("CLIENT LIFECYCLE | closed_and_cleared")
