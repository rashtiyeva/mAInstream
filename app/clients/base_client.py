from abc import ABC

import httpx

from app.core.settings import get_settings


class BaseClient(ABC):

    def __init__(self) -> None:
        settings = get_settings()

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout),
            follow_redirects=True,
            headers={
                "User-Agent": "mainstream",
                "Accept": "application/json",
            },
        )

    async def get(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        response = await self._client.get(url, **kwargs)
        response.raise_for_status()
        return response

    async def post(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        response = await self._client.post(url, **kwargs)
        response.raise_for_status()
        return response
    
    

    async def close(self) -> None:
        await self._client.aclose()