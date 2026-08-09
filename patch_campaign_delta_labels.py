#!/usr/bin/env python3
import re
from pathlib import Path


path = Path("index.html")
if not path.exists():
    path = Path("outputs/dashboard-to-cong-tac-so-3-gpmb.html")

html = path.read_text(encoding="utf-8")

helper_code = """
    const campaignProjectDelta = {
      1: { text: "tăng 3,2% (0,4 km)", color: colors.weekUp },
      2: { text: "tăng 8% (0,6 km)", color: colors.weekUp },
      3: { text: "chưa phát sinh tăng (0 km)", color: colors.weekFlat },
      4: { text: "tăng 15% (1,45 ha)", color: colors.weekUp },
      5: { text: "tăng 21,6% (5,14 ha)", color: colors.weekUp },
      6: { text: "tăng 14% (69,3055 ha)", color: colors.weekUp },
      7: { text: "tăng 1,26% (0,52 ha)", color: colors.weekUp },
      8: { text: "tăng 11,4% (0,7939 ha)", color: colors.weekUp }
    };

    const campaignLocalityDelta = {
      "xã Ô Loan": { text: "không thay đổi (0 km)", color: colors.weekFlat },
      "xã Tuy An Nam": { text: "tăng 2,2% (0,1 km)", color: colors.weekUp },
      "phường Bình Kiến": { text: "tăng 11,97% (0,2741 km; 0,7939 ha)", color: colors.weekUp },
      "phường Phú Yên": { text: "tăng 18,3% (6,59 ha)", color: colors.weekUp },
      "xã Tuy An Đông": { text: "tăng 4% (0,6 km)", color: colors.weekUp },
      "xã Hòa Xuân": { text: "tăng 7,63% (69,8255 ha)", color: colors.weekUp }
    };

    function projectCampaignMeta(project) {
      const delta = campaignProjectDelta[project.order];
      if (!delta) return null;
      return { label: `So với trước chiến dịch ${delta.text}`, color: delta.color };
    }

    function localityCampaignMeta(locality) {
      const delta = campaignLocalityDelta[locality];
      if (!delta) return null;
      return { label: `So với trước chiến dịch ${delta.text}`, color: delta.color };
    }
"""

html = html.replace("So với 07/7", "So với trước chiến dịch")

if "const campaignProjectDelta" not in html:
    html = html.replace("    function weeklyProgressMeta", helper_code + "\n    function weeklyProgressMeta", 1)

html = html.replace(
    "        return { locality, rows, progress: Math.max(0, Math.min(100, avg)) };",
    "        return { locality, rows, rowsForAverage, progress: Math.max(0, Math.min(100, avg)) };",
)
html = html.replace(
    "        const campaign = localityCampaignMeta(item.progress, item.rowsForAverage);",
    "        const campaign = localityCampaignMeta(item.locality);",
)
html = html.replace(
    "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);",
    "        const campaign = localityCampaignMeta(item.locality);",
)

html = re.sub(
    r"(        const detailLines = wrapSvgText\(`\(\$\{detail\}\)`, isMobile \? \d+ : \d+\)\.slice\(0, isMobile \? \d+ : \d+\);\n)"
    r"(?!        const campaign = localityCampaignMeta)",
    r"\1        const campaign = localityCampaignMeta(item.locality);\n"
    r"        const campaignLines = campaign ? wrapSvgText(campaign.label, isMobile ? 56 : 118).slice(0, 2) : [];\n",
    html,
    count=1,
)

html = html.replace(
    "        return { item, titleLines, detailLines, week, rowHeight };",
    "        return { item, titleLines, detailLines, campaign, campaignLines, week, rowHeight };",
)
html = html.replace(
    "      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, week, y, rowHeight }) => {",
    "      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, campaign, campaignLines, week, y, rowHeight }) => {",
)
html = html.replace(
    "          ? 134 + detailLines.length * 19 + Math.max(0, titleLines.length - 1) * 17",
    "          ? 134 + detailLines.length * 19 + campaignLines.length * 16 + Math.max(0, titleLines.length - 1) * 17",
)
html = html.replace(
    "          : 66 + detailLines.length * 14 + Math.max(0, titleLines.length - 1) * 13;",
    "          : 66 + detailLines.length * 14 + campaignLines.length * 13 + Math.max(0, titleLines.length - 1) * 13;",
)

