import os
import requests
import sys

LOG_FILE = "tastien_log.txt"


def add_log(text):
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def check_secrets(required_keys):
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    if missing_keys:
        print(f"❌ 错误: 未找到必要的环境变量: {', '.join(missing_keys)}")
        print("脚本停止执行。请在 GitHub Secrets 中配置这些值。")
        sys.exit(0)


def send_summary():
    if os.environ.get("COMBINED_SUMMARY_MODE") == "yes":
        print("ℹ️ 已启用统一汇总模式，跳过塔斯汀单独推送")
        return

    send_key = os.environ.get("SERVER_CHAN_SEND_KEY")
    if not send_key:
        print("⚠️ 未设置 SERVER_CHAN_SEND_KEY，跳过汇总通知推送")
        return

    if not os.path.exists(LOG_FILE):
        print("⚠️ 日志文件不存在，跳过推送")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("⚠️ 日志内容为空，跳过推送")
        return

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": "塔斯汀每日任务汇总",
        "desp": f"### 运行详情\n```text\n{content}\n```",
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            print("✅ 塔斯汀任务汇总通知推送成功")
            os.remove(LOG_FILE)
        else:
            print(f"❌ 塔斯汀任务汇总通知推送失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 塔斯汀任务汇总通知推送发生异常: {e}")
