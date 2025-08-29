from urllib.parse import urlparse

from rest_framework.exceptions import ValidationError

ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


def validate_youtube_url(value: str) -> str:
    """
    Разрешены только ссылки на YouTube.
    Пустое значение (если поле optional) — пропускаем.
    """
    if not value:
        return value

    try:
        host = urlparse(value).netloc.lower()
    except Exception:
        raise ValidationError("Невалидный URL.")

    if host not in ALLOWED_HOSTS:
        raise ValidationError("Разрешены только ссылки на YouTube (youtube.com / youtu.be).")

    return value
