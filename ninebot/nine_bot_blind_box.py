import os
import requests
import time
from notification import add_log, check_secrets, send_summary

REWARD_TYPE_LABELS = {
    1: "经验",
    2: "N币",
}


def is_receivable_box(box):
    reward_status = box.get("rewardStatus")
    left_days = box.get("leftDaysToOpen")

    if reward_status == 1:
        return True
    if left_days in (0, "0"):
        return True
    if left_days is None:
        return True
    return False

def check_blind_box():
    token = os.environ.get("NINEBOT_TOKEN")
    device_id = os.environ.get("NINEBOT_DEVICE_ID")
    
    if not token or not device_id:
        print("❌ 错误: 请设置环境变量 NINEBOT_TOKEN 和 NINEBOT_DEVICE_ID")
        return

    timestamp = int(time.time() * 1000)
    url = f"https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/blind-box/list?t={timestamp}"
    
    headers = {
        'Host': 'cn-cbu-gateway.ninebot.com',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': token,
        'platform': 'h5',
        'language': 'zh',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Segway v6 C 610013676',
        'device_id': device_id,
        'Origin': 'https://h5-bj.ninebot.com',
        'Referer': 'https://h5-bj.ninebot.com/',
        'sys_language': 'zh-CN'
    }

    try:
        response = requests.get(url, headers=headers)
        res_data = response.json()
        
        if res_data.get("code") != 0:
            add_log(f"❌ 获取盲盒列表失败: {res_data.get('msg')}")
            return

        boxes = res_data.get("data", {}).get("notOpenedBoxes", [])
        add_log("=== 九号盲盒检查 ===")
        add_log(f"📦 共有 {len(boxes)} 个未开启的盲盒里程碑")

        for box in boxes:
            award_days = box.get("awardDays")
            left_days = box.get("leftDaysToOpen")
            blind_box_ids = box.get("blindBoxIds") or []
            reward_id = blind_box_ids[0] if blind_box_ids else None
            reward_status = box.get("rewardStatus")

            if reward_status == 1:
                add_log(f"🔹 [{award_days}天]: 可立即开启")
            elif left_days is None:
                add_log(f"🔹 [{award_days}天]: 可立即开启")
            else:
                add_log(f"🔹 [{award_days}天]: 剩余 {left_days} 天可开启")

            if is_receivable_box(box):
                add_log(f"🎉 发现可领取的盲盒: {award_days}天里程碑!")
                open_blind_box(token, device_id, award_days, reward_id)

    except Exception as e:
        add_log(f"❌ 盲盒检查发生异常: {e}")

def format_reward_message(result):
    reward_info = result.get("data", {}) or {}
    reward_type = reward_info.get("rewardType")
    reward_value = reward_info.get("rewardValue")
    reward_label = REWARD_TYPE_LABELS.get(reward_type)

    if reward_label and reward_value is not None:
        return f"{reward_label} {reward_value}"
    if reward_value is not None:
        return str(reward_value)
    return "未知奖励"

def open_blind_box(token, device_id, days, reward_id):
    if not reward_id:
        add_log(f"❌ {days}天盲盒缺少 rewardId，跳过领取")
        return

    add_log(f"🚀 开始领取 {days} 天盲盒奖励")

    url = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/blind-box/receive"
    headers = {
        "Host": "cn-cbu-gateway.ninebot.com",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Authorization": token,
        "platform": "h5",
        "Origin": "https://h5-bj.ninebot.com",
        "language": "zh",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Segway v6 C 610023688",
        "Referer": "https://h5-bj.ninebot.com/",
        "device_id": device_id,
        "sys_language": "zh-CN",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    }
    payload = {"rewardId": str(reward_id)}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if response.status_code != 200:
            add_log(f"❌ 领取失败，状态码: {response.status_code}")
            return

        if result.get("code") == 0:
            add_log(f"✅ {days}天盲盒领取成功: {format_reward_message(result)}")
        else:
            add_log(f"❌ {days}天盲盒领取失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        add_log(f"❌ {days}天盲盒领取异常: {e}")

if __name__ == "__main__":
    check_secrets(["NINEBOT_TOKEN", "NINEBOT_DEVICE_ID"])
    check_blind_box()
    send_summary()
