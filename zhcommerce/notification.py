import os
import requests
import sys

LOG_FILE = "zhcommerce_log.txt"


def format_markdown_line(text):
    stripped = str(text).strip()
    if not stripped:
        return ""
    if stripped.startswith("##") or stripped.startswith("###"):
        return stripped
    if stripped.startswith("```"):
        return stripped
    if stripped.startswith("===") and stripped.endswith("==="):
        return f"## {stripped.strip('=').strip()}"
    if stripped.startswith("- "):
        return stripped
    return f"- {stripped}"


def add_log(text):
    formatted = format_markdown_line(text)
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


def check_secrets(required_keys):
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    if missing_keys:
        print(f"Error: missing required environment variables: {', '.join(missing_keys)}")
        print("Script stopped. Please configure these values in GitHub Secrets.")
        sys.exit(0)


def send_summary():
    if os.environ.get("COMBINED_SUMMARY_MODE") == "yes":
        print("已启用统一汇总模式，跳过单独 zhcommerce 通知。")
        return

    send_key = os.environ.get("SERVER_CHAN_SEND_KEY")
    if not send_key:
        print("未设置 SERVER_CHAN_SEND_KEY，跳过单独汇总推送。")
        return

    if not os.path.exists(LOG_FILE):
        print("未找到 zhcommerce 日志文件，跳过推送。")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("zhcommerce 日志为空，跳过推送。")
        return

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": "zhcommerce 每日汇总",
        "desp": content,
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            print("✅ zhcommerce 汇总通知推送成功")
            os.remove(LOG_FILE)
        else:
            print(f"❌ zhcommerce 汇总通知推送失败: {response.status_code}")
    except Exception as exc:
        print(f"❌ zhcommerce 汇总通知推送失败: {exc}")
