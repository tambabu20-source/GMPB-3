#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

WEEKLY_BLOCK = '''    const weeklyBaselineDate = "17/7/2026";
    const weeklyProjectProgress = {
      1: 90.28,
      2: 89.44,
      3: 0,
      4: 75.06,
      5: 67.66,
      6: 8.62,
      7: 99.06,
      8: 86.6,
      9: null
    };
    const weeklyLocalityProgress = {
      "xã Tuy An Đông": 63.15,
      "xã Tuy An Nam": 85.43,
      "xã Ô Loan": 97.58,
      "phường Bình Kiến": 81.61,
      "phường Phú Yên": 71.36,
      "xã Hòa Xuân": 53.84
    };
'''

HELPER_BLOCK = '''

    function formatPct(value, digits = 2) {
      return Number(value).toLocaleString("vi-VN", { maximumFractionDigits: digits });
    }

    function weeklyProgressMeta(current, baseline) {
      if (!Number.isFinite(current) || !Number.isFinite(baseline)) return null;
      const diff = current - baseline;
      if (Math.abs(diff) < 0.05) {
        return { label: `Tuần qua không thay đổi so với ${weeklyBaselineDate}`, color: colors.weekFlat, diff: 0 };
      }
      if (diff > 0) {
        return { label: `Tuần qua tăng ${formatPct(diff)}% so với ${weeklyBaselineDate}`, color: colors.weekUp, diff };
      }
      return { label: `Tuần qua giảm ${formatPct(Math.abs(diff))}% - cần rà soát`, color: colors.weekDown, diff };
    }

    function projectWeeklyMeta(project) {
      return weeklyProgressMeta(project.progress, weeklyProjectProgress[project.order]);
    }
'''


def replace_once(html: str, old: str, new: str) -> str:
    if old not in html:
        return html
    return html.replace(old, new, 1)


def patch_html(html: str) -> str:
    if "weeklyBaselineDate" not in html:
        html = re.sub(
            r'(    const dataUpdatedDate = "[^"]+";\n)',
            r'\1' + WEEKLY_BLOCK,
            html,
            count=1,
        )

    if "weekUp" not in html:
        html = html.replace(
            '      muted: "#5c697a",\n      watchOut: "#c2410c"',
            '      muted: "#5c697a",\n      watchOut: "#c2410c",\n      weekUp: "#15803d",\n      weekFlat: "#5c697a",\n      weekDown: "#b45309"',
            1,
        )

    if "function weeklyProgressMeta" not in html:
        html = html.replace('      .replace(/\'/g, "&#39;");', '      .replace(/\'/g, "&#39;");' + HELPER_BLOCK, 1)

    html = html.replace(
        '    .chart.progress-percent-chart {\n      height: 430px;\n    }',
        '    .chart.progress-percent-chart {\n      height: 520px;\n    }',
    )
    html = html.replace(
        '      .chart.progress-percent-chart {\n        height: 980px;\n      }',
        '      .chart.progress-percent-chart {\n        height: 1120px;\n      }',
    )

    if "weeklyLocalityProgress[item.locality]" not in html:
        html = html.replace(
            '        const detailLines = wrapSvgText(`(${detail})`, isMobile ? 50 : 96).slice(0, isMobile ? 6 : 5);\n        const rowHeight = isMobile\n          ? 82 + detailLines.length * 17 + Math.max(0, titleLines.length - 1) * 14\n          : 54 + detailLines.length * 15 + Math.max(0, titleLines.length - 1) * 14;\n        return { item, titleLines, detailLines, rowHeight };',
            '        const detailLines = wrapSvgText(`(${detail})`, isMobile ? 50 : 96).slice(0, isMobile ? 6 : 5);\n        const week = weeklyProgressMeta(item.progress, weeklyLocalityProgress[item.locality]);\n        const rowHeight = isMobile\n          ? 99 + detailLines.length * 17 + Math.max(0, titleLines.length - 1) * 14\n          : 72 + detailLines.length * 15 + Math.max(0, titleLines.length - 1) * 14;\n        return { item, titleLines, detailLines, week, rowHeight };',
            1,
        )
        html = html.replace(
            '      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, y, rowHeight }) => {',
            '      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, week, y, rowHeight }) => {',
            1,
        )
        html = html.replace(
            '          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="7" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="17" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");\n          const dividerY = y + rowHeight - 12;\n          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="16" rx="7" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="16" rx="7" fill="${color}"/><text x="18" y="${barY + 32}" font-weight="800"><tspan font-size="13.8" fill="${color}">${percent}</tspan>${detailText}</text><line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;',
            '          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="7" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="17" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");\n          const weekY = barY + 32 + Math.max(1, detailLines.length) * 17;\n          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.5" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n          const dividerY = y + rowHeight - 12;\n          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="16" rx="7" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="16" rx="7" fill="${color}"/><text x="18" y="${barY + 32}" font-weight="800"><tspan font-size="13.8" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}<line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;',
            1,
        )
        html = html.replace(
            '        return `<text x="22" y="${y}" font-size="12.4" fill="${colors.text}" font-weight="850">${title}</text><rect x="${left}" y="${y - 13}" width="${barW}" height="18" rx="7" fill="#e7edf2"/><rect x="${left}" y="${y - 13}" width="${fillW}" height="18" rx="7" fill="${color}"/><text x="${left}" y="${y + 24}" font-weight="800"><tspan font-size="12.8" fill="${color}">${percent}</tspan>${detailText}</text>`;',
            '        const weekY = y + 24 + Math.max(1, detailLines.length) * 15;\n        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="10.4" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n        return `<text x="22" y="${y}" font-size="12.4" fill="${colors.text}" font-weight="850">${title}</text><rect x="${left}" y="${y - 13}" width="${barW}" height="18" rx="7" fill="#e7edf2"/><rect x="${left}" y="${y - 13}" width="${fillW}" height="18" rx="7" fill="${color}"/><text x="${left}" y="${y + 24}" font-weight="800"><tspan font-size="12.8" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}`;',
            1,
        )

    if "projectWeeklyMeta(project)" not in html:
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
        html = html.replace(
            '      const rowHeight = 48;',
            '      const rowHeight = 64;',
            1,
        )
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
    parser = argparse.ArgumentParser(description="Thêm dòng tiến độ tuần qua vào biểu đồ dự án và địa phương.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã thêm hiển thị tiến độ tuần qua.")
    else:
        print("Hiển thị tiến độ tuần qua đã sẵn sàng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
