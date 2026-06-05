import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sources import library_source


class LibrarySourceLocalizedTest(unittest.TestCase):
    def test_kr_records_have_korean_name_local(self):
        recs = library_source.fetch(2026, "KR")
        self.assertTrue(recs, "expected KR holidays")
        self.assertTrue(all("name_local" in r for r in recs))
        seollal = next(r for r in recs if r["date"].isoformat() == "2026-02-17")
        self.assertEqual(seollal["name_local"], "설날")

    def test_us_name_local_is_none(self):
        recs = library_source.fetch(2026, "US")
        self.assertTrue(recs, "expected US holidays")
        self.assertTrue(all(r["name_local"] is None for r in recs))


if __name__ == "__main__":
    unittest.main()
