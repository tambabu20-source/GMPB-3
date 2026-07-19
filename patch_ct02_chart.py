#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

PROGRESS_LEGEND = '            <div class="legend"><span><i class="dot" style="background:#0b6b72"></i> Có tỷ lệ %</span><span><i class="dot" style="background:#7b8794"></i> Chưa có tỷ lệ %</span></div>\n'
SUMMARY_DONUT_FUNCTION = '''    function drawProgressDataChart() {
      const svg = document.getElementById("progressDataChart");
      const known = projects.filter(p => Number.isFinite(p.progress));
      const segments = [
        { label: "Từ 90% trở lên", count: known.filter(p => p.progress >= 90).length, color: colors.public },
        { label: "Từ 70% đến dưới 90%", count: known.filter(p => p.progress >= 70 && p.progress < 90).length, color: "#2f855a" },
        { label: "Dưới 70%", count: known.filter(p => p.progress > 0 && p.progress < 70).length, color: "#d97706" },
        { label: "0%", count: known.filter(p => p.progress === 0).length, color: colors.unknown }
      ];
      const total = known.length || 1;
      const cx = 118;
      const cy = 92;
      const r = 56;
      const width = 22;
      const circumference = 2 * Math.PI * r;
      let offset = 0;
      const arcs = segments.map(segment => {
        const length = segment.count / total * circumference;
        const dash = `${Math.max(0, length - 2)} ${circumference}`;
        const arc = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${segment.color}" stroke-width="${width}" stroke-dasharray="${dash}" stroke-dashoffset="${-offset}" transform="rotate(-90 ${cx} ${cy})" stroke-linecap="round"/>`;
        offset += length;
        return arc;
      }).join("");
      const legend = segments.map((segment, index) => {
        const y = 44 + index * 32;
        return `
          <rect x="235" y="${y - 13}" width="14" height="14" rx="4" fill="${segment.color}"/>
          <text x="260" y="${y - 2}" font-size="12.2" fill="${colors.text}" font-weight="700">${segment.label}</text>
          <text x="460" y="${y - 2}" font-size="12.2" fill="${colors.text}" font-weight="800" text-anchor="end">${segment.count} dự án</text>
        `;
      }).join("");
      svg.innerHTML = `
        <rect x="0" y="0" width="520" height="180" fill="transparent"/>
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e7edf2" stroke-width="${width}"/>
        ${arcs}
        <text x="${cx}" y="${cy - 4}" font-size="25" fill="${colors.text}" font-weight="800" text-anchor="middle">${known.length}</text>
        <text x="${cx}" y="${cy + 17}" font-size="11.5" fill="${colors.muted}" font-weight="700" text-anchor="middle">dự án có %</text>
        ${legend}
      `;
    }'''
CT02_CARD_CSS = '''
    .progress-panel.watch-out {
      border-color: #fb923c;
      background: #fff7ed;
      box-shadow: inset 0 0 0 1px rgba(251, 146, 60, .35);
    }

    .watch-out-label {
      display: block;
      padding: 9px 10px;
      border: 1px solid #fdba74;
      border-radius: 8px;
      background: #ffedd5;
      color: #c2410c;
      font-size: 13px;
      font-weight: 800;
      line-height: 1.25;
      text-align: center;
      overflow-wrap: anywhere;
    }

    .watch-out-note {
      margin-top: 8px;
      color: #9a3412;
      font-size: 12px;
      font-weight: 700;
      line-height: 1.3;
    }
'''


def patch_summary_chart(html: str) -> str:
    html = html.replace(PROGRESS_LEGEND, "")
    html = html.replace(
        '            <h3>Trạng thái dữ liệu tiến độ GPMB</h3>\n            <div class="legend"><span><i class="dot" style="background:#7b8794"></i> Chưa có tỷ lệ %</span></div>\n',
        '            <h3>Cơ cấu tiến độ 8 dự án có tỷ lệ GPMB</h3>\n',
    )
    html = html.replace(
        'aria-label="Biểu đồ trạng thái dữ liệu tiến độ GPMB"',
        'aria-label="Biểu đồ cơ cấu tiến độ 8 dự án có tỷ lệ GPMB"',
    )
    return re.sub(
        r'    function drawProgressDataChart\(\) \{[\s\S]*?\n    \}\n\n    function drawProgressPercentChart',
        SUMMARY_DONUT_FUNCTION + '\n\n    function drawProgressPercentChart',
        html,
        count=1,
    )


