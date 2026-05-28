"""Unit tests for planner.py algorithms: parse_workweek, best_single_break,
best_portfolio, classify_day, candidate_breaks.
"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from planner import (
    parse_workweek, daterange, candidate_breaks,
    best_single_break, best_portfolio, classify_day,
    visit_overlap,
    DEFAULT_LABELS,
)


# ─── parse_workweek ────────────────────────────────────────────────────────

class TestParseWorkweekHappy(unittest.TestCase):
    def test_standard(self):
        self.assertEqual(parse_workweek("sat,sun"), {5, 6})

    def test_single_day(self):
        self.assertEqual(parse_workweek("sat"), {5})

    def test_custom_combo_midweek(self):
        self.assertEqual(parse_workweek("wed,thu"), {2, 3})

    def test_non_contiguous(self):
        self.assertEqual(parse_workweek("sun,thu"), {3, 6})

    def test_all_seven_days(self):
        self.assertEqual(
            parse_workweek("mon,tue,wed,thu,fri,sat,sun"),
            {0, 1, 2, 3, 4, 5, 6},
        )


class TestParseWorkweekEdge(unittest.TestCase):
    def test_empty_string(self):
        # No off-days — 7-day workweek
        self.assertEqual(parse_workweek(""), set())

    def test_whitespace_tolerated(self):
        self.assertEqual(parse_workweek(" sat , sun "), {5, 6})

    def test_case_insensitive(self):
        self.assertEqual(parse_workweek("SAT,Sun"), {5, 6})

    def test_duplicates_dedup(self):
        self.assertEqual(parse_workweek("sat,sat,sun"), {5, 6})


class TestParseWorkweekFailure(unittest.TestCase):
    def test_invalid_day_raises_keyerror(self):
        with self.assertRaises(KeyError):
            parse_workweek("xyz")

    def test_partial_invalid_still_raises(self):
        with self.assertRaises(KeyError):
            parse_workweek("sat,bogus,sun")


# ─── daterange ────────────────────────────────────────────────────────────

class TestDaterange(unittest.TestCase):
    def test_normal_range(self):
        self.assertEqual(
            list(daterange(date(2026, 1, 1), date(2026, 1, 3))),
            [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)],
        )

    def test_single_day(self):
        self.assertEqual(
            list(daterange(date(2026, 1, 1), date(2026, 1, 1))),
            [date(2026, 1, 1)],
        )

    def test_reversed_returns_empty(self):
        self.assertEqual(
            list(daterange(date(2026, 1, 3), date(2026, 1, 1))),
            [],
        )


# ─── best_single_break ────────────────────────────────────────────────────

def _cand(start_str, end_str, cost, length, pto=None):
    return {
        "start": date.fromisoformat(start_str),
        "end": date.fromisoformat(end_str),
        "pto": pto or [],
        "cost": cost,
        "length": length,
    }


class TestBestSingleBreak(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(best_single_break([], budget=10))

    def test_picks_longest_within_budget(self):
        cands = [
            _cand("2026-01-01", "2026-01-05", cost=3, length=5),
            _cand("2026-02-01", "2026-02-10", cost=8, length=10),
            _cand("2026-03-01", "2026-03-20", cost=15, length=20),
        ]
        result = best_single_break(cands, budget=10)
        self.assertEqual(result["length"], 10)

    def test_zero_budget_picks_free_break(self):
        cands = [
            _cand("2026-01-01", "2026-01-02", cost=0, length=2),
            _cand("2026-02-01", "2026-02-05", cost=1, length=5),
        ]
        self.assertEqual(best_single_break(cands, budget=0)["cost"], 0)

    def test_negative_budget_returns_only_cost_zero(self):
        cands = [
            _cand("2026-01-01", "2026-01-02", cost=0, length=2),
            _cand("2026-02-01", "2026-02-05", cost=1, length=5),
        ]
        # Pathological: negative budget. Only cost=0 candidates affordable.
        self.assertIsNone(best_single_break(cands, budget=-1))

    def test_tie_break_prefers_lower_cost(self):
        cands = [
            _cand("2026-01-01", "2026-01-05", cost=5, length=5),
            _cand("2026-02-01", "2026-02-05", cost=2, length=5),
        ]
        result = best_single_break(cands, budget=10)
        # Same length; should prefer lower cost via secondary key (-cost)
        self.assertEqual(result["cost"], 2)


# ─── best_portfolio ──────────────────────────────────────────────────────

class TestBestPortfolio(unittest.TestCase):
    def test_empty_returns_empty(self):
        selected, value = best_portfolio([], budget=10)
        self.assertEqual(selected, [])
        self.assertEqual(value, 0)

    def test_two_non_overlapping_both_picked(self):
        cands = [
            _cand("2026-01-01", "2026-01-05", cost=2, length=5),
            _cand("2026-02-01", "2026-02-07", cost=3, length=7),
        ]
        selected, value = best_portfolio(cands, budget=10)
        self.assertEqual(len(selected), 2)
        self.assertEqual(value, 12)

    def test_overlapping_picks_better_value(self):
        cands = [
            _cand("2026-01-01", "2026-01-05", cost=2, length=5),
            _cand("2026-01-03", "2026-01-10", cost=3, length=8),
        ]
        selected, value = best_portfolio(cands, budget=10)
        self.assertEqual(len(selected), 1)
        self.assertEqual(value, 8)

    def test_budget_caps_selection(self):
        # 3 candidates of cost 5 each, budget 10 → can only fit 2
        cands = [
            _cand("2026-01-01", "2026-01-05", cost=5, length=5),
            _cand("2026-02-01", "2026-02-05", cost=5, length=5),
            _cand("2026-03-01", "2026-03-05", cost=5, length=5),
        ]
        selected, value = best_portfolio(cands, budget=10)
        self.assertEqual(len(selected), 2)
        self.assertEqual(value, 10)

    def test_zero_budget_returns_empty(self):
        cands = [_cand("2026-01-01", "2026-01-05", cost=2, length=5)]
        selected, value = best_portfolio(cands, budget=0)
        self.assertEqual(selected, [])
        self.assertEqual(value, 0)

    def test_excludes_zero_cost_candidates(self):
        # Free candidates aren't included in portfolio (they're added for free)
        cands = [_cand("2026-01-01", "2026-01-05", cost=0, length=5)]
        selected, value = best_portfolio(cands, budget=10)
        self.assertEqual(selected, [])


class TestBestPortfolioWorstCases(unittest.TestCase):
    """Pathological scaling and edge cases."""

    def test_single_huge_break_over_budget(self):
        cands = [_cand("2026-01-01", "2026-12-31", cost=200, length=365)]
        selected, value = best_portfolio(cands, budget=10)
        self.assertEqual(selected, [])
        self.assertEqual(value, 0)

    def test_many_identical_overlapping_candidates(self):
        # 20 candidates all overlapping with same metrics
        # Use safe date arithmetic via timedelta to avoid month-boundary bugs
        from datetime import timedelta
        base = date(2026, 6, 1)
        cands = []
        for i in range(20):
            start = base + timedelta(days=i)
            end = start + timedelta(days=4)
            cands.append({
                "start": start, "end": end, "pto": [],
                "cost": 2, "length": 5,
            })
        selected, value = best_portfolio(cands, budget=2)
        # Each costs 2 and budget is 2 → can fit at most 1
        self.assertLessEqual(sum(c["cost"] for c in selected), 2)
        self.assertLessEqual(len(selected), 1)


# ─── classify_day ────────────────────────────────────────────────────────

class TestClassifyDay(unittest.TestCase):
    def test_workday(self):
        label = classify_day(
            date(2026, 5, 14),  # Thu, not off
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("workday", label)

    def test_pto_day(self):
        label = classify_day(
            date(2026, 5, 14),
            pto_set={date(2026, 5, 14)},
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("PTO", label)

    def test_weekend(self):
        label = classify_day(
            date(2026, 5, 16),  # Sat
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("weekend", label)

    def test_red_day_overrides_weekend(self):
        # If both red day AND weekend, both shown? Implementation shows OFFICE HOLIDAY,
        # skips "weekend" tag when also red.
        label = classify_day(
            date(2026, 5, 16),  # Sat
            pto_set=set(),
            red_days={date(2026, 5, 16): "Hypothetical"},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("OFFICE HOLIDAY", label)
        self.assertNotIn("weekend", label)

    def test_double_tag_pto_and_festival(self):
        label = classify_day(
            date(2026, 5, 8),  # Fri (workday)
            pto_set={date(2026, 5, 8)},
            red_days={},
            festivals={date(2026, 5, 8): {
                "name_en": "Parents' Day", "name_ko": "어버이날",
            }},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("PTO", label)
        self.assertIn("Parents' Day", label)


# ─── candidate_breaks ────────────────────────────────────────────────────

class TestCandidateBreaks(unittest.TestCase):
    def test_no_off_days_in_short_year_window(self):
        # Use a small slice via max_break_len=3 to keep test fast.
        # With no off-days, every consecutive window of workdays starting on a
        # workday with workday-or-boundary on each side is a candidate.
        result = candidate_breaks(2026, set(), budget=5, max_break_len=3)
        # Should produce candidates (each costs its full length)
        self.assertGreater(len(result), 0)
        # All candidates should have cost == length (no off-days inside)
        for c in result:
            self.assertEqual(c["cost"], c["length"])

    def test_cost_never_exceeds_budget(self):
        off = {date(2026, 1, 3), date(2026, 1, 4)}  # weekend-ish
        result = candidate_breaks(2026, off, budget=2, max_break_len=10)
        for c in result:
            self.assertLessEqual(c["cost"], 2)


# ─── classify_day with visit-country overlay ─────────────────────────────

class TestClassifyDayVisit(unittest.TestCase):
    def test_visit_red_day_adds_overlay_tag(self):
        # Workday in home country that is a red day in visit country
        label = classify_day(
            date(2026, 10, 12),  # Mon — home workday
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
            visit_red_days={date(2026, 10, 12): "Dashain"},
            visit_country="NP",
        )
        self.assertIn("LOCAL HOLIDAY", label)
        self.assertIn("Dashain", label)
        self.assertIn("NP", label)

    def test_visit_overlay_does_not_replace_primary_tag(self):
        # PTO day that is also red in visit country → both tags
        label = classify_day(
            date(2026, 10, 12),
            pto_set={date(2026, 10, 12)},
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
            visit_red_days={date(2026, 10, 12): "Dashain"},
            visit_country="NP",
        )
        self.assertIn("PTO", label)
        self.assertIn("LOCAL HOLIDAY", label)
        self.assertIn("Dashain", label)

    def test_no_overlay_when_visit_red_days_empty(self):
        label = classify_day(
            date(2026, 10, 12),
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
            visit_red_days={},
            visit_country="NP",
        )
        self.assertNotIn("LOCAL HOLIDAY", label)

    def test_omitted_visit_args_preserve_legacy_behavior(self):
        # Calling classify_day without the new kwargs must still work
        label = classify_day(
            date(2026, 5, 14),
            pto_set=set(),
            red_days={},
            festivals={},
            weekend_days={5, 6},
            labels=DEFAULT_LABELS,
        )
        self.assertIn("workday", label)
        self.assertNotIn("LOCAL HOLIDAY", label)


# ─── visit_overlap ───────────────────────────────────────────────────────

class TestVisitOverlap(unittest.TestCase):
    def _trip(self, start_str, end_str):
        return {
            "start": date.fromisoformat(start_str),
            "end": date.fromisoformat(end_str),
            "pto": [], "cost": 0, "length": 1,
        }

    def test_no_visit_red_days_returns_empty(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        self.assertEqual(visit_overlap(trip, {}), [])

    def test_returns_only_dates_inside_trip(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        visit_red = {
            date(2026, 10, 9): "Before",
            date(2026, 10, 12): "Dashain",
            date(2026, 10, 13): "Vijaya Dashami",
            date(2026, 10, 16): "After",
        }
        result = visit_overlap(trip, visit_red)
        self.assertEqual(
            result,
            [(date(2026, 10, 12), "Dashain"),
             (date(2026, 10, 13), "Vijaya Dashami")],
        )

    def test_inclusive_at_both_endpoints(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        visit_red = {
            date(2026, 10, 10): "Start",
            date(2026, 10, 15): "End",
        }
        result = visit_overlap(trip, visit_red)
        self.assertEqual(
            result,
            [(date(2026, 10, 10), "Start"),
             (date(2026, 10, 15), "End")],
        )

    def test_sorted_by_date(self):
        trip = self._trip("2026-10-10", "2026-10-15")
        visit_red = {
            date(2026, 10, 14): "Later",
            date(2026, 10, 11): "Earlier",
        }
        result = visit_overlap(trip, visit_red)
        self.assertEqual([d for d, _ in result],
                         [date(2026, 10, 11), date(2026, 10, 14)])


if __name__ == "__main__":
    unittest.main()
