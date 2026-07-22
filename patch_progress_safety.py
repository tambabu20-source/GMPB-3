#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")


def parse_number(value: object) -> float | None:
    match = re.search(r"\d+(?:[,.]\d+)?", str(value or ""))
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def extract_projects(html: str) -> list[dict]:
    match = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not match:
        raise SystemExit("Không tìm thấy mảng projects trong index.html")
    return json.loads(match.group(1))


def replace_projects(html: str, projects: list[dict]) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    return re.sub(
        r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate",
        lambda _match: block,
        html,
        count=1,
    )


def project_total(project: dict) -> tuple[float | None, str]:
    total_text = str(project.get("totalArea") or "")
    unit = "ha" if "ha" in total_text.lower() else "km" if "km" in total_text.lower() else ""
    return parse_number(total_text), unit


def parse_area_ratio(value: object) -> tuple[float | None, float | None, str]:
    text = str(value or "")
    unit = "ha" if "ha" in text.lower() else "km" if "km" in text.lower() else ""
    match = re.search(r"([\d.,]+)\s*/\s*([\d.,]+)", text)
    if not match:
        return None, None, unit
    return float(match.group(1).replace(",", ".")), float(match.group(2).replace(",", ".")), unit


def source_progress_from_note(project: dict) -> tuple[float | None, str | None, str | None, str | None]:
    note = str(project.get("note") or "")
    match = re.search(
        r"đã bàn giao\s+([\d.,]+)\s*;\s*([\d.,]+)%\s*;\s*chưa bàn giao\s+([\d.,]+)\s*;\s*còn\s+([\d.,]+)%",
        note,
        re.I,
    )
    if not match:
        return None, None, None, None
    cleared = float(match.group(1).replace(",", "."))
    progress = float(match.group(2).replace(",", "."))
    remaining = float(match.group(3).replace(",", "."))
    remaining_rate = float(match.group(4).replace(",", "."))
    total, unit = project_total(project)
    cleared_area = f"{fmt(cleared)}/{fmt(total)} {unit}" if total and unit else project.get("clearedArea")
    remaining_area = f"{fmt(remaining)} {unit}" if unit else project.get("remainingArea")
    return progress, cleared_area, remaining_area, f"{fmt(remaining_rate, 2)}%"


def normalize_area_and_remaining(project: dict) -> None:
    progress = project.get("progress")
    if not isinstance(progress, (int, float)):
        return
    progress = max(0, min(100, float(progress)))
    project["progress"] = round(progress, 2)

    total, total_unit = project_total(project)
    cleared, denominator, ratio_unit = parse_area_ratio(project.get("clearedArea"))
    unit = ratio_unit or total_unit
    if total and unit:
        if denominator is None or abs(denominator - total) > max(0.01, total * 0.02):
            denominator = total
        if cleared is None or cleared > denominator or progress in (0, 100):
            cleared = denominator * progress / 100
        cleared = max(0, min(denominator, cleared))
        project["clearedArea"] = f"{fmt(cleared)}/{fmt(denominator)} {unit}"
        remaining = max(0, denominator - cleared)
        project["remainingArea"] = f"{fmt(remaining)} {unit}"

    expected_remaining_rate = max(0, 100 - progress)
    current_remaining_rate = parse_number(project.get("remainingRate"))
    if current_remaining_rate is None or abs(current_remaining_rate - expected_remaining_rate) > 1:
        project["remainingRate"] = f"{fmt(expected_remaining_rate, 2)}%"


def clamp_progress(projects: list[dict]) -> bool:
    changed = False
    for project in projects:
        progress = project.get("progress")
        if not isinstance(progress, (int, float)):
            continue
        old = json.dumps(project, ensure_ascii=False, sort_keys=True)
        if progress > 100:
            source_progress, cleared_area, remaining_area, remaining_rate = source_progress_from_note(project)
            if source_progress is not None:
                project["progress"] = round(max(0, min(100, source_progress)), 2)
                if cleared_area:
                    project["clearedArea"] = cleared_area
                if remaining_area:
                    project["remainingArea"] = remaining_area
                if remaining_rate:
                    project["remainingRate"] = remaining_rate
            else:
                project["progress"] = 100
        elif progress < 0:
            project["progress"] = 0
        normalize_area_and_remaining(project)
        if old != json.dumps(project, ensure_ascii=False, sort_keys=True):
            changed = True
    return changed


def patch_js_clamp(html: str) -> str:
    html = html.replace(
        '        const width = Number.isFinite(project.progress) ? `${project.progress}%` : "0%";',
        '        const displayProgress = Number.isFinite(project.progress) ? Math.max(0, Math.min(100, project.progress)) : null;\n        const width = displayProgress !== null ? `${displayProgress}%` : "0%";',
    )
    html = html.replace(
        '          const w = known ? Math.max(4, project.progress / 100 * barW) : barW;',
        '          const displayProgress = known ? Math.max(0, Math.min(100, project.progress)) : 0;\n          const w = known ? Math.max(4, displayProgress / 100 * barW) : barW;',
    )
    html = html.replace(
        '        const w = known ? Math.max(4, project.progress / 100 * barW) : barW;',
        '        const displayProgress = known ? Math.max(0, Math.min(100, project.progress)) : 0;\n        const w = known ? Math.max(4, displayProgress / 100 * barW) : barW;',
    )
    return html


def update_average(html: str, projects: list[dict]) -> str:
    known = [float(project["progress"]) for project in projects if isinstance(project.get("progress"), (int, float))]
    if not known:
        return html
    avg = fmt(sum(known) / len(known), 2)
    return re.sub(r"Bình quân 8 dự án có %</span><b>[^<]+</b>", f"Bình quân 8 dự án có %</span><b>{avg}%</b>", html)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rà soát và chuẩn hóa tỷ lệ GPMB sau khi cập nhật Drive.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    projects = extract_projects(html)
    changed = clamp_progress(projects)
    new_html = replace_projects(html, projects) if changed else html
    new_html = update_average(new_html, projects)
    new_html = patch_js_clamp(new_html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã rà soát tỷ lệ, diện tích và phần còn lại GPMB.")
    else:
        print("Tỷ lệ GPMB đã hợp lệ, không cần chỉnh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