html = html.replace(
    '          const weekY = barY + 38 + Math.max(1, detailLines.length) * 18;\n'
    '          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.9" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";',
    '          const campaignY = barY + 38 + Math.max(1, detailLines.length) * 18;\n'
    '          const campaignText = campaignLines.map((line, lineIndex) => `<text x="18" y="${campaignY + lineIndex * 16}" font-size="10.2" fill="${campaign.color}" font-weight="800">${escapeHtml(line)}</text>`).join("");\n'
    '          const weekY = campaignY + campaignLines.length * 16;\n'
    '          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.9" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";',
)
html = html.replace(
    "${percent}</tspan>${detailText}</text>${weekText}<line",
    "${percent}</tspan>${detailText}</text>${campaignText}${weekText}<line",
)
html = html.replace(
    '        const weekY = y + 22 + Math.max(1, detailLines.length) * 13;\n'
    '        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="11" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";',
    '        const campaignY = y + 22 + Math.max(1, detailLines.length) * 13;\n'
    '        const campaignText = campaignLines.map((line, lineIndex) => `<text x="${left}" y="${campaignY + lineIndex * 13}" font-size="9.6" fill="${campaign.color}" font-weight="800">${escapeHtml(line)}</text>`).join("");\n'
    '        const weekY = campaignY + campaignLines.length * 13;\n'
    '        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="11" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";',
)
html = html.replace(
    "${percent}</tspan>${detailText}</text>${weekText}`;",
    "${percent}</tspan>${detailText}</text>${campaignText}${weekText}`;",
)

html = html.replace(
    "const deadline = chartDeadline(project);\n          const percentText",
    "const percentText",
)
html = html.replace(
    "const week = projectWeeklyMeta(project);\n          const zeroReason",
    "const campaign = projectCampaignMeta(project);\n          const zeroReason",
)
html = re.sub(
    r"          const deadlineLines = deadline \? wrapSvgText\(`- mốc HT: \$\{deadline\}`, 48\)\.slice\(0, 2\) : \[\];\n"
    r"          const deadlineText = deadlineLines\.map\([^\n]+\n"
    r"          const zeroReasonY = metricY \+ 18 \+ deadlineLines\.length \* 15;",
    '          const campaignLines = campaign ? wrapSvgText(campaign.label, 48).slice(0, 2) : [];\n'
    '          const campaignText = campaignLines.map((line, index) => `<text x="18" y="${metricY + 18 + index * 15}" font-size="10.3" fill="${campaign.color}" font-weight="850">${escapeHtml(line)}</text>`).join("");\n'
    '          const zeroReasonY = metricY + 18 + campaignLines.length * 15;',
    html,
)
html = re.sub(
    r"          const weekY = zeroReasonY \+ zeroReasonLines\.length \* 15;\n"
    r"          const weekText = week \? `[^\n]+\n",
    "",
    html,
)
html = html.replace("deadlineLines.length * 15", "campaignLines.length * 15")
html = html.replace("${deadlineText}\n            ${zeroReasonText}\n            ${weekText}", "${campaignText}\n            ${zeroReasonText}")

html = html.replace(
    "const deadline = chartDeadline(project);\n        const percentText",
    "const percentText",
)
html = html.replace(
    "const week = projectWeeklyMeta(project);\n        const zeroReason",
    "const campaign = projectCampaignMeta(project);\n        const zeroReason",
)
html = re.sub(
    r"        const deadlineLines = deadline \? wrapSvgText\(`- mốc HT: \$\{deadline\}`, 40\)\.slice\(0, 2\) : \[\];\n"
    r"        const deadlineText = deadlineLines\.map\([^\n]+\n"
    r"        const zeroReasonY = y \+ 18 \+ deadlineLines\.length \* 14;",
    '        const campaignLines = campaign ? wrapSvgText(campaign.label, 40).slice(0, 2) : [];\n'
    '        const campaignText = campaignLines.map((line, index) => `<text x="${infoX}" y="${y + 18 + index * 14}" font-size="10.2" fill="${campaign.color}" font-weight="850">${escapeHtml(line)}</text>`).join("");\n'
    '        const zeroReasonY = y + 18 + campaignLines.length * 14;',
    html,
)
html = re.sub(
    r"        const weekLines = week \? wrapSvgText\(week\.label, 42\)\.slice\(0, 2\) : \[\];\n"
    r"        const weekStartY = zeroReasonY \+ zeroReasonLines\.length \* 14;\n"
    r"        const weekText = weekLines\.map\([^\n]+\n",
    "",
    html,
)
html = html.replace("deadlineLines.length * 14", "campaignLines.length * 14")
html = html.replace("${deadlineText}\n          ${zeroReasonText}\n          ${weekText}", "${campaignText}\n          ${zeroReasonText}")

path.write_text(html, encoding="utf-8")
