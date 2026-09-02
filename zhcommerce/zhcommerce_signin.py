# -*- coding: utf-8 -*-
"""
cron: 45 7 * * *
new Env('zhcommerce签到');
"""

import hashlib
import json
import os
import random
import string
import sys
import time
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zh_security

# --- 青龙内置通知适配 ---
def get_notify():
    try:
        sys.path.append("/ql/data/scripts")
        sys.path.append("/ql/scripts")
        from notify import send
        return send
    except Exception:
        return None

_logs = []
COMBINED_SUMMARY_MODE = os.environ.get("COMBINED_SUMMARY_MODE", "").lower() in {"1", "true", "yes", "on"}

def add_log(content):
    print(content)
    _logs.append(content)


def add_summary(title, details=None):
    add_log(f"### {title}")
    for detail in details or []:
        add_log(f"- {detail}")

def check_secrets(keys):
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        msg = f"❌ 缺少环境变量: {', '.join(missing)}"
        add_log(msg)
        send_summary("环境变量配置错误")
        sys.exit(1)

def send_summary(title_suffix=""):
    title = f"zhcommerce签到 {'- ' + title_suffix if title_suffix else ''}"
    content = "\n".join(_logs)
    send = get_notify()
    if send:
        send(title, content)
    else:
        print("\n" + "="*10 + " 运行汇总 " + "="*10)
        print(content)

# --- 脚本逻辑 ---
APP_KEY = "OW5OGNWC"
API_BASE = "https://m.zhcommerce.com/api/v3"
DEFAULT_APP_UID = "EZy8xWW3qzX7wtKA"
DEFAULT_SID = DEFAULT_APP_UID
DEFAULT_MALL_ID = "301"
DEFAULT_LAT = "34.80280327690972"
DEFAULT_LON = "113.69084635416667"
DEFAULT_APP_VERSION = "3.2.86"
DEFAULT_CUSTOM_VERSION = "9"
DEFAULT_OS_VERSION = "iOS 27.0"
DEFAULT_MODEL = "iPhone 15 pro max<iPhone16,2>"
DEFAULT_SDK_VERSION = "3.17.2"
DEFAULT_PROGRAM_VERSION = "8.0.76"
DEFAULT_SCENE_VALUE = "1104"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.76(0x18004c31) NetType/WIFI Language/zh_CN"
)


def env(name, default=""):
    return os.environ.get(name, default).strip()


def requests_retry_session(retries=3, backoff_factor=1):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=None,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"Connection": "close"})
    return session


def random_mixed(length):
    alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
    return "".join(random.choice(alphabet) for _ in range(length))


def build_request_config(sess):
    timestamp = int(time.time())
    body = {
        "lat": float(env("ZH_LAT", DEFAULT_LAT)),
        "lon": float(env("ZH_LON", DEFAULT_LON)),
        "mallId": env("ZH_MALL_ID", DEFAULT_MALL_ID),
    }
    body_json = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    query_params = {
        "currentPageType": "user",
        "clientType": "mini_weixin",
        "appUStatus": "1",
        "appVersion": DEFAULT_APP_VERSION,
        "customVersion": DEFAULT_CUSTOM_VERSION,
        "osVersion": DEFAULT_OS_VERSION,
        "model": DEFAULT_MODEL,
        "clientAppName": "memberClient",
        "rnd": random_mixed(30),
        "appKey": APP_KEY,
        "sid": env("ZH_SID", DEFAULT_SID),
        "appUid": env("ZH_APP_UID", DEFAULT_APP_UID),
        "deviceId": env("ZH_DEVICE_ID"),
        "sdkVersion": DEFAULT_SDK_VERSION,
        "programVersion": DEFAULT_PROGRAM_VERSION,
        "sceneValue": DEFAULT_SCENE_VALUE,
        "mallId": env("ZH_MALL_ID", DEFAULT_MALL_ID),
        "timestamp": timestamp,
        "accessToken": sess.get("accessToken") or env("ZH_ACCESS_TOKEN"),
    }
    sign_params = dict(query_params)
    sign_params["body"] = body_json
    path = f"member/{env('ZH_APP_UID', DEFAULT_APP_UID)}/signs"
    query_params["sign"] = zh_security.build_sign(sign_params, path, timestamp, sess)
    query_params["signType"] = "sha"
    return body, query_params


def build_url(uid, params):
    query = urlencode(
        [(key, str(value)) for key, value in params.items() if value not in ("", None)]
    )
    return f"{API_BASE}/member/{uid}/signs?{query}"


def run_signin():
    device_id = env("ZH_DEVICE_ID")
    cached = zh_security.load_session()
    sess = zh_security.ensure_session(device_id)
    uid = env("ZH_APP_UID", DEFAULT_APP_UID)

    add_log("### zhcommerce 每日签到报告\n")
    if cached and zh_security.session_valid(cached):
        add_log("> **设备会话**: 复用缓存会话")
    else:
        add_log("> **设备会话**: 本次新注册")

    result = None
    response = None
    for attempt in (1, 2):
        body, params = build_request_config(sess)
        url = build_url(uid, params)
        headers = {
            "Content-Type": "application/json",
            "EncryptBody": "false",
            "Mobcb-Encrypt": "true",
            "Mobcb-DevicesRegisterCheck": "true" if sess.get("devicesRegisterCheck") else "false",
            "User-Agent": DEFAULT_USER_AGENT,
            "Referer": "https://servicewechat.com/wxd4680abecbc3f014/354/page-frame.html",
        }

        add_log(f"> **时间戳**: `{params['timestamp']}`")
        add_log(f"> **签名**: `{params['sign']}`\n")

        session = requests_retry_session()
        response = session.post(
            url,
            headers=headers,
            data=json.dumps(body, separators=(",", ":"), ensure_ascii=False),
            timeout=(10, 30),
        )
        add_log(f"- **HTTP 状态**: `{response.status_code}`")
        try:
            result = response.json()
        except Exception:
            result = {"raw": response.text}

        add_log("```json")
        add_log(json.dumps(result, ensure_ascii=False, indent=2))
        add_log("```")

        if attempt == 1 and result.get("errorCode") == "PUB-00006":
            add_log("⚠️ **访问检查失败**, 强制重新注册设备后重试...")
            sess = zh_security.register_device(device_id)
            zh_security.save_session(sess)
            continue
        break

    if response is not None and response.status_code == 200 and result.get("errorCode") == "PUB-00000":
        reward = ((result.get("body") or {}).get("signInCreditValue")) or "0"
        continuous_days = (result.get("body") or {}).get("continuousDays")
        add_log("✅ **签到成功**")
        add_log(f"- 奖励积分: `{reward}`")
        add_log(f"- 连续签到: `{continuous_days}` 天")
    elif response is not None and response.status_code == 200 and result.get("errorCode") == "MBR-00029":
        message = result.get('errorMessage', '会员今天已签到')
        add_log("ℹ️ **今天已签到**")
        add_log(f"- 接口返回: {message}")
    else:
        error_message = (result or {}).get("errorMessage") or (result or {}).get("message") or \
                        (result or {}).get("raw") or f"HTTP {response.status_code if response is not None else '?'}"
        add_log("❌ **签到失败**")
        add_log(f"- 失败原因: {error_message}")


def main():
    check_secrets(["ZH_DEVICE_ID"])
    run_signin()


if __name__ == "__main__":
    main()
