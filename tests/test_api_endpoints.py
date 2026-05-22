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


if __name__ == "__main__":
    unittest.main()
