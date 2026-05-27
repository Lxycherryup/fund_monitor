import tempfile
import unittest
from pathlib import Path

from fund_monitor.storage import JsonStateStore


class StorageTests(unittest.TestCase):
    def test_records_notification_key_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonStateStore(Path(tmp) / "state.json")

            self.assertFalse(store.has_sent("2026-05-27", "remind", "000001"))
            store.mark_sent("2026-05-27", "remind", "000001")

            self.assertTrue(store.has_sent("2026-05-27", "remind", "000001"))

            reloaded = JsonStateStore(Path(tmp) / "state.json")
            self.assertTrue(reloaded.has_sent("2026-05-27", "remind", "000001"))


if __name__ == "__main__":
    unittest.main()
