#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def replace_once(pattern: str, repl: str, text: str, flags: int = 0) -> str:
    new_text, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"Không tìm thấy đúng 01 vùng cần thay: {pattern[:80]}")
    return new_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Cập nhật dashboard GPMB từ JSON tiến độ đã chuẩn hóa.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--data", default="work/latest_progress_data.json")
    args = parser.parse_args()

    index_path = Path(args.index)
    data_path = Path(args.data)
    html = index_path.read_text(encoding="utf-8")
    data = json.loads(data_path.read_text(encoding="utf-8"))

    projects_payload = json.dumps(data["projects"], ensure_ascii=False, indent=6)
    projects_block = "    const projects = " + "\n    ".join(projects_payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    pattern = r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate"
    html, count = re.subn(pattern, lambda _m: projects_block, html, count=1)
    if count != 1:
        raise SystemExit("Không tìm thấy đúng 01 vùng mảng projects để thay.")
    html = replace_once(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{data["dataUpdatedDate"]}";', html)
    html = re.sub(r"Cập nhật số liệu: \d{1,2}/\d{1,2}/\d{4}", f'Cập nhật số liệu: {data["dataUpdatedDate"]}', html)

    summary = data["summary"]
    html = replace_once(r"Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}, .*?</p>", summary["lead"] + "</p>", html, flags=re.S)
    html = replace_once(r"Nhóm có kết quả GPMB tốt gồm .*?</p>", summary["top"] + "</p>", html, flags=re.S)
    html = replace_once(r"Khó khăn nổi bật tập trung ở .*?</p>", summary["issues"] + "</p>", html, flags=re.S)
    html = replace_once(r"Thời gian tới .*?</p>", summary["next"] + "</p>", html, flags=re.S)

    html = re.sub(r'<div class="mini-metric"><span>Có tỷ lệ %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Có tỷ lệ %</span><b>{summary["known"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>{summary["above90"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Bình quân 8 dự án có %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Bình quân 8 dự án có %</span><b>{summary["average"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>{summary["unknown"]}</b></div>', html)

    chart_hint = (
        f'Các biểu đồ dùng dữ liệu từ file “PL Tien do (TB ket luan 326TB-UBND).xlsx” '
        f'và phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày {data["dataUpdatedDate"]}.'
    )
    html = replace_once(r'Các biểu đồ dùng dữ liệu từ .*?</p>', chart_hint + '</p>', html, flags=re.S)

    html = replace_once(r'<span class="hint">Nguồn .*?</span>', f'<span class="hint">{data["sourceNote"]}</span>', html, flags=re.S)

    index_path.write_text(html, encoding="utf-8")
    print(f'Đã cập nhật dashboard theo dữ liệu ngày {data["dataUpdatedDate"]}.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
