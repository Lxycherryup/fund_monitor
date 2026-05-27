from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import load_config
from .fund_data import TiantianFundClient
from .messages import render_candidates, render_recap, render_reminder
from .models import FundSnapshot
from .notifier import FeishuNotifier
from .screener import fetch_open_fund_rank, screen_open_funds
from .signals import analyze_many
from .storage import JsonStateStore


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.command == "test-feishu":
        notifier = FeishuNotifier(dry_run=args.dry_run)
        notifier.send_text("基金监控飞书测试消息：Webhook 配置正常。")
        return 0

    config = load_config(args.config)
    now = _now(config.settings.timezone)
    now_text = now.strftime("%Y-%m-%d %H:%M")

    if args.command == "screen":
        rows = fetch_open_fund_rank(args.screen_symbol)
        owned_codes = {fund.code for fund in config.funds if fund.owned}
        candidates = screen_open_funds(rows, owned_codes=owned_codes, limit=args.screen_limit)
        notifier = FeishuNotifier(dry_run=args.dry_run)
        notifier.send_text(render_candidates(candidates, now_text))
        return 0

    if not args.ignore_trading_day and not _is_likely_trading_day(now):
        logging.info("skip non-trading weekday/weekend: %s", now.date().isoformat())
        return 0

    client = TiantianFundClient()
    snapshots = _fetch_all(config.funds, client)
    signals = analyze_many(config.funds, snapshots)

    if args.command == "recap":
        message = render_recap(signals, now_text)
    else:
        message = render_reminder(signals, now_text)

    if args.command == "intraday":
        store = JsonStateStore(config.settings.state_path)
        day = now.date().isoformat()
        filtered = [
            signal
            for signal in signals
            if signal.estimate_change_pct is not None
            and signal.estimate_change_pct <= config.settings.intraday_drop_alert_pct
            and not store.has_sent(day, "intraday", signal.code)
        ]
        if not filtered:
            logging.info("no intraday alert matched")
            return 0
        message = render_reminder(filtered, now_text)
        for signal in filtered:
            store.mark_sent(day, "intraday", signal.code)

    notifier = FeishuNotifier(dry_run=args.dry_run)
    notifier.send_text(message)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fund-monitor")
    parser.add_argument(
        "command",
        choices=["remind", "recap", "intraday", "screen", "test-feishu"],
        help="运行模式：14:40 提醒、15:10 复盘、盘中阈值提醒、候选基金筛选或飞书测试",
    )
    parser.add_argument(
        "--config",
        default="config/funds.json",
        help="基金配置 JSON 文件路径，默认 config/funds.json",
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印消息，不发送飞书")
    parser.add_argument("--screen-limit", type=int, default=10, help="候选基金筛选返回数量")
    parser.add_argument("--screen-symbol", default="全部", help="AKShare 开放式基金排行分类")
    parser.add_argument(
        "--ignore-trading-day",
        action="store_true",
        help="忽略交易日判断，适合本地调试和节假日测试",
    )
    return parser


def _fetch_all(funds, client: TiantianFundClient) -> dict[str, FundSnapshot]:
    snapshots: dict[str, FundSnapshot] = {}
    for fund in funds:
        try:
            snapshot = client.fetch_snapshot(fund.code)
            snapshots[fund.code] = FundSnapshot(
                code=snapshot.code,
                name=snapshot.name or fund.name or fund.code,
                estimate_nav=snapshot.estimate_nav,
                estimate_change_pct=snapshot.estimate_change_pct,
                nav=snapshot.nav,
                nav_date=snapshot.nav_date,
                estimate_time=snapshot.estimate_time,
            )
        except RuntimeError as exc:
            logging.warning("failed to fetch %s: %s", fund.code, exc)
    return snapshots


def _now(timezone: str) -> dt.datetime:
    return dt.datetime.now(tz=ZoneInfo(timezone))


def _is_likely_trading_day(now: dt.datetime) -> bool:
    return now.weekday() < 5


if __name__ == "__main__":
    sys.exit(main())
