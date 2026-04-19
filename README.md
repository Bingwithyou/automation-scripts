# Automation Scripts

[![九号自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/ninebot.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/ninebot.yml)
[![什么值得买自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/smzdm.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/smzdm.yml)
[![每日自动脚本](https://github.com/Bingwithyou/automation-scripts/actions/workflows/daily.yml/badge.svg)](https://github.com/Bingwithyou/automation-scripts/actions/workflows/daily.yml)

这是一个基于 GitHub Actions 的自动化脚本仓库，主要用于每天定时执行签到、任务领取和结果汇总，并通过 Server 酱发送通知。

目前包含五组脚本：

- `ninebot/`：九号 (Ninebot) App 自动化任务，使用 Python
- `smzdm/`：什么值得买 (SMZDM) App 自动化任务，使用 Node.js
- `mxbc/`：蜜雪冰城小程序自动化任务，使用 Node.js
- `zhcommerce/`：正弘城 签到任务，使用 Python
- `tastien/`：塔斯汀签到任务，使用 Python

## Features

### 九号 (Ninebot)

- 每日签到
- 自动执行分享任务并领取奖励
- 检查盲盒里程碑状态
- 运行结束后汇总推送消息

### 什么值得买 (SMZDM)

- 每日签到
- 自动完成部分日常任务
- 支持全民众测能量值任务
- 运行结束后汇总推送消息

### 蜜雪冰城 (MXBC)

- 调用 `getLoginUrl` 完成每日签到
- 签到后自动查询最新用户信息
- 当前展示雪王币数量
- 运行结束后汇总推送消息

### Common

- 基于 GitHub Actions 定时运行
- 支持手动触发 workflow
- 启动前自动检查关键环境变量
- 默认定时任务只发送 1 条统一汇总通知

### 正弘城 (Zhcommerce)

- 每日签到
- 支持本地计算签名并按当前时间戳请求接口
- 保留脚本文件，适合本地或服务器定时运行

### 塔斯汀 (Tastien)

- 支持多账号签到
- 自动拉取当月签到活动 ID
- 保留脚本文件，适合本地或服务器定时运行

## 运行方式建议

### 可直接使用 GitHub Actions 运行

- `ninebot/` (九号)
- `smzdm/` (什么值得买)

### 不建议使用 GitHub Actions 运行

- `mxbc/` (蜜雪冰城)
- `zhcommerce/` (正弘城)
- `tastien/` (塔斯汀)

这三个应用目前都更依赖国内网络环境，使用 GitHub Actions 这类海外出口 IP 容易出现连接超时、接口无响应或被网关拦截的情况。建议在本地、国内服务器或青龙面板运行。

### 青龙运行示例 (推荐)

仓库提供了一个组合签到脚本 `combined_signin.py`，可以一次性运行正弘城、塔斯汀和蜜雪冰城的任务，并合并发送一条通知。

#### 环境变量配置

在青龙面板中创建以下环境变量：

- `MXBC_ACCESS_TOKEN`：蜜雪冰城请求头中的 `Access-Token`
- `MXBC_SSOS_CID`：蜜雪冰城请求头中的 `x-ssos-cid`
- `ZH_ACCESS_TOKEN`：正弘城小程序请求中的 `accessToken`
- `ZH_DEVICE_ID`：正弘城小程序请求中的 `deviceId`
- `TASTIEN_USER_TOKENS`：塔斯汀小程序请求头中的 `user-token`，多账号可用 `&` 或 `@` 分隔
- `PUSH_KEY`：可选，Server 酱推送 Key（用于接收运行汇总通知）

**注意**：即使在青龙“系统设置”里配置了通知，建议也在“环境变量”里手动添加 `PUSH_KEY`，以确保脚本能正确读取。

同时拉取组合签到脚本和各单项脚本作为任务：

```bash
ql repo https://github.com/Bingwithyou/automation-scripts.git "combined_signin|tastien_checkin|zhcommerce_signin|mxbc_checkin" "notification|send_summary" "" "main" "py|js"
```

**参数说明：**

- 白名单：`"combined_signin|tastien_checkin|zhcommerce_signin|mxbc_checkin"`，导入组合脚本及各子脚本作为任务。
- 黑名单：`"notification|send_summary"`，防止将通知模块和独立汇总脚本误导入为任务。
- 后缀：`"py|js"`，同时寻找 Python 和 Node.js 文件。

导入后，脚本会自动识别文件内的 `# cron` 注释并设置默认定时。建议在青龙“依赖管理”中安装 `requests` 库，并确保青龙环境里可用 `node`。

## Project Structure

```text
.
├── .github/workflows/
│   ├── daily.yml
│   ├── ninebot.yml
│   └── smzdm.yml
├── combined_signin.py         # 组合签到入口（推荐青龙使用）
├── mxbc/                      # 蜜雪冰城相关脚本
│   ├── mxbc_checkin.js
│   ├── notification.js
│   └── send_summary.js
├── ninebot/                   # 九号相关脚本
│   ├── nine_bot_checkin.py
│   ├── nine_bot_share_reward.py
│   ├── nine_bot_blind_box.py
│   └── notification.py
├── smzdm/                     # 什么值得买相关脚本
│   ├── ...
├── zhcommerce/                # 正弘城相关脚本
│   ├── notification.py
│   └── zhcommerce_signin.py
├── tastien/                   # 塔斯汀相关脚本
│   ├── notification.py
│   └── tastien_checkin.py
├── requirements.txt
└── README.md
```

## Workflows

当前仓库有 3 个 GitHub Actions 工作流：

- `daily.yml`：默认定时任务。分别执行九号和什么值得买，并在最后统一发送 1 条汇总通知
- `ninebot.yml`：手动单独执行九号任务
- `smzdm.yml`：手动单独执行什么值得买任务

默认定时由 `daily.yml` 在每天北京时间 `07:00` 触发；其余 workflow 保留给手动排查或单独执行使用。

## Required Secrets

在仓库的 `Settings -> Secrets and variables -> Actions` 中配置以下变量。

### 九号 (Ninebot)

| Name | Required | Description |
| :--- | :--- | :--- |
| `NINEBOT_TOKEN` | Yes | 九号接口请求头中的 `Authorization` |
| `NINEBOT_DEVICE_ID` | Yes | 九号接口请求头中的 `device_id` |

### 什么值得买 (SMZDM)

| Name | Required | Description |
| :--- | :--- | :--- |
| `SMZDM_COOKIE` | Yes | 什么值得买账号的 Cookie |
| `SMZDM_SK` | No | 部分签到场景可用的附加参数 |

### 蜜雪冰城 (MXBC)

| Name | Required | Description |
| :--- | :--- | :--- |
| `MXBC_ACCESS_TOKEN` | Yes | 蜜雪冰城请求头中的 `Access-Token` |
| `MXBC_SSOS_CID` | Yes | 蜜雪冰城请求头中的 `x-ssos-cid` |

### Notification

| Name | Required | Description |
| :--- | :--- | :--- |
| `SERVER_CHAN_SEND_KEY` | No | Server 酱推送 key；未配置时会跳过汇总通知 |

### 正弘城 (Zhcommerce)

| Name | Required | Description |
| :--- | :--- | :--- |
| `ZH_ACCESS_TOKEN` | Yes | 正弘城小程序请求中的 `accessToken` |
| `ZH_DEVICE_ID` | Yes | 正弘城小程序请求中的 `deviceId` |

### 塔斯汀 (Tastien)

| Name | Required | Description |
| :--- | :--- | :--- |
| `TASTIEN_USER_TOKENS` | Yes | 塔斯汀小程序请求头中的 `user-token`，多账号可用 `&` 或 `@` 分隔 |

## Workflow Environment Variables

除了 GitHub Secrets，工作流里还使用了几个固定运行参数：

| Name | Current Value | Description |
| :--- | :--- | :--- |
| `SMZDM_TASK_TESTING` | `yes` | 启用全民众测能量值任务 |
| `SMZDM_CROWD_SILVER_5` | `no` | 不启用 5 碎银抽奖 |
| `SMZDM_COMMENT` | `点赞支持，感谢分享！` | 评论类任务使用的默认文案 |

zhcommerce 当前版本中的 `appKey`、`appUid`、`sid`、`mallId`、定位坐标、版本号和请求头都已经按现有抓包固定到脚本默认值里，默认只需要维护 `ZH_ACCESS_TOKEN` 和 `ZH_DEVICE_ID`，更适合放在本地服务器、国内云主机或青龙面板中运行。

tastien 当前版本没有在仓库里硬编码任何账号 token 或 device id，账号信息统一通过 `TASTIEN_USER_TOKENS` 传入，更适合放在本地服务器、国内云主机或青龙面板中运行。

mxbc 当前版本中的签名逻辑和固定请求参数都已经内置在脚本中，默认只需要维护 `MXBC_ACCESS_TOKEN` 和 `MXBC_SSOS_CID`。

如果你后续调整 workflow，这些值也建议和 README 保持同步。

## Local Run

如果需要本地调试，可以分别运行：

### 九号 (Ninebot)

```bash
pip install -r requirements.txt
python3 ninebot/nine_bot_checkin.py
python3 ninebot/nine_bot_share_reward.py
python3 ninebot/nine_bot_blind_box.py
```

### 什么值得买 (SMZDM)

```bash
npm install crypto-js got@11 tough-cookie
node smzdm/smzdm_checkin.js
node smzdm/smzdm_task.js
node smzdm/smzdm_testing.js
node smzdm/send_summary.js
```

### 蜜雪冰城 (MXBC)

```bash
MXBC_ACCESS_TOKEN=你的token MXBC_SSOS_CID=你的ssosCid node mxbc/mxbc_checkin.js
node mxbc/send_summary.js
```

### 正弘城 (Zhcommerce)

```bash
pip install -r requirements.txt
ZH_ACCESS_TOKEN=你的最新token ZH_DEVICE_ID=你的device_id python3 zhcommerce/zhcommerce_signin.py
```

### 塔斯汀 (Tastien)

```bash
pip install -r requirements.txt
TASTIEN_USER_TOKENS=你的user-token python3 tastien/tastien_checkin.py
```

多账号示例：

```bash
TASTIEN_USER_TOKENS="token1&token2" python3 tastien/tastien_checkin.py
```

本地运行前同样需要先设置对应环境变量。

## Notes

- 这类自动化依赖第三方平台接口，接口字段、风控策略和任务规则都可能变化。
- 如果 GitHub Actions 突然报错，优先检查 Secrets 是否失效、接口字段是否变更、任务是否下线。
- 如果应用明显依赖国内 IP 或小程序环境，优先考虑本地服务器、国内云主机或青龙面板，而不是 GitHub Actions。
- 日志推送属于辅助能力，即使通知失败，也不一定代表主任务全部失败。

## Disclaimer

- 本项目仅供学习和个人研究使用。
- 请自行评估账号风控和平台规则变更带来的风险。
- 使用本项目造成的任何后果，由使用者自行承担。
