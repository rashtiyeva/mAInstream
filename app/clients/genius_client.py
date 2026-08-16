import httpx

from app.clients.base_client import BaseClient
from app.core.exceptions import GeniusApiException
from app.core.settings import get_settings


class GeniusClient(BaseClient):
    """
    Client responsible for communicating with Genius.
    """

    BASE_URL = "https://api.genius.com"

    def __init__(self) -> None:
        super().__init__()

        settings = get_settings()

        self._api_headers = {
            "Authorization": f"Bearer {settings.genius_access_token}",
            "Accept": "application/json",
        }

    async def search(self, query: str) -> httpx.Response:
        """
        Search for a song using the Genius API.
        """
        try:
            return await self.get(
                f"{self.BASE_URL}/search",
                params={"q": query},
                headers=self._api_headers,
            )

        except httpx.HTTPError as ex:
            raise GeniusApiException(
                "Failed to communicate with Genius API."
            ) from ex

    async def get_page(self, url: str) -> httpx.Response:
        """
        Retrieve the HTML page of a Genius song.
        """
        try:
            return await self.get(
                url,
                headers={
                    "Accept": "text/html",
                },
            )

        except httpx.HTTPError as ex:
            raise GeniusApiException(
                "Failed to retrieve Genius page."
            ) from ex