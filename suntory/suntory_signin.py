# -*- coding: utf-8 -*-
"""
cron: 35 7 * * *
new Env('三得利签到');
"""

import os
import sys
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://xiaodian.miyatech.com"
SIGN_IN_PATH = "/api/coupon/auth/signIn"
MEMBER_INFO_PATH = "/api/user/member/info"
COMBINED_SUMMARY_MODE = os.environ.get("COMBINED_SUMMARY_MODE", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

_logs = []


def add_log(content: str) -> None:
    print(content)
    _logs.append(content)


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def normalize_authorization(value: str) -> str:
    if value.lower().startswith("bearer "):
        return value
    return f"bearer {value}"


def build_headers() -> Dict[str, str]:
    return {
        "Authorization": normalize_authorization(env("SUNTORY_AUTHORIZATION")),
        "Content-Type": "application/json;charset=UTF-8",
        "componentSend": "1",
        "HH-APP": env("SUNTORY_HH_APP", "wxb33ed03c6c715482"),
        "HH-VERSION": env("SUNTORY_HH_VERSION", "0.6.8"),
        "HH-FROM": env("SUNTORY_HH_FROM", "20230130307725"),
        "appPublishType": "1",
        "HH-CI": "saas-wechat-app",
        "X-VERSION": env("SUNTORY_X_VERSION", "2.3.7"),
        "User-Agent": env(
            "SUNTORY_USER_AGENT",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
            "MicroMessenger/8.0.75 NetType/WIFI Language/zh_CN",
        ),
        "Referer": env(
            "SUNTORY_REFERER",
            "https://servicewechat.com/wxb33ed03c6c715482/78/page-frame.html",
        ),
    }


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=None,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def post_json(
    session: requests.Session, path: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    response = session.post(
        f"{BASE_URL}{path}",
        headers=build_headers(),
        json=payload,
        timeout=(10, 30),
    )
    response.raise_for_status()
    result = response.json()
    if not isinstance(result, dict):
        raise ValueError("接口返回格式异常")
    return result


def is_success(result: Dict[str, Any]) -> bool:
    return str(result.get("code")) == "200" and result.get("success") is True


def result_message(result: Dict[str, Any]) -> str:
    return str(result.get("msg") or result.get("detail") or "未知错误")


def run_signin(session: Optional[requests.Session] = None) -> bool:
    add_log("### 三得利 Suntory")
    authorization = env("SUNTORY_AUTHORIZATION")
    if not authorization:
        add_log("- 运行失败")
        add_log("- 原因: 缺少环境变量 SUNTORY_AUTHORIZATION")
        return False

    active_session = session or create_session()
    try:
        sign_result = post_json(
            active_session,
            SIGN_IN_PATH,
            {"miniappId": int(env("SUNTORY_MINIAPP_ID", "159"))},
        )
        if not is_success(sign_result):
            add_log("- 签到失败")
            add_log(f"- 原因: {result_message(sign_result)}")
            return False

        reward = (sign_result.get("data") or {}).get("integralToastText") or "签到成功"
        add_log(f"- 签到成功: {reward}")

        # 只有签到成功后才查询会员信息。
        member_result = post_json(active_session, MEMBER_INFO_PATH, {})
        if not is_success(member_result):
            add_log(f"- 用户信息查询失败: {result_message(member_result)}")
            return False

        member = member_result.get("data") or {}
        grade = member.get("gradeName") or "未知"
        score = member.get("currentScore")
        add_log(f"- 当前等级: {grade}")
        add_log(f"- 当前积分: {score if score is not None else '未知'}")
        return True
    except requests.RequestException as exc:
        add_log("- 运行失败")
        add_log(f"- 原因: 网络请求异常: {exc}")
    except (TypeError, ValueError) as exc:
        add_log("- 运行失败")
        add_log(f"- 原因: {exc}")
    return False


def send_standalone_summary() -> None:
    if COMBINED_SUMMARY_MODE:
        return
    try:
        sys.path.extend(["/ql/data/scripts", "/ql/scripts"])
        from notify import send

        send("三得利签到", "\n".join(_logs))
    except Exception:
        pass


def main() -> None:
    success = run_signin()
    send_standalone_summary()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
