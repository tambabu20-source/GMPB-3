#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
      min-height: 430px;
    }

    @media (max-width: 720px) {
      .chart.locality-progress-chart {
        min-height: 760px;
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
        .replace(/đoạn kết nối huyện Tuy An -/i, "Tuy An -")
        .replace(/đoạn phía Bắc cầu An Hải/i, "Bắc cầu An Hải")
        .trim();
    }

    function compactLocalityArea(text) {
      const value = String(text || "").trim().replace(/\s+/g, " ");
      if (!value || !value.includes("/")) return "diện tích đang rà soát";
      return value
        .replace(/\s*Km\b/g, "km")
        .replace(/\s*ha\b/g, "ha")
        .replace(/\s*m\b/g, "m");
    }

    function readLocalityNumber(text, unit) {
      const raw = String(text || "").trim();
      if (String(unit || "").toLowerCase() === "m" && /^\d{1,3}(?:\.\d{3})+$/.test(raw)) {
        return Number(raw.replace(/\./g, ""));
      }
      return Number(raw.replace(",", "."));
    }

    function calculateLocalityProgress(clearedText) {
      const match = String(clearedText || "").match(/([\d.,]+)\s*\/\s*([\d.,]+)\s*([a-zA-Z]*)/);
      if (!match) return null;
      const unit = match[3] || "";
      const cleared = readLocalityNumber(match[1], unit);
      const total = readLocalityNumber(match[2], unit);
      if (!Number.isFinite(cleared) || !Number.isFinite(total) || total <= 0) return null;
      return Math.max(0, Math.min(100, cleared / total * 100));
    }

    function extractLocalityRows() {
      const rows = [];
      const rx = /([^|\n:;]+)[:;]\s*đã bàn giao\s*([^;]+);\s*([\d.,]+)%+;\s*chưa bàn giao\s*([^;]+);\s*còn\s*([\d.,]+)%+/gi;
      projects.forEach(project => {
        const note = String(project.note || "");
        let match;
        while ((match = rx.exec(note)) !== null) {
          const locality = match[1].replace(/^Địa bàn\/tiến độ:\s*/i, "").trim();
          const sourceProgress = parseFloat(String(match[3]).replace(",", "."));
          const calculatedProgress = calculateLocalityProgress(match[2]);
          const progress = Number.isFinite(calculatedProgress) ? calculatedProgress : sourceProgress;
          if (!locality || !Number.isFinite(progress)) continue;
          rows.push({
            locality,
            projectName: compactLocalityProjectName(project.name),
            progress: Math.max(0, Math.min(100, progress)),
            cleared: compactLocalityArea(match[2])
          });
        }
      });
      return rows;
    }

    function localityDetail(rows) {
      return rows.map(row => {
        const percent = row.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 });
        return `${percent}% ${row.cleared} - ${row.projectName}`;
      }).join("; ");
    }

    function drawLocalityProgressChart() {
      const svg = document.getElementById("localityProgressChart");
      if (!svg) return;
      const grouped = new Map();
      extractLocalityRows().forEach(row => {
        if (!grouped.has(row.locality)) grouped.set(row.locality, []);
        grouped.get(row.locality).push(row);
      });
      const data = Array.from(grouped, ([locality, rows]) => {
        const avg = rows.reduce((sum, row) => sum + row.progress, 0) / rows.length;
        return { locality, rows, progress: Math.max(0, Math.min(100, avg)) };
      }).sort((a, b) => b.progress - a.progress || a.locality.localeCompare(b.locality, "vi"));
      if (!data.length) {
        svg.innerHTML = `<text x="24" y="48" font-size="14" fill="${colors.muted}" font-weight="700">Chưa có dữ liệu địa phương để thống kê.</text>`;
        return;
      }
      const isMobile = window.matchMedia("(max-width: 720px)").matches;
      const width = isMobile ? 420 : 900;
      const top = isMobile ? 28 : 34;
      const left = isMobile ? 18 : 260;
      const right = isMobile ? 24 : 260;
      const barW = width - left - right;
      const layouts = data.map(item => {
        const detail = localityDetail(item.rows);
        const titleLines = wrapSvgText(item.locality, isMobile ? 44 : 42).slice(0, 2);
        const detailLines = wrapSvgText(`(${detail})`, isMobile ? 56 : 74).slice(0, isMobile ? 5 : 4);
        const rowHeight = isMobile
          ? 58 + detailLines.length * 13 + Math.max(0, titleLines.length - 1) * 14
          : 38 + detailLines.length * 13 + Math.max(0, titleLines.length - 1) * 13;
        return { item, titleLines, detailLines, rowHeight };
      });
      let cursor = top;
      const positioned = layouts.map(layout => {
        const y = cursor;
        cursor += layout.rowHeight;
        return { ...layout, y };
      });
      const height = cursor + 24;
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, y }) => {
        const progress = Math.max(0, Math.min(100, item.progress));
        const fillW = Math.max(4, progress / 100 * barW);
        const color = progress >= 90 ? colors.public : progress >= 70 ? "#2f855a" : progress > 0 ? "#d97706" : colors.unknown;
        const percent = `${progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%`;
        if (isMobile) {
          const title = titleLines.map((line, lineIndex) => `<tspan x="18" dy="${lineIndex ? 14 : 0}">${escapeHtml(line)}</tspan>`).join("");
          const barY = y + 24 + titleLines.length * 14;
          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="6" font-size="10.3" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="13" font-size="10.3" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");
          return `
            <text x="18" y="${y}" font-size="11.8" fill="${colors.text}" font-weight="800">${title}</text>
            <rect x="18" y="${barY}" width="372" height="16" rx="7" fill="#e7edf2"/>
            <rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="16" rx="7" fill="${color}"/>
            <text x="18" y="${barY + 32}" font-weight="800"><tspan font-size="13.2" fill="${color}">${percent}</tspan>${detailText}</text>
          `;
        }
        const title = titleLines.map((line, lineIndex) => `<tspan x="22" dy="${lineIndex ? 13 : 0}">${escapeHtml(line)}</tspan>`).join("");
        const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="6" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="${left + barW + 22}" dy="13" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");
        return `
          <text x="22" y="${y}" font-size="11.5" fill="${colors.text}" font-weight="800">${title}</text>
          <rect x="${left}" y="${y - 13}" width="${barW}" height="18" rx="7" fill="#e7edf2"/>
          <rect x="${left}" y="${y - 13}" width="${fillW}" height="18" rx="7" fill="${color}"/>
          <text x="${left + barW + 22}" y="${y - 2}" font-weight="800"><tspan font-size="12.8" fill="${color}">${percent}</tspan>${detailText}</text>
        `;
      }).join("");
    }
