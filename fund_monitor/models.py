from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    timezone: str = "Asia/Shanghai"
    default_watch_drop_pct: float = -1.5
    default_cautious_rise_pct: float = 2.0
    intraday_drop_alert_pct: float = -2.5
    state_path: str = "data/state.json"
    production: bool = False


@dataclass(frozen=True)
class FundConfig:
    code: str
    name: str = ""
    owned: bool = False
    cost_nav: float | None = None
    holding_shares: float | None = None
    holding_amount: float | None = None
    target_position_pct: float | None = None
    target_profit_pct: float | None = None
    max_loss_pct: float | None = None
    watch_drop_pct: float = -1.5
    cautious_rise_pct: float = 2.0


@dataclass(frozen=True)
class AppConfig:
    settings: Settings
    funds: list[FundConfig] = field(default_factory=list)


@dataclass(frozen=True)
class FundSnapshot:
    code: str
    name: str
    estimate_nav: float | None
    estimate_change_pct: float | None
    nav: float | None
    nav_date: str
    estimate_time: str


@dataclass(frozen=True)
class FundSignal:
    code: str
    name: str
    group: str
    score: int
    status: str
    reasons: list[str]
    risk_note: str
    estimate_change_pct: float | None
    estimate_nav: float | None
    nav: float | None
    estimated_amount: float | None = None
    estimated_daily_profit: float | None = None
    estimated_total_profit: float | None = None
    estimated_total_profit_pct: float | None = None


@dataclass(frozen=True)
class CandidateFund:
    code: str
    name: str
    score: int
    status: str
    reasons: list[str]
    one_month_return_pct: float | None = None
    three_month_return_pct: float | None = None
    six_month_return_pct: float | None = None
    one_year_return_pct: float | None = None
    daily_change_pct: float | None = None
