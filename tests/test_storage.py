"""Unit tests for storage.py — SQLite persistence."""
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import storage


class TempDBTestCase(unittest.TestCase):
    """Base class that swaps storage.DB_PATH to a temp file."""
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test.db"
        self.patcher = patch.object(storage, "DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmpdir.cleanup()


class TestHolidayUpsert(TempDBTestCase):
    def test_first_insert_marked_new(self):
        rec = {"date": date(2026, 1, 1), "name": "New Year",
               "country": "KR", "source": "library"}
        new = storage.upsert([rec])
        self.assertEqual(len(new), 1)

    def test_duplicate_insert_not_marked_new(self):
        rec = {"date": date(2026, 1, 1), "name": "New Year",
               "country": "KR", "source": "library"}
        storage.upsert([rec])
        new2 = storage.upsert([rec])
        self.assertEqual(len(new2), 0)

    def test_same_date_different_source_is_new(self):
        rec1 = {"date": date(2026, 1, 1), "name": "New Year",
                "country": "KR", "source": "library"}
        rec2 = {"date": date(2026, 1, 1), "name": "New Year",
                "country": "KR", "source": "news"}
        storage.upsert([rec1])
        new = storage.upsert([rec2])
        self.assertEqual(len(new), 1)


class TestResolveWorkweek(TempDBTestCase):
    def test_no_data_returns_none(self):
        self.assertIsNone(storage.resolve_workweek("XX", date(2026, 1, 1)))

    def test_picks_most_recent_effective_date(self):
        storage.upsert_workweek_policies([
            {"country": "NP", "effective_date": date(2026, 1, 1),
             "weekend_spec": "sat", "source": "news", "confidence": "high",
             "headline": "old", "link": "x"},
            {"country": "NP", "effective_date": date(2026, 4, 5),
             "weekend_spec": "sat,sun", "source": "news", "confidence": "high",
             "headline": "new", "link": "y"},
        ])
        # Target after both effective dates → newest
        self.assertEqual(
            storage.resolve_workweek("NP", date(2026, 5, 1))["weekend_spec"],
            "sat,sun",
        )
        # Target between → only older applies
        self.assertEqual(
            storage.resolve_workweek("NP", date(2026, 2, 1))["weekend_spec"],
            "sat",
        )

    def test_future_only_policy_excluded(self):
        storage.upsert_workweek_policies([{
            "country": "NP", "effective_date": date(2026, 6, 1),
            "weekend_spec": "sat,sun", "source": "news", "confidence": "high",
            "headline": "future", "link": "z",
        }])
        # Target is BEFORE the policy's effective date → no result
        self.assertIsNone(storage.resolve_workweek("NP", date(2026, 1, 1)))

    def test_country_isolation(self):
        storage.upsert_workweek_policies([{
            "country": "NP", "effective_date": date(2026, 1, 1),
            "weekend_spec": "sat,sun", "source": "news", "confidence": "high",
            "headline": "x", "link": "y",
        }])
        # JP has nothing on record even though NP does
        self.assertIsNone(storage.resolve_workweek("JP", date(2026, 5, 1)))


class TestLatestPolicyAge(TempDBTestCase):
    def test_no_data_returns_none(self):
        self.assertIsNone(storage.latest_policy_age_days("XX"))

    def test_age_is_zero_when_just_inserted(self):
        storage.upsert_workweek_policies([{
            "country": "NP", "effective_date": date(2025, 1, 1),
            "weekend_spec": "sat", "source": "news", "confidence": "high",
            "headline": "x", "link": "y",
        }])
        # first_seen is today
        self.assertEqual(storage.latest_policy_age_days("NP"), 0)


class TestWorkweekPolicyUpsertWorst(TempDBTestCase):
    def test_idempotent_under_repeated_insert(self):
        rec = {"country": "NP", "effective_date": date(2026, 4, 5),
               "weekend_spec": "sat,sun", "source": "news", "confidence": "high",
               "headline": "x", "link": "y"}
        n1 = storage.upsert_workweek_policies([rec])
        n2 = storage.upsert_workweek_policies([rec])
        n3 = storage.upsert_workweek_policies([rec])
        self.assertEqual(len(n1), 1)
        self.assertEqual(len(n2), 0)
        self.assertEqual(len(n3), 0)

    def test_large_batch(self):
        recs = [
            {"country": "NP", "effective_date": date(2026, 1, 1) + timedelta(days=i),
             "weekend_spec": "sat,sun", "source": "news", "confidence": "high",
             "headline": f"h{i}", "link": f"l{i}"}
            for i in range(100)
        ]
        new = storage.upsert_workweek_policies(recs)
        self.assertEqual(len(new), 100)


if __name__ == "__main__":
    unittest.main()
