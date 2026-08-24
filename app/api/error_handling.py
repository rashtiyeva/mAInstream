import logging
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    ContinuationNotFoundException,
    LyricNotFoundException,
    LyricsNotFoundException,
    LyricTooGenericException,
    ProviderException,
    SongNotFoundException,
)
from app.models.dto.api_error_response import (
    ApiErrorCode,
    ApiErrorResponse,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ApiError:
    status_code: int
    response: ApiErrorResponse


def translate_exception(exception: Exception) -> ApiError:
    """Translate internal exceptions into the stable public API contract."""

    if isinstance(exception, LyricTooGenericException):
        return ApiError(
            status_code=422,
            response=ApiErrorResponse(
                code=ApiErrorCode.LYRIC_TOO_GENERIC,
                message="The provided lyric is too short to identify reliably.",
            ),
        )

    if isinstance(exception, SongNotFoundException):
        return ApiError(
            status_code=422,
            response=ApiErrorResponse(
                code=ApiErrorCode.SONG_NOT_FOUND,
                message="Unable to identify a song from the provided lyric.",
            ),
        )

    if isinstance(exception, LyricNotFoundException):
        return ApiError(
            status_code=422,
            response=ApiErrorResponse(
                code=ApiErrorCode.LYRIC_NOT_FOUND,
                message="The provided lyric was not found in the identified song.",
            ),
        )

    if isinstance(exception, ContinuationNotFoundException):
        return ApiError(
            status_code=422,
            response=ApiErrorResponse(
                code=ApiErrorCode.CONTINUATION_NOT_FOUND,
                message="No valid continuation was found after the matched lyric.",
            ),
        )

    if isinstance(exception, LyricsNotFoundException):
        return ApiError(
            status_code=422,
            response=ApiErrorResponse(
                code=ApiErrorCode.LYRICS_NOT_FOUND,
                message="Lyrics could not be found for the identified song.",
            ),
        )

    if isinstance(exception, ProviderException):
        return ApiError(
            status_code=503,
            response=ApiErrorResponse(
                code=ApiErrorCode.PROVIDER_UNAVAILABLE,
                message="A required external provider is currently unavailable.",
            ),
        )

    return ApiError(
        status_code=500,
        response=ApiErrorResponse(
            code=ApiErrorCode.INTERNAL_ERROR,
            message="An unexpected internal error occurred.",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exception: RequestValidationError,
    ) -> JSONResponse:
        logger.info(
            "Invalid request for %s %s: %s",
            request.method,
            request.url.path,
            exception.errors(),
        )
        response = ApiErrorResponse(
            code=ApiErrorCode.INVALID_REQUEST,
            message="The request payload is invalid.",
        )
        return JSONResponse(
            status_code=422,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(AppException)
    async def handle_app_exception(
        request: Request,
        exception: AppException,
    ) -> JSONResponse:
        error = translate_exception(exception)
        if error.status_code >= 500:
            logger.exception(
                "HTTP ERROR | method=%s | path=%s | code=%s",
                request.method,
                request.url.path,
                error.response.code,
                exc_info=exception,
            )
        else:
            logger.warning(
                "HTTP ERROR | method=%s | path=%s | code=%s | detail=%s",
                request.method,
                request.url.path,
                error.response.code,
                exception,
            )
        return JSONResponse(
            status_code=error.status_code,
            content=error.response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(
        request: Request,
        exception: Exception,
    ) -> JSONResponse:
        error = translate_exception(exception)
        logger.exception(
            "HTTP ERROR | unexpected | method=%s | path=%s",
            request.method,
            request.url.path,
            exc_info=exception,
        )
        return JSONResponse(
            status_code=error.status_code,
            content=error.response.model_dump(mode="json"),
        )
