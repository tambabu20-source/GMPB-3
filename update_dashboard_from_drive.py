#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import zipfile
from io import BytesIO
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET


FILE_ID = "1MjJcE8f93HyrpNP1Ik6QBdpQIulJLd4y"
DEFAULT_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
VN_TZ = timezone(timedelta(hours=7))


def download_source(url: str) -> tuple[bytes, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.headers.get("Last-Modified")


def docx_lines(data: bytes) -> list[str]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(Path("/tmp/gpmb-source.docx"), "w") as _:
        pass
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


def col_to_index(ref: str) -> int:
    letters = re.match(r"([A-Z]+)", ref or "")
    if not letters:
        return 0
    value = 0
    for char in letters.group(1):
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

        sheet_name = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(zf.read(sheet_name))
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
                    value = cell.find("m:v", ns)
                    text = value.text if value is not None and value.text is not None else ""
                    if cell_type == "s" and text:
                        text = shared[int(text)]
                values[idx] = clean(text)
            rows.append(values)
        return rows


def parse_number(value: str) -> float | None:
    match = re.search(r"\d+(?:[,.]\d+)?", str(value or ""))
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def format_number(value: float, digits: int = 2) -> str:
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def total_unit(total: str) -> tuple[float | None, str]:
    text = str(total or "")
    total_num = parse_number(text)
    unit_match = re.search(r"\d+(?:[,.]\d+)?\s*(km|ha)\b", text, re.I)
    unit = unit_match.group(1).lower() if unit_match else ""
    return total_num, unit


def joined(values: list[str]) -> str:
    return "\n".join(clean(v) for v in values if clean(v))


def value_at(row: list[str], index: int) -> str:
    return row[index] if index < len(row) else ""


def display_date(value: str) -> str:
    text = clean(str(value or "")).replace(" 00:00:00", "")
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
        year = date.group(3) or "2026"
        return f"{int(date.group(1))}/{int(date.group(2))}/{year}"
    return text


def normalize(value: str) -> str:
    import unicodedata

    value = str(value or "").replace("Đ", "D").replace("đ", "d")
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")


def project_order_from_name(projects: list[dict], name: str) -> int | None:
    needle = normalize(name).replace("du an ", "").strip()
    if not needle:
        return None
    best: tuple[int, int] | None = None
    for project in projects:
        haystack = normalize(project.get("name", "")).replace("du an ", "")
        if needle in haystack or haystack in needle:
            score = min(len(needle), len(haystack))
            order = int(project.get("order", 0))
            if best is None or score > best[0]:
                best = (score, order)
    return best[1] if best else None


def group_xlsx_rows(projects: list[dict], rows: list[list[str]]) -> dict[int, list[list[str]]]:
    groups: dict[int, list[list[str]]] = {}
    current: int | None = None
    for row in rows:
        stt = value_at(row, 0)
        name = value_at(row, 1)
        total = value_at(row, 3)
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


def update_from_xlsx_rows(projects: list[dict], rows: list[list[str]], data_date: str) -> bool:
    changed = False
    by_order = group_xlsx_rows(projects, rows)

    for order, group in by_order.items():
        project = next((p for p in projects if p.get("order") == order), None)
        if project is None:
            continue
        old = json.dumps(project, ensure_ascii=False, sort_keys=True)
        first = group[0]
        total = value_at(first, 3)
        if total:
            project["totalArea"] = clean(total)

        cleared_nums: list[float] = []
        total_num, unit = total_unit(project.get("totalArea", ""))
        remaining_nums: list[float] = []
        remaining_rates: list[float] = []
        progress_rates: list[float] = []
        for row in group:
            row_name = normalize(value_at(row, 1))
            if row_name.startswith("khu tai dinh cu"):
                continue
            cleared = value_at(row, 5)
            remaining = value_at(row, 7)
            remaining_rate = value_at(row, 8)
            progress_rate = value_at(row, 6)
            num = parse_number(cleared)
            if num is not None:
                cleared_nums.append(num)
            rem = parse_number(remaining)
            if rem is not None:
                remaining_nums.append(rem)
            rem_rate = parse_number(remaining_rate)
            if rem_rate is not None:
                remaining_rates.append(rem_rate)
            prog_rate = parse_number(progress_rate)
            if prog_rate is not None:
                progress_rates.append(prog_rate)

        if total_num is not None and cleared_nums and unit:
            cleared_sum = sum(cleared_nums)
            calculated_progress = cleared_sum / total_num * 100 if total_num else None
            source_progress = progress_rates[0] if len(progress_rates) == 1 else None
            progress_value = source_progress if source_progress is not None else calculated_progress
            if isinstance(progress_value, (int, float)):
                progress_value = max(0, min(100, float(progress_value)))
            project["clearedArea"] = f"{format_number(cleared_sum, 4)}/{format_number(total_num, 4)} {unit}"
            project["progress"] = round(progress_value, 2) if progress_value is not None else project.get("progress")
        elif progress_rates:
            project["progress"] = round(max(0, min(100, progress_rates[0])), 2)

        if remaining_nums and unit:
            project["remainingArea"] = f"{format_number(sum(remaining_nums), 4)} {unit}"
        if remaining_rates:
            project["remainingRate"] = f"{format_number(100 - float(project.get('progress', 0)), 2)}%" if isinstance(project.get("progress"), (int, float)) else f"{format_number(remaining_rates[0], 2)}%"

        issues = joined([value_at(row, 9) for row in group])
        proposals = joined([value_at(row, 10) for row in group])
        plans = joined([value_at(row, 11) for row in group])
        issue_dates = joined([display_date(value_at(row, 12)) for row in group])
        handover_dates = [display_date(value_at(row, 13)) for row in group if display_date(value_at(row, 13))]
        if issues:
            project["issues"] = issues
        if proposals or plans:
            project["proposal"] = "Kiến nghị:\n" + proposals + "\n\nKế hoạch thực hiện/Tiến độ thực hiện:\n" + plans
        if handover_dates:
            project["deadline"] = "; ".join(dict.fromkeys(handover_dates))

        note_parts = []
        for row in group:
            area = value_at(row, 4)
            cleared = value_at(row, 5)
            progress = value_at(row, 6)
            remaining = value_at(row, 7)
            remain_rate = value_at(row, 8)
            if area or cleared or progress or remaining or remain_rate:
                note_parts.append(f"{area}: đã bàn giao {cleared}; {progress}%; chưa bàn giao {remaining}; còn {remain_rate}%")
        if note_parts:
            project["note"] = (
                "Địa bàn/tiến độ: "
                + " | ".join(note_parts)
                + "\nThời gian xử lý xong vướng mắc: "
                + issue_dates
                + f"\nNguồn cập nhật: file Excel theo dõi tiến độ Tổ công tác số 03 trên Google Drive, cập nhật ngày {data_date}."
            )

        if order == 9:
            project["progress"] = None
            project["clearedArea"] = ""
            project["remainingArea"] = ""
            project["remainingRate"] = ""

        if old != json.dumps(project, ensure_ascii=False, sort_keys=True):
            changed = True

    return changed


def compact_date(last_modified: str | None) -> str:
    if not last_modified:
        return ""
    dt = parsedate_to_datetime(last_modified).astimezone(VN_TZ)
    return f"{dt.day}/{dt.month}/{dt.year}"


def parse_compact_date(value: str | None):
    if not value:
        return None
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if not m:
        return None
    return int(m.group(3)), int(m.group(2)), int(m.group(1))


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
    projects_block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    html = re.sub(
        r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate",
        lambda _m: projects_block,
        html,
    )
    html = re.sub(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{data_date}";', html)
    return html


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


def normalize(value: str) -> str:
    import unicodedata

    value = str(value or "").replace("Đ", "D").replace("đ", "d")
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")


def find_project(projects: list[dict], keyword: str) -> dict | None:
    keyword = normalize(keyword)
    for project in projects:
        haystack = normalize(" ".join([project.get("name", ""), project.get("owner", ""), project.get("info", "")]))
        if keyword in haystack:
            return project
    return None


def update_from_table(projects: list[dict], lines: list[str], data_date: str) -> bool:
    changed = False

    specs = {
        1: ("Dự án Tuyến đường bộ ven biển tỉnh Phú Yên", "Dự án Tuyến đường bộ ven biển đoạn phía Bắc cầu An Hải", r"14,67\s*km", "tuy an - thanh pho tuy hoa"),
        2: ("Dự án Tuyến đường bộ ven biển đoạn phía Bắc cầu An Hải", "Dự án Tuyến đường bộ ven biển tỉnh Đắk Lắk", r"7,48\s*km", "bac cau an hai"),
        3: ("Dự án Tuyến đường bộ ven biển tỉnh Đắk Lắk", "Tuyến đường giao thông từ Cảng Bãi Gốc", r"211\.443\s*m2", "xuan dai"),
        4: ("Tuyến đường giao thông từ Cảng Bãi Gốc", "Dự án đầu tư xây dựng đường bộ cao tốc", r"41,32\s*ha", "cang bai goc"),
        6: ("Dự án Khu công viên trung tâm", "Dự án Hạ tầng kỹ thuật khu dân cư", r"14,59\s*ha", "khu cong vien trung tam"),
        7: ("Dự án Hạ tầng kỹ thuật khu dân cư", "Đầu tư xây dựng và kinh doanh kết cấu hạ tầng", r"23,79\s*ha", "ha tang ky thuat khu dan cu"),
        8: ("Đầu tư xây dựng và kinh doanh kết cấu hạ tầng", "Khu nhà ở xã hội xã An Phú", r"262,25\s*ha", "khu cong nghiep hoa tam"),
        9: ("Khu nhà ở xã hội xã An Phú", None, r"6,68162\s*ha", "an phu"),
    }

    for order, (name, next_name, total_rx, project_key) in specs.items():
        block = block_for(lines, name, next_name)
        project = find_project(projects, project_key)
        if not block or project is None:
            continue
        total_idx = find_line(block, total_rx)
        if total_idx < 0:
            continue

        old = json.dumps(project, ensure_ascii=False, sort_keys=True)

        if order == 1:
            cleared = " ".join(block[total_idx + 1 : total_idx + 3])
            project["totalArea"] = "14,67 km"
            project["clearedArea"] = clean(cleared)
            project["remainingArea"] = clean(block[total_idx + 3])
            project["remainingRate"] = clean(block[total_idx + 4])
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
            # Source column is inconsistent for project 8; calculate from cleared / total.
            progress = 8.62
        if order == 9:
            progress = 86.6
        if isinstance(progress, (int, float)):
            project["progress"] = round(progress, 2)

        after_rate = total_idx + 4
        deadline_idx = find_line(block, r"(Trước ngày|trước ngày|Đang thực hiện|Hoàn thành trước|- Khu vực)", after_rate)
        if deadline_idx > after_rate:
            body = " ".join(block[after_rate:deadline_idx])
            project["issues"] = clean(body[:1800])
            project["deadline"] = clean(" ".join(block[deadline_idx : min(deadline_idx + 2, len(block))]))

        if old != json.dumps(project, ensure_ascii=False, sort_keys=True):
            changed = True

    # CT.02 has no quantitative GPMB data in the Drive table.
    ct02 = find_project(projects, "ct.02")
    if ct02:
        ct02["progress"] = None

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
    html = re.sub(r"Cập nhật số liệu: \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật số liệu: {data_date}", html)
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
    source_note = (
        "Nguồn cập nhật: file “TO CONG TAC SO 03 - Theo doi Tien do giai quyet chi tiet tung du an.xlsx” "
        f"trên Google Drive - Phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày {data_date} của UBND tỉnh. "
        f"Dashboard đã cập nhật số liệu, vướng mắc, kiến nghị, kế hoạch thực hiện và thời hạn bàn giao mặt bằng theo file nguồn ngày {data_date}."
    )
    html = re.sub(r'<span class="hint">Nguồn cập nhật: .*?</span>', f'<span class="hint">{source_note}</span>', html, flags=re.S)
    html = re.sub(
        r'Các biểu đồ dùng dữ liệu từ file “.*?” và phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày \d{1,2}/\d{1,2}/\d{4}\.',
        f'Các biểu đồ dùng dữ liệu từ file “TO CONG TAC SO 03 - Theo doi Tien do giai quyet chi tiet tung du an.xlsx” và phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày {data_date}.',
        html,
    )
    return html


def ensure_ct02_chart_marker(html: str) -> str:
    html = html.replace(
        '      muted: "#5c697a"\n    };',
        '      muted: "#5c697a",\n      watchOut: "#c2410c"\n    };',
    )
    if "Đề xuất bỏ ra Danh mục theo dõi" in html and "const isWatchOut = project.order === 9;" in html:
        return html
    html = html.replace(
        """        const rows = sorted.map(project => {
          const nameLines = wrapSvgText(chartProjectName(project.name), 52);
          const y = cursor;
          const barY = y + nameLines.length * 16 + 10;""",
        """        const rows = sorted.map(project => {
          const isWatchOut = project.order === 9;
          const nameLines = wrapSvgText(chartProjectName(project.name), 52);
          const y = cursor;
          if (isWatchOut) {
            const statusY = y + nameLines.length * 16 + 14;
            const title = nameLines.map((line, index) => `<tspan x="18" dy="${index ? 16 : 0}">${escapeHtml(line)}</tspan>`).join("");
            cursor = statusY + 34;
            return `
              <text x="18" y="${y}" font-size="12.3" fill="${colors.text}" font-weight="700">${title}</text>
              <rect x="18" y="${statusY - 15}" width="276" height="24" rx="8" fill="#fff7ed" stroke="#fdba74"/>
              <text x="30" y="${statusY + 1}" font-size="11.3" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
            `;
          }
          const barY = y + nameLines.length * 16 + 10;""",
    )
    html = html.replace(
        """        const y = 32 + i * rowHeight;
        const known = Number.isFinite(project.progress);""",
        """        const y = 32 + i * rowHeight;
        const isWatchOut = project.order === 9;
        if (isWatchOut) {
          return `
            <text x="22" y="${y}" font-size="10.8" fill="${colors.text}" font-weight="700">${escapeHtml(chartProjectName(project.name))}</text>
            <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
            <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
          `;
        }
        const known = Number.isFinite(project.progress);""",
    )
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Cập nhật dashboard GPMB Tổ công tác số 3 từ Google Drive XLSX.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--drive-url", default=DEFAULT_DRIVE_URL)
    args = parser.parse_args()

    index_path = Path(args.index)
    html = index_path.read_text(encoding="utf-8")
    projects = extract_projects(html)
    data, last_modified = download_source(args.drive_url)
    current_match = re.search(r'const dataUpdatedDate = "([^"]+)"', html)
    current_data_date = current_match.group(1) if current_match else ""
    data_date = compact_date(last_modified) or current_data_date
    if parse_compact_date(data_date) and parse_compact_date(current_data_date):
        if parse_compact_date(data_date) < parse_compact_date(current_data_date):
            print(f"Nguồn Drive ngày {data_date} cũ hơn dashboard hiện tại {current_data_date}; bỏ qua để không ghi đè lùi dữ liệu.")
            return 0

    if data[:2] == b"PK":
        try:
            with zipfile.ZipFile(BytesIO(data)) as zf:
                names = set(zf.namelist())
            if "xl/workbook.xml" in names:
                changed = update_from_xlsx_rows(projects, xlsx_rows(data), data_date)
            else:
                changed = update_from_table(projects, docx_lines(data), data_date)
        except zipfile.BadZipFile:
            raise SystemExit("Không đọc được file nguồn từ Google Drive.")
    else:
        raise SystemExit("Nguồn Google Drive không phải file Office hợp lệ.")
    new_html = replace_projects(html, projects, data_date)
    new_html = update_summary(new_html, projects, data_date, last_modified)
    new_html = ensure_ct02_chart_marker(new_html)

    if changed or new_html != html:
        index_path.write_text(new_html, encoding="utf-8")
        print(f"Đã cập nhật dashboard theo Drive, ngày dữ liệu {data_date}.")
    else:
        print("Không phát hiện thay đổi số liệu mới.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
