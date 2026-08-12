#!/usr/bin/env python3
import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--index", default="index.html")
args = parser.parse_args()

path = Path(args.index)
if not path.exists():
    path = Path("outputs/dashboard-to-cong-tac-so-3-gpmb.html")

html = path.read_text(encoding="utf-8")

css = """
    .summary-area-metrics {
      margin-top: 12px;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .summary-area-metric {
      min-width: 0;
      padding: 12px;
      border-radius: var(--radius);
      border: 1px solid #b9d8ec;
      background: linear-gradient(180deg, #f0f8ff 0%, #ffffff 100%);
    }

    .summary-area-metric span {
      display: block;
      color: #31546f;
      font-size: 12px;
      font-weight: 750;
      line-height: 1.3;
    }

    .summary-area-metric b {
      display: block;
      margin-top: 6px;
      color: #0f766e;
      font-size: 18px;
      line-height: 1.15;
      white-space: nowrap;
    }

    .summary-area-metric.campaign b {
      color: #15803d;
    }
"""

if ".summary-area-metrics" not in html:
    html = html.replace(
        "    .summary-chart-title {\n      margin: 14px 0 8px;\n    }\n",
        "    .summary-chart-title {\n      margin: 14px 0 8px;\n    }\n" + css,
        1,
    )

if "Tổng diện tích/chiều dài phải GPMB 7 dự án" not in html:
    block = """
          <div class="summary-area-metrics" aria-label="Tổng hợp khối lượng GPMB 7 dự án">
            <div class="summary-area-metric">
              <span>Tổng diện tích/chiều dài phải GPMB 7 dự án</span>
              <b>29,62 km + 578,25 ha</b>
            </div>
            <div class="summary-area-metric">
              <span>Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>
              <b>28,18 km + 381,77 ha</b>
            </div>
            <div class="summary-area-metric campaign">
              <span>Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>
              <b>1,00 km + 77,21 ha</b>
            </div>
          </div>"""
    html = html.replace(
        '          <svg id="progressDataChart" class="chart summary-status-chart" viewBox="0 0 520 180" role="img" aria-label="Biểu đồ cơ cấu tiến độ 7 dự án có GPMB"></svg>',
        '          <svg id="progressDataChart" class="chart summary-status-chart" viewBox="0 0 520 180" role="img" aria-label="Biểu đồ cơ cấu tiến độ 7 dự án có GPMB"></svg>' + block,
        1,
    )

if ".summary-area-metrics" in html and "grid-template-columns: 1fr;\n      }\n\n      .summary-area-metric b" not in html:
    html = html.replace(
        "      .overall-summary,\n      .summary-metrics {\n        grid-template-columns: 1fr;\n      }\n",
        "      .overall-summary,\n      .summary-metrics {\n        grid-template-columns: 1fr;\n      }\n\n      .summary-area-metrics {\n        grid-template-columns: 1fr;\n      }\n\n      .summary-area-metric b {\n        white-space: normal;\n      }\n",
        1,
    )

path.write_text(html, encoding="utf-8")
