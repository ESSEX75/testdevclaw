import unittest
from html.parser import HTMLParser
from pathlib import Path


STATUS_HTML_PATH = Path(__file__).resolve().parents[1] / "status.html"


class StatusContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_status = False
        self.status_role_found = False
        self.status_text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "p" and attributes.get("role") == "status":
            self.in_status = True
            self.status_role_found = True

    def handle_endtag(self, tag):
        if tag == "p" and self.in_status:
            self.in_status = False

    def handle_data(self, data):
        if self.in_status:
            self.status_text.append(data)


class StatusPageTest(unittest.TestCase):
    def test_renders_application_status(self):
        status_parser = StatusContentParser()
        status_parser.feed(STATUS_HTML_PATH.read_text(encoding="utf-8"))

        self.assertTrue(status_parser.status_role_found)
        self.assertEqual("".join(status_parser.status_text).strip(), "All systems operational")


if __name__ == "__main__":
    unittest.main()
