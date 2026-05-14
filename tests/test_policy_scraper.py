"""Unit tests for sources/policy_scraper.py — workweek pattern matching.

Only tests pure logic (_detect_workweek). The live `fetch()` makes network
calls and is left for integration tests.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sources import policy_scraper


class TestDetectWorkweekHappy(unittest.TestCase):
    def test_saturday_and_sunday(self):
        result = policy_scraper._detect_workweek(
            "Cabinet decision: Saturday and Sunday as weekly holiday"
        )
        self.assertEqual(result, ("sat,sun", "high"))

    def test_two_day_weekend(self):
        result = policy_scraper._detect_workweek(
            "Government announces two-day weekly holiday"
        )
        self.assertEqual(result[0], "sat,sun")

    def test_friday_and_saturday(self):
        result = policy_scraper._detect_workweek(
            "Friday and Saturday as official weekend declared"
        )
        self.assertEqual(result, ("fri,sat", "high"))

    def test_saturday_only(self):
        result = policy_scraper._detect_workweek(
            "Saturday-only weekly holiday remains for civil servants"
        )
        self.assertEqual(result, ("sat", "high"))

    def test_six_day_workweek(self):
        result = policy_scraper._detect_workweek(
            "Country still operates a six-day workweek for government"
        )
        self.assertEqual(result, ("sat", "medium"))

    def test_sunday_through_thursday(self):
        result = policy_scraper._detect_workweek(
            "Offices work Sunday through Thursday under new rules"
        )
        self.assertEqual(result, ("fri,sat", "high"))


class TestDetectWorkweekNoMatch(unittest.TestCase):
    def test_unrelated_text(self):
        self.assertIsNone(policy_scraper._detect_workweek(
            "Stock market closes higher amid economic news"
        ))

    def test_empty_string(self):
        self.assertIsNone(policy_scraper._detect_workweek(""))

    def test_only_holiday_announcement_not_workweek(self):
        self.assertIsNone(policy_scraper._detect_workweek(
            "Government declares Oct 28 a public holiday for Chhath"
        ))


class TestRegexPatterns(unittest.TestCase):
    """Probe the regexes directly to catch subtle pattern bugs."""

    def test_confirm_re_matches_decisions(self):
        for word in ["announced", "declared", "approved", "cabinet decision",
                     "implemented", "introduced", "reintroduce", "adopted",
                     "gazetted"]:
            self.assertIsNotNone(
                policy_scraper.CONFIRM_RE.search(f"Govt {word} new rule"),
                f"CONFIRM_RE missed: {word}",
            )

    def test_negate_re_matches_proposals(self):
        for word in ["proposal", "considering", "debate", "rejected",
                     "withdrawn", "may", "might", "could"]:
            self.assertIsNotNone(
                policy_scraper.NEGATE_RE.search(f"Govt {word} the new rule"),
                f"NEGATE_RE missed: {word}",
            )


class TestDetectWorkweekWorst(unittest.TestCase):
    def test_multiple_patterns_in_one_blob_picks_first(self):
        # If a blob matches multiple patterns, first match wins (iteration order)
        text = ("Cabinet announces five-day workweek with Saturday and Sunday "
                "as weekly holiday")
        result = policy_scraper._detect_workweek(text)
        # "saturday and sunday" pattern is higher in PATTERNS list, so wins
        self.assertEqual(result, ("sat,sun", "high"))

    def test_very_long_text(self):
        # 10kB of irrelevant text + one matching phrase
        text = ("lorem ipsum " * 1000) + " two-day weekly holiday announced"
        result = policy_scraper._detect_workweek(text)
        self.assertIsNotNone(result)

    def test_case_insensitive(self):
        result = policy_scraper._detect_workweek(
            "SATURDAY AND SUNDAY AS WEEKLY HOLIDAY"
        )
        self.assertEqual(result[0], "sat,sun")


class TestFetchEarlyReturn(unittest.TestCase):
    def test_unsupported_country_returns_empty(self):
        # XX has no entry in COUNTRY_QUERIES → empty list, no network call
        self.assertEqual(policy_scraper.fetch("XX"), [])


if __name__ == "__main__":
    unittest.main()
