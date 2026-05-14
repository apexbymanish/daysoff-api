"""Unit tests for config.py (JSON backend + module facade)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config


class TestJsonBackendHappyPath(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "config.json"
        self.backend = config.JsonBackend(path=self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load_when_no_file_returns_empty(self):
        self.assertEqual(self.backend.load("default"), {})

    def test_save_then_load_roundtrip(self):
        self.backend.save({"budget": 15}, "default")
        self.assertEqual(self.backend.load("default"), {"budget": 15})

    def test_subsequent_save_merges_keys(self):
        self.backend.save({"budget": 15}, "default")
        self.backend.save({"country": "KR"}, "default")
        self.assertEqual(
            self.backend.load("default"),
            {"budget": 15, "country": "KR"},
        )

    def test_nested_dict_keys_merge(self):
        self.backend.save({"workweeks": {"KR": "sat,sun"}}, "default")
        self.backend.save({"workweeks": {"NP": "sat"}}, "default")
        self.assertEqual(
            self.backend.load("default")["workweeks"],
            {"KR": "sat,sun", "NP": "sat"},
        )

    def test_multi_user_isolation(self):
        self.backend.save({"budget": 15}, "alice")
        self.backend.save({"budget": 99}, "bob")
        self.assertEqual(self.backend.load("alice")["budget"], 15)
        self.assertEqual(self.backend.load("bob")["budget"], 99)
        # Cross-user reads return empty
        self.assertEqual(self.backend.load("carol"), {})


class TestJsonBackendEdgeCases(unittest.TestCase):
    """Failed inputs / unusual scenarios."""
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "config.json"
        self.backend = config.JsonBackend(path=self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_none_values_are_skipped(self):
        self.backend.save({"budget": 15}, "default")
        # Saving budget=None should NOT wipe existing budget
        self.backend.save({"budget": None, "country": "KR"}, "default")
        self.assertEqual(self.backend.load("default")["budget"], 15)
        self.assertEqual(self.backend.load("default")["country"], "KR")

    def test_corrupted_json_returns_empty(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{ not valid json at all")
        self.assertEqual(self.backend.load("default"), {})

    def test_empty_json_file_returns_empty(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("")
        self.assertEqual(self.backend.load("default"), {})

    def test_file_has_chmod_600_after_save(self):
        self.backend.save({"budget": 15}, "default")
        mode = self.path.stat().st_mode & 0o777
        # Only owner read/write
        self.assertEqual(mode, 0o600)

    def test_overwrite_existing_key_keeps_value(self):
        self.backend.save({"budget": 15}, "default")
        self.backend.save({"budget": 20}, "default")
        self.assertEqual(self.backend.load("default")["budget"], 20)

    def test_empty_updates_dict_is_noop(self):
        self.backend.save({"budget": 15}, "default")
        self.backend.save({}, "default")
        self.assertEqual(self.backend.load("default"), {"budget": 15})


class TestJsonBackendWorstCases(unittest.TestCase):
    """Pathological inputs."""
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "config.json"
        self.backend = config.JsonBackend(path=self.path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_unicode_user_id_and_values(self):
        self.backend.save({"country": "한국", "workweek": "토,일"}, "사용자1")
        self.assertEqual(self.backend.load("사용자1")["country"], "한국")

    def test_very_large_workweeks_dict(self):
        # Simulate 100 countries' workweeks saved at once
        big = {f"C{i:02d}": "sat,sun" for i in range(100)}
        self.backend.save({"workweeks": big}, "default")
        self.assertEqual(len(self.backend.load("default")["workweeks"]), 100)

    def test_deeply_nested_structures_not_merged_below_top_level(self):
        # We only merge one level deep; deeper nesting is overwritten wholesale
        self.backend.save({"workweeks": {"KR": {"detail": "x"}}}, "default")
        self.backend.save({"workweeks": {"KR": {"detail": "y"}}}, "default")
        # The inner dict is OVERWRITTEN, not merged
        self.assertEqual(
            self.backend.load("default")["workweeks"]["KR"],
            {"detail": "y"},
        )


class TestModuleFacade(unittest.TestCase):
    """Test the public module-level functions (get/save/load/reset_backend)."""
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        path = Path(self.tmpdir.name) / "config.json"
        self._original_backend = config._backend
        config.reset_backend(config.JsonBackend(path=path))

    def tearDown(self):
        self.tmpdir.cleanup()
        config._backend = self._original_backend

    def test_get_with_default_when_missing(self):
        self.assertEqual(config.get("budget", default=42), 42)

    def test_save_and_get_facade(self):
        config.save({"budget": 15})
        self.assertEqual(config.get("budget"), 15)

    def test_per_user_facade(self):
        config.save({"budget": 1}, user_id="u1")
        config.save({"budget": 2}, user_id="u2")
        self.assertEqual(config.get("budget", user_id="u1"), 1)
        self.assertEqual(config.get("budget", user_id="u2"), 2)


class TestBackendSelectionFromEnv(unittest.TestCase):
    def test_unknown_backend_raises(self):
        os.environ["DAYSOFF_BACKEND"] = "bogus"
        try:
            with self.assertRaises(ValueError):
                config.reset_backend()
        finally:
            os.environ.pop("DAYSOFF_BACKEND", None)
            config.reset_backend()

    def test_legacy_holiday_backend_env_still_works(self):
        os.environ.pop("DAYSOFF_BACKEND", None)
        os.environ["HOLIDAY_BACKEND"] = "json"
        try:
            config.reset_backend()
            self.assertIsInstance(config._backend, config.JsonBackend)
        finally:
            os.environ.pop("HOLIDAY_BACKEND", None)
            config.reset_backend()

    def test_sqlite_stub_raises_not_implemented(self):
        bk = config.SqliteBackend()
        with self.assertRaises(NotImplementedError):
            bk.load("default")
        with self.assertRaises(NotImplementedError):
            bk.save({}, "default")

    def test_api_stub_raises_not_implemented(self):
        bk = config.ApiBackend()
        with self.assertRaises(NotImplementedError):
            bk.load("default")
        with self.assertRaises(NotImplementedError):
            bk.save({}, "default")


if __name__ == "__main__":
    unittest.main()
