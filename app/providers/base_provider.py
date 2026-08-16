from abc import ABC, abstractmethod

from app.models.domain.song import Song
from app.models.domain.song_source import SongSource


class BaseProvider(ABC):

    @abstractmethod
    async def find_song(
        self,
        song: Song,
    ) -> SongSource | None:
        pass