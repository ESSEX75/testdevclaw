"""Tiny module used to verify the DevClaw development pipeline."""

DEFAULT_PIPELINE_NAME = "DevClaw"
DEMO_PIPELINE_CONSTANT = "demo-pipeline-value"
SPRINT_STEP_ONE_MARKER = "test-step-one"
SPRINT_STEP_TWO_MARKER = "test-step-two"
SPRINT_STEP_THREE_MARKER = "test-step-three"
SPRINT_STEP_FOUR_MARKER = "test-step-four"
SPRINT_STEP_FIVE_MARKER = "test-step-five"


def build_message(name: str = DEFAULT_PIPELINE_NAME) -> str:
    """Return a predictable message for CLI output and tests."""
    clean_name = name.strip() or DEFAULT_PIPELINE_NAME
    return f"Pipeline verification passed for {clean_name}."


def sprint_step_marker() -> str:
    """Return the marker for sprint step one."""
    return SPRINT_STEP_ONE_MARKER


def sprint_step_two_marker() -> str:
    """Return the marker for sprint step two."""
    return SPRINT_STEP_TWO_MARKER


def sprint_step_three_marker() -> str:
    """Return the marker for sprint step three."""
    return SPRINT_STEP_THREE_MARKER


def sprint_step_four_marker() -> str:
    """Return the marker for sprint step four."""
    return SPRINT_STEP_FOUR_MARKER


def sprint_step_five_marker() -> str:
    """Return the marker for sprint step five."""
    return SPRINT_STEP_FIVE_MARKER


def main() -> None:
    print(build_message())


if __name__ == "__main__":
    main()
