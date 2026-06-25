import unittest

from devclaw_pipeline import (
    build_message,
    sprint_step_marker,
    sprint_step_two_marker,
    three_step_sprint_step_one_marker,
)


class BuildMessageTest(unittest.TestCase):
    def test_build_message_uses_default_name(self):
        self.assertEqual(build_message(), "Pipeline check passed for DevClaw.")

    def test_build_message_trims_custom_name(self):
        self.assertEqual(build_message(" test_dev_project "), "Pipeline check passed for test_dev_project.")

    def test_sprint_step_marker_identifies_step_one(self):
        self.assertEqual(sprint_step_marker(), "test-step-one")

    def test_sprint_step_two_marker_identifies_step_two(self):
        self.assertEqual(sprint_step_two_marker(), "test-step-two")

    def test_three_step_sprint_step_one_marker_identifies_step_one(self):
        self.assertEqual(three_step_sprint_step_one_marker(), "three-step-sprint-step-one")


if __name__ == "__main__":
    unittest.main()
