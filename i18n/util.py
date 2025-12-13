# i18n/util.py

from .messages import MESSAGES

DEFAULT_LANGUAGE = "uz"

def get_language_from_path(path: str) -> str:
    if path.startswith("/ru/"):
        return "ru"
    return DEFAULT_LANGUAGE


def t(key: str, language: str) -> str:
    return (
        MESSAGES.get(key, {}).get(language)
        or MESSAGES.get(key, {}).get(DEFAULT_LANGUAGE)
        or key
    )