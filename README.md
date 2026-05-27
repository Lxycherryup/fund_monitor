# 国内基金监控

一个轻量 Python 脚本，用来监控国内基金的当日估值涨跌，并在支付宝 15:00 购买截止前通过飞书发送提醒。

第一版支持两类基金：

- 已持有基金：可配置持仓成本，输出补仓观察、定投观察、继续持有观察等信号。
- 未持有观察基金：用于分析还没有买的基金，输出可关注买入、继续观察、谨慎追高等信号。

所有建议都是规则化观察信号，不构成投资建议。

## 运行要求

- Python 3.11 或更高版本
- Linux 服务器、macOS 或其他可运行 Python 的环境
- 飞书群机器人 Webhook

当前运行时只使用 Python 标准库，不需要安装第三方依赖。

## 配置基金

复制示例配置：

```bash
cp config/funds.example.json config/funds.json
```

编辑 `config/funds.json`：

```json
{
  "settings": {
    "timezone": "Asia/Shanghai",
    "default_watch_drop_pct": -1.5,
    "default_cautious_rise_pct": 2.0,
    "intraday_drop_alert_pct": -2.5,
    "state_path": "data/state.json",
    "production": false
  },
  "funds": [
    {
      "code": "000001",
      "name": "我的持有基金",
      "owned": true,
      "cost_nav": 1.2,
      "target_position_pct": 20
    },
    {
      "code": "161725",
      "name": "观察中的基金",
      "owned": false,
      "watch_drop_pct": -2.0
    }
  ]
}
```

字段说明：

- `code`：基金代码。
- `name`：展示名称，可留空，脚本会优先使用数据源返回名称。
- `owned`：是否已持有。
- `cost_nav`：持有基金的成本净值，可不填。
- `target_position_pct`：目标仓位百分比，当前版本保留字段。
- `watch_drop_pct`：当日估值跌幅达到该阈值时提高关注评分。
- `cautious_rise_pct`：当日估值涨幅达到该阈值时标记谨慎追高。

## 飞书 Webhook

设置环境变量：

```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/你的-token"
```

测试飞书发送：

```bash
python3 -m fund_monitor.cli test-feishu
```

本地只看消息不发送：

```bash
python3 -m fund_monitor.cli test-feishu --dry-run
```

## 手动运行

14:40 操作窗口提醒：

```bash
python3 -m fund_monitor.cli remind --config config/funds.json --ignore-trading-day --dry-run
```

15:10 收盘复盘：

```bash
python3 -m fund_monitor.cli recap --config config/funds.json --ignore-trading-day --dry-run
```

盘中阈值提醒：

```bash
python3 -m fund_monitor.cli intraday --config config/funds.json --ignore-trading-day --dry-run
```

去掉 `--dry-run` 后会真实发送飞书消息。

## 服务器定时任务

cron 示例：

```cron
40 14 * * 1-5 cd /path/to/fund-monitor && /usr/bin/python3 -m fund_monitor.cli remind --config config/funds.json >> logs/fund-monitor.log 2>&1
10 15 * * 1-5 cd /path/to/fund-monitor && /usr/bin/python3 -m fund_monitor.cli recap --config config/funds.json >> logs/fund-monitor.log 2>&1
*/30 13-14 * * 1-5 cd /path/to/fund-monitor && /usr/bin/python3 -m fund_monitor.cli intraday --config config/funds.json >> logs/fund-monitor.log 2>&1
```

脚本内部会跳过周末。国内节假日休市判断第一版还没有接入交易日历，因此节假日建议暂时由 cron 或服务器计划任务控制。

## 测试

```bash
python3 -m unittest discover -s tests
```

## 数据源说明

当前使用天天基金公开估值接口：

```text
https://fundgz.1234567.com.cn/js/{基金代码}.js
```

该接口不是正式付费 API，可能存在延迟、字段变化或临时不可用。脚本会尽量失败隔离，但重要操作前请自行核对支付宝或基金平台显示的数据。

