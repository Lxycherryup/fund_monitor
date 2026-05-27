import json
import tempfile
import unittest
from pathlib import Path

from fund_monitor.config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_owned_and_watch_funds_from_json(self):
        payload = {
            "settings": {
                "timezone": "Asia/Shanghai",
                "default_watch_drop_pct": -1.5,
                "default_cautious_rise_pct": 2.0,
                "intraday_drop_alert_pct": -2.5,
                "state_path": "data/state.json",
            },
            "funds": [
                {
                    "code": "000001",
                    "name": "持有示例",
                    "owned": True,
                    "cost_nav": 1.2,
                    "target_position_pct": 20,
                },
                {
                    "code": "000002",
                    "name": "观察示例",
                    "owned": False,
                    "watch_drop_pct": -2.0,
                    "cautious_rise_pct": 1.8,
                },
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funds.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            config = load_config(path)

        self.assertEqual(config.settings.timezone, "Asia/Shanghai")
        self.assertEqual(len(config.funds), 2)
        self.assertTrue(config.funds[0].owned)
        self.assertEqual(config.funds[0].cost_nav, 1.2)
        self.assertFalse(config.funds[1].owned)
        self.assertEqual(config.funds[1].watch_drop_pct, -2.0)

    def test_rejects_fund_without_code(self):
        payload = {"funds": [{"name": "缺少代码"}]}

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funds.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "code"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
