from typing import Protocol

from app.models.dto.progress_event import ProgressEvent


class ProgressReporter(Protocol):
    async def report(self, event: ProgressEvent) -> None:
        """Publish one application-level progress event."""


class NoOpProgressReporter:
    async def report(self, event: ProgressEvent) -> None:
        return None
