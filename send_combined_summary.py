import os
import requests


def read_log(path):
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def append_log_section(sections, title, content):
    sections.append(f"## {title}")
    if content:
        sections.append(content)
    else:
        sections.append("- 未找到日志文件，可能任务未执行完成或提前失败。")
    sections.append("")


def main():
    send_key = os.environ.get("SERVER_CHAN_SEND_KEY")
    if not send_key:
        print("⚠️ 未设置 SERVER_CHAN_SEND_KEY，跳过统一汇总推送")
        return

    ninebot_result = os.environ.get("NINEBOT_JOB_RESULT", "unknown")
    smzdm_result = os.environ.get("SMZDM_JOB_RESULT", "unknown")
    suntory_result = os.environ.get("SUNTORY_JOB_RESULT", "unknown")
    dailycharge_result = os.environ.get("DAILYCHARGE_JOB_RESULT", "unknown")
    ninebot_log = read_log("artifacts/ninebot/ninebot_log.txt")
    smzdm_log = read_log("artifacts/smzdm/smzdm_log.txt")
    suntory_log = read_log("artifacts/suntory/suntory_log.txt")
    dailycharge_log = read_log("artifacts/dailycharge/dailycharge_log.txt")

    sections = [
        "## 每日汇总",
        f"- 九号任务状态: {ninebot_result}",
        f"- 什么值得买状态: {smzdm_result}",
        f"- 三得利状态: {suntory_result}",
        f"- 天天充电状态: {dailycharge_result}",
        "",
    ]

    append_log_section(sections, "九号", ninebot_log)
    append_log_section(sections, "什么值得买", smzdm_log)
    append_log_section(sections, "三得利", suntory_log)
    append_log_section(sections, "天天充电", dailycharge_log)
    content = "\n".join(sections).strip()

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": "自动化脚本每日汇总",
        "desp": content,
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            print("✅ 统一汇总通知推送成功")
        else:
            print(f"❌ 统一汇总通知推送失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统一汇总通知推送发生异常: {e}")


if __name__ == "__main__":
    main()
