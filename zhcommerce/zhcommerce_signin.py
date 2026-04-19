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
import time
import sys
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    title = f"zhcommerce签到 {'- ' + title_suffix if title_suffix else ''}"
    content = "\n".join(_logs)
    send = get_notify()
    if send:
        send(title, content)
    else:
        print("\n" + "="*10 + " 运行汇总 " + "="*10)
        print(content)

# --- 脚本逻辑 ---
WAP_KEYS = [
    "N94QKAZD289GQARELPOJQGZM8",
    "GFNCV79W9U1CYFEXQ904OI6BB",
    "C1BOEMXCP1A5KUBVQIXKGBH51",
    "0RU2DV7E67T7ZMPQXWAVD99MY",
    "EPOJKLVKIQQMGG9XWT9C28F5C",
    "8GTBBWEADC6RG237EUEC7KZFU",
    "1XP3TLH0BZMZS7TT3TF7JD500",
    "TNFVOH7WHTC4NCD6SI9QZ3W5N",
    "ZZNEL2ULF9TPAC9NU3493GL7I",
    "8SABWT2MB1JOHOM02QVN36TGI",
]

APP_KEY = "OW5OGNWC"
API_BASE = "https://m.zhcommerce.com/api/v3"
DEFAULT_APP_UID = "EZy8xWW3qzX7wtKA"
DEFAULT_SID = DEFAULT_APP_UID
DEFAULT_MALL_ID = "201"
DEFAULT_LAT = "34.80280327690972"
DEFAULT_LON = "113.69084635416667"
DEFAULT_APP_VERSION = "3.2.73"
DEFAULT_CUSTOM_VERSION = "9"
DEFAULT_OS_VERSION = "iOS 26.4"
DEFAULT_MODEL = "iPhone 15 pro max<iPhone16,2>"
DEFAULT_SDK_VERSION = "3.15.2"
DEFAULT_PROGRAM_VERSION = "8.0.70"
DEFAULT_SCENE_VALUE = "1104"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_4 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.70(0x18004634) NetType/WIFI Language/zh_CN"
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


def build_sign_source(params, timestamp):
    items = []
    for key in sorted(params.keys()):
        value = params[key]
        if value in ("", None):
            continue
        items.append(f"{key}={value}")
    raw = "&".join(items) + WAP_KEYS[timestamp % 10]
    sign = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return raw, sign


def build_request_config():
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
        "accessToken": env("ZH_ACCESS_TOKEN"),
    }
    sign_params = dict(query_params)
    sign_params["body"] = body_json
    sign_source, sign = build_sign_source(sign_params, timestamp)
    query_params["sign"] = sign
    query_params["signType"] = "sha"
    return body, query_params, sign_source


def build_url(uid, params):
    query = urlencode(
        [(key, str(value)) for key, value in params.items() if value not in ("", None)]
    )
    return f"{API_BASE}/member/{uid}/signs?{query}"


def run_signin():
    uid = env("ZH_APP_UID", DEFAULT_APP_UID)
    body, params, sign_source = build_request_config()
    url = build_url(uid, params)
    headers = {
        "Content-Type": "application/json",
        "EncryptBody": "false",
        "Mobcb-Encrypt": "true",
        "User-Agent": DEFAULT_USER_AGENT,
        "Referer": "https://servicewechat.com/wxd4680abecbc3f014/339/page-frame.html",
    }

    add_log("### zhcommerce 每日签到报告\n")
    add_log(f"> **时间戳**: `{params['timestamp']}`")
    add_log(f"> **签名**: `{params['sign']}`\n")

    try:
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

        if response.status_code == 200 and result.get("errorCode") == "PUB-00000":
            reward = ((result.get("body") or {}).get("signInCreditValue")) or "0"
            continuous_days = (result.get("body") or {}).get("continuousDays")
            add_log("✅ **签到成功**")
            add_log(f"- 奖励积分: `{reward}`")
            add_log(f"- 连续签到: `{continuous_days}` 天")
        elif response.status_code == 200 and result.get("errorCode") == "MBR-00029":
            add_log("ℹ️ **今天已签到**")
            add_log(f"- 接口返回: {result.get('errorMessage', '会员今天已签到')}")
        else:
            add_log("❌ **签到失败**")
            add_log("```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```")
    except Exception as exc:
        add_log(f"❌ **执行异常**: {exc}")
        raise


def main():
    check_secrets(["ZH_ACCESS_TOKEN", "ZH_DEVICE_ID"])
    run_signin()


if __name__ == "__main__":
    main()
