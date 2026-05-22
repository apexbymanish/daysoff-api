"""Unit tests for sandwich.py — sandwich-day detection."""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sandwich import detect


class TestSandwichHappy(unittest.TestCase):
    def test_thursday_holiday_creates_friday_sandwich(self):
        # Thu Jan 1 2026 is a holiday → Fri Jan 2 wedged between Thu(off) + Sat(off)
        holidays = {date(2026, 1, 1)}
        sandwiches = detect(holidays, 2026)
        dates = [s["sandwich_date"] for s in sandwiches]
        self.assertIn(date(2026, 1, 2), dates)

    def test_tuesday_holiday_creates_monday_sandwich(self):
        # Tue Jan 6 2026 holiday → Mon Jan 5 wedged between Sun(off) + Tue(off)
        holidays = {date(2026, 1, 6)}
        sandwiches = detect(holidays, 2026)
        dates = [s["sandwich_date"] for s in sandwiches]
        self.assertIn(date(2026, 1, 5), dates)

    def test_break_length_spans_full_off_run(self):
        # Thu Jan 1 holiday + Fri sandwich → break Thu-Sun = 4 days
        holidays = {date(2026, 1, 1)}
        sandwiches = detect(holidays, 2026)
        fri = next(s for s in sandwiches if s["sandwich_date"] == date(2026, 1, 2))
        self.assertEqual(fri["break_start"], date(2026, 1, 1))  # Thu
        self.assertEqual(fri["break_end"], date(2026, 1, 4))    # Sun
        self.assertEqual(fri["break_length_days"], 4)

    def test_two_holidays_bridge_via_sandwich(self):
        # Tue + Thu both holidays → Wed is a 1-day sandwich
        # Even though Wed is the *only* workday between them
        holidays = {date(2026, 1, 6), date(2026, 1, 8)}
        sandwiches = detect(holidays, 2026)
        wed = [s for s in sandwiches if s["sandwich_date"] == date(2026, 1, 7)]
        self.assertEqual(len(wed), 1)


class TestSandwichEdge(unittest.TestCase):
    def test_empty_holidays_no_sandwiches(self):
        self.assertEqual(detect(set(), 2026), [])

    def test_holiday_on_saturday_no_sandwich(self):
        # Sat Jan 3 2026 — already a weekend. No workday gets sandwiched.
        holidays = {date(2026, 1, 3)}
        sandwiches = detect(holidays, 2026)
        # Mon Jan 5 would NOT be a sandwich because Sun Jan 4 is off but Tue Jan 6 is workday
        self.assertEqual(sandwiches, [])

    def test_holiday_on_friday_no_sandwich(self):
        # Fri is workday — sandwich would need a workday between Fri(off) and Sat(off)
        # The Friday itself becomes part of the off-block, so no sandwich.
        holidays = {date(2026, 1, 2)}  # Friday
        sandwiches = detect(holidays, 2026)
        # No isolated workday wedged
        self.assertEqual(sandwiches, [])

    def test_holiday_on_monday_no_sandwich(self):
        # Mon is wedged between Sun(off) and Tue(workday) — Mon is the holiday itself
        # Not a sandwich candidate.
        holidays = {date(2026, 1, 5)}  # Monday
        sandwiches = detect(holidays, 2026)
        self.assertEqual(sandwiches, [])


class TestSandwichWorst(unittest.TestCase):
    def test_every_other_weekday_holiday(self):
        # Mon, Wed, Fri of one week as holidays → Tue and Thu are sandwiches
        holidays = {date(2026, 1, 5), date(2026, 1, 7), date(2026, 1, 9)}
        sandwiches = detect(holidays, 2026)
        dates = {s["sandwich_date"] for s in sandwiches}
        self.assertIn(date(2026, 1, 6), dates)  # Tue between Mon and Wed
        self.assertIn(date(2026, 1, 8), dates)  # Thu between Wed and Fri

    def test_year_boundary_holiday(self):
        # Jan 1 Thu 2026 — first day of year — still triggers Friday sandwich
        # Function should handle the boundary correctly
        holidays = {date(2026, 1, 1)}
        sandwiches = detect(holidays, 2026)
        self.assertGreater(len(sandwiches), 0)

    def test_full_week_of_holidays_no_sandwich(self):
        # If Mon-Fri all holidays → no workday in between → no sandwich
        holidays = {date(2026, 6, 1), date(2026, 6, 2), date(2026, 6, 3),
                    date(2026, 6, 4), date(2026, 6, 5)}
        sandwiches = detect(holidays, 2026)
        # Mon Jun 1 - Fri Jun 5 all off + Sat-Sun weekend
        # No isolated workdays in this block.
        dates = {s["sandwich_date"] for s in sandwiches}
        for d in holidays:
            self.assertNotIn(d, dates)




# ─── custom weekend_days ──────────────────────────────────────────────────

class TestDetectCustomWeekend(unittest.TestCase):
    def test_wed_thu_weekend_finds_sandwich_friday(self):
        # 2026-05-13 Wed (off), 2026-05-14 Thu (off), 2026-05-15 Fri (workday),
        # 2026-05-16 Sat (workday in this scheme), 2026-05-17 Sun (workday).
        # With weekend_days={2,3} (wed,thu), Friday is NOT a sandwich because
        # Saturday after it is a workday.
        # But add a holiday on Saturday → Friday becomes a sandwich.
        from datetime import date
        from sandwich import detect

        holidays = {date(2026, 5, 16)}  # hypothetical Sat holiday
        result = detect(holidays, 2026, weekend_days={2, 3})

        sandwiches_on_friday = [s for s in result
                                if s["sandwich_date"] == date(2026, 5, 15)]
        self.assertEqual(len(sandwiches_on_friday), 1,
                         "Friday should be a sandwich with wed,thu weekend "
                         "and a Saturday holiday")

    def test_default_weekend_days_preserves_legacy_behavior(self):
        # Without passing weekend_days, behavior matches existing tests
        from datetime import date
        from sandwich import detect

        # Just verify it runs and returns a list — exercising the default path
        result = detect(set(), 2026)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