'''


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
    marker = f"    function {function_name}"
    start = html.find(marker)
    if start == -1:
        return html
    next_function = html.find("\n    function ", start + len(marker))
    if next_function == -1:
        return html[:start] + replacement.rstrip() + "\n"
    return html[:start] + replacement.rstrip() + "\n" + html[next_function:]


def patch_js(html: str) -> str:
    for name in [
        "compactLocalityProjectName",
        "compactLocalityArea",
        "readLocalityNumber",
        "calculateLocalityProgress",
        "extractLocalityRows",
        "localityDetail",
        "drawLocalityProgressChart",
    ]:
        html = replace_function_block(html, name, "")
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = html.replace("    function drawProgressPercentChart() {", JS + "\n    function drawProgressPercentChart() {", 1)
    html = re.sub(r"(?:\n\s*drawLocalityProgressChart\(\);)+", "\n    drawLocalityProgressChart();", html)
    html = html.replace("        drawProgressPercentChart();\n    drawLocalityProgressChart();", "        drawProgressPercentChart();\n        drawLocalityProgressChart();")
    if "drawLocalityProgressChart();" not in html:
        html = html.replace("    drawProgressPercentChart();", "    drawProgressPercentChart();\n    drawLocalityProgressChart();")
    return html


def patch_html(html: str) -> str:
    html = patch_markup(html)
    html = patch_js(html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Thêm và chỉnh biểu đồ tiến độ GPMB theo địa phương.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã cập nhật biểu đồ địa phương.")
    else:
        print("Dashboard đã có biểu đồ địa phương đúng định dạng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
