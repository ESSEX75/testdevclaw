# test_dev_project

Minimal Python project used to verify the DevClaw development pipeline.

Sprint smoke marker: parallel minimal code change A (#35).

## Run

```bash
python3 devclaw_pipeline.py
```

Expected output:

```text
Pipeline verification passed for DevClaw.
```

## Test

```bash
python3 -m unittest discover -s tests
```

## Sprint smoke marker

- minimal-code-a: branch and PR creation check for sprint-minimal-pr-smoke-2.
- issue-69: standard DevClaw worker workflow check.
