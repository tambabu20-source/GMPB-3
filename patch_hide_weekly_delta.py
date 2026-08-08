#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


FLAG = "const showWeeklyDelta = false;"


def main() -> int:
    parser = argparse.ArgumentParser(description="Tạm ẩn nhãn diễn biến tuần qua nhưng giữ số liệu nền để so sánh sau.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = html
    if "const showWeeklyDelta =" in new_html:
        new_html = re.sub(r"const showWeeklyDelta = (?:true|false);", FLAG, new_html, count=1)
    else:
        new_html = new_html.replace(
            "    const weeklyLocalityCleared =",
            f"    {FLAG}\n    const weeklyLocalityCleared =",
            1,
        )
    new_html = new_html.replace(
        "function weeklyProgressMeta(current, baseline, areaText = \"\") {\n      if (!Number.isFinite(current) || !Number.isFinite(baseline)) return null;",
        "function weeklyProgressMeta(current, baseline, areaText = \"\") {\n      if (!showWeeklyDelta) return null;\n      if (!Number.isFinite(current) || !Number.isFinite(baseline)) return null;",
    )
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã tạm ẩn nhãn tuần qua; dữ liệu nền vẫn được giữ lại.")
    else:
        print("Nhãn tuần qua đã được tạm ẩn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
