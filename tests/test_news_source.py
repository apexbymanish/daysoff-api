"""Tests for sources/news_source.py (the dispatcher)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sources import news_source


class TestSupportedCountries(unittest.TestCase):
    def test_returns_kr_and_np(self):
        result = news_source.supported_countries()
        self.assertEqual(result, {"KR", "NP"})

    def test_returns_a_set(self):
        result = news_source.supported_countries()
        self.assertIsInstance(result, set)


if __name__ == "__main__":
    unittest.main()
