# -*- coding: utf-8 -*-
"""
cron: 30 7 * * *
new Env('塔斯汀签到');
"""

import json
import os
import sys
from datetime import datetime
from typing import List

import requests

# --- 青龙内置通知适配 ---
def get_notify():
    try:
        # 尝试导入青龙内置的 notify 模块
        sys.path.append("/ql/data/scripts")
        sys.path.append("/ql/scripts")
        from notify import send
        return send
    except Exception:
        return None

_logs = []

def add_log(content):
    print(content)
    _logs.append(content)

def check_secrets(keys):
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        msg = f"❌ 缺少环境变量: {', '.join(missing)}"
        add_log(msg)
        send_summary("环境变量配置错误")
        sys.exit(1)

def send_summary(title_suffix=""):
    title = f"塔斯汀签到 {'- ' + title_suffix if title_suffix else ''}"
    content = "\n".join(_logs)
    send = get_notify()
    if send:
        send(title, content)
    else:
        print("\n" + "="*10 + " 运行汇总 " + "="*10)
        print(content)

# --- 脚本逻辑 ---
BASE_URL = "https://sss-web.tastientech.com"
APP_VERSION = "1.46.8"
FALLBACK_ACTIVITY_BASE_ID = 59
FALLBACK_ACTIVITY_START_DATE = "2025-05-01"


def split_tokens(raw_tokens: str) -> List[str]:
    tokens = []
    for chunk in raw_tokens.replace("@", "&").split("&"):
        token = chunk.strip()
        if token:
            tokens.append(token)
    return tokens


def build_headers(user_token: str):
    return {
        "user-token": user_token,
        "version": APP_VERSION,
        "channel": "1",
    }


def months_between_today(start_date: str) -> int:
    current_date = datetime.today()
    start = datetime.strptime(start_date, "%Y-%m-%d")
    return (current_date.year - start.year) * 12 + current_date.month - start.month


def fetch_activity_id(session: requests.Session, headers):
    payload = {
        "shopId": "",
        "birthday": "",
        "gender": 0,
        "nickName": None,
        "phone": "",
    }
    response = session.post(
        f"{BASE_URL}/api/minic/shop/intelligence/banner/c/list",
        json=payload,
        headers=headers,
        timeout=30,
    )
    result = response.json()

    for item in result.get("result", []):
        banner_name = item.get("bannerName", "")
        if "每日签到" in banner_name or "签到" in banner_name:
            jump_para = item.get("jumpPara", "{}")
            activity_id = json.loads(jump_para).get("activityId")
            if activity_id:
                return activity_id

    return None


def get_fallback_activity_id():
    return FALLBACK_ACTIVITY_BASE_ID + months_between_today(FALLBACK_ACTIVITY_START_DATE)


def fetch_member_phone(session: requests.Session, headers):
    response = session.get(
        f"{BASE_URL}/api/intelligence/member/getMemberDetail",
        headers=headers,
        timeout=30,
    )
    result = response.json()

    if result.get("code") != 200:
        raise ValueError(result.get("msg", "获取会员信息失败"))

    phone = result.get("result", {}).get("phone")
    if not phone:
        raise ValueError("接口未返回手机号")

    return phone


def sign_in(session: requests.Session, headers, activity_id, phone):
    payload = {
        "activityId": activity_id,
        "memberName": "",
        "memberPhone": phone,
    }
    response = session.post(
        f"{BASE_URL}/api/sign/member/signV2",
        json=payload,
        headers=headers,
        timeout=30,
    )
    return response.json()


def format_reward(sign_result):
    rewards = sign_result.get("result", {}).get("rewardInfoList") or []
    if not rewards:
        return "接口未返回奖励信息"

    reward = rewards[0]
    reward_name = reward.get("rewardName")
    if reward_name:
        return f"**获得 {reward_name}**"

    point = reward.get("point")
    if point is not None:
        return f"**获得 {point} 积分**"

    return "签到成功，但奖励信息为空"


def run_for_account(user_token: str, index: int):
    add_log(f"#### 账号 {index} 运行结果")
    session = requests.Session()
    headers = build_headers(user_token)

    try:
        activity_id = None
        try:
            activity_id = fetch_activity_id(session, headers)
        except Exception as exc:
            add_log(f"> ⚠️ 获取活动 ID 失败: {exc}")

        if not activity_id:
            activity_id = get_fallback_activity_id()
            add_log(f"> ℹ️ 使用兜底 ID: `{activity_id}`")
        else:
            add_log(f"> ✅ 获取活动 ID: `{activity_id}`")

        phone = fetch_member_phone(session, headers)
        masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone
        add_log(f"> ✅ 登录成功: `{masked_phone}`")

        result = sign_in(session, headers, activity_id, phone)
        if result.get("code") == 200:
            add_log(f"> ✅ 签到结果: {format_reward(result)}")
        else:
            add_log(f"> ❌ 签到失败: {result.get('msg', '未知错误')}")
    except Exception as exc:
        add_log(f"> ❌ 执行异常: {exc}")
    add_log("")


def main():
    check_secrets(["TASTIEN_USER_TOKENS"])

    raw_tokens = os.environ.get("TASTIEN_USER_TOKENS", "")
    user_tokens = split_tokens(raw_tokens)
    if not user_tokens:
        add_log("❌ 未解析到可用账号，请检查 TASTIEN_USER_TOKENS")
        send_summary("配置错误")
        return

    add_log(f"### 塔斯汀签到汇总报告\n")
    add_log(f"- 检测到账号数: {len(user_tokens)}")
    add_log("-" * 20 + "\n")
    
    for index, user_token in enumerate(user_tokens, start=1):
        run_for_account(user_token, index)


if __name__ == "__main__":
    main()
