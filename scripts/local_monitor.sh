#!/usr/bin/env zsh
set -u

cd "$(dirname "$0")/.." || exit 1

PY="${PYTHON_BIN:-./.conda-fund-monitor/bin/python}"
CONFIG_PATH="${CONFIG_PATH:-config/funds.json}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-300}"

mkdir -p data logs
echo "$$" > data/fund-monitor-local.pid
echo "[$(date '+%F %T')] local monitor started pid=$$"

while true; do
  now_hm="$(date +%H%M)"
  day="$(date +%F)"
  echo "[$(date '+%F %T')] local monitor tick hm=$now_hm"

  if [ "$now_hm" -ge 1330 ] && [ "$now_hm" -le 1450 ]; then
    "$PY" -m fund_monitor.cli intraday --config "$CONFIG_PATH" --ignore-trading-day
  fi

  if [ "$now_hm" -ge 1440 ] && [ "$now_hm" -lt 1450 ] && [ ! -f "data/local-remind-$day.done" ]; then
    "$PY" -m fund_monitor.cli remind --config "$CONFIG_PATH" --ignore-trading-day
    touch "data/local-remind-$day.done"
  fi

  if [ "$now_hm" -ge 1510 ] && [ ! -f "data/local-recap-$day.done" ]; then
    "$PY" -m fund_monitor.cli recap --config "$CONFIG_PATH" --ignore-trading-day
    touch "data/local-recap-$day.done"
  fi

  sleep "$INTERVAL_SECONDS"
done
