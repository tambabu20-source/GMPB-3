#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
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
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value or "")
    if not m:
        return None
    return int(m.group(3)), int(m.group(2)), int(m.group(1))


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
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return 0
    value = 0
    for char in m.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def xlsx_rows(data: bytes) -> list[list[str]]:
    with zipfile.ZipFile(BytesIO(data)) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            for si in root.findall(".//m:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//m:t", ns)))
        root = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
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
    m = re.search(r"\d+(?:[,.]\d+)?", str(value or ""))
    if not m:
        return None
    return float(m.group(0).replace(",", "."))


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")


def total_num_unit(total: str) -> tuple[float | None, str]:
    unit = "ha" if "ha" in total.lower() else "km" if "km" in total.lower() else ""
    return parse_number(total), unit


def extract_projects(html: str) -> list[dict]:
    m = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not m:
        raise SystemExit("Không tìm thấy mảng projects trong index.html")
    return json.loads(m.group(1))


def replace_projects(html: str, projects: list[dict], data_date: str) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    html = re.sub(r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate", lambda _m: block, html)
    return re.sub(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{data_date}";', html)


def joined(values: list[str]) -> str:
    return "\n".join(v for v in (clean(x) for x in values) if v)


def group_rows(rows: list[list[str]]) -> dict[int, list[list[str]]]:
    groups: dict[int, list[list[str]]] = {}
    current: int | None = None
    for row in rows:
        stt = value_at(row, 0)
        if re.fullmatch(r"\d+(?:\.0)?", stt or ""):
            current = int(float(stt))
            groups[current] = [row]
        elif current is not None:
            groups[current].append(row)
    return groups


def update_projects(projects: list[dict], rows: list[list[str]], data_date: str) -> bool:
    changed = False
    groups = group_rows(rows)
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

        cleared_nums = [parse_number(value_at(r, 4)) for r in group if parse_number(value_at(r, 4)) is not None]
        remaining_nums = [parse_number(value_at(r, 6)) for r in group if parse_number(value_at(r, 6)) is not None]
        if order == 9:
            project.update({"progress": None, "clearedArea": "", "remainingArea": "", "remainingRate": ""})
        elif total_num and unit and cleared_nums:
            cleared = sum(float(x) for x in cleared_nums)
            progress = cleared / total_num * 100
            project["clearedArea"] = f"{fmt(cleared)}/{fmt(total_num)} {unit}"
            project["progress"] = round(progress, 2)
            project["remainingArea"] = f"{fmt(sum(float(x) for x in remaining_nums))} {unit}" if remaining_nums else project.get("remainingArea", "")
            project["remainingRate"] = f"{fmt(max(0, 100 - progress), 2)}%"

        issues = joined([value_at(r, 8) for r in group])
        proposals = joined([value_at(r, 9) for r in group])
        plans = joined([value_at(r, 10) for r in group])
        issue_dates = joined([display_date(value_at(r, 11)) for r in group])
        handover_dates = [display_date(value_at(r, 12)) for r in group if display_date(value_at(r, 12))]
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
            progress = clean(value_at(row, 5))
            remaining = clean(value_at(row, 6))
            remain_rate = clean(value_at(row, 7))
            if area or cleared or progress or remaining or remain_rate:
                note_rows.append(f"{area}: đã bàn giao {cleared}; {progress}%; chưa bàn giao {remaining}; còn {remain_rate}%")
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
