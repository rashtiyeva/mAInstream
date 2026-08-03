
from app.core.settings import get_settings

settings = get_settings()

print(settings.openai_model)
print(settings.request_timeout)