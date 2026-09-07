import os
import re
import requests


# 将 max_chars 默认值改为 3000
def read_log(path, max_chars=3000):
    """读取日志，若过长则只截取末尾最新的 3000 字符（报错关键信息通常在末尾）"""
    if not os.path.exists(path):
        return ""

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
            if len(content) > max_chars:
                return f"...(前面内容过长已省略，仅展示最新 3000 字符)\n{content[-max_chars:]}"
            return content
    except Exception as e:
        return f"- 读取日志异常: {e}"


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

    # 1. 过滤前后空格与换行符
    send_key = send_key.strip()

    ninebot_result = os.environ.get("NINEBOT_JOB_RESULT", "unknown")
    smzdm_result = os.environ.get("SMZDM_JOB_RESULT", "unknown")
    dailycharge_result = os.environ.get("DAILYCHARGE_JOB_RESULT", "unknown")

    # 2. 读取各个任务日志（每个最多 3000 字符）
    ninebot_log = read_log("artifacts/ninebot/ninebot_log.txt", max_chars=3000)
    smzdm_log = read_log("artifacts/smzdm/smzdm_log.txt", max_chars=3000)
    dailycharge_log = read_log("artifacts/dailycharge/dailycharge_log.txt", max_chars=3000)

    sections = [
        "## 每日汇总",
        f"- 九号任务状态: {ninebot_result}",
        f"- 什么值得买状态: {smzdm_result}",
        f"- 天天充电状态: {dailycharge_result}",
        "",
    ]

    append_log_section(sections, "九号", ninebot_log)
    append_log_section(sections, "什么值得买", smzdm_log)
    append_log_section(sections, "天天充电", dailycharge_log)
    content = "\n".join(sections).strip()

    # 3. 自动适配 Server酱 Turbo 与 Server酱³
    match_sctp = re.match(r"^sctp(\d+)t", send_key, re.I)
    if match_sctp:
        uid = match_sctp.group(1)
        url = f"https://{uid}.push.ft07.com/send/{send_key}.send"
    else:
        url = f"https://sctapi.ftqq.com/{send_key}.send"

    data = {
        "title": "自动化脚本每日汇总",
        "desp": content,
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        # 打印响应信息，便于排查
        print(f"Server酱响应状态码: {response.status_code}")
        print(f"Server酱返回内容: {response.text}")

        if response.status_code == 200:
            print("✅ 统一汇总通知推送成功")
        else:
            print(f"❌ 统一汇总通知推送失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统一汇总通知推送发生异常: {e}")


if __name__ == "__main__":
    main()
