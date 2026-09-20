import json
import threading
import unittest
import uuid
from urllib.error import HTTPError
from urllib.request import Request
from urllib.request import urlopen

from health_server import create_server


class HealthEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def test_health_endpoint_returns_successful_status(self):
        port = self.server.server_address[1]

        with urlopen(f"http://127.0.0.1:{port}/health") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_response_includes_generated_request_id(self):
        port = self.server.server_address[1]

        with urlopen(f"http://127.0.0.1:{port}/health") as response:
            request_id = response.headers["X-Request-Id"]

        self.assertEqual(str(uuid.UUID(request_id)), request_id)

    def test_response_preserves_valid_incoming_request_id(self):
        port = self.server.server_address[1]
        request = Request(
            f"http://127.0.0.1:{port}/health",
            headers={"X-Request-Id": "client-request_123"},
        )

        with urlopen(request) as response:
            self.assertEqual(response.headers["X-Request-Id"], "client-request_123")

    def test_error_response_includes_request_id(self):
        port = self.server.server_address[1]

        with self.assertRaises(HTTPError) as error:
            urlopen(f"http://127.0.0.1:{port}/missing")

        self.assertIsNotNone(error.exception.headers["X-Request-Id"])


if __name__ == "__main__":
    unittest.main()
