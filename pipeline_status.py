"""Helpers for formatting pipeline status messages."""

DEFAULT_PIPELINE_NAME = "DevClaw"


def format_pipeline_status(name: str, passed: bool) -> str:
    """Return a normalized pipeline status message."""
    clean_name = name.strip() or DEFAULT_PIPELINE_NAME
    status = "passed" if passed else "failed"
    return f"Pipeline {clean_name}: {status}"
