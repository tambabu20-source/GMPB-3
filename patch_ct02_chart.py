#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

MARKER = "Đề xuất bỏ ra Danh mục theo dõi"
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


def patch_html(html: str) -> str:
    html = html.replace(PROGRESS_LEGEND, "")
    html = html.replace(
        '            <h3>Trạng thái dữ liệu tiến độ GPMB</h3>\n            <div class="legend"><span><i class="dot" style="background:#7b8794"></i> Chưa có tỷ lệ %</span></div>\n',
        '            <h3>Cơ cấu tiến độ 8 dự án có tỷ lệ GPMB</h3>\n',
    )
    html = html.replace(
        'aria-label="Biểu đồ trạng thái dữ liệu tiến độ GPMB"',
        'aria-label="Biểu đồ cơ cấu tiến độ 8 dự án có tỷ lệ GPMB"',
    )
    html = re.sub(
        r'    function drawProgressDataChart\(\) \{[\s\S]*?\n    \}\n\n    function drawProgressPercentChart',
        SUMMARY_DONUT_FUNCTION + '\n\n    function drawProgressPercentChart',
        html,
        count=1,
    )
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

    desktop_old_a = '''const rows = sorted.map((project, i) => {
  const y = 32 + i * rowHeight;
  const known = Number.isFinite(project.progress);'''
    desktop_new_a = '''const rows = sorted.map((project, i) => {
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
    desktop_old_b = '''        const rows = sorted.map((project, i) => {
        const y = 32 + i * rowHeight;
        const known = Number.isFinite(project.progress);'''
    desktop_new_b = '''        const rows = sorted.map((project, i) => {
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
    if desktop_new_a not in html and desktop_new_b not in html:
        html = html.replace(desktop_old_a, desktop_new_a)
        html = html.replace(desktop_old_b, desktop_new_b)

    desktop_existing_a = '''  if (isWatchOut) {
    return `
      <text x="22" y="${y}" font-size="10.8" fill="${colors.text}" font-weight="700">${escapeHtml(chartProjectName(project.name))}</text>
      <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
      <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
    `;
  }'''
    desktop_existing_b = '''        if (isWatchOut) {
          return `
            <text x="22" y="${y}" font-size="10.8" fill="${colors.text}" font-weight="700">${escapeHtml(chartProjectName(project.name))}</text>
            <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
            <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
          `;
        }'''
    desktop_fixed_a = '''  if (isWatchOut) {
    const ct02Lines = wrapSvgText(chartProjectName(project.name), 58);
    const ct02Title = ct02Lines.map((line, index) => `<tspan x="22" dy="${index ? 14 : 0}">${escapeHtml(line)}</tspan>`).join("");
    const ct02TitleY = y - (ct02Lines.length > 1 ? 8 : 0);
    return `
      <text x="22" y="${ct02TitleY}" font-size="10.8" fill="${colors.text}" font-weight="700">${ct02Title}</text>
      <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
      <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
    `;
  }'''
    desktop_fixed_b = '''        if (isWatchOut) {
          const ct02Lines = wrapSvgText(chartProjectName(project.name), 58);
          const ct02Title = ct02Lines.map((line, index) => `<tspan x="22" dy="${index ? 14 : 0}">${escapeHtml(line)}</tspan>`).join("");
          const ct02TitleY = y - (ct02Lines.length > 1 ? 8 : 0);
          return `
            <text x="22" y="${ct02TitleY}" font-size="10.8" fill="${colors.text}" font-weight="700">${ct02Title}</text>
            <rect x="500" y="${y - 16}" width="180" height="22" rx="8" fill="#fff7ed" stroke="#fdba74"/>
            <text x="512" y="${y - 1}" font-size="9.8" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>
          `;
        }'''
    html = html.replace(desktop_existing_a, desktop_fixed_a)
    html = html.replace(desktop_existing_b, desktop_fixed_b)

    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Vá biểu đồ CT.02 trong dashboard GPMB.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã thay biểu đồ trạng thái bằng biểu đồ cơ cấu tiến độ, bỏ chú giải và chống đè chữ CT.02.")
    else:
        print("Biểu đồ CT.02 đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
