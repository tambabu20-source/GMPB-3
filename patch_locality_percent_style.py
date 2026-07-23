#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Giữ nguyên bố cục biểu đồ địa phương đã được script chính chuẩn hóa.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    Path(args.index).read_text(encoding="utf-8")
    print("Bố cục biểu đồ địa phương đã do patch_locality_chart.py xử lý; không ghi đè thêm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
