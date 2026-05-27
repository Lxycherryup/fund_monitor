import unittest

from fund_monitor.screener import screen_open_funds


class ScreenerTests(unittest.TestCase):
    def test_screens_candidate_funds_from_rank_rows(self):
        rows = [
            {
                "基金代码": "000001",
                "基金简称": "已持有基金",
                "近1月": "4.2",
                "近3月": "8.1",
                "近6月": "12.5",
                "近1年": "18.0",
                "日增长率": "0.8",
            },
            {
                "基金代码": "000002",
                "基金简称": "候选基金",
                "近1月": "3.5",
                "近3月": "7.2",
                "近6月": "10.1",
                "近1年": "16.0",
                "日增长率": "-0.4",
            },
            {
                "基金代码": "000003",
                "基金简称": "短期过热基金",
                "近1月": "14.5",
                "近3月": "22.0",
                "近6月": "35.0",
                "近1年": "60.0",
                "日增长率": "3.5",
            },
        ]

        candidates = screen_open_funds(rows, owned_codes={"000001"}, limit=5)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].code, "000002")
        self.assertEqual(candidates[0].name, "候选基金")
        self.assertGreaterEqual(candidates[0].score, 60)
        self.assertTrue(any("近3月" in reason for reason in candidates[0].reasons))


if __name__ == "__main__":
    unittest.main()
