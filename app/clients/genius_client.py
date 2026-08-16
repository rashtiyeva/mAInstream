import httpx

from app.clients.base_client import BaseClient
from app.core.exceptions import GeniusApiException
from app.core.settings import get_settings


class GeniusClient(BaseClient):
    """
    Client responsible for communicating with the Genius API.
    """

    BASE_URL = "https://api.genius.com"

    def __init__(self) -> None:
        super().__init__()

        settings = get_settings()

        self._headers = {
            "Authorization": f"Bearer {settings.genius_access_token}",
        }

    async def search(self, query: str) -> httpx.Response:
        try:
            return await self.get(
                f"{self.BASE_URL}/search",
                params={"q": query},
                headers=self._headers,
            )

        except httpx.HTTPError as ex:
            raise GeniusApiException(
                "Failed to communicate with Genius API."
            ) from ex