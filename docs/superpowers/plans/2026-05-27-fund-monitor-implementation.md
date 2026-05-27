# Fund Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI that analyzes owned and watch-only domestic funds, generates rule-based purchase/holding suggestions, and sends Feishu notifications before the 15:00 purchase cutoff.

**Architecture:** Use a lightweight scheduled-script architecture. Keep data fetching, signal calculation, message rendering, storage, and notification delivery in separate modules so the CLI can later become a service without rewriting core logic.

**Tech Stack:** Python 3.11+, standard library only for runtime, `unittest` for tests, JSON config, Feishu webhook over HTTPS.

---

## File Structure

- `fund_monitor/__init__.py`: package marker and version.
- `fund_monitor/models.py`: dataclasses for config, fund snapshots, signals, and suggestions.
- `fund_monitor/config.py`: JSON config loading and validation.
- `fund_monitor/fund_data.py`: public fund data fetching and Tiantian Fund JSONP parsing.
- `fund_monitor/signals.py`: deterministic rule engine for owned and watch-only funds.
- `fund_monitor/messages.py`: Feishu text message rendering.
- `fund_monitor/notifier.py`: Feishu webhook sender with dry-run support.
- `fund_monitor/storage.py`: local JSON state for duplicate notification suppression.
- `fund_monitor/cli.py`: command entry point for `remind`, `recap`, `intraday`, and `test-feishu`.
- `tests/`: unit tests for config, signals, message rendering, storage, and data parsing.
- `config/funds.example.json`: sample owned and watch-only fund config.
- `README.md`: setup, config, cron, and usage guide.

## Tasks

### Task 1: Data Model, Config, and Signal Tests

**Files:**
- Create: `tests/test_config.py`
- Create: `tests/test_signals.py`
- Create: `fund_monitor/models.py`
- Create: `fund_monitor/config.py`
- Create: `fund_monitor/signals.py`

- [ ] Write tests for loading owned and watch-only fund config from JSON.
- [ ] Run tests and verify they fail because modules do not exist.
- [ ] Implement dataclasses and config loader.
- [ ] Write tests for owned-fund and watch-only suggestion rules.
- [ ] Run tests and verify they fail before signal implementation.
- [ ] Implement minimal signal engine.
- [ ] Run config and signal tests until green.

### Task 2: Fund Data Fetching and Message Rendering

**Files:**
- Create: `tests/test_fund_data.py`
- Create: `tests/test_messages.py`
- Create: `fund_monitor/fund_data.py`
- Create: `fund_monitor/messages.py`

- [ ] Write tests for parsing Tiantian Fund JSONP estimate responses.
- [ ] Run parser test and verify it fails because parser does not exist.
- [ ] Implement JSONP parser and public data client.
- [ ] Write tests for reminder and recap message text.
- [ ] Run rendering tests and verify they fail before implementation.
- [ ] Implement message rendering.
- [ ] Run parser and rendering tests until green.

### Task 3: Notification, Storage, and CLI

**Files:**
- Create: `tests/test_storage.py`
- Create: `fund_monitor/notifier.py`
- Create: `fund_monitor/storage.py`
- Create: `fund_monitor/cli.py`
- Create: `fund_monitor/__init__.py`

- [ ] Write tests for duplicate notification keys.
- [ ] Run storage tests and verify they fail because storage does not exist.
- [ ] Implement JSON state storage.
- [ ] Implement Feishu webhook sender with dry-run mode.
- [ ] Implement CLI commands using argparse.
- [ ] Run the full unit test suite until green.

### Task 4: Documentation and Example Config

**Files:**
- Create: `config/funds.example.json`
- Create: `README.md`
- Create: `.gitignore`

- [ ] Add example config with owned and watch-only funds.
- [ ] Add README usage, cron examples, Feishu setup, and disclaimer.
- [ ] Add `.gitignore` for local secrets, logs, data, and virtualenvs.
- [ ] Run dry-run reminder command with example config.
- [ ] Run full test suite.
- [ ] Commit implementation.

