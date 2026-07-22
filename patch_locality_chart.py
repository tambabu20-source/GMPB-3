#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CHART_CARD = '''        <article class="card card-pad locality-progress-card">
          <div class="chart-title">
            <h3>Thống kê tiến độ GPMB theo địa phương</h3>
          </div>
          <svg id="localityProgressChart" class="chart locality-progress-chart" viewBox="0 0 900 320" role="img" aria-label="Biểu đồ thống kê tiến độ GPMB theo địa phương"></svg>
        </article>'''

CSS = '''
    .chart.locality-progress-chart {
      min-height: 360px;
    }

    @media (max-width: 720px) {
      .chart.locality-progress-chart {
        min-height: 520px;
      }
    }
'''

JS = r'''    function compactLocalityProjectName(name) {
      return chartProjectName(name)
        .replace(/^Tuyến đường giao thông từ\s+/i, "")
        .replace(/^Tuyến đường bộ ven biển,?\s*/i, "Ven biển ")
        .replace(/^Đầu tư xây dựng và kinh doanh kết cấu hạ tầng\s+/i, "")
        .replace(/^Đầu tư xây dựng\s+/i, "")
        .replace(/Khu kinh tế Vân Phong/i, "KKT Vân Phong")
        .replace(/Thành phố Tuy Hòa/i, "TP Tuy Hòa")
        .replace(/Khu đô thị mới Nam/i, "KĐT mới Nam")
        .trim();
    }

    function compactLocalityArea(text) {
      const value = String(text || "").trim().replace(/\s+/g, " ");
      if (!value) return "";
      return value
        .replace(/\s*Km\b/g, "km")
        .replace(/\s*ha\b/g, "ha")
        .replace(/\s*m\b/g, "m");
    }

    function extractLocalityRows() {
      const rows = [];
      const rx = /([^|\n:]+):\s*đã bàn giao\s*([^;]+);\s*([\d.,]+)%+;\s*chưa bàn giao\s*([^;]+);\s*còn\s*([\d.,]+)%+/gi;
      projects.forEach(project => {
        const note = String(project.note || "");
        let match;
        while ((match = rx.exec(note)) !== null) {
          const locality = match[1].replace(/^Địa bàn\/tiến độ:\s*/i, "").trim();
          const progress = parseFloat(String(match[3]).replace(",", "."));
          if (!locality || !Number.isFinite(progress)) continue;
          rows.push({
            locality,
            projectName: compactLocalityProjectName(project.name),
            progress: Math.max(0, Math.min(100, progress)),
            cleared: compactLocalityArea(match[2]),
            remaining: compactLocalityArea(match[4]),
            remainingRate: match[5].trim()
          });
        }
      });
      return rows;
    }

    function drawLocalityProgressChart() {
      const svg = document.getElementById("localityProgressChart");
      if (!svg) return;
      const data = extractLocalityRows().sort((a, b) => b.progress - a.progress || a.locality.localeCompare(b.locality, "vi"));
      if (!data.length) {
        svg.innerHTML = `<text x="24" y="48" font-size="14" fill="${colors.muted}" font-weight="700">Chưa có dữ liệu địa phương để thống kê.</text>`;
        return;
      }
      const isMobile = window.matchMedia("(max-width: 720px)").matches;
      const width = isMobile ? 390 : 900;
      const rowHeight = isMobile ? 76 : 48;
      const top = isMobile ? 30 : 34;
      const left = isMobile ? 18 : 275;
      const right = isMobile ? 24 : 300;
      const barW = width - left - right;
      const height = top + data.length * rowHeight + 28;
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      svg.innerHTML = data.map((item, index) => {
        const y = top + index * rowHeight;
        const progress = Math.max(0, Math.min(100, item.progress));
        const fillW = Math.max(4, progress / 100 * barW);
        const color = progress >= 90 ? colors.public : progress >= 70 ? "#2f855a" : progress > 0 ? "#d97706" : colors.unknown;
        const percent = `${progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%`;
        const detail = `${percent} (${item.cleared} - Dự án ${item.projectName})`;
        if (isMobile) {
          const localityLines = wrapSvgText(item.locality, 38).slice(0, 2);
          const title = localityLines.map((line, lineIndex) => `<tspan x="18" dy="${lineIndex ? 14 : 0}">${escapeHtml(line)}</tspan>`).join("");
          const barY = y + localityLines.length * 14 + 8;
          const detailLines = wrapSvgText(detail, 48).slice(0, 2);
          const detailText = detailLines.map((line, lineIndex) => `<tspan x="18" dy="${lineIndex ? 13 : 0}">${escapeHtml(line)}</tspan>`).join("");
          return `
            <text x="18" y="${y}" font-size="11.8" fill="${colors.text}" font-weight="800">${title}</text>
            <rect x="18" y="${barY}" width="348" height="13" rx="6.5" fill="#e7edf2"/>
            <rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 348)}" height="13" rx="6.5" fill="${color}"/>
            <text x="18" y="${barY + 30}" font-size="10.8" fill="${colors.text}" font-weight="800">${detailText}</text>
          `;
        }
        const localityLines = wrapSvgText(item.locality, 45).slice(0, 2);
        const title = localityLines.map((line, lineIndex) => `<tspan x="22" dy="${lineIndex ? 13 : 0}">${escapeHtml(line)}</tspan>`).join("");
        const detailLines = wrapSvgText(detail, 58).slice(0, 2);
        const detailText = detailLines.map((line, lineIndex) => `<tspan x="${left + barW + 22}" dy="${lineIndex ? 13 : 0}">${escapeHtml(line)}</tspan>`).join("");
        return `
          <text x="22" y="${y}" font-size="11.5" fill="${colors.text}" font-weight="800">${title}</text>
          <rect x="${left}" y="${y - 13}" width="${barW}" height="16" rx="8" fill="#e7edf2"/>
          <rect x="${left}" y="${y - 13}" width="${fillW}" height="16" rx="8" fill="${color}"/>
          <text x="${left + barW + 22}" y="${y - 2}" font-size="10.5" fill="${colors.text}" font-weight="800">${detailText}</text>
        `;
      }).join("");
    }
