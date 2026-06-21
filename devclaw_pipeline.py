"""Tiny module used to verify the DevClaw development pipeline."""

DEFAULT_PIPELINE_NAME = "DevClaw"


def build_message(name: str = DEFAULT_PIPELINE_NAME) -> str:
    """Return a predictable message for CLI output and tests."""
    clean_name = name.strip() or DEFAULT_PIPELINE_NAME
    return f"Pipeline check passed for {clean_name}."


def main() -> None:
    print(build_message())


if __name__ == "__main__":
    main()
