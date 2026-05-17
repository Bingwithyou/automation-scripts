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
        "k": "KNhHmPDZ221B6hzzNbKJLj1Eyo\/zo+sYJ6jZa1BkGNF9RULrhAq\/Wrdj4LYpMbiZgqN2kqQjiu2iXvVDRhJ1WBc1000I9htvIMeJeMywbffqBuQucSnK1n+VIjpotwXsFrKO3TFl9n\/b\/IFapVX80NssejpFMsbqO3w4T2GhnYM=",
        "p": 101,
        "d" : "AeFXZGo90c3OE07kkHpF2TkIG8Ot0DBZ3LVjj7hS2N3kF69HR8UoG83lTDzLgxoQXiMLv\/WwFuSGB\/hi6X5mx3Q8XV6P+qINQqM0+teEX8bWI72N65uFEkvuxjlMEp6cIwN0C+WELQAMrVf1UZmFW77U3\/I85wHNLITeupnI5XMcS74Q1l45spS2PMuLRmURnM2PiSzM7MOizCpRex0ND1hMsaOmf6WBTDvowYT\/IIC4ns69ZewRsDXw0EPuGbZPvtFFvIrU3GPyHxKeEyRMy7ecCauXc2AUvcp6BUBvWXRKeZGwjFTqNbVswjfqS8sWovBhzqY4IfJhxdALWXYrL4zVqD\/1wmgktXGjsQnOkKS3WjrKlwUo4wq0vvEVXjt4nhjwU+3YyjUOiIPsF0Q0VTK70Shop\/fhuRYs42y+EjaRvu5LqXeNJ\/WKeQg6zkzvLEYan9ERe7lgkO5UoX3jOk+8B0yTtd7x1GkmzfjEStMn1XlYXJA4zltrO8WnqrIR+LOXrDQrzC7OGAm48JYkaLLSSEQg3EeOChuPZzkPHng8oKoeF5nd5ADxh1XS+mVUhzvTdAv5KbH6WQb+6lzjiDFo7ZW8acmKuAxpKACuqo+tlKyhEPuESBuwqttLymATJA4QeEKJ07QdhZQm3uVdqt4rMHn4tJFlE1G3fIXgRasKmNhvw7cm+tmTOpMEX7QS08IsYdPzELLe9nyaBqVhjMSgc8H43spvfSYa3B8yUF7Gk33H\/4v82WLz1VK9wdWOLX0id8ps8fkPv\/UbzyGCL1eB1HCVBDNUpGznLh5vqLj1zYql4+pdyVGM7Yo6gC\/LmbmHTGd2FgdHo6OZQXj22UDu8Tjukjdh8qXWvaFDgIVsF1N2U3S5V5czzjkJwalwKRtTz+brPePYu9T\/5MiMXjKNmmUczW+bkfbcNKr12cedrjHiwEn9hOVvofKBp5z0RdZH4KIqR7HT3GvXXG3X0EaxSLpjbt7UWql2D66kAFnl2vE2WetrlC78yny1BTdaKOHoDD9TLYpvZ5sNEgGL2Io+Vj6E0+qu4HpAf2XPCvaDPkHOWUz\/\/i85vyfmyqj2kT7OUYMsX0JB\/GC4zxCfWvA5rr+zwbPs4+F0cqTb1MsDcUV0rFoS5Kk96ZMUePhrA1Gl5WyG1QuAH0jkuI5y2pYLm0GJIX\/OsQjX2TNDnIiba1f0GDMyxQJ812lugKJlvBhEIZ\/Fpnz0E90tJ0818i97MUt4t6c0jDe89fgcldIaOpcINuIB2axyaW+pp8crlqPsguF5zLTsEKirvI1C5A7FBR3Vu97NEe1JX0udlOdsCxqmYw9Wjuq62ZMamZesDAaA1j6ltabL+C7EukfK+Ov4sC4g5GsigyQS84Be7hmr+mXfUrik8e4Py6DgVXUN\/\/Dqroz4XbkDeNOLZK1ZQ6QmrhUmU2RVyYOOcs4x+u5UQOASuWwG8x+am3+8lU\/xn5KfXTnZ0SuxcUJX6VBtoDt1aTyMxQOpvfAwZCIq0GM1mB2YdNUBuI\/m3dH5pHjg9\/DCKh5RrhkHB0s5ptmbsAQiT24yC65PI4E1xX1xSHGvfCWOpolt609gp86DPaAczi8xCLao0koIuQ5TB2ANQ4TvmYuQCKDMzY7EsOEIHz\/+Ytc+wKXnXjEV3+hxkuiocBEM9y0olh0razx4DW4yAbSJ2vh7YekddqtyzJOous82SZ97xni5xrF\/tqYR3jZMnzGTZDXsxyBSYIkxanWaulLl8ohYUib+Y6ZjiQlTT5Sm\/X\/cnroBDutS+\/qEqHKGpu\/wQyxAbaUjpBjuimxhl8jxkRiaQkChTL5yrbXsaq+5UsGOA1dvMDzmufhJrY+dtetkhj6JMbZtdzkyvhNo64jp3Ybvj7foFhDto4mWZeYDHs6w04pp\/X+PCtdut2qxZqeVxHydi\/Xlw0MqpBOVFk11CHZKumd60Vk4w+6irsc=",
        "h": "92373df1f6c4272930d4d5471048827c",
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
