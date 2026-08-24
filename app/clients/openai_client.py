import logging

from openai import APIConnectionError, APIStatusError, AsyncOpenAI
from pydantic import ValidationError

from app.core.exceptions import (
    InvalidProviderResponseException,
    OpenAIException,
)
from app.core.settings import get_settings
from app.models.domain.song import Song
from app.prompts.identify_song import IDENTIFY_SONG_PROMPT


logger = logging.getLogger(__name__)


class OpenAIClient:

    def __init__(self) -> None:
        settings = get_settings()

        self._model = settings.openai_model

        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

    async def identify_song(self, lyric: str) -> Song:

        try:
            response = await self._client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": IDENTIFY_SONG_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": lyric,
                    },
                ],
            )

            logger.debug("OpenAI raw response: %s", response.output_text)

            if not response.output_text:
                raise InvalidProviderResponseException(
                    "OpenAI returned an empty response."
                )

            song = Song.model_validate_json(response.output_text)

            logger.debug("Parsed song response: %s", song)

            return song

        except ValidationError as ex:
            raise InvalidProviderResponseException(
                "OpenAI returned an invalid JSON response."
            ) from ex

        except (APIConnectionError, APIStatusError) as ex:
            raise OpenAIException(
                "Failed to communicate with OpenAI."
            ) from ex
