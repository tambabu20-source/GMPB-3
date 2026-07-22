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
    parser = argparse.ArgumentParser(description="Làm sạch CSS/call lặp của biểu đồ địa phương.")
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
