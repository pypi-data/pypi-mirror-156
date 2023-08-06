"""Module containing utility functions for strings."""

from __future__ import annotations

from functools import lru_cache

import uuid


_UUID_NAMESPACE = uuid.UUID('45ca38a3-63c4-4ee8-9f41-9240e063ec24')


@lru_cache(maxsize=None)
def generate_id(seed: str | None = None) -> str:
    """Generate a UUID based from a seed string or random."""

    if not seed:
        return uuid.uuid4().hex
    return uuid.uuid5(_UUID_NAMESPACE, seed).hex


@lru_cache(maxsize=None)
def lowerstrip(input_string: str) -> str:
    return "".join(str(input_string).split()).lower()


if __name__ == "__main__":
    assert generate_id("test") == "e615ea65d14457b99a5b443e9ee3b4e0"
