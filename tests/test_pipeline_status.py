import unittest

from pipeline_status import format_pipeline_status


class FormatPipelineStatusTest(unittest.TestCase):
    def test_formats_passed_status(self):
        self.assertEqual(
            format_pipeline_status("release", True),
            "Pipeline release: passed",
        )

    def test_formats_failed_status(self):
        self.assertEqual(
            format_pipeline_status("release", False),
            "Pipeline release: failed",
        )

    def test_trims_pipeline_name(self):
        self.assertEqual(
            format_pipeline_status("  release  ", True),
            "Pipeline release: passed",
        )

    def test_uses_default_for_empty_name(self):
        self.assertEqual(
            format_pipeline_status("   ", False),
            "Pipeline DevClaw: failed",
        )


if __name__ == "__main__":
    unittest.main()
