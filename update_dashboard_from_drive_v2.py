#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
import zipfile
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

FILE_ID = "1MjJcE8f93HyrpNP1Ik6QBdpQIulJLd4y"
DEFAULT_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
VN_TZ = timezone(timedelta(hours=7))
SOURCE_FILE_NAME = "TO CONG TAC SO 03 - Theo doi Tien do giai quyet chi tiet tung du an.xlsx"


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\xa0", " ")).strip()


def normalize(value: object) -> str:
    text = str(value or "").replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def download_source(url: str) -> tuple[bytes, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as res:
        data = res.read()
        if data[:2] != b"PK":
            raise SystemExit("Nguồn Google Drive không trả về file Excel hợp lệ. Kiểm tra quyền chia sẻ file.")
        return data, res.headers.get("Last-Modified")


def compact_date(last_modified: str | None) -> str:
    if not last_modified:
        return ""
    dt = parsedate_to_datetime(last_modified).astimezone(VN_TZ)
    return f"{dt.day}/{dt.month}/{dt.year}"


def parse_compact_date(value: str | None):
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not match:
        return None
    return int(match.group(3)), int(match.group(2)), int(match.group(1))


def display_date(value: object) -> str:
    text = clean(value).replace(" 00:00:00", "")
    if not text:
        return ""
    iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if iso:
        return f"{int(iso.group(3))}/{int(iso.group(2))}/{iso.group(1)}"
    if re.fullmatch(r"\d+(?:\.0+)?", text):
        serial = int(float(text))
        if 30000 <= serial <= 60000:
            dt = datetime(1899, 12, 30) + timedelta(days=serial)
            return f"{dt.day}/{dt.month}/{dt.year}"
    date = re.search(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?", text)
    if date:
        return f"{int(date.group(1))}/{int(date.group(2))}/{date.group(3) or '2026'}"
    return text


def col_to_index(ref: str) -> int:
    match = re.match(r"([A-Z]+)", ref or "")
    if not match:
        return 0
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def xlsx_rows(data: bytes) -> list[list[str]]:
    with zipfile.ZipFile(BytesIO(data)) as zf:
        shared: list[str] = []
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for item in root.findall(".//m:si", ns):
                shared.append("".join(t.text or "" for t in item.findall(".//m:t", ns)))
        root = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
    rows: list[list[str]] = []
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    for row in root.findall(".//m:sheetData/m:row", ns):
        values: list[str] = []
        for cell in row.findall("m:c", ns):
            idx = col_to_index(cell.attrib.get("r", ""))
            while len(values) <= idx:
                values.append("")
            cell_type = cell.attrib.get("t")
            if cell_type == "inlineStr":
                text = "".join(t.text or "" for t in cell.findall(".//m:t", ns))
            else:
                node = cell.find("m:v", ns)
                text = node.text if node is not None and node.text is not None else ""
                if cell_type == "s" and text:
                    text = shared[int(text)]
            values[idx] = clean(text)
        rows.append(values)
    return rows


def value_at(row: list[str], idx: int) -> str:
    return row[idx] if idx < len(row) else ""


def parse_number(value: object) -> float | None:
    match = re.search(r"\d+(?:[,.]\d+)?", str(value or ""))
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")


def total_num_unit(total: str) -> tuple[float | None, str]:
    unit = "ha" if "ha" in total.lower() else "km" if "km" in total.lower() else ""
    return parse_number(total), unit


def project_order_from_name(projects: list[dict], name: str) -> int | None:
    needle = normalize(name).replace("du an ", "").strip()
    best: tuple[int, int] | None = None
    for project in projects:
        haystack = normalize(project.get("name", "")).replace("du an ", "")
        if needle and (needle in haystack or haystack in needle):
            score = min(len(needle), len(haystack))
            order = int(project.get("order", 0))
            if best is None or score > best[0]:
                best = (score, order)
    return best[1] if best else None


def group_rows(projects: list[dict], rows: list[list[str]]) -> dict[int, list[list[str]]]:
    groups: dict[int, list[list[str]]] = {}
    current: int | None = None
    for row in rows:
        stt = value_at(row, 0)
        name = value_at(row, 1)
        total = value_at(row, 2)
        starts_project = name.startswith("Dự án ") and bool(total)
        if re.fullmatch(r"\d+(?:\.0)?", stt or ""):
            current = int(float(stt))
            groups[current] = [row]
        elif starts_project:
            current = project_order_from_name(projects, name)
            if current is not None:
                groups[current] = [row]
        elif current is not None:
            groups.setdefault(current, []).append(row)
    return groups


def extract_projects(html: str) -> list[dict]:
    match = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not match:
        raise SystemExit("Không tìm thấy mảng projects trong index.html")
    return json.loads(match.group(1))


def replace_projects(html: str, projects: list[dict], data_date: str) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    html = re.sub(r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate", lambda _m: block, html, count=1)
    return re.sub(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{data_date}";', html)


def joined(values: list[str]) -> str:
    return "\n".join(v for v in (clean(x) for x in values) if v)


def update_projects(projects: list[dict], rows: list[list[str]], data_date: str) -> bool:
    changed = False
    groups = group_rows(projects, rows)
    for order, group in groups.items():
        project = next((p for p in projects if p.get("order") == order), None)
        if not project:
            continue
        old = json.dumps(project, ensure_ascii=False, sort_keys=True)
        first = group[0]
        total = clean(value_at(first, 2))
        if total:
            project["totalArea"] = total
        total_num, unit = total_num_unit(project.get("totalArea", ""))

        cleared_nums = [parse_number(value_at(row, 4)) for row in group if parse_number(value_at(row, 4)) is not None]
        progress_rates = [parse_number(value_at(row, 5)) for row in group if parse_number(value_at(row, 5)) is not None]
        remaining_nums = [parse_number(value_at(row, 6)) for row in group if parse_number(value_at(row, 6)) is not None]
        remaining_rates = [parse_number(value_at(row, 7)) for row in group if parse_number(value_at(row, 7)) is not None]

        if order == 9:
            project.update({"progress": None, "clearedArea": "", "remainingArea": "", "remainingRate": ""})
        elif total_num and unit and cleared_nums:
            cleared = sum(float(x) for x in cleared_nums)
            calculated = cleared / total_num * 100
            progress = progress_rates[0] if len(progress_rates) == 1 else calculated
            progress = max(0, min(100, float(progress)))
            project["clearedArea"] = f"{fmt(cleared)}/{fmt(total_num)} {unit}"
            project["progress"] = round(progress, 2)
            if remaining_nums:
                project["remainingArea"] = f"{fmt(sum(float(x) for x in remaining_nums))} {unit}"
            remaining_rate = remaining_rates[0] if len(remaining_rates) == 1 else max(0, 100 - progress)
            project["remainingRate"] = f"{fmt(max(0, remaining_rate), 2)}%"
        elif progress_rates:
            project["progress"] = round(max(0, min(100, progress_rates[0])), 2)

        issues = joined([value_at(row, 8) for row in group])
        proposals = joined([value_at(row, 9) for row in group])
        plans = joined([value_at(row, 10) for row in group])
        issue_dates = joined([display_date(value_at(row, 11)) for row in group])
        handover_dates = [display_date(value_at(row, 12)) for row in group if display_date(value_at(row, 12))]
        if issues:
            project["issues"] = issues
        if proposals or plans:
            project["proposal"] = f"Kiến nghị:\n{proposals}\n\nKế hoạch thực hiện/Tiến độ thực hiện:\n{plans}"
        if handover_dates:
            project["deadline"] = "; ".join(dict.fromkeys(handover_dates))

        note_rows = []
        for row in group:
            area = clean(value_at(row, 3))
            cleared = clean(value_at(row, 4))
            progress_text = clean(value_at(row, 5))
            remaining = clean(value_at(row, 6))
            remain_rate = clean(value_at(row, 7))
            if area or cleared or progress_text or remaining or remain_rate:
                note_rows.append(f"{area}: đã bàn giao {cleared}; {progress_text}%; chưa bàn giao {remaining}; còn {remain_rate}%")
        if note_rows:
            project["note"] = (
                "Địa bàn/tiến độ: " + " | ".join(note_rows)
                + "\nThời gian xử lý xong vướng mắc: " + issue_dates
                + f"\nNguồn cập nhật: file Excel theo dõi tiến độ Tổ công tác số 03 trên Google Drive, cập nhật ngày {data_date}."
            )
        if old != json.dumps(project, ensure_ascii=False, sort_keys=True):
            changed = True
    return changed


def update_summary_and_source(html: str, projects: list[dict], data_date: str) -> str:
    known = [p for p in projects if isinstance(p.get("progress"), (int, float))]
    avg = sum(float(p["progress"]) for p in known) / len(known) if known else 0
    html = re.sub(r"Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật ngày {data_date}", html)
    html = re.sub(r"Cập nhật số liệu: \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật số liệu: {data_date}", html)
    html = re.sub(r"Bình quân 8 dự án có %</span><b>[^<]+</b>", f"Bình quân 8 dự án có %</span><b>{fmt(avg, 2)}%</b>", html)
    chart_hint = f'Các biểu đồ dùng dữ liệu từ file “{SOURCE_FILE_NAME}” và phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày {data_date}.'
    html = re.sub(r"Các biểu đồ dùng dữ liệu từ .*?</p>", chart_hint + "</p>", html, flags=re.S)
    source_note = (
        f"Nguồn cập nhật: file “{SOURCE_FILE_NAME}” trên Google Drive - Phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày {data_date} của UBND tỉnh. "
        f"Dashboard đã cập nhật số liệu, vướng mắc, kiến nghị, kế hoạch thực hiện và thời hạn bàn giao mặt bằng theo file nguồn ngày {data_date}."
    )
    return re.sub(r'<span class="hint">Nguồn cập nhật: .*?</span>', f'<span class="hint">{source_note}</span>', html, flags=re.S)


def main() -> int:
    parser = argparse.ArgumentParser(description="Cập nhật dashboard GPMB Tổ công tác số 3 từ file Excel Google Drive.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--drive-url", default=DEFAULT_DRIVE_URL)
    args = parser.parse_args()
    index_path = Path(args.index)
    html = index_path.read_text(encoding="utf-8")
    current = re.search(r'const dataUpdatedDate = "([^"]+)"', html)
    current_date = current.group(1) if current else ""
    data, last_modified = download_source(args.drive_url)
    data_date = compact_date(last_modified) or current_date
    if parse_compact_date(data_date) and parse_compact_date(current_date) and parse_compact_date(data_date) < parse_compact_date(current_date):
        print(f"Nguồn Drive ngày {data_date} cũ hơn dashboard hiện tại {current_date}; bỏ qua.")
        return 0
    projects = extract_projects(html)
    changed = update_projects(projects, xlsx_rows(data), data_date)
    new_html = replace_projects(html, projects, data_date)
    new_html = update_summary_and_source(new_html, projects, data_date)
    if changed or new_html != html:
        index_path.write_text(new_html, encoding="utf-8")
        print(f"Đã cập nhật dashboard theo file Excel Google Drive, ngày dữ liệu {data_date}.")
    else:
        print("Không phát hiện thay đổi số liệu mới.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
