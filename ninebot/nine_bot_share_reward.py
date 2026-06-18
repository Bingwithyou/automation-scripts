import requests
import os
import time
import json
from notification import add_log, check_secrets

def format_json_block(title, payload):
    return f"{title}\n```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"

def do_share_and_collect_reward():
    # 从环境变量获取 Token 和 Device ID
    token = os.environ.get("NINEBOT_TOKEN")
    device_id = os.environ.get("NINEBOT_DEVICE_ID")

    # ================= 步骤一：执行分享任务 =================
    share_url = "https://cn-cbu-gateway.ninebot.com/app-api/circle/v1/share-callback"
    
    # 构建分享接口的专属 Headers
    share_headers = {
        "Host": "cn-cbu-gateway.ninebot.com",
        "User-Agent": "Ninebot/6.10.1 (cn.ninebot.segway; build:3676; iOS 26.3.1) Alamofire/5.6.1",
        "Access-Token": token,  
        "Device-Id": device_id, 
        "Content-Type": "text/html", 
        "Platform": "iOS",
        "Language": "zh",
        "App-Version": "610013676",
        "Accept": "application/json"
    }

    # 抓包提示：抓取 circle/v1/share-callback 请求，复制整个 Request Body 存入 NINEBOT_SHARE_PAYLOAD
    share_payload_str = os.environ["NINEBOT_SHARE_PAYLOAD"]
    share_payload = json.loads(share_payload_str)

    add_log("=== 九号分享与领奖 ===")
    add_log("开始执行分享任务...")
    try:
        share_response = requests.post(share_url, headers=share_headers, data=json.dumps(share_payload))
        share_response.raise_for_status()
        share_result = share_response.json()
        add_log(format_json_block("分享任务接口返回：", share_result))

    except Exception as e:
        add_log(f"请求分享接口时发生网络错误: {e}")
        return

    # ================= 等待缓冲 =================
    add_log("等待 3 秒后尝试领取奖励...")
    time.sleep(3)

    # ================= 步骤二：收取任务奖励 =================
    reward_url = "https://cn-cbu-gateway.ninebot.com/portal/self-service/task/reward"
    
    # 构建领奖接口的专属 Headers
    reward_headers = {
        "Host": "cn-cbu-gateway.ninebot.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Segway v6 C 610013676",
        "Authorization": token, 
        "device_id": device_id, 
        "Content-Type": "application/json",
        "Origin": "https://h5-bj.ninebot.com",
        "Referer": "https://h5-bj.ninebot.com/",
        "platform": "h5",
        "language": "zh",
        "sys_language": "zh-CN",
        "Accept": "application/json, text/plain, */*",
    }

    # 分享任务的ID
    reward_payload = {
        "taskId": "1823622692036079618"
    }

    add_log("开始领取任务奖励...")
    try:
        reward_response = requests.post(reward_url, headers=reward_headers, json=reward_payload)
        reward_response.raise_for_status()
        reward_result = reward_response.json()
        
        if reward_result.get("code") == 0:
            add_log("✅ 奖励领取成功！")
            add_log(format_json_block("领取任务奖励服务器返回：", reward_result))
        else:
            add_log("❌ 奖励领取失败。")
            add_log(format_json_block("领取任务奖励服务器返回：", reward_result))

    except Exception as e:
        add_log(f"❌ 请求领奖接口时发生网络错误: {e}")

# 当作为独立脚本运行时触发
if __name__ == "__main__":
    check_secrets(["NINEBOT_TOKEN", "NINEBOT_DEVICE_ID", "NINEBOT_SHARE_PAYLOAD"])
    do_share_and_collect_reward()
