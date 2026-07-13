"""Helpers for reading environment values in Django settings."""

from __future__ import annotations


def csv_list(value: str | None, *, strip: bool = True) -> list[str]:
    """Split a comma-separated env string into a list of non-empty items."""
    if not value:
        return []
    items = value.split(",")
    if strip:
        return [item.strip() for item in items if item.strip()]
    return [item for item in items if item]


def env_bool(value: str | bool | None, default: bool = False) -> bool:
    """Parse common truthy/falsy string forms from the environment."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
