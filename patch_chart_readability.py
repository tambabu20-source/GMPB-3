#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        return text
    return text.replace(old, new, 1)


def patch_between(text: str, start: str, end: str, patcher) -> str:
    start_at = text.find(start)
    if start_at == -1:
        return text
    end_at = text.find(end, start_at + len(start))
    if end_at == -1:
        return text
    before = text[:start_at]
    block = text[start_at:end_at]
    after = text[end_at:]
    return before + patcher(block) + after


def patch_css(html: str) -> str:
    html = html.replace(
        ".chart.locality-progress-chart {\n      min-height: 430px;\n    }",
        ".chart.locality-progress-chart {\n      min-height: 500px;\n    }",
    )
    html = html.replace(
        ".chart.progress-percent-chart {\n      height: 520px;\n    }",
        ".chart.progress-percent-chart {\n      height: 610px;\n    }",
    )
    html = html.replace(
        "    .chart-title {\n"
        "      display: flex;\n"
        "      align-items: baseline;\n"
        "      justify-content: space-between;\n"
        "      gap: 10px;\n"
        "      margin-bottom: 12px;\n"
        "    }",
        "    .chart-title {\n"
        "      display: flex;\n"
        "      align-items: baseline;\n"
        "      justify-content: center;\n"
        "      gap: 10px;\n"
        "      margin-bottom: 12px;\n"
        "      text-align: center;\n"
        "    }",
    )
    marker = (
        "    .chart-title h3,\n"
        "    .project-title h3 {\n"
        "      margin: 0;\n"
        "      font-size: 16px;\n"
        "      line-height: 1.25;\n"
        "    }\n"
    )
    extra = (
        marker
        + "\n"
        "    .chart-title h3 {\n"
        "      width: 100%;\n"
        "      font-size: 18px;\n"
        "      text-align: center;\n"
        "    }\n"
    )
    if ".chart-title h3 {\n      width: 100%;" not in html and "".join(marker) in html:
        html = html.replace("".join(marker), "".join(extra), 1)
    return html


def patch_locality_chart(html: str) -> str:
    def patch_block(block: str) -> str:
        replacements = [
            ("const top = isMobile ? 28 : 34;", "const top = isMobile ? 30 : 40;"),
            ("const left = isMobile ? 18 : 260;", "const left = isMobile ? 18 : 285;"),
            ("const right = isMobile ? 24 : 60;", "const right = isMobile ? 20 : 40;"),
            (
                "? 126 + detailLines.length * 18 + Math.max(0, titleLines.length - 1) * 16\n"
                "          : 72 + detailLines.length * 15 + Math.max(0, titleLines.length - 1) * 14;",
                "? 134 + detailLines.length * 19 + Math.max(0, titleLines.length - 1) * 17\n"
                "          : 84 + detailLines.length * 16 + Math.max(0, titleLines.length - 1) * 15;",
            ),
            ('font-size="10.1" fill="${colors.muted}"', 'font-size="10.4" fill="${colors.muted}"'),
            ('dy="18" font-size="10.4"', 'dy="19" font-size="10.4"'),
            ('font-size="10.6" fill="${week.color}"', 'font-size="10.9" fill="${week.color}"'),
            ('font-size="12.2" fill="${colors.text}"', 'font-size="12.8" fill="${colors.text}"'),
            ('height="16" rx="7"', 'height="18" rx="8"'),
            ('height="16" rx="7"', 'height="18" rx="8"'),
            ('barY + 34', 'barY + 36'),
            ('font-size="13.5" fill="${color}"', 'font-size="14.2" fill="${color}"'),
            ('font-size="9.6" fill="${colors.muted}"', 'font-size="10.3" fill="${colors.muted}"'),
            ('dy="15" font-size="10.3"', 'dy="16" font-size="10.3"'),
            ('font-size="10.4" fill="${week.color}"', 'font-size="11" fill="${week.color}"'),
            ('font-size="12.4" fill="${colors.text}"', 'font-size="13.5" fill="${colors.text}"'),
            ('y="${y - 13}" width="${barW}" height="18" rx="7"', 'y="${y - 15}" width="${barW}" height="22" rx="8"'),
            ('y="${y - 13}" width="${fillW}" height="18" rx="7"', 'y="${y - 15}" width="${fillW}" height="22" rx="8"'),
            ('y="${y + 24}" font-weight="800"', 'y="${y + 26}" font-weight="800"'),
            ('font-size="12.8" fill="${color}"', 'font-size="14.2" fill="${color}"'),
        ]
        for old, new in replacements:
            block = replace_once(block, old, new)
        return block

    return patch_between(html, "function drawLocalityProgressChart()", "function drawProgressPercentChart()", patch_block)


def patch_project_chart(html: str) -> str:
    def patch_block(block: str) -> str:
        replacements = [
            ("let cursor = 24;", "let cursor = 28;"),
            ('font-size="12.3" fill="${colors.text}"', 'font-size="12.8" fill="${colors.text}"'),
            ('font-size="12.3" fill="${colors.text}"', 'font-size="12.8" fill="${colors.text}"'),
            ('font-size="10.4" fill="${week.color}"', 'font-size="10.8" fill="${week.color}"'),
            ('height="20" rx="7"', 'height="21" rx="8"'),
            ('height="20" rx="7"', 'height="21" rx="8"'),
            ('font-size="8.8" font-weight="800"', 'font-size="9.4" font-weight="800"'),
            ("const rowHeight = 64;", "const rowHeight = 76;"),
            ("const chartHeight = 38 + sorted.length * rowHeight;", "const chartHeight = 46 + sorted.length * rowHeight;"),
            ('font-size="10.8" fill="${colors.text}"', 'font-size="12" fill="${colors.text}"'),
            ('y="${y - 16}" width="180" height="22" rx="8"', 'y="${y - 18}" width="202" height="26" rx="9"'),
            ('font-size="9.8" fill="${colors.watchOut}"', 'font-size="10.5" fill="${colors.watchOut}"'),
            ("const barW = 190;", "const barW = 220;"),
            ('font-size="10.8" fill="${colors.text}"', 'font-size="12" fill="${colors.text}"'),
            ('height="18" rx="7"', 'height="22" rx="8"'),
            ('height="18" rx="7"', 'height="22" rx="8"'),
            ('<text x="706" y="${y}" font-size="9.2"', '<text x="740" y="${y}" font-size="10.2"'),
            ('<text x="706" y="${y + 17}" font-size="9.6"', '<text x="740" y="${y + 19}" font-size="10.5"'),
        ]
        for old, new in replacements:
            block = replace_once(block, old, new)
        return block

    return patch_between(html, "function drawProgressPercentChart()", '["q", "fundFilter", "ownerFilter"]', patch_block)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    html = patch_css(html)
    html = patch_locality_chart(html)
    html = patch_project_chart(html)
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
