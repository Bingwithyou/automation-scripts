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

    # 加密 Payload
    share_payload = {
        "k": "F12JvkpNeV8Jlhu/YPi4o56+enLTyFrhWqAluv5GU6ZZNoWTdhv0obhoIRwglUA2z4CyfnWGxhNC1/Qygpxz49NVCERFaapH3qxGiLh8FzgASkVy95aPayD88EM5xIefENWLmZ3rsDoUtHNCjBFcsdp7N/C67Zz6hf+4ZM83Wno=",
        "p": 101,
        "d": "gZcxTIYSxFaXL0zLFn8zVb2+OxHmXMYsEhp/NAEfc+RTWMCT8WdRsBHwjCARrP992jCayUL7szKeQ0Rb2DQ7Y0R7A5pdsifUmuKLgefYXMfVkjTJnDZS6H8OrZJX5kcvT490mZFpH8k1SyN6LaUyQuOBPq7CTC4DN4Qv+dVZWS9HE4KFeoy2dnw4WcIf2eOVOrqfSDQw+A9eNd1rCg+DGoLClZd6i6bDthKCFGxmgeAWlgxa8dvUntTa6JKP0L5nPkw2vcTlOQy9F9/QoAdqHy4ZXmp3PUdvjap1TaQTe5auG4qHa4iqstr5g4NmK1PZm0PLagMZBfzwlvpngs2+er+3NZ/Ae++j2VQv9aYWCwbW0DGVp3R8NkDB0RNe+yWFYUCxadU+b1DvYfNeBBA2BwAUJTfCieRxBveWaQx4Dcz7Cg4RsObRPLmDZbfEhTqbXYoHNI1LJi9kdzTmtq6V8u8Pkw5xmJQvgsh0YSgFbQ87FaLn64sYxiRCX9g4IkKD9ja42fj2bKCCUBlb5/0q10xKOogoKlG9zYqN9CSd8hbLAHbZ2Y8IyPrA+/NqRtPd1dcZSHb3/9A0nNKQCkvmUqmSH6PPb/WJh3CF/WgCzomxS7uNy44qzth5prEKpoNQ05lmRG3ZkE06MleLOG7nZ31g9Pgus5dsBSGoUxMooiWCoUsW8PC2DU6bq0V+prrHr+piQmenCo4R+Vd9T2SxAIDhncoxKWfIPHsRivSs1zfRuP3plUDLVi0x/yJwtHwF++69f33KeZbyO+jE04QXlFyIbPESTBRQ5ReRXNUnQWeqV0SB50MzaOJq+KJVHlA8ewkn6hqlZQ5odaiSFxtyJqEJI7GgYrbsAA9d4UJU6/djRPiYSf1Ds52/YYCvQWA1v6EjF/2hxi+HEQG/B7SLQwFPuKaRXpLAlDa8RMP0p0wXGstTZ02cMd7JBPTlKN5uQp+zwsEzNDQvhjoXkLHJ1seqmO5I87Z5675dV0DgilnOUa3ycsWfPXChqWnuW5uOkwd7U6gpuNgF4tAVg7ybEdFMhUCo7jQ7v4Mc+6BnwHVWwruv6204KCqfdn0Mj51I3otUXnvw6w4wmaojNUZo3+6Tde9C3HVpxC2mhfeyo93rbFC8lYP0x9bZyh7hOFzql/OckrIrNtM4V2lDBbCwbOFRV+0aWMrOS0OfwvqUrzyA0zxkxJWWR6PMYlHEKc493ZJbcrss97nYByLc7gbBnXAdcOF8kf7EES0MRUfGuDxnszj9B/nh2ngtANHZe7EXSkMA4MGIGpo/1UmN8nnz24TOqF3kj5dk0WAFsHLxhDtjxc690CMj5Gjvp/1WQ31rs+az7c7VzlZZt+9DLFsaPSIIke+4Ci7+5oF+aiu/Ab9k0L86JrBEvphzS0nDE8B1DQS7I8F5zb7BbIpkJ7fczQD2CC1U4Hl5BqQtKdpjkPYuc86AfX5mmm+m99PH0XiZijHYT8gYJJ0V4+QHzHTKWHS7v1P9j+GDeh35hDcmmMPA2oClWywgYB22ZBr5kJ5ASGsFhBYhVr6RfMPl4dYHFE9xTnpd3gUQAaMXct2nh7/Yj4qHzGIH+n/MajAvtiph0fLaPoFZMWBkwC5W8aCn5nlDy07+ZqTWrFMHCwXziHR26C+0uPhYtM+lawQGO0jdXMjjvdsvqmZpsTglAJNynHEGjZH0N0tpmYtwFm+C6j5wE0vMjqBYfN3lFCEWM8GV7CHiu4qWiy9x3BNubVtntA1E42g/Y0ZdSTCxdS9fH6xxjodH2oxxJ+0QuTAw15Vbdw7fjNBMxd80VXTGnDAbEV2j/stzGuJbtjPjnWomBbfu/enwbafaBhdNubPWFZpnTjyzbeYzE9PfOMxxcYvqubkelBlMdNWVekpohx1D3ueFVGs3guO2oGIclI2QyLp5xQX0NKmYpXYyHZgJsNFjDknRjYEO0kK3e1N28kWmq5U=",
        "h": "346a0efe0c19f73d80a0373fb358622b",
        "t": 0
    }

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
    check_secrets(["NINEBOT_TOKEN", "NINEBOT_DEVICE_ID"])
    do_share_and_collect_reward()
