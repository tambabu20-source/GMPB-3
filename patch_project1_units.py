#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")


def read_number(text: str, unit: str) -> float:
    text = text.strip()
    if unit.lower() == "m" and re.fullmatch(r"\d{1,3}(?:\.\d{3})+", text):
        return float(text.replace(".", ""))
    return float(text.replace(",", "."))


def extract_projects(html: str) -> list[dict]:
    match = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not match:
        raise SystemExit("Không tìm thấy mảng projects trong index.html")
    return json.loads(match.group(1))


def replace_projects(html: str, projects: list[dict]) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    return re.sub(r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate", lambda _m: block, html, count=1)


def locality_pairs(note: str) -> list[tuple[float, float]]:
    normalized = re.sub(r"([\d.,]+)\s*([a-zA-Z]+)\s*/\s*([\d.,]+)\s*\2", r"\1/\3 \2", note)
    rx = re.compile(r"đã bàn giao\s*([\d.,]+)(?:\s*/\s*([\d.,]+))?\s*([a-zA-Z]*)\s*;\s*([\d.,]+)%+", re.I)
    pairs: list[tuple[float, float]] = []
    for match in rx.finditer(normalized):
        unit = (match.group(3) or "").lower()
        cleared = read_number(match.group(1), unit)
        total = read_number(match.group(2), unit) if match.group(2) else None
        if unit == "m":
            cleared = cleared / 1000
            if total is not None:
                total = total / 1000
        if total and total > 0:
            pairs.append((min(cleared, total), total))
    return pairs


def patch_project1(projects: list[dict]) -> bool:
    project = next((item for item in projects if item.get("order") == 1), None)
    if not project:
        return False
    pairs = locality_pairs(str(project.get("note") or ""))
    total_match = re.search(r"\d+(?:[,.]\d+)?", str(project.get("totalArea") or ""))
    if len(pairs) < 2 or not total_match:
        return False
    total = float(total_match.group(0).replace(",", "."))
    progress = max(0, min(99.99, sum(c for c, _ in pairs) / sum(t for _, t in pairs) * 100))
    cleared = total * progress / 100
    remaining = max(0, total - cleared)
    old = json.dumps(project, ensure_ascii=False, sort_keys=True)
    project["progress"] = round(progress, 2)
    project["clearedArea"] = f"{fmt(cleared)}/{fmt(total)} km"
    project["remainingArea"] = f"{fmt(remaining)} km"
    project["remainingRate"] = f"{fmt(100 - progress, 2)}%"
    return old != json.dumps(project, ensure_ascii=False, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Chuẩn hóa đơn vị mét và tỷ lệ dự án 1.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    projects = extract_projects(html)
    changed = patch_project1(projects)
    if changed:
        path.write_text(replace_projects(html, projects), encoding="utf-8")
        print("Đã chuẩn hóa tỷ lệ dự án 1 theo các địa phương.")
    else:
        print("Tỷ lệ dự án 1 đã hợp lệ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
