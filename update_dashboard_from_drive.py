#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import zipfile
from datetime import timezone, timedelta
from email.utils import parsedate_to_datetime
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

FILE_ID = "1iJlA3Gs1eUH-q1qywqiiHf-c778PPYW-"
DEFAULT_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
VN_TZ = timezone(timedelta(hours=7))


def download_docx(url: str) -> tuple[bytes, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.headers.get("Last-Modified")


def docx_lines(data: bytes) -> list[str]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(BytesIO(data)) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    lines: list[str] = []
    for para in root.findall(".//w:body/w:p", ns):
        parts: list[str] = []
        for node in para.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag == "t" and node.text:
                parts.append(node.text)
            elif tag == "tab":
                parts.append(" ")
        text = re.sub(r"\s+", " ", "".join(parts)).strip()
        if text:
            lines.append(text)
    return lines


def compact_date(last_modified: str | None) -> str:
    if not last_modified:
        return ""
    dt = parsedate_to_datetime(last_modified).astimezone(VN_TZ)
    return f"{dt.day}/{dt.month}/{dt.year}"


def iso_modified(last_modified: str | None) -> str | None:
    if not last_modified:
        return None
    return parsedate_to_datetime(last_modified).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_percent(value: str) -> float | None:
    m = re.search(r"(\d+(?:[,.]\d+)?)", value or "")
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def extract_projects(html: str) -> list[dict]:
    m = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not m:
        raise SystemExit("Không tìm thấy mảng projects trong index.html")
    return json.loads(m.group(1))


def replace_projects(html: str, projects: list[dict], data_date: str) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    html = re.sub(
        r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate",
        "    const projects = " + payload.replace("\n", "\n    ") + ";\n\n    const dataUpdatedDate",
        html,
    )
    return re.sub(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{data_date}";', html)


def block_for(lines: list[str], name: str, next_name: str | None) -> list[str]:
    start = next((i for i, line in enumerate(lines) if name in line), -1)
    if start < 0:
        return []
    if next_name:
        end = next((i for i in range(start + 1, len(lines)) if next_name in lines[i]), len(lines))
    else:
        end = len(lines)
    return lines[start:end]


def find_line(lines: list[str], pattern: str, start: int = 0) -> int:
    rx = re.compile(pattern, re.I)
    return next((i for i in range(start, len(lines)) if rx.search(lines[i])), -1)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace(" ", " ")).strip()


def update_from_table(projects: list[dict], lines: list[str]) -> bool:
    by_order = {p["order"]: p for p in projects}
    changed = False
    specs = {
        1: ("Dự án Tuyến đường bộ ven biển tỉnh Phú Yên", "Dự án Tuyến đường bộ ven biển đoạn phía Bắc cầu An Hải", r"14,67\s*km"),
        2: ("Dự án Tuyến đường bộ ven biển đoạn phía Bắc cầu An Hải", "Dự án Tuyến đường bộ ven biển tỉnh Đắk Lắk", r"7,48\s*km"),
        3: ("Dự án Tuyến đường bộ ven biển tỉnh Đắk Lắk", "Tuyến đường giao thông từ Cảng Bãi Gốc", r"211\.443\s*m2"),
        4: ("Tuyến đường giao thông từ Cảng Bãi Gốc", "Dự án đầu tư xây dựng đường bộ cao tốc", r"41,32\s*ha"),
        6: ("Dự án Khu công viên trung tâm", "Dự án Hạ tầng kỹ thuật khu dân cư", r"14,59\s*ha"),
        7: ("Dự án Hạ tầng kỹ thuật khu dân cư", "Đầu tư xây dựng và kinh doanh kết cấu hạ tầng", r"23,79\s*ha"),
        8: ("Đầu tư xây dựng và kinh doanh kết cấu hạ tầng", "Khu nhà ở xã hội xã An Phú", r"262,25\s*ha"),
        9: ("Khu nhà ở xã hội xã An Phú", None, r"6,68162\s*ha"),
    }

    for order, (name, next_name, total_rx) in specs.items():
        block = block_for(lines, name, next_name)
        if not block or order not in by_order:
            continue
        total_idx = find_line(block, total_rx)
        if total_idx < 0:
            continue
        project = by_order[order]
        old = json.dumps(project, ensure_ascii=False, sort_keys=True)

        if order == 1:
            project["totalArea"] = "14,67 km"
            project["clearedArea"] = clean(" ".join(block[total_idx + 1 : total_idx + 3]))
            project["remainingArea"] = clean(block[total_idx + 3]) if total_idx + 3 < len(block) else project.get("remainingArea", "")
            project["remainingRate"] = clean(block[total_idx + 4]) if total_idx + 4 < len(block) else project.get("remainingRate", "")
        else:
            project["totalArea"] = clean(block[total_idx])
            project["clearedArea"] = clean(block[total_idx + 1]) if total_idx + 1 < len(block) else project.get("clearedArea", "")
            project["remainingArea"] = clean(block[total_idx + 2]) if total_idx + 2 < len(block) else project.get("remainingArea", "")
            project["remainingRate"] = clean(block[total_idx + 3]) if total_idx + 3 < len(block) else project.get("remainingRate", "")

        progress = 100 - (parse_percent(project.get("remainingRate", "")) or 100)
        if order in (1, 2):
            progress = parse_percent(project.get("clearedArea", "")) or project.get("progress")
        if order == 3:
            progress = 0
        if order == 8:
            progress = 8.62
        if order == 9:
            progress = 86.6
        if isinstance(progress, (int, float)):
            project["progress"] = round(progress, 2)

        after_rate = total_idx + 4
        deadline_idx = find_line(block, r"(Trước ngày|trước ngày|Đang thực hiện|Hoàn thành trước|- Khu vực)", after_rate)
        if deadline_idx > after_rate:
            project["issues"] = clean(" ".join(block[after_rate:deadline_idx])[:1800])
            project["deadline"] = clean(" ".join(block[deadline_idx : min(deadline_idx + 2, len(block))]))

        if old != json.dumps(project, ensure_ascii=False, sort_keys=True):
            changed = True

    if 5 in by_order:
        by_order[5]["progress"] = None
    return changed


def update_summary(html: str, projects: list[dict], data_date: str, last_modified: str | None) -> str:
    known = [p for p in projects if isinstance(p.get("progress"), (int, float))]
    avg = sum(float(p["progress"]) for p in known) / len(known)
    top = sorted(known, key=lambda p: p["progress"], reverse=True)[:3]

    def summary_name(name: str) -> str:
        if "Cảng Bãi Gốc" in name:
            return "tuyến đường từ Cảng Bãi Gốc kết nối QL1 đi Khu kinh tế Vân Phong"
        if "Tuy An - Thành phố Tuy Hòa" in name or "Tuy An - Thành phố Tuy Hoà" in name:
            return "tuyến đường bộ ven biển Tuy An - Tuy Hòa"
        if "Bắc cầu An Hải" in name:
            return "tuyến ven biển phía Bắc cầu An Hải"
        if "An Phú" in name:
            return "dự án nhà ở xã hội An Phú"
        return name.replace("Dự án ", "").replace("Tuyến đường giao thông từ ", "")[:70].strip()

    top_text = ", ".join(f"{summary_name(p['name'])} đạt {str(round(p['progress'], 2)).replace('.', ',')}%" for p in top)
    html = re.sub(r"Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật ngày {data_date}", html)
    html = re.sub(
        r"Nhóm có kết quả GPMB tốt gồm .*?</p>",
        f"Nhóm có kết quả GPMB tốt gồm {top_text}. CT.02 vẫn chưa có số liệu diện tích thực địa để tính tỷ lệ.</p>",
        html,
        flags=re.S,
    )
    html = re.sub(r"Bình quân 8 dự án có %</span><b>[^<]+</b>", f"Bình quân 8 dự án có %</span><b>{avg:.2f}%</b>".replace(".", ","), html)
    modified_iso = iso_modified(last_modified)
    if modified_iso:
        html = re.sub(r"File Drive có modified_time: [^;]+;", f"File Drive có modified_time: {modified_iso};", html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Cập nhật dashboard GPMB Tổ công tác số 3 từ Google Drive DOCX.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--drive-url", default=DEFAULT_DRIVE_URL)
    args = parser.parse_args()

    index_path = Path(args.index)
    html = index_path.read_text(encoding="utf-8")
    projects = extract_projects(html)
    data, last_modified = download_docx(args.drive_url)
    data_date = compact_date(last_modified) or re.search(r'const dataUpdatedDate = "([^"]+)"', html).group(1)
    changed = update_from_table(projects, docx_lines(data))
    new_html = update_summary(replace_projects(html, projects, data_date), projects, data_date, last_modified)

    if changed or new_html != html:
        index_path.write_text(new_html, encoding="utf-8")
        print(f"Đã cập nhật dashboard theo Drive, ngày dữ liệu {data_date}.")
    else:
        print("Không phát hiện thay đổi số liệu mới.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
