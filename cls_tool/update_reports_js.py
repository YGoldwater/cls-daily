"""把指定日期（默认今天）插入 reports.js 报告列表首位，幂等。

从 .github/workflows/daily-report.yml 的内联 `python -c "..."` 抽出来：
内联写法在 `run: |` 块里必须整体缩进，历史上因未缩进导致 YAML 块标量提前
终止、workflow 启动即失败（649 次全红）。独立成文件后不再有该风险。
"""
import json
import os
import sys
from datetime import datetime

REPORTS_JS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports.js")
)


def update(date_str: str = None) -> None:
    date_str = date_str or datetime.now().strftime("%Y%m%d")
    dt = datetime.strptime(date_str, "%Y%m%d")
    label = f"{dt.year}年{dt.month:02d}月{dt.day:02d}日"

    with open(REPORTS_JS, "r", encoding="utf-8") as f:
        content = f.read()

    start = content.index("[")
    end = content.rindex("]") + 1
    arr = json.loads(content[start:end])

    if arr and arr[0].get("date") == date_str:
        print(f"[SKIP] reports.js 已含 {date_str}")
        return

    arr.insert(0, {
        "date": date_str,
        "label": label,
        "file": f"reports/CLS_早报_{date_str}.html",
    })
    new_content = content[:start] + json.dumps(arr, ensure_ascii=False, indent=2) + content[end:]
    with open(REPORTS_JS, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] reports.js 已更新，新增 {date_str}（共 {len(arr)} 条）")


if __name__ == "__main__":
    update(sys.argv[1] if len(sys.argv) > 1 else None)
