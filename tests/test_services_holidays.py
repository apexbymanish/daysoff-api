import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import services


class GetHolidaysLocalNameTest(unittest.TestCase):
    def test_kr_records_carry_non_ascii_name_local(self):
        recs = services.get_holidays("KR", 2026)
        self.assertTrue(recs, "expected KR holidays")
        self.assertTrue(all("name_local" in r for r in recs))
        # At least one localized name is present and non-ASCII (Korean).
        localized = [r["name_local"] for r in recs if r["name_local"]]
        self.assertTrue(localized, "expected at least one localized name")
        self.assertTrue(any(not n.isascii() for n in localized))

    def test_us_records_have_null_name_local(self):
        recs = services.get_holidays("US", 2026)
        self.assertTrue(recs, "expected US holidays")
        self.assertTrue(all(r["name_local"] is None for r in recs))


if __name__ == "__main__":
    unittest.main()
