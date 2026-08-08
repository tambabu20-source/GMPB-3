#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


DATA_DATE = "07/8/2026"
TB_326_DATE = "17/7/2026"


def main() -> int:
    parser = argparse.ArgumentParser(description="Khóa ngày nguồn hiển thị cuối cùng cho dashboard.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = html.replace(
        "Thông báo kết luận số 326/TB-UBND ngày 07/8/2026",
        f"Thông báo kết luận số 326/TB-UBND ngày {TB_326_DATE}",
    )
    new_html = new_html.replace("Cập nhật tiến độ đến ngày: 46150.0", DATA_DATE)
    new_html = new_html.replace("Ghi chú nguồn: 46150.0", f"Ghi chú nguồn: cập nhật ngày {DATA_DATE}")
    new_html = new_html.replace("cập nhật ngày 46150.0", f"cập nhật ngày {DATA_DATE}")

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã khóa ngày TB 326 và ngày dữ liệu nguồn cuối cùng.")
    else:
        print("Ngày nguồn cuối cùng đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
