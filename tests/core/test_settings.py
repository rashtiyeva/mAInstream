from app.core.settings import Settings


def test_unused_legacy_settings_are_not_required() -> None:
    settings = Settings(
        openai_api_key="test-openai-key",
        genius_access_token="test-genius-token",
        openai_model="test-model",
        request_timeout=10,
        _env_file=None,
    )

    assert settings.openai_model == "test-model"


def test_legacy_environment_values_are_ignored() -> None:
    settings = Settings(
        openai_api_key="test-openai-key",
        genius_access_token="test-genius-token",
        openai_model="test-model",
        request_timeout=10,
        google_api_key="unused",
        redis_url="unused",
        cache_ttl=60,
        _env_file=None,
    )

    assert settings.openai_model == "test-model"
