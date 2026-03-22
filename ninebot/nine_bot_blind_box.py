import os
import requests
import time
import json
from notification import add_log, check_secrets, send_summary

def check_blind_box():
    token = os.environ.get("NINEBOT_TOKEN")
    device_id = os.environ.get("DEVICE_ID")
    
    if not token or not device_id:
        print("❌ 错误: 请设置环境变量 NINEBOT_TOKEN 和 DEVICE_ID")
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
            
            add_log(f"🔹 [{award_days}天]: 剩余 {left_days} 天可开启")
            
            if left_days == 0:
                add_log(f"🎉 发现可领取的盲盒: {award_days}天里程碑!")
                open_blind_box(token, device_id, award_days)

    except Exception as e:
        add_log(f"❌ 盲盒检查发生异常: {e}")

def open_blind_box(token, device_id, days):
    """
    领取奖励的逻辑 (占位)
    """
    add_log(f"🚀 准备执行领取接口... (针对 {days} 天盒子)")
    add_log("⚠️ 领取接口尚未配置。")

if __name__ == "__main__":
    check_secrets(["NINEBOT_TOKEN", "DEVICE_ID"])
    check_blind_box()
    send_summary()
