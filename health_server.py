"""Minimal HTTP server exposing the service health status."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthRequestHandler(BaseHTTPRequestHandler):
    """Serve the health check endpoint."""

    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return

        body = json.dumps({"status": "ok"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """Keep routine health requests out of command-line output."""


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Create a health server bound to the requested address."""
    return ThreadingHTTPServer((host, port), HealthRequestHandler)


def main() -> None:
    server = create_server()
    print("Health endpoint listening at http://127.0.0.1:8000/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
