import httpx
import pytest

from app.clients.genius_client import GeniusClient
from app.core.exceptions import GeniusApiException


@pytest.mark.asyncio
async def test_get_page_returns_html_response(monkeypatch):
    client = GeniusClient()

    expected_response = httpx.Response(
        status_code=200,
        text="<html>lyrics page</html>",
    )

    async def mock_get(url, **kwargs):
        assert url == "https://genius.com/the-beatles-yesterday-lyrics"
        assert kwargs["headers"]["Accept"] == "text/html"

        return expected_response

    monkeypatch.setattr(client, "get", mock_get)

    response = await client.get_page(
        "https://genius.com/the-beatles-yesterday-lyrics"
    )

    assert response.status_code == 200
    assert response.text == "<html>lyrics page</html>"

    await client.close()


@pytest.mark.asyncio
async def test_get_page_raises_genius_api_exception(monkeypatch):
    client = GeniusClient()

    async def mock_get(url, **kwargs):
        raise httpx.ConnectError("Connection failed")

    monkeypatch.setattr(client, "get", mock_get)

    with pytest.raises(GeniusApiException, match="Failed to retrieve Genius page."):
        await client.get_page(
            "https://genius.com/the-beatles-yesterday-lyrics"
        )

    await client.close()