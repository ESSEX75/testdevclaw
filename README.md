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

## Application version

With the local server running, `GET http://127.0.0.1:8000/version` returns
`200 OK` and the version declared in `pyproject.toml`:

```json
{"version": "1.0.0"}
```

Every HTTP response includes an `X-Request-Id` header. The server preserves an
incoming identifier when it contains 1–128 letters, numbers, periods,
underscores, or hyphens. If the header is absent or invalid, the server returns
a newly generated UUID instead.

## Sprint smoke marker

- minimal-code-a: branch and PR creation check for sprint-minimal-pr-smoke-2.
- issue-69: standard DevClaw worker workflow check.
