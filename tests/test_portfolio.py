import unittest

from fund_monitor.models import FundConfig, FundSnapshot
from fund_monitor.signals import analyze_fund


class PortfolioTests(unittest.TestCase):
    def test_owned_fund_calculates_estimated_amount_and_profit(self):
        fund = FundConfig(
            code="008987",
            name="广发上海金ETF联接C",
            owned=True,
            holding_shares=1000,
            cost_nav=2.0,
        )
        snapshot = FundSnapshot(
            code="008987",
            name="广发上海金ETF联接C",
            estimate_nav=2.1,
            estimate_change_pct=-0.5,
            nav=2.08,
            nav_date="2026-05-26",
            estimate_time="2026-05-27 14:40",
        )

        signal = analyze_fund(fund, snapshot)

        self.assertEqual(signal.estimated_amount, 2100)
        self.assertAlmostEqual(signal.estimated_daily_profit, 20)
        self.assertAlmostEqual(signal.estimated_total_profit, 100)
        self.assertAlmostEqual(signal.estimated_total_profit_pct, 5)

    def test_target_profit_marks_take_profit_watch(self):
        fund = FundConfig(
            code="270023",
            name="广发全球精选股票(QDII)A",
            owned=True,
            holding_shares=100,
            cost_nav=5.0,
            target_profit_pct=20,
        )
        snapshot = FundSnapshot(
            code="270023",
            name="广发全球精选股票(QDII)A",
            estimate_nav=6.2,
            estimate_change_pct=0.3,
            nav=6.18,
            nav_date="2026-05-26",
            estimate_time="2026-05-27 14:40",
        )

        signal = analyze_fund(fund, snapshot)

        self.assertEqual(signal.status, "止盈观察")
        self.assertTrue(any("达到止盈观察线" in reason for reason in signal.reasons))


if __name__ == "__main__":
    unittest.main()
