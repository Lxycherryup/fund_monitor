from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request

from .models import FundSnapshot

TIANTIAN_URL = "https://fundgz.1234567.com.cn/js/{code}.js"
JSONP_RE = re.compile(r"^[^(]*\((.*)\)\s*;?\s*$")


def parse_tiantian_jsonp(body: str) -> FundSnapshot:
    match = JSONP_RE.match(body.strip())
    if not match:
        raise ValueError("invalid Tiantian Fund JSONP response")

    payload = json.loads(match.group(1))
    return FundSnapshot(
        code=str(payload.get("fundcode", "")).strip(),
        name=str(payload.get("name", "")).strip(),
        estimate_nav=_optional_float(payload.get("gsz")),
        estimate_change_pct=_optional_float(payload.get("gszzl")),
        nav=_optional_float(payload.get("dwjz")),
        nav_date=str(payload.get("jzrq", "")).strip(),
        estimate_time=str(payload.get("gztime", "")).strip(),
    )


class TiantianFundClient:
    def __init__(self, timeout: float = 8.0, retries: int = 2):
        self.timeout = timeout
        self.retries = retries

    def fetch_snapshot(self, code: str) -> FundSnapshot:
        url = TIANTIAN_URL.format(code=code)
        headers = {
            "User-Agent": "fund-monitor/0.1",
            "Referer": "https://fund.eastmoney.com/",
        }
        request = urllib.request.Request(url, headers=headers)
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read().decode("utf-8")
                return parse_tiantian_jsonp(body)
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"failed to fetch fund {code}: {last_error}") from last_error


def fetch_snapshots(codes: list[str], client: TiantianFundClient | None = None) -> dict[str, FundSnapshot]:
    active_client = client or TiantianFundClient()
    snapshots: dict[str, FundSnapshot] = {}
    for code in codes:
        snapshots[code] = active_client.fetch_snapshot(code)
    return snapshots


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return float(text)
