#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def patch_html(html: str) -> str:
    mobile_pattern = r'''          const detailLines = wrapSvgText\(`\$\{percent\} \(\$\{detail\}\)`, 52\)\.slice\(0, 2\);
          const detailText = detailLines\.map\(\(line, lineIndex\) => `<tspan x="18" dy="\$\{lineIndex \? 13 : 0\}">\$\{escapeHtml\(line\)\}</tspan>`\)\.join\(""\);
          return `
            <text x="18" y="\$\{y\}" font-size="11\.8" fill="\$\{colors\.text\}" font-weight="800">\$\{title\}</text>
            <rect x="18" y="\$\{barY\}" width="372" height="16" rx="7" fill="#e7edf2"/>
            <rect x="18" y="\$\{barY\}" width="\$\{Math\.max\(4, progress / 100 \* 372\)\}" height="16" rx="7" fill="\$\{color\}"/>
            <text x="18" y="\$\{barY \+ 32\}" font-size="10\.6" fill="\$\{colors\.text\}" font-weight="800">\$\{detailText\}</text>
          `;'''
    mobile_repl = '''          const detailLines = wrapSvgText(`(${detail})`, 52).slice(0, 2);
          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="6" font-size="10.3" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="13" font-size="10.3" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");
          return `
            <text x="18" y="${y}" font-size="11.8" fill="${colors.text}" font-weight="800">${title}</text>
            <rect x="18" y="${barY}" width="372" height="16" rx="7" fill="#e7edf2"/>
            <rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="16" rx="7" fill="${color}"/>
            <text x="18" y="${barY + 32}" font-weight="800"><tspan font-size="13.2" fill="${color}">${percent}</tspan>${detailText}</text>
          `;'''
    html = re.sub(mobile_pattern, mobile_repl, html, count=1)

    desktop_pattern = r'''        const detailLines = wrapSvgText\(`\$\{percent\} \(\$\{detail\}\)`, 64\)\.slice\(0, 2\);
        const detailText = detailLines\.map\(\(line, lineIndex\) => `<tspan x="\$\{left \+ barW \+ 22\}" dy="\$\{lineIndex \? 13 : 0\}">\$\{escapeHtml\(line\)\}</tspan>`\)\.join\(""\);
        return `
          <text x="22" y="\$\{y\}" font-size="11\.5" fill="\$\{colors\.text\}" font-weight="800">\$\{title\}</text>
          <rect x="\$\{left\}" y="\$\{y - 13\}" width="\$\{barW\}" height="18" rx="7" fill="#e7edf2"/>
          <rect x="\$\{left\}" y="\$\{y - 13\}" width="\$\{fillW\}" height="18" rx="7" fill="\$\{color\}"/>
          <text x="\$\{left \+ barW \+ 22\}" y="\$\{y - 2\}" font-size="10\.3" fill="\$\{colors\.text\}" font-weight="800">\$\{detailText\}</text>
        `;'''
    desktop_repl = '''        const detailLines = wrapSvgText(`(${detail})`, 64).slice(0, 2);
        const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="6" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="${left + barW + 22}" dy="13" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");
        return `
          <text x="22" y="${y}" font-size="11.5" fill="${colors.text}" font-weight="800">${title}</text>
          <rect x="${left}" y="${y - 13}" width="${barW}" height="18" rx="7" fill="#e7edf2"/>
          <rect x="${left}" y="${y - 13}" width="${fillW}" height="18" rx="7" fill="${color}"/>
          <text x="${left + barW + 22}" y="${y - 2}" font-weight="800"><tspan font-size="12.8" fill="${color}">${percent}</tspan>${detailText}</text>
        `;'''
    html = re.sub(desktop_pattern, desktop_repl, html, count=1)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Làm nổi bật số phần trăm tổng trong biểu đồ địa phương.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã làm nổi bật tỷ lệ tổng trong biểu đồ địa phương.")
    else:
        print("Tỷ lệ tổng trong biểu đồ địa phương đã đúng kiểu hiển thị.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
