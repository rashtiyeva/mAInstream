import asyncio

from app.models.dto.progress_event import ProgressEvent


class QueueProgressReporter:
    """Adapt application progress events to an in-process async queue."""

    def __init__(self) -> None:
        self.events: asyncio.Queue[tuple[str, str]] = asyncio.Queue()

    async def report(self, event: ProgressEvent) -> None:
        await self.events.put(
            ("progress", event.model_dump_json(exclude_none=True))
        )


def encode_sse(event: str, data_json: str) -> str:
    """Encode one JSON payload as an SSE event."""

    return f"event: {event}\ndata: {data_json}\n\n"
