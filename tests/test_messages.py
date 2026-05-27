import unittest

from fund_monitor.messages import render_reminder, render_recap
from fund_monitor.models import FundSignal


class MessageTests(unittest.TestCase):
    def test_reminder_groups_owned_and_watch_funds(self):
        signals = [
            FundSignal(
                code="000001",
                name="持有示例",
                group="持有",
                score=78,
                status="可补仓观察",
                reasons=["当前估值低于持仓成本 10.00%", "当日估值跌幅 -1.70%"],
                risk_note="公开数据可能延迟，本提醒仅为规则化观察信号，不构成投资建议。",
                estimate_change_pct=-1.7,
                estimate_nav=1.08,
                nav=1.09,
            ),
            FundSignal(
                code="000002",
                name="观察示例",
                group="未持有",
                score=70,
                status="可关注买入",
                reasons=["当日估值跌幅 -2.10%，达到观察跌幅 -1.50%"],
                risk_note="公开数据可能延迟，本提醒仅为规则化观察信号，不构成投资建议。",
                estimate_change_pct=-2.1,
                estimate_nav=0.92,
                nav=0.94,
            ),
        ]

        message = render_reminder(signals, now_text="2026-05-27 14:40")

        self.assertIn("15:00 前操作窗口提醒", message)
        self.assertIn("持有基金", message)
        self.assertIn("未持有观察基金", message)
        self.assertIn("持有示例", message)
        self.assertIn("观察示例", message)
        self.assertIn("不构成投资建议", message)

    def test_recap_uses_summary_language(self):
        signal = FundSignal(
            code="000003",
            name="复盘示例",
            group="未持有",
            score=42,
            status="谨慎追高",
            reasons=["当日估值涨幅较大 2.60%，谨慎追高"],
            risk_note="公开数据可能延迟，本提醒仅为规则化观察信号，不构成投资建议。",
            estimate_change_pct=2.6,
            estimate_nav=1.3,
            nav=1.27,
        )

        message = render_recap([signal], now_text="2026-05-27 15:10")

        self.assertIn("收盘复盘摘要", message)
        self.assertIn("不再作为今日操作提示", message)
        self.assertIn("复盘示例", message)


if __name__ == "__main__":
    unittest.main()
