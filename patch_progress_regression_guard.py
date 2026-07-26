#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FIELDS_TO_KEEP = [
    "progress",
    "clearedArea",
    "remainingArea",
    "remainingRate",
    "note",
]


def load_projects(html: str) -> list[dict]:
    match = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not match:
        raise SystemExit("Không tìm thấy mảng projects.")
    return json.loads(match.group(1))


def write_projects(html: str, projects: list[dict]) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    html, count = re.subn(
        r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate",
        lambda _m: block,
        html,
        count=1,
    )
    if count != 1:
        raise SystemExit("Không thay được mảng projects.")
    return html


def finite_number(value) -> float | None:
    if isinstance(value, (int, float)) and value == value:
        return float(value)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Không tự động kéo lùi tỷ lệ GPMB nếu nguồn cập nhật thấp hơn số đã công khai.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--baseline", default="index-before-update.html")
    parser.add_argument("--tolerance", type=float, default=0.05)
    args = parser.parse_args()

    index_path = Path(args.index)
    baseline_path = Path(args.baseline)
    if not baseline_path.exists():
        print("Không có baseline để so sánh, bỏ qua kiểm tra lùi tiến độ.")
        return 0

    html = index_path.read_text(encoding="utf-8")
    baseline_html = baseline_path.read_text(encoding="utf-8")
    projects = load_projects(html)
    baseline = {project.get("order"): project for project in load_projects(baseline_html)}

    guarded: list[str] = []
    for project in projects:
        order = project.get("order")
        old_project = baseline.get(order)
        if not old_project:
            continue
        old_progress = finite_number(old_project.get("progress"))
        new_progress = finite_number(project.get("progress"))
        if old_progress is None or new_progress is None:
            continue
        if new_progress + args.tolerance < old_progress:
            for field in FIELDS_TO_KEEP:
                if field in old_project:
                    project[field] = old_project[field]
            note = str(project.get("note") or "")
            warning = (
                f"\nCảnh báo tự động: nguồn cập nhật ghi tỷ lệ {new_progress:.2f}% thấp hơn "
                f"số đã công khai {old_progress:.2f}%; tạm giữ số liệu cũ để rà soát, tránh lùi tiến độ do nhập sai."
            )
            if "Cảnh báo tự động: nguồn cập nhật ghi tỷ lệ" not in note:
                project["note"] = note + warning
            guarded.append(f"{order}: {new_progress:.2f}% -> giữ {old_progress:.2f}%")

    if guarded:
        html = write_projects(html, projects)
        index_path.write_text(html, encoding="utf-8")
        print("Đã giữ số liệu cũ cho các dự án có dấu hiệu lùi tiến độ:")
        for item in guarded:
            print(f"- {item}")
    else:
        print("Không phát hiện dự án bị lùi tỷ lệ GPMB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
