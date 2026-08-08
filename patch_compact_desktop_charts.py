#!/usr/bin/env python3
"""Compact desktop chart spacing without changing mobile chart layout."""

from __future__ import annotations

import argparse
from pathlib import Path


REPLACEMENTS = [
    (".chart.locality-progress-chart {\n      min-height: 500px;\n    }", ".chart.locality-progress-chart {\n      min-height: 455px;\n    }"),
    (".chart.progress-percent-chart {\n      height: 610px;\n    }", ".chart.progress-percent-chart {\n      height: 540px;\n    }"),
    ("const top = isMobile ? 30 : 40;", "const top = isMobile ? 30 : 30;"),
    (": 84 + detailLines.length * 16 + Math.max(0, titleLines.length - 1) * 15;", ": 66 + detailLines.length * 14 + Math.max(0, titleLines.length - 1) * 13;"),
    ("const height = cursor + 24;", "const height = cursor + (isMobile ? 24 : 12);"),
    ("const weekY = y + 24 + Math.max(1, detailLines.length) * 15;", "const weekY = y + 22 + Math.max(1, detailLines.length) * 13;"),
    (
        'return `<text x="22" y="${y}" font-size="13.5" fill="${colors.text}" font-weight="850">${title}</text><rect x="${left}" y="${y - 15}" width="${barW}" height="22" rx="8" fill="#e7edf2"/><rect x="${left}" y="${y - 15}" width="${fillW}" height="22" rx="8" fill="${color}"/><text x="${left}" y="${y + 26}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}`;',
        'return `<text x="22" y="${y}" font-size="13.5" fill="${colors.text}" font-weight="850">${title}</text><rect x="${left}" y="${y - 14}" width="${barW}" height="20" rx="8" fill="#e7edf2"/><rect x="${left}" y="${y - 14}" width="${fillW}" height="20" rx="8" fill="${color}"/><text x="${left}" y="${y + 24}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}`;',
    ),
    ("const rowHeight = 78;", "const rowHeight = 66;"),
    ("const chartHeight = 46 + sorted.length * rowHeight;", "const chartHeight = 38 + sorted.length * rowHeight;"),
    ("const y = 32 + i * rowHeight;", "const y = 28 + i * rowHeight;"),
    (
        '<rect x="560" y="${y - 18}" width="230" height="26" rx="9" fill="#fff7ed" stroke="#fdba74"/>\n            <text x="575" y="${y - 1}" font-size="10.5" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>',
        '<rect x="560" y="${y - 16}" width="230" height="24" rx="9" fill="#fff7ed" stroke="#fdba74"/>\n            <text x="575" y="${y}" font-size="10.5" fill="${colors.watchOut}" font-weight="800">Đề xuất bỏ ra Danh mục theo dõi</text>',
    ),
    (
        '<rect x="${barX}" y="${y - 16}" width="${barW}" height="22" rx="8" fill="#e7edf2"/>\n          <rect x="${barX}" y="${y - 16}" width="${w}" height="22" rx="8" fill="${fill}"/>',
        '<rect x="${barX}" y="${y - 15}" width="${barW}" height="20" rx="8" fill="#e7edf2"/>\n          <rect x="${barX}" y="${y - 15}" width="${w}" height="20" rx="8" fill="${fill}"/>',
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    updated = html
    for old, new in REPLACEMENTS:
        updated = updated.replace(old, new)

    if updated != html:
        path.write_text(updated, encoding="utf-8")
        print("Đã thu gọn khoảng cách biểu đồ desktop.")
    else:
        print("Biểu đồ desktop đã ở trạng thái gọn.")


if __name__ == "__main__":
    main()
