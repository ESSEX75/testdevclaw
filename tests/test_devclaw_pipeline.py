import unittest

from devclaw_pipeline import build_message


class BuildMessageTest(unittest.TestCase):
    def test_build_message_uses_default_name(self):
        self.assertEqual(build_message(), "Pipeline check passed for DevClaw.")

    def test_build_message_trims_custom_name(self):
        self.assertEqual(build_message(" test_dev_project "), "Pipeline check passed for test_dev_project.")


if __name__ == "__main__":
    unittest.main()
