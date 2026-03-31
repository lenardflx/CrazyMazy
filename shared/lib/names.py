from __future__ import annotations

from random import shuffle


DISPLAY_NAMES: tuple[str, ...] = (
    "Sarah Kommt",
    "Merz leck Eier",
    "WTF is a Kilometer",
    "Orange Man",
    "Sleepy Joe",
    "Mama Merkel",
)


def generate_display_name(taken_names: set[str] | None = None) -> str:
    """Return a random curated display name that is not already taken."""
    taken = set() if taken_names is None else taken_names
    candidates = list(DISPLAY_NAMES)
    shuffle(candidates)
    for name in candidates:
        if name not in taken:
            return name
    raise ValueError("No unique display names available")
