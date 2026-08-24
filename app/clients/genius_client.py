import logging

import httpx

from app.clients.base_client import BaseClient
from app.core.exceptions import GeniusApiException
from app.core.settings import get_settings


logger = logging.getLogger(__name__)


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
            logger.info("GENIUS API | search | started")
            logger.debug("GENIUS API | search | query=%r", query)
            response = await self.get(
                f"{self.BASE_URL}/search",
                params={"q": query},
                headers=self._api_headers,
            )
            logger.info(
                "GENIUS API | search | completed | status=%s",
                response.status_code,
            )
            return response

        except httpx.HTTPError as ex:
            raise GeniusApiException(
                "Failed to communicate with Genius API."
            ) from ex

    async def get_page(self, url: str) -> httpx.Response:
        """
        Retrieve the HTML page of a Genius song.
        """
        try:
            logger.info("GENIUS PAGE | fetch | started | url=%s", url)
            response = await self.get(
                url,
                headers={
                    "Accept": "text/html",
                },
            )
            logger.info(
                "GENIUS PAGE | fetch | completed | status=%s | "
                "characters=%d",
                response.status_code,
                len(response.text),
            )
            return response

        except httpx.HTTPError as ex:
            raise GeniusApiException(
                "Failed to retrieve Genius page."
            ) from ex
