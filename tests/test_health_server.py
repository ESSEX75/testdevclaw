import json
import threading
import tomllib
import unittest
from pathlib import Path
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

    def test_version_endpoint_returns_package_version(self):
        port = self.server.server_address[1]
        metadata_path = Path(__file__).parents[1] / "pyproject.toml"
        with metadata_path.open("rb") as metadata_file:
            package_version = tomllib.load(metadata_file)["project"]["version"]

        with urlopen(f"http://127.0.0.1:{port}/version") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertEqual(json.load(response), {"version": package_version})


if __name__ == "__main__":
    unittest.main()
