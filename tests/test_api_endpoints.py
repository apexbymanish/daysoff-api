"""Endpoint-level tests for the daysoff-api FastAPI service."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from api.main import API_VERSION, app


class TestHealthz(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_returns_200_and_status_ok(self):
        r = self.client.get("/v1/healthz")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["version"], API_VERSION)


class TestCountries(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_returns_200_with_non_empty_list(self):
        r = self.client.get("/v1/countries")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertGreater(body["count"], 100)
        self.assertEqual(len(body["countries"]), body["count"])

    def test_kr_and_np_flagged_news_enriched(self):
        r = self.client.get("/v1/countries")
        by_code = {c["code"]: c for c in r.json()["countries"]}
        self.assertTrue(by_code["KR"]["news_enriched"])
        self.assertTrue(by_code["NP"]["news_enriched"])

    def test_ph_not_news_enriched(self):
        r = self.client.get("/v1/countries")
        by_code = {c["code"]: c for c in r.json()["countries"]}
        self.assertFalse(by_code["PH"]["news_enriched"])

    def test_uses_static_name_map(self):
        # KR is in our hand-curated COUNTRY_NAMES map
        r = self.client.get("/v1/countries")
        by_code = {c["code"]: c for c in r.json()["countries"]}
        self.assertEqual(by_code["KR"]["name"], "South Korea")


class TestHolidays(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_kr_2026_returns_known_holidays(self):
        r = self.client.get("/v1/holidays?country=KR&year=2026")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["country"], "KR")
        self.assertEqual(body["year"], 2026)
        self.assertGreater(body["count"], 10)
        dates = [h["date"] for h in body["holidays"]]
        self.assertIn("2026-01-01", dates)  # New Year's Day always present

    def test_holidays_sorted_by_date(self):
        r = self.client.get("/v1/holidays?country=KR&year=2026")
        dates = [h["date"] for h in r.json()["holidays"]]
        self.assertEqual(dates, sorted(dates))

    def test_from_today_filters_past_dates(self):
        # With from_today=true and a past year, every date should already be past
        r = self.client.get("/v1/holidays?country=KR&year=2024&from_today=true")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 0)

    def test_unsupported_country_returns_400(self):
        r = self.client.get("/v1/holidays?country=ZZ&year=2026")
        self.assertEqual(r.status_code, 400)
        self.assertIn("ZZ", r.json()["detail"])

    def test_missing_country_returns_422(self):
        # FastAPI returns 422 for missing required query params by default
        r = self.client.get("/v1/holidays?year=2026")
        self.assertEqual(r.status_code, 422)

    def test_bad_year_returns_400(self):
        r = self.client.get("/v1/holidays?country=KR&year=1800")
        self.assertEqual(r.status_code, 400)

    def test_kr_holidays_include_korean_name_local(self):
        r = self.client.get("/v1/holidays?country=KR&year=2026")
        self.assertEqual(r.status_code, 200)
        hols = r.json()["holidays"]
        self.assertTrue(all("name_local" in h for h in hols))
        self.assertTrue(any(h.get("name_local") == "설날" for h in hols))

    def test_us_holidays_name_local_null(self):
        r = self.client.get("/v1/holidays?country=US&year=2026")
        self.assertEqual(r.status_code, 200)
        hols = r.json()["holidays"]
        self.assertTrue(all(h["name_local"] is None for h in hols))


class TestCompare(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_kr_np_2026_has_shared_christmas(self):
        r = self.client.get("/v1/compare?countries=KR,NP&year=2026")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        shared_dates = [s["date"] for s in body["shared"]]
        self.assertIn("2026-12-25", shared_dates)

    def test_kr_unique_dates_present(self):
        r = self.client.get("/v1/compare?countries=KR,NP&year=2026")
        kr_only_names = " ".join(h["name"] for h in r.json()["only"]["KR"])
        self.assertIn("Chuseok", kr_only_names)

    def test_np_unique_dates_present(self):
        r = self.client.get("/v1/compare?countries=KR,NP&year=2026")
        np_only_names = " ".join(h["name"] for h in r.json()["only"]["NP"])
        self.assertIn("Dashain", np_only_names)

    def test_single_country_returns_400(self):
        r = self.client.get("/v1/compare?countries=KR&year=2026")
        self.assertEqual(r.status_code, 400)
        self.assertIn("at least 2", r.json()["detail"])

    def test_unsupported_member_returns_400(self):
        r = self.client.get("/v1/compare?countries=KR,ZZ&year=2026")
        self.assertEqual(r.status_code, 400)
        self.assertIn("ZZ", r.json()["detail"])

    def test_three_country_intersection(self):
        # Christmas should be shared in any 3-way containing countries that
        # observe it. Use KR, GB, US — all have Christmas (Dec 25).
        r = self.client.get("/v1/compare?countries=KR,GB,US&year=2026")
        self.assertEqual(r.status_code, 200)
        shared_dates = [s["date"] for s in r.json()["shared"]]
        self.assertIn("2026-12-25", shared_dates)


class TestSandwiches(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_kr_2026_with_explicit_workweek(self):
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["country"], "KR")
        self.assertEqual(body["workweek"], ["sat", "sun"])
        self.assertGreater(body["count"], 0)
        for s in body["sandwiches"]:
            # Default endpoint bridges cost 1..3 PTO; pto_dates lists each day.
            self.assertGreaterEqual(s["pto_cost"], 1)
            self.assertLessEqual(s["pto_cost"], 3)
            self.assertEqual(len(s["pto_dates"]), s["pto_cost"])
            self.assertEqual(s["pto_dates"][0], s["pto_date"])
            self.assertIn("break_start", s)
            self.assertIn("break_end", s)
            self.assertIn("break_length", s)
            self.assertIn("context", s)

    def test_sandwiches_sorted_by_efficiency(self):
        # Best deal (most days off per PTO day) first.
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun"
        )
        effs = [s["break_length"] / s["pto_cost"]
                for s in r.json()["sandwiches"]]
        for prev, curr in zip(effs, effs[1:]):
            self.assertGreaterEqual(prev, curr)

    def test_max_pto_one_returns_only_single_day_sandwiches(self):
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun&max_pto=1"
        )
        self.assertEqual(r.status_code, 200)
        for s in r.json()["sandwiches"]:
            self.assertEqual(s["pto_cost"], 1)

    def test_default_surfaces_multi_pto_bridge(self):
        # KR 2026 has a 2-PTO Lunar New Year bridge (take Feb 19 + 20).
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun"
        )
        self.assertTrue(any(s["pto_cost"] >= 2 for s in r.json()["sandwiches"]))

    def test_invalid_max_pto_returns_400(self):
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun&max_pto=0"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("max_pto", r.json()["detail"].lower())

    def test_budget_filters_out_unaffordable_bridges(self):
        # With budget=1, no bridge costing more than 1 PTO may appear.
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun&budget=1"
        )
        self.assertEqual(r.status_code, 200)
        costs = [s["pto_cost"] for s in r.json()["sandwiches"]]
        self.assertTrue(costs)  # some 1-PTO sandwiches still exist
        self.assertTrue(all(c <= 1 for c in costs))

    def test_break_length_range_filters_bridges(self):
        # max_length=4 keeps only short bridges; the 9-day Lunar New Year
        # bridge (2 PTO) must be excluded.
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun&max_length=4"
        )
        self.assertEqual(r.status_code, 200)
        lengths = [s["break_length"] for s in r.json()["sandwiches"]]
        self.assertTrue(all(le <= 4 for le in lengths))

    def test_budget_zero_returns_no_bridges(self):
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=sat,sun&budget=0"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 0)

    def test_invalid_workweek_returns_400(self):
        r = self.client.get(
            "/v1/sandwiches?country=KR&year=2026&workweek=xyz,bogus"
        )
        self.assertEqual(r.status_code, 400)

    def test_unsupported_country_returns_400(self):
        r = self.client.get(
            "/v1/sandwiches?country=ZZ&year=2026&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 400)

    def test_missing_workweek_with_no_policy_returns_400(self):
        # AQ (Antarctica) has no policy in storage, no fallback in
        # WORKWEEK_FALLBACKS — should 400 with a clear message.
        r = self.client.get("/v1/sandwiches?country=AQ&year=2026")
        self.assertEqual(r.status_code, 400)
        self.assertIn("workweek", r.json()["detail"].lower())


class TestPlan(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_menu_view_returns_one_per_length_in_range(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=3&max_length=7&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["country"], "KR")
        self.assertEqual(body["year"], 2026)
        self.assertEqual(body["budget"], 15)
        self.assertEqual(body["workweek"], ["sat", "sun"])
        # range 3..7 = 5 lengths, each capped at top=1 (default)
        self.assertEqual(
            sorted(body["results_by_length"].keys()),
            ["3", "4", "5", "6", "7"],
        )
        for length_key, entries in body["results_by_length"].items():
            self.assertLessEqual(len(entries), 1)
            for trip in entries:
                self.assertEqual(trip["break_length"], int(length_key))
                self.assertIn("break_start", trip)
                self.assertIn("break_end", trip)
                self.assertIn("pto_dates", trip)
                self.assertIn("pto_cost", trip)
                self.assertIn("anchors", trip)

    def test_single_length_with_top_returns_alternatives(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&length=5&top=5&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        # Only key "5" is present, ignoring min/max defaults.
        self.assertEqual(list(body["results_by_length"].keys()), ["5"])
        entries = body["results_by_length"]["5"]
        self.assertLessEqual(len(entries), 5)
        self.assertGreater(len(entries), 0)
        for trip in entries:
            self.assertEqual(trip["break_length"], 5)

    def test_alternatives_sorted_by_pto_cost_ascending(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&length=5&top=5&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        entries = r.json()["results_by_length"]["5"]
        if len(entries) < 2:
            self.skipTest("need at least 2 alternatives to compare sort order")
        for prev, curr in zip(entries, entries[1:]):
            self.assertLessEqual(prev["pto_cost"], curr["pto_cost"])
            if prev["pto_cost"] == curr["pto_cost"]:
                # tie-break: earlier break_start first
                self.assertLessEqual(prev["break_start"], curr["break_start"])

    def test_pto_dates_consistent_with_cost(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=3&max_length=10&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        for entries in r.json()["results_by_length"].values():
            for trip in entries:
                self.assertEqual(len(trip["pto_dates"]), trip["pto_cost"])

    def test_anchors_present_when_break_spans_holiday(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&length=5&top=10&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        entries = r.json()["results_by_length"]["5"]
        any_chuseok = any(
            any("Chuseok" in a for a in trip["anchors"])
            for trip in entries
        )
        self.assertTrue(
            any_chuseok,
            f"expected at least one length-5 trip with a Chuseok anchor; "
            f"got entries={entries}",
        )

    def test_month_filter_anchors_every_result_to_that_month(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=3&max_length=10&month=9&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        # With month=9, every returned break must START in September.
        for entries in body["results_by_length"].values():
            for trip in entries:
                self.assertEqual(
                    trip["break_start"][:7], "2026-09",
                    f"trip does not start in September: {trip}",
                )

    def test_month_filter_surfaces_longer_chuseok_bridge(self):
        # Globally the cheapest length-7 break is elsewhere (Korean New Year in
        # February), so the default (month-less) menu never shows a 7-day
        # September option. Anchored to month=9 the length-7 result must be a
        # Chuseok bridge (Sep 22 -> Sep 28, 3 PTO: Tue 22 + Wed 23 + Mon 28).
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=3&max_length=10&month=9&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 200)
        seven = r.json()["results_by_length"]["7"]
        self.assertTrue(seven, "expected a length-7 September break")
        trip = seven[0]
        self.assertEqual(trip["break_start"], "2026-09-22")
        self.assertEqual(trip["break_end"], "2026-09-28")
        self.assertEqual(trip["pto_cost"], 3)
        self.assertTrue(
            any("Chuseok" in a for a in trip["anchors"]),
            f"expected a Chuseok anchor; got {trip['anchors']}",
        )

    def test_invalid_month_returns_400(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&month=13&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("month", r.json()["detail"].lower())

    def test_unsupported_country_returns_400(self):
        r = self.client.get(
            "/v1/plan?country=ZZ&year=2026&budget=15&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("ZZ", r.json()["detail"])

    def test_min_greater_than_max_returns_400(self):
        r = self.client.get(
            "/v1/plan?country=KR&year=2026&budget=15"
            "&min_length=10&max_length=5&workweek=sat,sun"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("min_length", r.json()["detail"])

    def test_no_workweek_with_no_policy_returns_400(self):
        # AQ has no saved policy and no entry in WORKWEEK_FALLBACKS.
        r = self.client.get(
            "/v1/plan?country=AQ&year=2026&budget=15"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("workweek", r.json()["detail"].lower())


if __name__ == "__main__":
    unittest.main()
