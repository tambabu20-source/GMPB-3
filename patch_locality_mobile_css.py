#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

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


def patch_html(html: str) -> str:
    html = re.sub(
        r"\n\s*\.chart\.locality-progress-chart \{\s*min-height:\s*\d+px;\s*\}\s*\n\s*@media \(max-width: 720px\) \{\s*\.chart\.locality-progress-chart \{\s*min-height:\s*\d+px;\s*\}\s*\}\s*\n",
        "\n",
        html,
        flags=re.S,
    )
    if ".chart.locality-progress-chart" not in html:
        html = html.replace("    .chart.progress-percent-chart {", CSS + "\n    .chart.progress-percent-chart {", 1)

    html = html.replace(
        'const detailLines = wrapSvgText(`(${detail})`, isMobile ? 56 : 96).slice(0, isMobile ? 5 : 5);',
        'const detailLines = wrapSvgText(`(${detail})`, isMobile ? 50 : 96).slice(0, isMobile ? 6 : 5);',
    )
    html = html.replace(
        '          ? 108 + detailLines.length * 18 + Math.max(0, titleLines.length - 1) * 16',
        '          ? 82 + detailLines.length * 17 + Math.max(0, titleLines.length - 1) * 14',
    )
    html = html.replace(
        '          const barY = y + 28 + titleLines.length * 16;',
        '          const barY = y + 22 + Math.max(0, titleLines.length - 1) * 14;',
    )
    html = html.replace(
        '          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="6" font-size="10.1" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="18" font-size="10.1" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");',
        '          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="7" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="17" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");',
    )
    html = html.replace(
        '          const dividerY = y + rowHeight - 22;',
        '          const dividerY = y + rowHeight - 12;',
    )
    html = html.replace(
        '          return `<text x="18" y="${y}" font-size="12.2" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="16" rx="7" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="16" rx="7" fill="${color}"/><text x="18" y="${barY + 34}" font-weight="800"><tspan font-size="13.5" fill="${color}">${percent}</tspan>${detailText}</text><line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;',
        '          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="16" rx="7" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="16" rx="7" fill="${color}"/><text x="18" y="${barY + 32}" font-weight="800"><tspan font-size="13.8" fill="${color}">${percent}</tspan>${detailText}</text><line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;',
    )

    html = re.sub(
        r"(drawProgressPercentChart\(\);\s*)(?:\n\s*drawLocalityProgressChart\(\);)+",
        lambda m: m.group(1) + "\n        drawLocalityProgressChart();",
        html,
    )
    html = re.sub(
        r"(drawProgressPercentChart\(\);\s*)(?:\n\s*drawLocalityProgressChart\(\);)+",
        lambda m: m.group(1) + "\n    drawLocalityProgressChart();",
        html,
    )
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Làm sạch CSS/call lặp và gom nhóm biểu đồ địa phương trên mobile.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã làm sạch hiển thị biểu đồ địa phương.")
    else:
        print("Hiển thị biểu đồ địa phương đã gọn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
