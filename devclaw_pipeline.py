"""Tiny module used to verify the DevClaw development pipeline."""


def build_message(name: str = "DevClaw") -> str:
    """Return a predictable message for CLI output and tests."""
    clean_name = name.strip() or "DevClaw"
    return f"Pipeline check passed for {clean_name}."


def main() -> None:
    print(build_message())


if __name__ == "__main__":
    main()
