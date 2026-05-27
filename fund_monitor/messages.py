from __future__ import annotations

from collections.abc import Iterable

from .models import CandidateFund, FundSignal


def render_reminder(signals: Iterable[FundSignal], now_text: str) -> str:
    ordered = sorted(signals, key=lambda item: item.score, reverse=True)
    lines = [
        f"国内基金 15:00 前操作窗口提醒（{now_text}）",
        "说明：仅按规则给出关注信号，请结合个人仓位和风险承受能力判断。",
        "",
    ]
    lines.extend(_render_group("持有基金", [item for item in ordered if item.group == "持有"]))
    lines.append("")
    lines.extend(_render_group("未持有观察基金", [item for item in ordered if item.group == "未持有"]))
    lines.append("")
    lines.append("风险提示：公开数据可能延迟，本提醒仅为规则化观察信号，不构成投资建议。")
    return "\n".join(lines)


def render_recap(signals: Iterable[FundSignal], now_text: str) -> str:
    ordered = sorted(signals, key=lambda item: item.score, reverse=True)
    lines = [
        f"国内基金收盘复盘摘要（{now_text}）",
        "说明：15:00 后消息只用于复盘，不再作为今日操作提示。",
        "",
    ]
    lines.extend(_render_group("持有基金", [item for item in ordered if item.group == "持有"]))
    lines.append("")
    lines.extend(_render_group("未持有观察基金", [item for item in ordered if item.group == "未持有"]))
    lines.append("")
    lines.append("风险提示：公开数据可能延迟，本提醒仅为规则化观察信号，不构成投资建议。")
    return "\n".join(lines)


def render_candidates(candidates: Iterable[CandidateFund], now_text: str) -> str:
    ordered = sorted(candidates, key=lambda item: item.score, reverse=True)
    lines = [
        f"候选基金筛选（{now_text}）",
        "说明：以下为公开数据规则筛选结果，用于加入观察池，不构成投资建议。",
        "",
        "【可关注候选】",
    ]
    if not ordered:
        lines.append("- 暂无符合条件的候选基金")
    for candidate in ordered:
        reason = "；".join(candidate.reasons[:3])
        lines.append(
            f"- {candidate.name}（{candidate.code}）：{candidate.status}，评分 {candidate.score}。原因：{reason}"
        )
    lines.append("")
    lines.append("风险提示：公开数据可能延迟，候选结果需结合基金规模、行业集中度和个人仓位复核，不构成投资建议。")
    return "\n".join(lines)


def _render_group(title: str, signals: list[FundSignal]) -> list[str]:
    lines = [f"【{title}】"]
    if not signals:
        lines.append("- 暂无")
        return lines
    for signal in signals:
        change = _format_pct(signal.estimate_change_pct)
        nav = _format_number(signal.estimate_nav)
        reason = "；".join(signal.reasons[:2])
        portfolio = _format_portfolio(signal)
        lines.append(
            f"- {signal.name}（{signal.code}）：{signal.status}，评分 {signal.score}，"
            f"估值涨跌 {change}，估值 {nav}{portfolio}。原因：{reason}"
        )
    return lines


def _format_pct(value: float | None) -> str:
    if value is None:
        return "未知"
    return f"{value:.2f}%"


def _format_number(value: float | None) -> str:
    if value is None:
        return "未知"
    return f"{value:.4f}"


def _format_money(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def _format_portfolio(signal: FundSignal) -> str:
    parts = []
    if signal.estimated_amount is not None:
        parts.append(f"估算金额 {_format_money(signal.estimated_amount)}")
    if signal.estimated_daily_profit is not None:
        parts.append(f"当日估算盈亏 {_format_money(signal.estimated_daily_profit)}")
    if signal.estimated_total_profit is not None:
        total = f"总盈亏 {_format_money(signal.estimated_total_profit)}"
        if signal.estimated_total_profit_pct is not None:
            total += f"（{signal.estimated_total_profit_pct:.2f}%）"
        parts.append(total)
    if not parts:
        return ""
    return "，" + "，".join(parts)
