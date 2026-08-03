from app.clients.openai_client import OpenAIClient
from app.core.exceptions import SongNotFoundException
from app.models.domain.song import Song


class SongIdentifierService:

    def __init__(self, client: OpenAIClient):
        self._client = client

    async def identify_song(self, lyric: str) -> Song:
        song = await self._client.identify_song(lyric)

        if not song.title or not song.artist:
            raise SongNotFoundException(
                "Unable to identify the song."
            )

        return song