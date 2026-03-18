import os
import requests
import sys

LOG_FILE = "ninebot_log.txt"

def add_log(text):
    print(text) # 同时在控制台打印
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def check_secrets(required_keys):
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    if missing_keys:
        print(f"❌ 错误: 未找到必要的环境变量: {', '.join(missing_keys)}")
        print("脚本停止执行。请在 GitHub Secrets 中配置这些值。")
        sys.exit(0) # 正常退出但不继续执行逻辑

def send_summary():
    send_key = os.environ.get("SERVER_CHAN_SEND_KEY")
    if not send_key:
        print("⚠️ 未设置 SERVER_CHAN_SEND_KEY，跳过汇总通知推送")
        return
    
    if not os.path.exists(LOG_FILE):
        print("⚠️ 日志文件不存在，跳过推送")
        return
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    if not content.strip():
        print("⚠️ 日志内容为空，跳过推送")
        return

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": "九号每日任务汇总",
        "desp": f"### 运行详情\n```text\n{content}\n```"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ 九号任务汇总通知推送成功")
            os.remove(LOG_FILE) # 发送后删除，防止下次累加
        else:
            print(f"❌ 九号任务汇总通知推送失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 九号任务汇总通知推送发生异常: {e}")
