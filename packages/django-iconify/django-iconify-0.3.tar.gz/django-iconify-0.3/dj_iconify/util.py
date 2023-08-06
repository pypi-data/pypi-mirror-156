"""Utility code used by other parts of django-iconify."""
import os
import re

from .conf import COLLECTIONS_ALLOWED, COLLECTIONS_DISALLOWED, JSON_ROOT


def split_css_unit(string: str):
    """Split string into value and unit.

    >>> split_css_unit("12px")
    (12, 'px')
    >>> split_css_unit("1.5em")
    (1.5, 'em')
    >>> split_css_unit("18%")
    (18, '%')
    >>> split_css_unit("200")
    (200, '')
    """
    _value = re.findall("^[0-9.]+", string)
    value = float(_value[0]) if "." in _value[0] else int(_value[0])
    unit = string[len(_value[0]) :]

    return value, unit


def collection_allowed(collection: str) -> bool:
    """Determine whether a collection is allowed by settings."""

    if collection in COLLECTIONS_DISALLOWED:
        return False

    if COLLECTIONS_ALLOWED and collection not in COLLECTIONS_ALLOWED:
        return False

    return True


def icon_choices(collection: str) -> list[tuple[str, str]]:
    """Get Django model/form choices for icons in one collection."""

    from .types import IconifyJSON

    if not collection_allowed(collection):
        raise KeyError("The collection %s is disallowed." % collection)

    # Load icon set through Iconify types
    collection_file = os.path.join(JSON_ROOT, "json", f"{collection}.json")
    icon_set = IconifyJSON.from_file(collection_file)

    return [(name, name) for name in sorted(icon_set.icons.keys())]
