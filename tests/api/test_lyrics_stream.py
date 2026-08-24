import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.error_handling import register_exception_handlers
from app.api.lyrics_controller import router
from app.core.exceptions import SongNotFoundException
from app.dependencies.services import get_lyrics_orchestrator
from app.models.dto.lyric_continuation_response import (
    LyricContinuationResponse,
)
from app.models.dto.progress_event import ProgressEvent, ProgressStep


class FakeOrchestrator:
    def __init__(self, failure: Exception | None = None) -> None:
        self.calls = 0
        self.failure = failure

    async def get_continuation(
        self,
        lyric: str,
        progress_reporter=None,
    ) -> LyricContinuationResponse:
        self.calls += 1

        if progress_reporter is not None:
            await progress_reporter.report(
                ProgressEvent(step=ProgressStep.VALIDATING_INPUT)
            )
            await progress_reporter.report(
                ProgressEvent(step=ProgressStep.IDENTIFYING_SONG)
            )

        if self.failure is not None:
            raise self.failure

        if progress_reporter is not None:
            await progress_reporter.report(
                ProgressEvent(
                    step=ProgressStep.SONG_IDENTIFIED,
                    song="Shake It Off",
                    artist="Taylor Swift",
                )
            )

        return LyricContinuationResponse(
            song="Shake It Off",
            artist="Taylor Swift",
            continuation="I stay out too late",
        )


def create_test_app(orchestrator: FakeOrchestrator) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_lyrics_orchestrator] = lambda: orchestrator
    return app


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []

    for block in body.strip().split("\n\n"):
        lines = block.splitlines()
        event = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((event, data))

    return events


def test_stream_emits_ordered_progress_then_final_result() -> None:
    orchestrator = FakeOrchestrator()
    client = TestClient(create_test_app(orchestrator))

    response = client.post(
        "/lyrics/identify/stream",
        json={"lyric": "making the bed"},
    )
    events = parse_sse(response.text)

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert [event for event, _ in events] == [
        "progress",
        "progress",
        "progress",
        "result",
    ]
    assert [data["step"] for event, data in events if event == "progress"] == [
        "VALIDATING_INPUT",
        "IDENTIFYING_SONG",
        "SONG_IDENTIFIED",
    ]
    assert events[-1][1]["continuation"] == "I stay out too late"
    assert response.text.endswith("\n\n")


def test_stream_emits_error_as_final_event_and_terminates() -> None:
    orchestrator = FakeOrchestrator(
        failure=SongNotFoundException("internal identification detail")
    )
    client = TestClient(create_test_app(orchestrator))

    response = client.post(
        "/lyrics/identify/stream",
        json={"lyric": "making the bed"},
    )
    events = parse_sse(response.text)

    assert [event for event, _ in events] == [
        "progress",
        "progress",
        "error",
    ]
    assert events[-1][1] == {
        "code": "SONG_NOT_FOUND",
        "message": "Unable to identify a song from the provided lyric.",
    }
    assert response.text.endswith("\n\n")


def test_json_and_stream_endpoints_use_same_orchestrator_workflow() -> None:
    orchestrator = FakeOrchestrator()
    client = TestClient(create_test_app(orchestrator))

    json_response = client.post(
        "/lyrics/identify",
        json={"lyric": "making the bed"},
    )
    stream_response = client.post(
        "/lyrics/identify/stream",
        json={"lyric": "making the bed"},
    )

    assert json_response.status_code == 200
    assert stream_response.status_code == 200
    assert orchestrator.calls == 2
