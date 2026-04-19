import requests
import json
import os
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from notification import add_log, check_secrets

def requests_retry_session(retries=5, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=False,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({"Connection": "close"})
    return session

def daily_sign():
    # 从环境变量获取敏感信息
    token = os.environ.get("NINEBOT_TOKEN")
    device_id = os.environ.get("NINEBOT_DEVICE_ID")
    
    url = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/sign"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "platform": "h5",
        "language": "zh",
        "sys_language": "zh-CN",
        "device_id": device_id,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }

    payload = {"deviceId": device_id}

    try:
        session = requests_retry_session()
        response = None
        last_error = None

        for attempt in range(1, 4):
            try:
                response = session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=(10, 30),
                )
                break
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt == 3:
                    raise
                time.sleep(attempt)

        add_log("=== 九号每日签到 ===")
        if response is not None and response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                add_log("✅ 签到成功！")
            else:
                add_log(f"❌ 签到结果: {result.get('msg')}")
        else:
            status_code = response.status_code if response is not None else "未知"
            add_log(f"❌ 签到失败。状态码: {status_code}")
    except Exception as e:
        add_log(f"❌ 签到发生错误: {str(e)}")

def main():
    check_secrets(["NINEBOT_TOKEN", "NINEBOT_DEVICE_ID"])
    daily_sign()

if __name__ == "__main__":
    main()
