# Automation Scripts

[![九号自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/ninebot.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/ninebot.yml)
[![什么值得买自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/smzdm.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/smzdm.yml)
[![每日自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/daily.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/daily.yml)

这是一个基于 GitHub Actions 的自动化脚本仓库，主要用于每天定时执行签到、任务领取和结果汇总，并通过 Server 酱发送通知。

目前包含两组脚本：

- `ninebot/`：九号相关自动化任务，使用 Python
- `smzdm/`：什么值得买相关自动化任务，使用 Node.js

## Features

### Ninebot

- 每日签到
- 自动执行分享任务并领取奖励
- 检查盲盒里程碑状态
- 运行结束后汇总推送消息

### SMZDM

- 每日签到
- 自动完成部分日常任务
- 支持全民众测能量值任务
- 运行结束后汇总推送消息

### Common

- 基于 GitHub Actions 定时运行
- 支持手动触发 workflow
- 启动前自动检查关键环境变量
- 默认定时任务只发送 1 条统一汇总通知

## Project Structure

```text
.
├── .github/workflows/
│   ├── daily.yml
│   ├── ninebot.yml
│   └── smzdm.yml
├── ninebot/
│   ├── nine_bot_checkin.py
│   ├── nine_bot_share_reward.py
│   ├── nine_bot_blind_box.py
│   └── notification.py
├── smzdm/
│   ├── bot.js
│   ├── env.js
│   ├── library_task.js
│   ├── notification.js
│   ├── send_summary.js
│   ├── smzdm_checkin.js
│   ├── smzdm_lottery.js
│   ├── smzdm_task.js
│   └── smzdm_testing.js
├── requirements.txt
└── README.md
```

## Workflows

当前仓库有 3 个 GitHub Actions 工作流：

- `daily.yml`：默认定时任务。分别执行九号和什么值得买，并在最后统一发送 1 条汇总通知
- `ninebot.yml`：手动单独执行九号任务
- `smzdm.yml`：手动单独执行什么值得买任务

默认定时由 `daily.yml` 在每天北京时间 `07:00` 触发；另外两个 workflow 保留给手动排查或单独执行使用。

## Required Secrets

在仓库的 `Settings -> Secrets and variables -> Actions` 中配置以下变量。

### Ninebot

| Name | Required | Description |
| --- | --- | --- |
| `NINEBOT_TOKEN` | Yes | 九号接口请求头中的 `Authorization` |
| `DEVICE_ID` | Yes | 九号接口请求头中的 `device_id` |

### SMZDM

| Name | Required | Description |
| --- | --- | --- |
| `SMZDM_COOKIE` | Yes | 什么值得买账号的 Cookie |
| `SMZDM_SK` | No | 部分签到场景可用的附加参数 |

### Notification

| Name | Required | Description |
| --- | --- | --- |
| `SERVER_CHAN_SEND_KEY` | No | Server 酱推送 key；未配置时会跳过汇总通知 |

## Workflow Environment Variables

除了 GitHub Secrets，SMZDM 工作流里还使用了几个运行参数：

| Name | Current Value | Description |
| --- | --- | --- |
| `SMZDM_TASK_TESTING` | `yes` | 启用全民众测能量值任务 |
| `SMZDM_CROWD_SILVER_5` | `no` | 不启用 5 碎银抽奖 |
| `SMZDM_COMMENT` | `点赞支持，感谢分享！` | 评论类任务使用的默认文案 |

如果你后续调整 workflow，这些值也建议和 README 保持同步。

## Local Run

如果需要本地调试，可以分别运行：

### Ninebot

```bash
pip install -r requirements.txt
python3 ninebot/nine_bot_checkin.py
python3 ninebot/nine_bot_share_reward.py
python3 ninebot/nine_bot_blind_box.py
```

### SMZDM

```bash
npm install crypto-js got@11 tough-cookie
node smzdm/smzdm_checkin.js
node smzdm/smzdm_task.js
node smzdm/smzdm_testing.js
node smzdm/send_summary.js
```

本地运行前同样需要先设置对应环境变量。

## Notes

- 这类自动化依赖第三方平台接口，接口字段、风控策略和任务规则都可能变化。
- 如果 GitHub Actions 突然报错，优先检查 Secrets 是否失效、接口字段是否变更、任务是否下线。
- 日志推送属于辅助能力，即使通知失败，也不一定代表主任务全部失败。

## Disclaimer

- 本项目仅供学习和个人研究使用。
- 请自行评估账号风控和平台规则变更带来的风险。
- 使用本项目造成的任何后果，由使用者自行承担。
