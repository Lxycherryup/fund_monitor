from __future__ import annotations

from collections.abc import Iterable

from .models import FundSignal


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


def _render_group(title: str, signals: list[FundSignal]) -> list[str]:
    lines = [f"【{title}】"]
    if not signals:
        lines.append("- 暂无")
        return lines
    for signal in signals:
        change = _format_pct(signal.estimate_change_pct)
        nav = _format_number(signal.estimate_nav)
        reason = "；".join(signal.reasons[:2])
        lines.append(
            f"- {signal.name}（{signal.code}）：{signal.status}，评分 {signal.score}，"
            f"估值涨跌 {change}，估值 {nav}。原因：{reason}"
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
