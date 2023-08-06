"""App configuration for django-iconify."""
from django.conf import settings

_prefix = "ICONIFY_"

JSON_ROOT = getattr(settings, f"{_prefix}JSON_ROOT")

COLLECTIONS_ALLOWED = getattr(settings, f"{_prefix}COLLECTIONS_ALLOWED", [])
COLLECTIONS_DISALLOWED = getattr(settings, f"{_prefix}COLLECTIONS_DISALLOWED", [])
