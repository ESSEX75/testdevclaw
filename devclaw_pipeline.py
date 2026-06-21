"""Tiny module used to verify the DevClaw development pipeline."""

SPRINT_STEP_ONE_MARKER = "test-step-one"
SPRINT_STEP_TWO_MARKER = "test-step-two"


def build_message(name: str = "DevClaw") -> str:
    """Return a predictable message for CLI output and tests."""
    clean_name = name.strip() or "DevClaw"
    return f"Pipeline check passed for {clean_name}."


def sprint_step_marker() -> str:
    """Return the marker for sprint step one."""
    return SPRINT_STEP_ONE_MARKER


def sprint_step_two_marker() -> str:
    """Return the marker for sprint step two."""
    return SPRINT_STEP_TWO_MARKER


def main() -> None:
    print(build_message())


if __name__ == "__main__":
    main()
