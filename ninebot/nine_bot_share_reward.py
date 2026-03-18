import requests
import os
import time
import json
from notification import add_log, check_secrets

def do_share_and_collect_reward():
    # 从环境变量获取 Token 和 Device ID
    token = os.environ.get("NINEBOT_TOKEN")
    device_id = os.environ.get("DEVICE_ID")

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
        "k": "mx0Zdjf6ayfjFkX4rC9CHVZNOlorWSG0ZDEjpE+Raxq6v75m83DPHtUwy1VTpO4hBdjCDR/yIh+15IOSC0a1zKkuOILH/D/Z94K9bVc4wcqw4d46qt4WbDlITizRKZT6sS2N3OzwHMUIKbm9Kitk4CnTqvsY4y3LTbyp1bM6X1E=",
        "p": 101,
        "d": "xj6QFv+/qPlSnjGEqdPHrjlcX5mN4cJafdDmoMigAxtLUodCbc9daapDU7PdjDuHxerEadqjugf2NWknfrzx+rN14Zt1dNv0k8f3//90HPyRRcKZ44wj7ZVnZFHRHj6xCnZrU/bI6h6ruQZ7s4JQNqviIiBs4rZ95u8618+K/V7KRYyl6k55nz45/EzgOQC4ZTXksA0YoaI2kNlz6IQqwk1SsyVGBOCjlv0o4ud1hrM4sjQJjG6ZatIhDuTmfuN+s+hJhXNK+7NXOOsEtXgYGLtF5c47XkJ6njAOlfzOSgO5qyxPyU55s+9zNVeJryt8We0sbA0ryP7u7DTnxH/Khb1tpRcAl3wsQnr0rC9mO+rx8tAsu6kPNBj+ezEkoiHPCSvg3gh6aj+Ib1rUtjW5+1Or9a5DnDLWoa8+atT07TEWqUbeDeaHIntC1T7tcZDKQKFkbZQdAkRryuCpw5XVmj6uGOBVzyW+YQ+4VKn/03f4u3xXRw1BWKgdER86/ZFyGSdmPIoeWAK8zqx6HGG59AWpKYLpAhVPlAQRN4ckpdeyYWL3WlEOifnDCIN+VO4GA5xbxB5wYOFBYjm7wMfqG+J1Jt9ZVh+Mi/NEhuq3caM+2vGEo+hHNXTyaMZtcytKY/uWQvsCX3muCaL8xteLZJHsawdYXd1UIIUfCh+uyIWWz6jUDcVzUQuitgyC9+0S8dMJGqskJ+bLhW/kGF2Gsv2vRqHuoULSaszB8QFilr6SdaF6ew+FWbpN8iShl5YzLpfBBQ+1j9xFkF5wMX+DdTRcuFIJ58hjWfp/MnWdcICKBTRmdJ4Uz2rjHgjEsw2qA06cA4tP2wZmANzm0fSX2s9Smogt3ULE9MjAevOQ+pqimHzHPT6dpvONVLnNTclZAGdSWl8YQpwzlt2iRdMfErWufGBqG6PfkTvpAdu4wKVhB+uvLHuC6fxUSioZ3OSLdwJqvirmx8x6Glo1OkQose7Qi6sdRRU0RL/ChttxwnaUkoWj1ASTLuwIbYMUn6RXtaBhR159mVU0zesfmK8wYkomNQH4KxVGoC+wQOcxaFIE7YU46pt4jXKORupDDlHRcoiyKLVhP+dGt2Av7C1zptG9+pMfXxOY1IFV/3/TfCgNzorl8geVaFrVfuZVac560AWU+ctjp0mvG8Htbfen25Z/zi4Kh8R4VFCU1hkqntVqMQouJMqr/g8C2+6OfJA5OL3pldQQpjWK3gfmLWzDrJ/U26CmOEyYEOI0nr0NWhbHXVGShb8gHDWkHrCS6ApPyu1wSksb+0zwMSmgH1ihEYdpEGgZoPaMbFElHTiBjWaegdFQrx3LnrmyFFNlXb0l8qwLAWogOwEvOIRIgurlqMIQg7+VxDIXZDajyR1sqsrW/s5TZCcl1ASpm4iczK18fW/SaW9VIm+ZBQnLxJ8ZmJkQ8XSYuibKKti09BigMPesU43fJbGtL6VkRvnwNVM8PA+U1Rf/U8u2mXcRNFGj4j3MnqWeX7wm2u8vaRshiMZveONARcz2/3L7PvQ4FoGXDXg7xRkfB3qquEal/auouOnQC7hZXqRXe1GcBOvfrMjPALqqkWa3AWvEDwDnsVK2yquMActrL9Ey+lyDApRk67ZDdw5KDj77yjlFYE+ICpyEjRivIL40F727VMSmG4otxrFIADtfqIbuFrJq0RNlAnyMQGtHdcTA93/tu6imOx26OyfYtSZIym3Q8k4VYBn6Pjx8/uv9pHFSk3VY1FevgeDEf6tNBtir4GJ4o8R4Egbq4/kV9IiXU6h7ZvbRmf92E0sMdwc9mT89cMqPYQA01wthdBE1oejcdKSJBWnV0Ig37/LeiJ1C/kKlgWweLYCETeacTiz02L5SRqhCXlv3gTKbH670Rbrr4NHivwF1npMGJIi6/12+GFY+blr5p01SeIwK5K1rsP6N1rZCebR6vobYKF+5YClGmy8v4dPpJkQ=",
        "h": "2ccbf9853ffb096d891d0b7ff6262b42",
        "t": 0
    }

    add_log("=== 九号分享与领奖 ===")
    add_log("开始执行分享任务...")
    try:
        share_response = requests.post(share_url, headers=share_headers, data=json.dumps(share_payload))
        share_response.raise_for_status()
        share_result = share_response.json()
        add_log(f"分享任务接口返回: {share_result}")

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
            add_log(f"✅ 奖励领取成功！服务器返回: {reward_result}")
        else:
            add_log(f"❌ 奖励领取失败。服务器返回: {reward_result}")

    except Exception as e:
        add_log(f"❌ 请求领奖接口时发生网络错误: {e}")

# 当作为独立脚本运行时触发
if __name__ == "__main__":
    check_secrets(["NINEBOT_TOKEN", "DEVICE_ID"])
    do_share_and_collect_reward()
