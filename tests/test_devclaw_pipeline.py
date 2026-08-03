import unittest

from devclaw_pipeline import (
    build_message,
    sprint_step_five_marker,
    sprint_step_four_marker,
    sprint_step_marker,
    sprint_step_three_marker,
    sprint_step_two_marker,
)


class BuildMessageTest(unittest.TestCase):
    def test_build_message_uses_default_name(self):
        self.assertEqual(build_message(), "Pipeline verification passed for DevClaw.")

    def test_build_message_trims_custom_name(self):
        self.assertEqual(build_message(" test_dev_project "), "Pipeline verification passed for test_dev_project.")

    def test_sprint_step_marker_identifies_step_one(self):
        self.assertEqual(sprint_step_marker(), "test-step-one")

    def test_sprint_step_two_marker_identifies_step_two(self):
        self.assertEqual(sprint_step_two_marker(), "test-step-two")

    def test_sprint_step_three_marker_identifies_step_three(self):
        self.assertEqual(sprint_step_three_marker(), "test-step-three")

    def test_sprint_step_four_marker_identifies_step_four(self):
        self.assertEqual(sprint_step_four_marker(), "test-step-four")

    def test_sprint_step_five_marker_identifies_step_five(self):
        self.assertEqual(sprint_step_five_marker(), "test-step-five")


if __name__ == "__main__":
    unittest.main()
