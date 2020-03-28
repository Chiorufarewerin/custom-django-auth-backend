import os

try:
    from django.conf import settings
    getattr(settings, 'SOME_VALUE', None)
except Exception:
    settings = None


def get_from_settings_or_env(name: str, default=None):
    return getattr(settings, name, os.getenv(name, default))
