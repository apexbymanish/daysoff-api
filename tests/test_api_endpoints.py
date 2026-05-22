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


if __name__ == "__main__":
    unittest.main()