def patch_ct02_project_card(html: str) -> str:
    if ".progress-panel.watch-out" not in html:
        html = html.replace(
            '''    .progress-panel.no-rate {
      border-color: #b8c7e6;
      background: #f1f5ff;
    }
''',
            '''    .progress-panel.no-rate {
      border-color: #b8c7e6;
      background: #f1f5ff;
    }
''' + CT02_CARD_CSS,
        )
    html = html.replace(
        '        const hasSingleRate = Number.isFinite(project.progress);\n        const compactRatio = compactAreaRatio(project);',
        '        const hasSingleRate = Number.isFinite(project.progress);\n        const isWatchOutProject = project.order === 9;\n        const compactRatio = compactAreaRatio(project);',
    )
    old_panel = '''          <div class="progress-panel ${hasSingleRate ? "" : "no-rate"}" aria-label="Tiến độ GPMB">
            <div class="progress-row"><span class="progress-label">Tiến độ GPMB</span><strong>${percent}</strong>${areaRatio ? `<span class="area-ratio">Đã GPMB ${areaRatio}</span>` : ""}</div>
            ${deadlineLabel ? `<div class="progress-deadline"><span>Dự kiến hoàn thành</span><strong>${deadlineLabel}</strong></div>` : ""}
            <div class="bar"><div class="fill ${hasSingleRate ? "" : "pending"}" style="--p:${width}"></div></div>
            <div class="status ${statusClass}">${hasSingleRate ? `Theo số liệu đến ngày ${dataUpdatedDate}` : "Chưa có tỷ lệ % GPMB"}</div>
          </div>'''
    new_panel = '''          <div class="progress-panel ${isWatchOutProject ? "watch-out" : (hasSingleRate ? "" : "no-rate")}" aria-label="Tiến độ GPMB">
            ${isWatchOutProject ? `
              <span class="watch-out-label">Đề xuất bỏ ra khỏi Danh mục theo dõi</span>
              <div class="watch-out-note">CT.02 chưa có số liệu diện tích thực địa để tính tỷ lệ GPMB.</div>
            ` : `
              <div class="progress-row"><span class="progress-label">Tiến độ GPMB</span><strong>${percent}</strong>${areaRatio ? `<span class="area-ratio">Đã GPMB ${areaRatio}</span>` : ""}</div>
              ${deadlineLabel ? `<div class="progress-deadline"><span>Dự kiến hoàn thành</span><strong>${deadlineLabel}</strong></div>` : ""}
              <div class="bar"><div class="fill ${hasSingleRate ? "" : "pending"}" style="--p:${width}"></div></div>
              <div class="status ${statusClass}">${hasSingleRate ? `Theo số liệu đến ngày ${dataUpdatedDate}` : "Chưa có tỷ lệ % GPMB"}</div>
            `}
          </div>'''
    return html.replace(old_panel, new_panel)


def patch_ct02_progress_chart(html: str) -> str:
    html = html.replace(
        '      muted: "#5c697a"\n    };',
        '      muted: "#5c697a",\n      watchOut: "#c2410c"\n    };',
    )
    mobile_old = '''        const rows = sorted.map(project => {
          const nameLines = wrapSvgText(chartProjectName(project.name), 52);
          const y = cursor;
          const barY = y + nameLines.length * 16 + 10;'''
    mobile_new = '''        const rows = sorted.map(project => {
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
          const barY = y + nameLines.length * 16 + 10;'''
    if mobile_new not in html:
        html = html.replace(mobile_old, mobile_new)

    old_watch = '''  if (isWatchOut) {
    return `
      <text x="22" y="${y}" font-size="10.8" fill="${colors.text}" font-weight="700">${escapeHtml(chartProjectName(project.name))}</text>
      <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
      <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
    `;
  }'''
    new_watch = '''  if (isWatchOut) {
    const ct02Lines = wrapSvgText(chartProjectName(project.name), 58);
    const ct02Title = ct02Lines.map((line, index) => `<tspan x="22" dy="${index ? 14 : 0}">${escapeHtml(line)}</tspan>`).join("");
    const ct02TitleY = y - (ct02Lines.length > 1 ? 8 : 0);
    return `
      <text x="22" y="${ct02TitleY}" font-size="10.8" fill="${colors.text}" font-weight="700">${ct02Title}</text>
      <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
      <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
    `;
  }'''
    html = html.replace(old_watch, new_watch)
    old_start = '''const rows = sorted.map((project, i) => {
  const y = 32 + i * rowHeight;
  const known = Number.isFinite(project.progress);'''
    new_start = '''const rows = sorted.map((project, i) => {
  const y = 32 + i * rowHeight;
  const isWatchOut = project.order === 9;
  if (isWatchOut) {
    const ct02Lines = wrapSvgText(chartProjectName(project.name), 58);
    const ct02Title = ct02Lines.map((line, index) => `<tspan x="22" dy="${index ? 14 : 0}">${escapeHtml(line)}</tspan>`).join("");
    const ct02TitleY = y - (ct02Lines.length > 1 ? 8 : 0);
    return `
      <text x="22" y="${ct02TitleY}" font-size="10.8" fill="${colors.text}" font-weight="700">${ct02Title}</text>
      <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
      <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
    `;
  }
  const known = Number.isFinite(project.progress);'''
    return html.replace(old_start, new_start)


def patch_html(html: str) -> str:
    html = patch_summary_chart(html)
    html = patch_ct02_project_card(html)
    html = patch_ct02_progress_chart(html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Vá dashboard GPMB Tổ công tác số 3.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã cập nhật biểu đồ và nhãn đề xuất loại CT.02.")
    else:
        print("Dashboard đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
