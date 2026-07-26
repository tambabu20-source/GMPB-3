#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

PROJECT_CLEARED = '''    const weeklyProjectCleared = {
      1: "13,24/14,67 km",
      2: "6,69/7,48 km",
      3: "0/3,4 km",
      4: "10,95/14,59 ha",
      5: "16,1/23,79 ha",
      6: "22,61/262,25 ha",
      7: "40,93/41,32 ha",
      8: "5,78532/6,68162 ha",
      9: ""
    };
'''

LOCALITY_CLEARED = '''    const weeklyLocalityCleared = {
      "xã Tuy An Đông": { km: 6.89 },
      "xã Tuy An Nam": { km: 3.93 },
      "xã Ô Loan": { km: 7.34 },
      "phường Bình Kiến": { km: 1.774, ha: 5.78532 },
      "phường Phú Yên": { ha: 27.05 },
      "xã Hòa Xuân": { ha: 63.54 }
    };
'''

HELPERS = '''    function formatPct(value, digits = 2) {
      return Number(value).toLocaleString("vi-VN", { maximumFractionDigits: digits });
    }

    function formatAreaValue(value) {
      return Number(value).toLocaleString("vi-VN", { maximumFractionDigits: 4 });
    }

    function parseClearedAmount(value) {
      const match = String(value || "").match(/([\d.,]+)\s*(?:\/\s*[\d.,]+)?\s*(km|ha|m)\b/i);
      if (!match) return null;
      const amount = Number(match[1].replace(/\./g, "").replace(",", "."));
      const unit = match[2].toLowerCase();
      if (!Number.isFinite(amount)) return null;
      return { amount, unit };
    }

    function areaDeltaText(currentArea, baselineArea) {
      const current = parseClearedAmount(currentArea);
      const baseline = parseClearedAmount(baselineArea);
      if (!current || !baseline || current.unit !== baseline.unit) return "";
      const diff = current.amount - baseline.amount;
      if (Math.abs(diff) < 0.0005) return `(0 ${current.unit})`;
      if (diff < 0) return "";
      return `(+${formatAreaValue(diff)} ${current.unit})`;
    }

    function aggregateClearedByUnit(rows) {
      return rows.reduce((acc, row) => {
        const parsed = parseClearedAmount(row.cleared);
        if (!parsed) return acc;
        acc[parsed.unit] = (acc[parsed.unit] || 0) + parsed.amount;
        return acc;
      }, {});
    }

    function localityAreaDeltaText(currentByUnit, baselineByUnit) {
      if (!baselineByUnit) return "";
      const units = [...new Set([...Object.keys(currentByUnit || {}), ...Object.keys(baselineByUnit || {})])].sort();
      const parts = units.map(unit => {
        const diff = (currentByUnit?.[unit] || 0) - (baselineByUnit?.[unit] || 0);
        if (Math.abs(diff) < 0.0005) return `0 ${unit}`;
        if (diff < 0) return null;
        return `+${formatAreaValue(diff)} ${unit}`;
      }).filter(Boolean);
      return parts.length ? `(${parts.join("; ")})` : "";
    }

    function weeklyProgressMeta(current, baseline, areaText = "") {
      if (!Number.isFinite(current) || !Number.isFinite(baseline)) return null;
      const diff = current - baseline;
      const suffix = areaText ? ` ${areaText}` : "";
      if (diff < -0.05) {
        return { label: "Tuần qua không thay đổi - cần rà soát số liệu", color: colors.weekDown, diff };
      }
      if (Math.abs(diff) < 0.05) {
        return { label: `Tuần qua không thay đổi${suffix} so với ${weeklyBaselineDate}`, color: colors.weekFlat, diff: 0 };
      }
      return { label: `Tuần qua tăng ${formatPct(diff)}% ${areaText} so với ${weeklyBaselineDate}`, color: colors.weekUp, diff };
    }

    function projectWeeklyMeta(project) {
      return weeklyProgressMeta(project.progress, weeklyProjectProgress[project.order], areaDeltaText(project.clearedArea, weeklyProjectCleared[project.order]));
    }
'''


def add_after_object(html: str, object_name: str, marker: str, block: str) -> str:
    if marker in html:
        return html
    pattern = rf'(    const {object_name} = \{{[\s\S]*?\n    \}};\n)'
    return re.sub(pattern, lambda m: m.group(1) + block, html, count=1)


def patch_html(html: str) -> str:
    html = add_after_object(html, "weeklyProjectProgress", "weeklyProjectCleared", PROJECT_CLEARED)
    html = add_after_object(html, "weeklyLocalityProgress", "weeklyLocalityCleared", LOCALITY_CLEARED)

    html = re.sub(
        r'    function formatPct\(value, digits = 2\) \{[\s\S]*?\n    function projectWeeklyMeta\(project\) \{[\s\S]*?\n    \}\n',
        HELPERS,
        html,
        count=1,
    )

    html = html.replace(
        '        const week = weeklyProgressMeta(item.progress, weeklyLocalityProgress[item.locality]);',
        '        const week = weeklyProgressMeta(\n          item.progress,\n          weeklyLocalityProgress[item.locality],\n          localityAreaDeltaText(aggregateClearedByUnit(item.rows), weeklyLocalityCleared[item.locality])\n        );',
    )

    html = re.sub(
        r'Tuần qua giảm \$\{formatPct\(Math\.abs\(diff\)\)\}%[^`]*- cần rà soát',
        'Tuần qua không thay đổi - cần rà soát số liệu',
        html,
    )
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Bổ sung khối lượng tăng/giảm tuần qua vào nhãn biểu đồ.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã bổ sung khối lượng tăng/giảm tuần qua.")
    else:
        print("Khối lượng tăng/giảm tuần qua đã sẵn sàng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
