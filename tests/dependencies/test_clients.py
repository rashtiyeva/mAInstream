from unittest.mock import AsyncMock

import pytest

from app.core.settings import get_settings
from app.dependencies.clients import (
    close_clients,
    get_genius_client,
    get_openai_client,
)


@pytest.mark.asyncio
async def test_close_clients_closes_and_clears_created_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GENIUS_ACCESS_TOKEN", "test-genius-token")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("REQUEST_TIMEOUT", "10")
    get_settings.cache_clear()
    get_openai_client.cache_clear()
    get_genius_client.cache_clear()

    openai_client = get_openai_client()
    genius_client = get_genius_client()
    openai_client._client.close = AsyncMock()
    genius_client._client.aclose = AsyncMock()

    await close_clients()

    openai_client._client.close.assert_awaited_once()
    genius_client._client.aclose.assert_awaited_once()
    assert get_openai_client.cache_info().currsize == 0
    assert get_genius_client.cache_info().currsize == 0
