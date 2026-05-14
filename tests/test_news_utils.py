"""Unit tests for sources/_news_utils.py — year resolution for bare dates."""
import sys
import time
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from sources._news_utils import entry_pub_date, resolve_year_for_bare_date


class TestEntryPubDate(unittest.TestCase):
    def test_published_parsed_present(self):
        e = MagicMock()
        e.get.side_effect = lambda k: {
            "published_parsed": time.struct_time((2026, 5, 14, 0, 0, 0, 0, 0, 0)),
            "updated_parsed": None,
        }.get(k)
        self.assertEqual(entry_pub_date(e), date(2026, 5, 14))

    def test_falls_back_to_updated_parsed(self):
        e = MagicMock()
        e.get.side_effect = lambda k: {
            "published_parsed": None,
            "updated_parsed": time.struct_time((2026, 3, 1, 0, 0, 0, 0, 0, 0)),
        }.get(k)
        self.assertEqual(entry_pub_date(e), date(2026, 3, 1))

    def test_no_date_returns_none(self):
        e = MagicMock()
        e.get.return_value = None
        self.assertIsNone(entry_pub_date(e))


class TestResolveYearHappy(unittest.TestCase):
    def test_pub_date_near_parsed_date_picks_same_year(self):
        # Article pub May 10 2026, holiday mentioned "May 14" → 2026
        self.assertEqual(
            resolve_year_for_bare_date(5, 14, date(2026, 5, 10), 9999),
            2026,
        )

    def test_late_year_january_ref_wraps_to_next_year(self):
        # Pub Dec 15 2026, mentions "January 3" → 2027 (closer than 2026-01-03)
        self.assertEqual(
            resolve_year_for_bare_date(1, 3, date(2026, 12, 15), 9999),
            2027,
        )

    def test_early_year_december_ref_picks_previous(self):
        # Pub Jan 5 2026, mentions "December 25" → 2025 (closer than 2026-12-25)
        self.assertEqual(
            resolve_year_for_bare_date(12, 25, date(2026, 1, 5), 9999),
            2025,
        )


class TestResolveYearEdge(unittest.TestCase):
    def test_no_pub_date_uses_fallback(self):
        self.assertEqual(
            resolve_year_for_bare_date(5, 14, None, fallback_year=2026),
            2026,
        )

    def test_feb_29_in_non_leap_years_falls_back(self):
        # 2025, 2026, 2027 are all non-leap. None have Feb 29.
        # Function should return fallback_year (which may itself be invalid).
        result = resolve_year_for_bare_date(2, 29, date(2026, 3, 1),
                                            fallback_year=2024)
        # When no candidates produce valid dates, return fallback
        self.assertEqual(result, 2024)

    def test_pub_exactly_on_holiday_date(self):
        self.assertEqual(
            resolve_year_for_bare_date(5, 14, date(2026, 5, 14), 9999),
            2026,
        )


class TestResolveYearWorst(unittest.TestCase):
    def test_pub_date_year_2100(self):
        # Far-future pub date should still pick that year
        self.assertEqual(
            resolve_year_for_bare_date(7, 4, date(2100, 6, 1), 1900),
            2100,
        )

    def test_pub_date_year_1900(self):
        # Far past
        self.assertEqual(
            resolve_year_for_bare_date(7, 4, date(1900, 6, 1), 2026),
            1900,
        )


if __name__ == "__main__":
    unittest.main()
