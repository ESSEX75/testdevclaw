"""Utilities for validating DevClaw worker levels."""

SUPPORTED_WORKER_LEVELS = frozenset({"junior", "medior", "senior"})


def normalize_worker_level(level: str) -> str:
    """Return a canonical worker level or raise ``ValueError`` if invalid."""
    if not isinstance(level, str):
        raise ValueError("Worker level must be a non-empty string.")

    normalized_level = level.strip().lower()
    if not normalized_level:
        raise ValueError("Worker level must not be empty.")
    if normalized_level not in SUPPORTED_WORKER_LEVELS:
        supported = ", ".join(sorted(SUPPORTED_WORKER_LEVELS))
        raise ValueError(
            f"Unsupported worker level {level!r}. Supported levels: {supported}."
        )

    return normalized_level
