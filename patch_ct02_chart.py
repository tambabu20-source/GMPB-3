#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "Đề xuất bỏ ra Danh mục theo dõi"


def patch_html(html: str) -> str:
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
        print("Đã thêm nhãn CT.02 và chống đè chữ trong biểu đồ tỷ lệ GPMB.")
    else:
        print("Biểu đồ CT.02 đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
