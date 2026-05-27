from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import CandidateFund


def screen_open_funds(
    rows: Iterable[dict[str, Any]],
    owned_codes: set[str],
    limit: int = 10,
) -> list[CandidateFund]:
    candidates: list[CandidateFund] = []
    for row in rows:
        code = _text(row, "基金代码")
        if not code or code in owned_codes:
            continue

        one_month = _pct(row, "近1月")
        three_month = _pct(row, "近3月")
        six_month = _pct(row, "近6月")
        one_year = _pct(row, "近1年")
        daily = _pct(row, "日增长率")

        score = 50
        reasons: list[str] = []
        if three_month is not None and three_month >= 5:
            score += 14
            reasons.append(f"近3月收益 {three_month:.2f}%")
        if six_month is not None and six_month >= 8:
            score += 12
            reasons.append(f"近6月收益 {six_month:.2f}%")
        if one_year is not None and one_year >= 12:
            score += 10
            reasons.append(f"近1年收益 {one_year:.2f}%")
        if daily is not None and daily < 0:
            score += 6
            reasons.append(f"当日回调 {daily:.2f}%")
        if one_month is not None and one_month >= 12:
            score -= 25
            reasons.append(f"近1月涨幅 {one_month:.2f}%，短期偏热")
        if daily is not None and daily >= 2.5:
            score -= 20
            reasons.append(f"当日涨幅 {daily:.2f}%，避免追高")
        if one_year is not None and one_year < 0:
            score -= 20
            reasons.append(f"近1年收益 {one_year:.2f}%，长期表现偏弱")

        score = max(0, min(100, score))
        if score < 60:
            continue

        candidates.append(
            CandidateFund(
                code=code,
                name=_text(row, "基金简称") or code,
                score=score,
                status="可关注买入",
                reasons=reasons,
                one_month_return_pct=one_month,
                three_month_return_pct=three_month,
                six_month_return_pct=six_month,
                one_year_return_pct=one_year,
                daily_change_pct=daily,
            )
        )

    return sorted(candidates, key=lambda item: item.score, reverse=True)[:limit]


def fetch_open_fund_rank(symbol: str = "全部") -> list[dict[str, Any]]:
    try:
        import akshare as ak
    except ImportError as exc:
        raise RuntimeError("缺少 akshare 依赖，请先运行：pip install -r requirements.txt") from exc

    frame = ak.fund_open_fund_rank_em(symbol=symbol)
    return frame.to_dict(orient="records")


def _text(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _pct(row: dict[str, Any], key: str) -> float | None:
    value = row.get(key)
    if value is None:
        return None
    text = str(value).replace("%", "").strip()
    if not text or text == "--":
        return None
    return float(text)
