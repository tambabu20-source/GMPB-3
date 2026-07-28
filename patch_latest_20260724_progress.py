#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


ARCHIVED_DATA_DATE = "24/7/2026"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bước lịch sử 24/7 đã được lưu để tham chiếu, không ghi đè dữ liệu Drive mới.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    html = Path(args.index).read_text(encoding="utf-8")
    current = re.search(r'const dataUpdatedDate = "([^"]+)"', html)
    current_date = current.group(1) if current else "không rõ"
    print(
        f"Bỏ qua vá phụ lục {ARCHIVED_DATA_DATE}; dashboard đang dùng dữ liệu Drive hiện tại {current_date}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
