import os
import requests


def read_log(path):
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def main():
    send_key = os.environ.get("SERVER_CHAN_SEND_KEY")
    if not send_key:
        print("⚠️ 未设置 SERVER_CHAN_SEND_KEY，跳过统一汇总推送")
        return

    ninebot_result = os.environ.get("NINEBOT_JOB_RESULT", "unknown")
    smzdm_result = os.environ.get("SMZDM_JOB_RESULT", "unknown")
    tastien_result = os.environ.get("TASTIEN_JOB_RESULT", "unknown")

    ninebot_log = read_log("artifacts/ninebot/ninebot_log.txt")
    smzdm_log = read_log("artifacts/smzdm/smzdm_log.txt")
    tastien_log = read_log("artifacts/tastien/tastien_log.txt")

    sections = [
        f"九号任务状态: {ninebot_result}",
        f"什么值得买状态: {smzdm_result}",
        f"塔斯汀状态: {tastien_result}",
        "",
    ]

    if ninebot_log:
        sections.append("## 九号")
        sections.append("```text")
        sections.append(ninebot_log)
        sections.append("```")
        sections.append("")
    else:
        sections.append("## 九号")
        sections.append("未找到日志文件，可能任务未执行完成或提前失败。")
        sections.append("")

    if smzdm_log:
        sections.append("## 什么值得买")
        sections.append("```text")
        sections.append(smzdm_log)
        sections.append("```")
    else:
        sections.append("## 什么值得买")
        sections.append("未找到日志文件，可能任务未执行完成或提前失败。")

    sections.append("")

    if tastien_log:
        sections.append("## 塔斯汀")
        sections.append("```text")
        sections.append(tastien_log)
        sections.append("```")
    else:
        sections.append("## 塔斯汀")
        sections.append("未找到日志文件，可能任务未执行完成或提前失败。")

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
