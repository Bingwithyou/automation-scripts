# 🤖 自动化脚本汇总 (Automation Scripts)

[![九号自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/ninebot.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/ninebot.yml)

[![什么值得买自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/smzdm.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/smzdm.yml)

本项目基于 GitHub Actions 实现每日自动执行任务，并集成 **Server 酱** 实现微信消息推送。主要包含 **九号 (Ninebot)** 和 **什么值得买 (SMZDM)** 的自动化逻辑。

---

## 📂 项目结构

```text
.
├── ninebot/                # 九号相关脚本 (Python)
│   ├── nine_bot_checkin.py      # 每日签到
│   ├── nine_bot_share_reward.py  # 分享领奖 (已集成日志记录)
│   ├── nine_bot_blind_box.py     # 盲盒里程碑检查 (汇总推送入口)
│   └── notification.py           # Python 通知与环境检查模块
├── smzdm/                  # 什么值得买相关脚本 (Node.js)
│   ├── smzdm_checkin.js          # 每日签到
│   ├── smzdm_task.js             # 每日任务 (阅读/关注/收藏等)
│   ├── smzdm_testing.js          # 全民众测能量值任务
│   ├── send_summary.js           # 汇总推送脚本 (新)
│   ├── bot.js / env.js           # 基础执行环境 (支持本地日志累加)
│   └── notification.js           # Server 酱 Node.js 通知模块
└── .github/workflows/      # GitHub Actions 自动化配置
    ├── main.yml                  # 九号任务流 (同步至 08:20 运行)
    └── smzdm.yml                 # 值得买任务流 (08:20 运行)
```

---

## ✨ 核心功能

### 🛡️ 运行安全 (Security)
- **环境检查**：所有脚本执行前会自动判断 `Secrets` 是否配置。若未配置（如 `SMZDM_COOKIE` 或 `NINEBOT_TOKEN`），脚本将停止执行并友好提示，避免无效请求。

### 🛴 九号 (Ninebot)
- **自动签到**：每日获取积分奖励。
- **任务领奖**：自动完成分享任务并领取对应奖励（已修复通知缺失问题，现在会详细展示分享与领奖状态）。
- **盲盒监控**：自动检查连续签到盲盒的剩余开启天数，到达里程碑时提醒领取。
- **汇总通知**：每日运行结束后，将签到、分享、领奖及盲盒进度汇总成**一条**微信消息推送。

### 🛍️ 什么值得买 (SMZDM)
- **多功能签到**：支持金币、碎银、经验值及补签卡获取。
- **智能任务**：自动执行阅读文章、达人关注、收藏、点赞等任务。
- **全民众测**：自动获取众测能量值（需开启 `SMZDM_TASK_TESTING='yes'`）。
- **汇总通知**：修复了原先通知缺失的问题。现在所有任务执行完毕后，会通过 `send_summary.js` 统一推送执行详情。

---

## 🚀 部署指南

### 1. 配置 Secrets (必须)
在 GitHub 仓库的 `Settings` -> `Secrets and variables` -> `Actions` 中添加以下变量：

| Secret 名称 | 归属项目 | 说明 |
| :--- | :--- | :--- |
| `NINEBOT_TOKEN` | 九号 | 抓包获取 `Authorization` 字段的完整 JWT |
| `DEVICE_ID` | 九号 | 抓包获取请求头中的 `device_id` (通常为 UUID) |
| `SMZDM_COOKIE` | 值得买 | 浏览器或 App 抓包获取的完整 Cookie 字符串 |
| `SERVER_CHAN_SEND_KEY` | 通用 | Server 酱官网获取的 `SCT` 推送密钥 |

### 2. 定时安排 (北京时间)

| 任务名称 | 运行时间 | 状态 |
| :--- | :--- | :--- |
| **什么值得买** | **08:20** | 每天自动运行 |
| **九号** | **08:20** | 每天自动运行 |

---

## ⚠️ 免责声明
1. 本项目脚本仅供学习交流使用，请勿用于非法用途。
2. 请合理设置运行频率，因使用不当导致的账号封禁等风险由用户自行承担。
3. 脚本中所涉及的第三方库版权归原作者所有。
