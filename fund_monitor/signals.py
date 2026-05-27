from __future__ import annotations

from .models import FundConfig, FundSignal, FundSnapshot

RISK_NOTE = "公开数据可能延迟，本提醒仅为规则化观察信号，不构成投资建议。"


def analyze_fund(fund: FundConfig, snapshot: FundSnapshot) -> FundSignal:
    change_pct = snapshot.estimate_change_pct
    score = 50
    reasons: list[str] = []
    group = "持有" if fund.owned else "未持有"

    if change_pct is None:
        score -= 20
        reasons.append("缺少实时估值涨跌幅，降低信号置信度")
    elif change_pct <= fund.watch_drop_pct:
        score += 20
        reasons.append(f"当日估值跌幅 {change_pct:.2f}%，达到观察跌幅 {fund.watch_drop_pct:.2f}%")
    elif change_pct >= fund.cautious_rise_pct:
        score -= 20
        reasons.append(f"当日估值涨幅较大 {change_pct:.2f}%，谨慎追高")
    elif change_pct < 0:
        score += 8
        reasons.append(f"当日估值小幅下跌 {change_pct:.2f}%，适合继续观察")
    else:
        reasons.append(f"当日估值变化 {change_pct:.2f}%，未触发明显低吸信号")

    if fund.owned and fund.cost_nav and snapshot.estimate_nav:
        cost_gap_pct = (snapshot.estimate_nav - fund.cost_nav) / fund.cost_nav * 100
        if cost_gap_pct <= -5:
            score += 22
            reasons.append(f"当前估值低于持仓成本 {abs(cost_gap_pct):.2f}%")
        elif cost_gap_pct >= 8:
            score -= 10
            reasons.append(f"当前估值高于持仓成本 {cost_gap_pct:.2f}%，加仓需谨慎")

    portfolio = _portfolio_metrics(fund, snapshot)
    total_profit_pct = portfolio["estimated_total_profit_pct"]
    if fund.owned and total_profit_pct is not None:
        if fund.target_profit_pct is not None and total_profit_pct >= fund.target_profit_pct:
            score += 12
            reasons.append(f"持有收益率 {total_profit_pct:.2f}%，达到止盈观察线 {fund.target_profit_pct:.2f}%")
        if fund.max_loss_pct is not None and total_profit_pct <= -abs(fund.max_loss_pct):
            score -= 8
            reasons.append(f"持有收益率 {total_profit_pct:.2f}%，超过回撤控制线 {fund.max_loss_pct:.2f}%")

    score = max(0, min(100, score))
    status = _status_for(fund, score, change_pct, total_profit_pct)

    return FundSignal(
        code=fund.code,
        name=snapshot.name or fund.name or fund.code,
        group=group,
        score=score,
        status=status,
        reasons=reasons,
        risk_note=RISK_NOTE,
        estimate_change_pct=change_pct,
        estimate_nav=snapshot.estimate_nav,
        nav=snapshot.nav,
        estimated_amount=portfolio["estimated_amount"],
        estimated_daily_profit=portfolio["estimated_daily_profit"],
        estimated_total_profit=portfolio["estimated_total_profit"],
        estimated_total_profit_pct=portfolio["estimated_total_profit_pct"],
    )


def _status_for(
    fund: FundConfig,
    score: int,
    change_pct: float | None,
    total_profit_pct: float | None = None,
) -> str:
    if change_pct is not None and change_pct >= fund.cautious_rise_pct:
        return "谨慎追高"
    if fund.owned:
        if (
            fund.target_profit_pct is not None
            and total_profit_pct is not None
            and total_profit_pct >= fund.target_profit_pct
        ):
            return "止盈观察"
        if (
            fund.max_loss_pct is not None
            and total_profit_pct is not None
            and total_profit_pct <= -abs(fund.max_loss_pct)
        ):
            return "控制回撤"
        if score >= 70:
            return "加仓观察"
        if score >= 55:
            return "定投观察"
        return "继续持有观察"
    if score >= 60:
        return "可关注买入"
    if score >= 50:
        return "继续观察"
    return "暂不操作"


def _portfolio_metrics(fund: FundConfig, snapshot: FundSnapshot) -> dict[str, float | None]:
    if not fund.owned or fund.holding_shares is None or snapshot.estimate_nav is None:
        return {
            "estimated_amount": None,
            "estimated_daily_profit": None,
            "estimated_total_profit": None,
            "estimated_total_profit_pct": None,
        }

    estimated_amount = fund.holding_shares * snapshot.estimate_nav
    estimated_daily_profit = None
    if snapshot.nav is not None:
        estimated_daily_profit = fund.holding_shares * (snapshot.estimate_nav - snapshot.nav)

    estimated_total_profit = None
    estimated_total_profit_pct = None
    if fund.cost_nav is not None:
        cost_amount = fund.holding_shares * fund.cost_nav
        estimated_total_profit = estimated_amount - cost_amount
        if cost_amount:
            estimated_total_profit_pct = estimated_total_profit / cost_amount * 100

    return {
        "estimated_amount": round(estimated_amount, 2),
        "estimated_daily_profit": _round_optional(estimated_daily_profit),
        "estimated_total_profit": _round_optional(estimated_total_profit),
        "estimated_total_profit_pct": _round_optional(estimated_total_profit_pct),
    }


def _round_optional(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 2)


def analyze_many(
    funds: list[FundConfig], snapshots: dict[str, FundSnapshot]
) -> list[FundSignal]:
    signals = []
    for fund in funds:
        snapshot = snapshots.get(fund.code)
        if snapshot is None:
            snapshot = FundSnapshot(
                code=fund.code,
                name=fund.name or fund.code,
                estimate_nav=None,
                estimate_change_pct=None,
                nav=None,
                nav_date="",
                estimate_time="",
            )
        signals.append(analyze_fund(fund, snapshot))
    return sorted(signals, key=lambda item: item.score, reverse=True)
