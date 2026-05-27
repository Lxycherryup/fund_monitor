import unittest

from fund_monitor.models import FundConfig, FundSnapshot
from fund_monitor.signals import analyze_fund


class SignalTests(unittest.TestCase):
    def test_owned_fund_below_cost_suggests_add_attention(self):
        fund = FundConfig(
            code="000001",
            name="持有示例",
            owned=True,
            cost_nav=1.2,
            target_position_pct=20,
        )
        snapshot = FundSnapshot(
            code="000001",
            name="持有示例",
            estimate_nav=1.08,
            estimate_change_pct=-1.7,
            nav=1.09,
            nav_date="2026-05-26",
            estimate_time="2026-05-27 14:35",
        )

        signal = analyze_fund(fund, snapshot)

        self.assertEqual(signal.group, "持有")
        self.assertGreaterEqual(signal.score, 70)
        self.assertIn(signal.status, {"可补仓观察", "定投观察"})
        self.assertTrue(any("低于持仓成本" in reason for reason in signal.reasons))

    def test_watch_fund_drop_suggests_purchase_attention(self):
        fund = FundConfig(
            code="000002",
            name="观察示例",
            owned=False,
            watch_drop_pct=-1.5,
        )
        snapshot = FundSnapshot(
            code="000002",
            name="观察示例",
            estimate_nav=0.92,
            estimate_change_pct=-2.1,
            nav=0.94,
            nav_date="2026-05-26",
            estimate_time="2026-05-27 14:35",
        )

        signal = analyze_fund(fund, snapshot)

        self.assertEqual(signal.group, "未持有")
        self.assertGreaterEqual(signal.score, 60)
        self.assertEqual(signal.status, "可关注买入")
        self.assertTrue(any("达到观察跌幅" in reason for reason in signal.reasons))

    def test_large_rise_marks_cautious_chasing(self):
        fund = FundConfig(
            code="000003",
            name="上涨示例",
            owned=False,
            cautious_rise_pct=2.0,
        )
        snapshot = FundSnapshot(
            code="000003",
            name="上涨示例",
            estimate_nav=1.3,
            estimate_change_pct=2.6,
            nav=1.27,
            nav_date="2026-05-26",
            estimate_time="2026-05-27 14:35",
        )

        signal = analyze_fund(fund, snapshot)

        self.assertEqual(signal.status, "谨慎追高")
        self.assertLessEqual(signal.score, 45)
        self.assertTrue(any("涨幅较大" in reason for reason in signal.reasons))


if __name__ == "__main__":
    unittest.main()
