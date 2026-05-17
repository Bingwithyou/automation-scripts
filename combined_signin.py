# -*- coding: utf-8 -*-
"""
cron: 30 7 * * *
new Env('组合签到(塔斯汀&zhcommerce&mxbc)');
"""
import subprocess
import sys
import os
from datetime import datetime

def run_script(command, display_name, extra_env=None):
    print(f"--- 正在执行: {display_name} ---")
    try:
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env,
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            if output:
                output += "\n"
            output += result.stderr.strip()
        return output
    except Exception as e:
        return f"❌ 运行脚本 {display_name} 失败: {e}"

def main():
    base_dir = os.path.dirname(os.path.realpath(__file__))

    scripts = [
        {
            "name": "tastien_checkin.py",
            "path": os.path.join(base_dir, "tastien", "tastien_checkin.py"),
            "command": [sys.executable, os.path.join(base_dir, "tastien", "tastien_checkin.py")],
            "env": {"COMBINED_SUMMARY_MODE": "yes"},
        },
        {
            "name": "zhcommerce_signin.py",
            "path": os.path.join(base_dir, "zhcommerce", "zhcommerce_signin.py"),
            "command": [sys.executable, os.path.join(base_dir, "zhcommerce", "zhcommerce_signin.py")],
            "env": {"COMBINED_SUMMARY_MODE": "yes"},
        },
        {
            "name": "mxbc_checkin.js",
            "path": os.path.join(base_dir, "mxbc", "mxbc_checkin.js"),
            "command": ["node", os.path.join(base_dir, "mxbc", "mxbc_checkin.js")],
            "env": {"COMBINED_SUMMARY_MODE": "yes"},
        },
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [
        "# 每日签到汇总报告",
        f"> **生成时间**: `{now}`",
        f"> **任务数量**: {len(scripts)}",
        "\n---"
    ]

    for script in scripts:
        script_name = script["name"]
        script_path = script["path"]
        if os.path.exists(script_path):
            output = run_script(script["command"], script_name, script.get("env"))
            if output:
                report_lines.append(output)
            else:
                report_lines.append(f"### {script_name} 运行结果\n> ⚠️ 脚本执行成功但无输出内容")
        else:
            report_lines.append(f"### {script_name}\n> ❌ 未找到脚本文件")
        report_lines.append("\n---\n")

    if report_lines[-1] == "\n---\n":
        report_lines.pop()

    combined_content = "\n".join(report_lines)

    print(combined_content)

    try:
        sys.path.append("/ql/data/scripts")
        sys.path.append("/ql/scripts")
        from notify import send
        send("每日签到汇总报告", combined_content)
    except Exception as e:
        print(f"通知发送失败或环境不在青龙: {e}")

if __name__ == "__main__":
    main()
