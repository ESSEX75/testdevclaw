import unittest

from worker_level import normalize_worker_level


class NormalizeWorkerLevelTest(unittest.TestCase):
    def test_accepts_all_supported_levels(self):
        for level in ("junior", "medior", "senior"):
            with self.subTest(level=level):
                self.assertEqual(normalize_worker_level(level), level)

    def test_normalizes_case(self):
        self.assertEqual(normalize_worker_level("MeDiOr"), "medior")

    def test_trims_surrounding_whitespace(self):
        self.assertEqual(normalize_worker_level("  senior\n"), "senior")

    def test_rejects_empty_level(self):
        for level in ("", "   ", "\t\n"):
            with self.subTest(level=level):
                with self.assertRaisesRegex(ValueError, "must not be empty"):
                    normalize_worker_level(level)

    def test_rejects_unsupported_level(self):
        with self.assertRaisesRegex(ValueError, "Unsupported worker level"):
            normalize_worker_level("lead")


if __name__ == "__main__":
    unittest.main()
