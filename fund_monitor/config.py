from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AppConfig, FundConfig, Settings


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        raise ValueError("config root must be an object")

    settings = _load_settings(raw.get("settings", {}))
    funds_raw = raw.get("funds")
    if not isinstance(funds_raw, list) or not funds_raw:
        raise ValueError("funds must be a non-empty list")

    funds = [_load_fund(item, settings) for item in funds_raw]
    return AppConfig(settings=settings, funds=funds)


def _load_settings(raw: Any) -> Settings:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("settings must be an object")

    return Settings(
        timezone=str(raw.get("timezone", "Asia/Shanghai")),
        default_watch_drop_pct=float(raw.get("default_watch_drop_pct", -1.5)),
        default_cautious_rise_pct=float(raw.get("default_cautious_rise_pct", 2.0)),
        intraday_drop_alert_pct=float(raw.get("intraday_drop_alert_pct", -2.5)),
        state_path=str(raw.get("state_path", "data/state.json")),
        production=bool(raw.get("production", False)),
    )


def _load_fund(raw: Any, settings: Settings) -> FundConfig:
    if not isinstance(raw, dict):
        raise ValueError("fund item must be an object")
    code = str(raw.get("code", "")).strip()
    if not code:
        raise ValueError("fund code is required")

    return FundConfig(
        code=code,
        name=str(raw.get("name", "")).strip(),
        owned=bool(raw.get("owned", False)),
        cost_nav=_optional_float(raw.get("cost_nav")),
        target_position_pct=_optional_float(raw.get("target_position_pct")),
        watch_drop_pct=float(raw.get("watch_drop_pct", settings.default_watch_drop_pct)),
        cautious_rise_pct=float(
            raw.get("cautious_rise_pct", settings.default_cautious_rise_pct)
        ),
    )


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
