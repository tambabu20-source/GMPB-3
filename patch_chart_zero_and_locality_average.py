#!/usr/bin/env python3
"""Fix zero-progress reason wrapping and locality average calculation."""

from __future__ import annotations

import argparse
from pathlib import Path


REPLACEMENTS = [
    (
        "const avg = rows.reduce((sum, row) => sum + row.progress, 0) / rows.length;\n"
        "        return { locality, rows, progress: Math.max(0, Math.min(100, avg)) };",
        "const rowsForAverage = rows.some(row => row.progress > 0)\n"
        "          ? rows.filter(row => row.progress > 0)\n"
        "          : rows;\n"
        "        const avg = rowsForAverage.reduce((sum, row) => sum + row.progress, 0) / rowsForAverage.length;\n"
        "        return { locality, rows, progress: Math.max(0, Math.min(100, avg)) };",
    ),
    (
        'const zeroReasonY = metricY + 18 + deadlineLines.length * 15;\n'
        '          const zeroReasonText = zeroReason ? `<text x="18" y="${zeroReasonY}" font-size="10.6" fill="#c2410c" font-weight="850">${escapeHtml(zeroReason)}</text>` : "";\n'
        '          const weekY = zeroReasonY + (zeroReason ? 17 : 0);',
        'const zeroReasonY = metricY + 18 + deadlineLines.length * 15;\n'
        '          const zeroReasonLines = zeroReason ? wrapSvgText(zeroReason, 52).slice(0, 2) : [];\n'
        '          const zeroReasonText = zeroReasonLines.map((line, index) => `<text x="18" y="${zeroReasonY + index * 15}" font-size="10.6" fill="#c2410c" font-weight="850">${escapeHtml(line)}</text>`).join("");\n'
        '          const weekY = zeroReasonY + zeroReasonLines.length * 15;',
    ),
    (
        "cursor = metricY + 22 + deadlineLines.length * 15 + (zeroReason ? 17 : 0) + (week ? 22 : 0);",
        "cursor = metricY + 22 + deadlineLines.length * 15 + zeroReasonLines.length * 15 + (week ? 22 : 0);",
    ),
    (
        'const zeroReasonY = y + 18 + deadlineLines.length * 14;\n'
        '        const zeroReasonText = zeroReason ? `<text x="${infoX}" y="${zeroReasonY}" font-size="10.3" fill="#c2410c" font-weight="850">${escapeHtml(zeroReason)}</text>` : "";',
        'const zeroReasonY = y + 18 + deadlineLines.length * 14;\n'
        '        const zeroReasonLines = zeroReason ? wrapSvgText(zeroReason, 37).slice(0, 2) : [];\n'
        '        const zeroReasonText = zeroReasonLines.map((line, index) => `<text x="${infoX}" y="${zeroReasonY + index * 14}" font-size="10.3" fill="#c2410c" font-weight="850">${escapeHtml(line)}</text>`).join("");',
    ),
    (
        "const weekStartY = zeroReasonY + (zeroReason ? 16 : 0);",
        "const weekStartY = zeroReasonY + zeroReasonLines.length * 14;",
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
        print("Đã sửa nguyên nhân 0% và cách tính tỷ lệ địa phương.")
    else:
        print("Nguyên nhân 0% và tỷ lệ địa phương đã đúng.")


if __name__ == "__main__":
    main()
