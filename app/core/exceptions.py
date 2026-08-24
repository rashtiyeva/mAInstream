class AppException(Exception):
    """Base exception for the application."""


class ProviderException(AppException):
    """Raised when an external provider fails."""


class OpenAIException(ProviderException):
    """Raised when the OpenAI provider fails."""


class GeniusException(ProviderException):
    """Raised when the Genius provider fails."""


class GeniusApiException(GeniusException):
    """Raised when the Genius API request fails."""


class GeniusResponseException(GeniusException):
    """Raised when the Genius API returns an unexpected response."""
    

class GoogleSearchException(ProviderException):
    """Raised when Google Search fails."""


class SongNotFoundException(AppException):
    """Raised when the song cannot be identified."""


class LyricsNotFoundException(AppException):
    """Raised when lyrics cannot be retrieved."""


class LyricNotFoundException(AppException):
    """Raised when the user's lyric is not found in the song."""


class LyricTooGenericException(AppException):
    """Raised when the submitted lyric has too few meaningful words."""


class ContinuationNotFoundException(AppException):
    """Raised when a matched lyric has no valid continuation."""


class InvalidProviderResponseException(ProviderException):
    """Raised when a provider returns an unexpected response."""
