# Domestic Fund Monitor Design

Date: 2026-05-26

## Goal

Build a server-side monitor for a user-defined list of domestic funds. The first version fetches public fund data, calculates daily movement and rule-based attention signals, and sends Feishu messages before the 15:00 purchase cutoff.

The system should be simple enough to deploy on a server as scheduled scripts, while keeping clean module boundaries so it can later grow into a long-running API service.

## Scope

Included in version 1:

- Monitor a configured list of fund codes.
- Fetch public fund estimate/net-value data from a public source such as Eastmoney/Tiantian Fund.
- Generate rule-based attention scores and explanations.
- Send Feishu group robot webhook notifications.
- Send the main actionable reminder before 15:00.
- Send a post-market recap after 15:00.
- Persist notification state locally to avoid duplicate alerts.
- Run on a Linux server through cron or systemd timer.

Not included in version 1:

- Automatic full-market fund discovery.
- Direct trading integration.
- Personal cost-basis and position-aware recommendations.
- Interactive Feishu application bot.
- Guaranteed financial advice.

## Recommendation Semantics

The system must not produce hard buy/sell commands. It should produce explainable, rule-based signals:

- `score`: 0-100 attention score.
- `status`: one of `watch`, `定投观察`, `谨慎追高`, `暂不操作`.
- `reasons`: short factual explanations such as daily estimate movement, recent drawdown, or trend condition.
- `risk_note`: a reminder that data may be delayed and the output is not investment advice.

## Architecture

The first version uses a lightweight Python scheduled-script architecture.

Modules:

- `config`: Loads fund list, thresholds, Feishu webhook, and runtime settings.
- `fund_data`: Fetches current estimate, latest net value, historical net values, and fund metadata.
- `signals`: Converts raw fund data into scores, statuses, reasons, and alert decisions.
- `notifier`: Defines a notification interface and implements Feishu webhook delivery.
- `storage`: Stores recent signals and sent notification keys in a local SQLite database or JSON file.
- `scheduler`: Provides command entry points for actionable reminders, post-market recaps, and optional intraday checks.
- `logging`: Writes structured logs for data fetch failures, skipped non-trading days, and notification results.

## Data Flow

1. A scheduled command starts on the server.
2. Configuration is loaded from local config and environment variables.
3. The command checks whether today is a trading day.
4. Fund data is fetched for each configured code.
5. Signal rules calculate score, status, reasons, and whether an alert should be sent.
6. Storage is checked to prevent duplicate noisy alerts.
7. Feishu messages are generated and sent through the notifier.
8. Results and failures are logged.

## Notification Schedule

Recommended server schedule:

- Trading days at 14:40: actionable reminder for decisions before the 15:00 cutoff.
- Trading days between 13:30 and 14:50: optional threshold-triggered intraday alert, with per-fund daily rate limiting.
- Trading days at 15:10: post-market recap. This message should summarize only and avoid same-day action wording.
- Non-trading days: no default notification.

## Signal Rules

Initial rule set:

- Daily estimate decline beyond a configurable threshold increases attention score.
- Recent multi-day drawdown increases attention score.
- Large same-day rise reduces buying enthusiasm and may mark `谨慎追高`.
- High volatility or missing data reduces confidence.
- A stable or mildly negative day can produce `定投观察` if configured.

The rule engine should be deterministic, transparent, and covered by unit tests.

## Configuration

Configuration should avoid hard-coding secrets.

Suggested files and environment variables:

- `config/funds.yaml`: fund codes, display names, optional per-fund thresholds.
- `.env`: `FEISHU_WEBHOOK_URL`, optional webhook signing secret.
- `config/settings.yaml`: schedule mode, thresholds, timezone, storage path.

Example fund item:

```yaml
funds:
  - code: "000001"
    name: "示例基金"
    watch_drop_pct: -1.5
    cautious_rise_pct: 2.0
```

## Deployment

The first deployment target is a Linux server.

Recommended runtime:

- Python 3.11 or newer.
- Virtual environment.
- Cron or systemd timer.
- Logs written to `logs/fund-monitor.log`.
- Local persistent state written to `data/fund-monitor.db` or `data/state.json`.

Cron shape:

```cron
40 14 * * 1-5 fund-monitor remind
10 15 * * 1-5 fund-monitor recap
*/30 13-14 * * 1-5 fund-monitor intraday
```

The implementation should still check trading-day status internally because weekday cron alone does not account for holidays.

## Error Handling

- Data source failure: retry with backoff, then include a concise failure line in logs.
- Partial data failure: continue processing other funds.
- Feishu send failure: retry; if still failing, log the response status and body.
- Invalid fund configuration: fail fast with a clear error.
- Missing webhook: allow dry-run output for local validation, but fail in production mode.

## Testing

Minimum tests:

- Signal score and status for down day, up day, missing data, and recent drawdown.
- Feishu message rendering without sending real network requests.
- Configuration validation.
- Duplicate notification suppression.

Manual verification:

- Run a dry-run reminder command.
- Run a dry-run recap command.
- Send one test Feishu message after webhook is configured.

## GitHub Upload

After implementation and verification, initialize a Git repository if needed, commit the code, and upload it to GitHub. The upload step needs either:

- An existing GitHub remote URL, or
- Permission to create a new repository with the GitHub CLI.

