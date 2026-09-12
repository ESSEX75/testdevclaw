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

Open `status.html` in a browser to view the responsive sample application
status page.

## Test

```bash
python3 -m unittest discover -s tests
```

## Health check

Start the local health server:

```bash
python3 health_server.py
```

`GET http://127.0.0.1:8000/health` returns `200 OK` with:

```json
{"status": "ok"}
```

## Sprint smoke marker

- minimal-code-a: branch and PR creation check for sprint-minimal-pr-smoke-2.
- issue-69: standard DevClaw worker workflow check.
