"""Minimal HTTP server exposing service metadata and health status."""

import json
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PACKAGE_METADATA = Path(__file__).with_name("pyproject.toml")


def application_version() -> str:
    """Return the application version from the project package metadata."""
    with PACKAGE_METADATA.open("rb") as metadata_file:
        return tomllib.load(metadata_file)["project"]["version"]


class HealthRequestHandler(BaseHTTPRequestHandler):
    """Serve the application metadata and health endpoints."""

    def do_GET(self) -> None:
        if self.path == "/health":
            response = {"status": "ok"}
        elif self.path == "/version":
            response = {"version": application_version()}
        else:
            self.send_error(404)
            return

        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
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
