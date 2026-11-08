import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import progress  # noqa: E402


class TestNextLevel(unittest.TestCase):
    def test_advances(self):
        self.assertEqual(progress.next_level(0, 3), 1)

    def test_wraps(self):
        self.assertEqual(progress.next_level(2, 3), 0)

    def test_single_level(self):
        self.assertEqual(progress.next_level(0, 1), 0)


class TestBest(unittest.TestCase):
    def test_first_clear_is_new_best(self):
        s = {}
        self.assertTrue(progress.record_best(s, 0, 12.34))
        self.assertEqual(progress.best_for(s, 0), 12.3)

    def test_slower_not_new_best(self):
        s = {}
        progress.record_best(s, 0, 10.0)
        self.assertFalse(progress.record_best(s, 0, 11.0))
        self.assertEqual(progress.best_for(s, 0), 10.0)

    def test_faster_replaces(self):
        s = {}
        progress.record_best(s, 0, 10.0)
        self.assertTrue(progress.record_best(s, 0, 9.0))
        self.assertEqual(progress.best_for(s, 0), 9.0)

    def test_levels_independent(self):
        s = {}
        progress.record_best(s, 0, 10.0)
        self.assertTrue(progress.record_best(s, 1, 50.0))
        self.assertEqual(progress.best_for(s, 0), 10.0)
        self.assertEqual(progress.best_for(s, 1), 50.0)

    def test_unset_is_zero(self):
        self.assertEqual(progress.best_for({}, 3), 0)


class TestMigrate(unittest.TestCase):
    def test_legacy_save(self):
        s = progress.migrate({"best": 14.2})
        self.assertEqual(progress.best_for(s, 0), 14.2)

    def test_empty_legacy(self):
        self.assertEqual(progress.best_for(progress.migrate({"best": 0}), 0), 0)

    def test_new_format_untouched(self):
        s = progress.migrate({"bests": {"1": 5.0}})
        self.assertEqual(progress.best_for(s, 1), 5.0)

    def test_empty_dict(self):
        self.assertEqual(progress.best_for(progress.migrate({}), 0), 0)


if __name__ == "__main__":
    unittest.main()
