import unittest

from devclaw_pipeline import build_message, sprint_step_marker


class BuildMessageTest(unittest.TestCase):
    def test_build_message_uses_default_name(self):
        self.assertEqual(build_message(), "Pipeline check passed for DevClaw.")

    def test_build_message_trims_custom_name(self):
        self.assertEqual(build_message(" test_dev_project "), "Pipeline check passed for test_dev_project.")

    def test_sprint_step_marker_identifies_step_one(self):
        self.assertEqual(sprint_step_marker(), "test-step-one")


if __name__ == "__main__":
    unittest.main()