'''


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
    return re.sub(r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate", lambda _m: block, html, count=1)


def parse_project1_localities(note: str) -> list[tuple[float, float]]:
    rows: list[tuple[float, float]] = []
    normalized = re.sub(r"([\d.,]+)\s*([a-zA-Z]+)\s*/\s*([\d.,]+)\s*\2", r"\1/\3 \2", note)
    rx = re.compile(r"đã bàn giao\s*([\d.,]+)(?:\s*/\s*([\d.,]+))?\s*([a-zA-Z]*)\s*;\s*([\d.,]+)%+", re.I)
    for match in rx.finditer(normalized):
        cleared = float(match.group(1).replace(",", "."))
        total = float(match.group(2).replace(",", ".")) if match.group(2) else None
        unit = (match.group(3) or "").lower()
        percent = float(match.group(4).replace(",", "."))
        if unit == "m":
            cleared = cleared / 1000
            if total is not None:
                total = total / 1000
        if total and total > 0:
            rows.append((min(cleared, total), total))
        elif percent <= 100:
            rows.append((percent, 100.0))
    return rows


def fix_project1(projects: list[dict]) -> bool:
    project = next((p for p in projects if p.get("order") == 1), None)
    if not project:
        return False
    rows = parse_project1_localities(str(project.get("note") or ""))
    total_match = re.search(r"\d+(?:[,.]\d+)?", str(project.get("totalArea") or ""))
    total = float(total_match.group(0).replace(",", ".")) if total_match else None
    if len(rows) < 2 or not total:
        return False
    cleared_sum = sum(row[0] for row in rows)
    denom_sum = sum(row[1] for row in rows)
    if denom_sum <= 0:
        return False
    progress = max(0, min(99.99, cleared_sum / denom_sum * 100))
    cleared = total * progress / 100
    remaining = max(0, total - cleared)
    old = json.dumps(project, ensure_ascii=False, sort_keys=True)
    project["progress"] = round(progress, 2)
    project["clearedArea"] = f"{fmt(cleared)}/{fmt(total)} km"
    project["remainingArea"] = f"{fmt(remaining)} km"
    project["remainingRate"] = f"{fmt(100 - progress, 2)}%"
    return old != json.dumps(project, ensure_ascii=False, sort_keys=True)


def patch_markup(html: str) -> str:
    if "localityProgressChart" not in html:
        html = html.replace(
            '''          <svg id="progressPercentChart" class="chart progress-percent-chart" viewBox="0 0 900 340" role="img" aria-label="Biểu đồ tỷ lệ phần trăm tiến độ GPMB các dự án"></svg>
        </article>''',
            '''          <svg id="progressPercentChart" class="chart progress-percent-chart" viewBox="0 0 900 340" role="img" aria-label="Biểu đồ tỷ lệ phần trăm tiến độ GPMB các dự án"></svg>
        </article>
''' + CHART_CARD,
        )
    html = re.sub(r"\n\s*\.chart\.locality-progress-chart \{[\s\S]*?\n\s*\}\n\n\s*@media \(max-width: 720px\) \{\n\s*\.chart\.locality-progress-chart \{[\s\S]*?\n\s*\}\n\s*\}\n", "\n" + CSS + "\n", html, count=1)
    if ".chart.locality-progress-chart" not in html:
        html = html.replace("    .chart.progress-percent-chart {", CSS + "\n    .chart.progress-percent-chart {")
    return html


def replace_function_block(html: str, function_name: str, replacement: str) -> str:
    marker = f"    function {function_name}()"
    start = html.find(marker)
    if start == -1:
        return html
    brace = html.find("{", start)
    depth = 0
    for i in range(brace, len(html)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                return html[:start] + replacement.rstrip() + "\n" + html[i + 1:]
    return html


def patch_js(html: str) -> str:
    if "function drawLocalityProgressChart" in html:
        html = replace_function_block(html, "extractLocalityRows", "")
        html = replace_function_block(html, "drawLocalityProgressChart", "")
        html = re.sub(r"\n{3,}", "\n\n", html)
    html = html.replace("    function drawProgressPercentChart() {", JS + "\n    function drawProgressPercentChart() {")
    html = re.sub(r"(?:\n\s*drawLocalityProgressChart\(\);)+", "\n    drawLocalityProgressChart();", html)
    html = html.replace("        drawProgressPercentChart();\n    drawLocalityProgressChart();", "        drawProgressPercentChart();\n        drawLocalityProgressChart();")
    if "drawLocalityProgressChart();" not in html:
        html = html.replace("    drawProgressPercentChart();", "    drawProgressPercentChart();\n    drawLocalityProgressChart();")
    return html


def patch_html(html: str) -> str:
    projects = extract_projects(html)
    if fix_project1(projects):
        html = replace_projects(html, projects)
    html = patch_markup(html)
    html = patch_js(html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Sửa tỷ lệ dự án 1 và thêm biểu đồ địa phương.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã sửa tỷ lệ dự án 1 và cập nhật biểu đồ địa phương.")
    else:
        print("Dashboard đã có biểu đồ địa phương và tỷ lệ dự án 1 hợp lệ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
