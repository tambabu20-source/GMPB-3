#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")


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
    unit = "ha" if "ha" in str(project.get("totalArea", "")).lower() else "km" if "km" in str(project.get("totalArea", "")).lower() else ""
    total_match = re.search(r"\d+(?:[,.]\d+)?", str(project.get("totalArea") or ""))
    total = float(total_match.group(0).replace(",", ".")) if total_match else None
    cleared_area = f"{fmt(cleared)}/{fmt(total)} {unit}" if total and unit else project.get("clearedArea")
    remaining_area = f"{fmt(remaining)} {unit}" if unit else project.get("remainingArea")
    return progress, cleared_area, remaining_area, f"{fmt(remaining_rate, 2)}%"


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
                project["remainingRate"] = "0%"
        elif progress < 0:
            project["progress"] = 0
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
    parser = argparse.ArgumentParser(description="Rà soát và chặn tỷ lệ GPMB vượt 100% sau khi cập nhật Drive.")
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
        print("Đã rà soát tỷ lệ GPMB và không còn dự án vượt 100%.")
    else:
        print("Tỷ lệ GPMB đã hợp lệ, không cần chỉnh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
