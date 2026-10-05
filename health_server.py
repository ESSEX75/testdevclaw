"""Minimal HTTP server exposing service metadata and health status."""

import json
import re
import tomllib
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PACKAGE_METADATA = Path(__file__).with_name("pyproject.toml")


def application_version() -> str:
    """Return the application version from the project package metadata."""
    with PACKAGE_METADATA.open("rb") as metadata_file:
        return tomllib.load(metadata_file)["project"]["version"]


REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
GET_ROUTES = frozenset({"/health", "/ready", "/version"})
NOT_FOUND_RESPONSE = {"error": "not_found", "message": "Route not found"}


class HealthRequestHandler(BaseHTTPRequestHandler):
    """Serve the application metadata and health endpoints."""

    def end_headers(self) -> None:
        """Add a request identifier to every response."""
        request_id = self.headers.get("X-Request-Id", "")
        if not REQUEST_ID_PATTERN.fullmatch(request_id):
            request_id = str(uuid.uuid4())
        self.send_header("X-Request-Id", request_id)
        super().end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            response = {"status": "ok"}
        elif self.path == "/ready":
            response = {"status": "ready"}
        elif self.path == "/version":
            response = {"version": application_version()}
        else:
            self._send_json(404, NOT_FOUND_RESPONSE)
            return

        self._send_json(200, response)

    def _handle_other_method(self) -> None:
        if self.path in GET_ROUTES:
            self.send_error(501, f"Unsupported method ({self.command!r})")
        else:
            self._send_json(404, NOT_FOUND_RESPONSE, send_body=self.command != "HEAD")

    do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = _handle_other_method

    def _send_json(
        self, status: int, response: dict[str, str], *, send_body: bool = True
    ) -> None:
        body = json.dumps(response).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """Keep routine health requests out of command-line output."""


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Create the HTTP server bound to the requested address."""
    return ThreadingHTTPServer((host, port), HealthRequestHandler)


def main() -> None:
    server = create_server()
    print("Application endpoints listening at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
