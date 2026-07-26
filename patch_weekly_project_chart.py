#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def patch_html(html: str) -> str:
    if "const week = projectWeeklyMeta(project);" in html:
        return html

    html = html.replace(
        '    .chart.progress-percent-chart {\n      height: 430px;\n    }',
        '    .chart.progress-percent-chart {\n      height: 520px;\n    }',
    )
    html = html.replace(
        '      .chart.progress-percent-chart {\n        height: 980px;\n      }',
        '      .chart.progress-percent-chart {\n        height: 1120px;\n      }',
    )

    html = html.replace(
        '          const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";\n          const title = nameLines.map((line, index) => `<tspan x="18" dy="${index ? 16 : 0}">${escapeHtml(line)}</tspan>`).join("");\n          cursor = metricY + 24;',
        '          const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";\n          const week = projectWeeklyMeta(project);\n          const weekText = week ? `<text x="18" y="${metricY + 22}" font-size="10.4" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n          const title = nameLines.map((line, index) => `<tspan x="18" dy="${index ? 16 : 0}">${escapeHtml(line)}</tspan>`).join("");\n          cursor = metricY + (week ? 46 : 24);',
        1,
    )
    html = html.replace(
        '            </text>\n          `;\n        }).join("");\n        const height = Math.max(420, cursor + 8);',
        '            </text>\n            ${weekText}\n          `;\n        }).join("");\n        const height = Math.max(420, cursor + 8);',
        1,
    )
    html = html.replace('      const rowHeight = 48;', '      const rowHeight = 64;', 1)
    html = html.replace(
        '        const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";\n        return `',
        '        const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";\n        const week = projectWeeklyMeta(project);\n        return `',
        1,
    )
    html = html.replace(
        '          </text>\n        `;\n      }).join("");\n      svg.innerHTML = `<rect x="0" y="0" width="900" height="${chartHeight}" fill="transparent"/>${rows}`;',
        '          </text>\n          ${week ? `<text x="706" y="${y + 17}" font-size="9.6" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : ""}\n        `;\n      }).join("");\n      svg.innerHTML = `<rect x="0" y="0" width="900" height="${chartHeight}" fill="transparent"/>${rows}`;',
        1,
    )
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Bổ sung dòng tiến độ tuần qua cho biểu đồ tỷ lệ % dự án.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã bổ sung tiến độ tuần qua cho biểu đồ dự án.")
    else:
        print("Biểu đồ dự án đã có tiến độ tuần qua.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
