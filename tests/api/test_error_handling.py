import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.error_handling import register_exception_handlers
from app.core.exceptions import (
    GeniusApiException,
    ContinuationNotFoundException,
    LyricNotFoundException,
    LyricsNotFoundException,
    LyricTooGenericException,
    OpenAIException,
    SongNotFoundException,
)


@pytest.mark.parametrize(
    ("exception", "status", "code"),
    [
        (LyricTooGenericException("technical"), 422, "LYRIC_TOO_GENERIC"),
        (SongNotFoundException("technical"), 422, "SONG_NOT_FOUND"),
        (LyricNotFoundException("technical"), 422, "LYRIC_NOT_FOUND"),
        (
            ContinuationNotFoundException("technical"),
            422,
            "CONTINUATION_NOT_FOUND",
        ),
        (LyricsNotFoundException("technical"), 422, "LYRICS_NOT_FOUND"),
        (OpenAIException("secret provider detail"), 503, "PROVIDER_UNAVAILABLE"),
        (GeniusApiException("secret provider detail"), 503, "PROVIDER_UNAVAILABLE"),
    ],
)
def test_expected_exception_mapping(
    exception: Exception,
    status: int,
    code: str,
) -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/fail")
    async def fail() -> None:
        raise exception

    response = TestClient(app, raise_server_exceptions=False).get("/fail")

    assert response.status_code == status
    assert response.json()["code"] == code
    assert "technical" not in response.json()["message"]
    assert "secret" not in response.json()["message"]


def test_unexpected_exception_is_safe_internal_error() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/fail")
    async def fail() -> None:
        raise RuntimeError("database password and internal trace")

    response = TestClient(app, raise_server_exceptions=False).get("/fail")

    assert response.status_code == 500
    assert response.json() == {
        "code": "INTERNAL_ERROR",
        "message": "An unexpected internal error occurred.",
    }
    assert "password" not in response.text


def test_invalid_request_uses_stable_error_contract() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/needs-number")
    async def needs_number(value: int) -> int:
        return value

    response = TestClient(app).get(
        "/needs-number",
        params={"value": "not-a-number"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "INVALID_REQUEST",
        "message": "The request payload is invalid.",
    }
