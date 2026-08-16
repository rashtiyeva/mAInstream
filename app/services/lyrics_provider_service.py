from app.core.exceptions import SongNotFoundException
from app.models.domain.song import Song
from app.models.domain.song_source import SongSource
from app.providers.genius_provider import GeniusProvider


class LyricsProviderService:

    def __init__(self, genius_provider: GeniusProvider) -> None:
        self._genius_provider = genius_provider

    async def find_song_source(
        self,
        song: Song,
    ) -> SongSource:
        source = await self._genius_provider.find_song(song)

        if source is None:
            raise SongNotFoundException(
                "Unable to find the song on Genius."
            )

        return source