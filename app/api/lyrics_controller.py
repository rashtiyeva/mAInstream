import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.error_handling import translate_exception
from app.api.sse import QueueProgressReporter, encode_sse
from app.dependencies.services import get_lyrics_orchestrator
from app.models.dto.api_error_response import ApiErrorResponse
from app.models.dto.lyric_continuation_response import (
    LyricContinuationResponse,
)
from app.models.dto.request import LyricContinuationRequest
from app.services.lyrics_orchestrator import LyricsOrchestrator

router = APIRouter(prefix="/lyrics", tags=["Lyrics"])
logger = logging.getLogger(__name__)


@router.post(
    "/identify",
    response_model=LyricContinuationResponse,
    responses={
        422: {"model": ApiErrorResponse},
        503: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def identify_song(
    request: LyricContinuationRequest,
    orchestrator: Annotated[
        LyricsOrchestrator,
        Depends(get_lyrics_orchestrator),
    ],
) -> LyricContinuationResponse:
    logger.info("HTTP | POST /lyrics/identify | started")
    return await orchestrator.get_continuation(request.lyric)


@router.post(
    "/identify/stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "Progress events followed by a result or error.",
        }
    },
)
async def identify_song_stream(
    request: LyricContinuationRequest,
    orchestrator: Annotated[
        LyricsOrchestrator,
        Depends(get_lyrics_orchestrator),
    ],
) -> StreamingResponse:
    async def event_stream() -> AsyncIterator[str]:
        reporter = QueueProgressReporter()
        logger.info("SSE | POST /lyrics/identify/stream | opened")

        async def run_workflow() -> None:
            try:
                result = await orchestrator.get_continuation(
                    request.lyric,
                    progress_reporter=reporter,
                )
                await reporter.events.put(
                    ("result", result.model_dump_json())
                )
                logger.info("SSE | terminal_event_queued | event=result")
            except Exception as exception:
                error = translate_exception(exception)
                if error.status_code >= 500:
                    logger.exception(
                        "Streaming lyric workflow failed.",
                        exc_info=exception,
                    )
                else:
                    logger.warning(
                        "Streaming lyric workflow ended with %s: %s",
                        error.response.code,
                        exception,
                        exc_info=True,
                    )
                await reporter.events.put(
                    ("error", error.response.model_dump_json())
                )
                logger.info(
                    "SSE | terminal_event_queued | event=error | code=%s",
                    error.response.code,
                )

        task = asyncio.create_task(run_workflow())

        try:
            while True:
                event_name, data_json = await reporter.events.get()
                logger.debug("SSE | emitting | event=%s", event_name)
                yield encode_sse(event_name, data_json)

                if event_name in {"result", "error"}:
                    break
        finally:
            if not task.done():
                logger.debug("SSE | cancelling_workflow")
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            logger.info("SSE | stream_closed")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
