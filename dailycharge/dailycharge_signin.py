# -*- coding: utf-8 -*-
"""
cron: 40 7 * * *
new Env('天天充电签到');
"""

import os
import sys
import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


SIGN_IN_URL = "https://api.cd1a.cn/index.php/driven19/Activity/sign"
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


def build_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "User-Agent": env(
            "DAILYCHARGE_USER_AGENT",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
            "MicroMessenger/8.0.75 NetType/WIFI Language/zh_CN",
        ),
        "Referer": env(
            "DAILYCHARGE_REFERER",
            "https://servicewechat.com/wx1625cc237a4195d9/245/page-frame.html",
        ),
    }


def build_payload() -> Dict[str, Any]:
    return {
        "integral": env("DAILYCHARGE_INTEGRAL", "10"),
        "userid_locked": env("DAILYCHARGE_USERID_LOCKED"),
        "uid": env("DAILYCHARGE_UID"),
        "newTime": int(time.time() * 1000),
        "userid_open": env("DAILYCHARGE_USERID_OPEN"),
        "scene": int(env("DAILYCHARGE_SCENE", "1089")),
        "version": env("DAILYCHARGE_VERSION", "4.2.38"),
        "platform": "applet",
        "ttcd_plus": env("DAILYCHARGE_PLUS", "0"),
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


def run_signin(session: Optional[requests.Session] = None) -> bool:
    add_log("### 天天充电 DailyCharge")
    required = [
        "DAILYCHARGE_UID",
        "DAILYCHARGE_USERID_LOCKED",
        "DAILYCHARGE_USERID_OPEN",
    ]
    missing = [name for name in required if not env(name)]
    if missing:
        add_log("- 运行失败")
        add_log(f"- 原因: 缺少环境变量 {', '.join(missing)}")
        return False

    active_session = session or create_session()
    try:
        response = active_session.post(
            SIGN_IN_URL,
            headers=build_headers(),
            json=build_payload(),
            timeout=(10, 30),
        )
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError("接口返回格式异常")

        message = str(result.get("msg") or "未知结果")
        return_code = str(result.get("return_code"))
        result_code = str(result.get("result_code"))
        if return_code == "200" and result_code == "352":
            add_log(f"- 签到成功: {message}")
            return True
        if return_code == "200" and result_code == "351":
            add_log(f"- 今日已签到: {message}")
            return True

        add_log("- 签到失败")
        add_log(f"- 原因: {message}")
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

        send("天天充电签到", "\n".join(_logs))
    except Exception:
        pass


def main() -> None:
    success = run_signin()
    send_standalone_summary()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
