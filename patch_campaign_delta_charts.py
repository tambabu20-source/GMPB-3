#!/usr/bin/env python3
from pathlib import Path


path = Path("index.html")
if not path.exists():
    path = Path("outputs/dashboard-to-cong-tac-so-3-gpmb.html")

html = path.read_text(encoding="utf-8")

helpers_after = """    function localityAreaDeltaText(currentByUnit, baselineByUnit) {
      if (!baselineByUnit) return "";
      const units = [...new Set([...Object.keys(currentByUnit || {}), ...Object.keys(baselineByUnit || {})])].sort();
      const parts = units.map(unit => {
        const diff = (currentByUnit?.[unit] || 0) - (baselineByUnit?.[unit] || 0);
        if (Math.abs(diff) < 0.0005) return `0 ${unit}`;
        return `${diff > 0 ? "+" : "-"}${formatAreaValue(Math.abs(diff))} ${unit}`;
      });
      return parts.length ? `(${parts.join("; ")})` : "";
    }
"""

campaign_helpers = helpers_after + """
    function campaignAreaTextFromCurrent(currentArea) {
      const current = parseClearedAmount(currentArea);
      if (!current) return "";
      return `(${formatAreaValue(Math.max(0, current.amount))} ${current.unit})`;
    }

    function campaignAreaTextByUnit(currentByUnit) {
      const parts = Object.entries(currentByUnit || {})
        .filter(([, amount]) => Number.isFinite(amount))
        .sort(([unitA], [unitB]) => unitA.localeCompare(unitB))
        .map(([unit, amount]) => `${formatAreaValue(Math.max(0, amount))} ${unit}`);
      return parts.length ? `(${parts.join("; ")})` : "";
    }

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

    function campaignProgressMeta(current, areaText = "") {
      if (!Number.isFinite(current)) return null;
      const safeCurrent = Math.max(0, current);
      const suffix = areaText ? ` ${areaText}` : "";
      const color = safeCurrent > 0.05 ? colors.weekUp : colors.weekFlat;
      return {
        label: `So với trước chiến dịch tăng ${formatPct(safeCurrent)}%${suffix}`,
        color
      };
    }

    function projectCampaignMeta(project) {
      const delta = campaignProjectDelta[project.order];
      if (delta) return { label: `So với trước chiến dịch ${delta.text}`, color: delta.color };
      return campaignProgressMeta(project.progress, campaignAreaTextFromCurrent(project.clearedArea));
    }

    function localityCampaignMeta(locality, current, rows) {
      const delta = campaignLocalityDelta[locality];
      if (delta) return { label: `So với trước chiến dịch ${delta.text}`, color: delta.color };
      return campaignProgressMeta(current, campaignAreaTextByUnit(aggregateClearedByUnit(rows)));
    }
"""

if "function campaignProgressMeta" not in html and helpers_after in html:
    html = html.replace(helpers_after, campaign_helpers)

html = html.replace(
    "        return { locality, rows, progress: Math.max(0, Math.min(100, avg)) };",
    "        return { locality, rows, rowsForAverage, progress: Math.max(0, Math.min(100, avg)) };",
)
html = html.replace(
    "        const detailLines = wrapSvgText(`(${detail})`, isMobile ? 56 : 118).slice(0, isMobile ? 5 : 5);\n"
    "        const week = weeklyProgressMeta(",
    "        const detailLines = wrapSvgText(`(${detail})`, isMobile ? 56 : 118).slice(0, isMobile ? 5 : 5);\n"
    "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n"
    "        const campaignLines = campaign ? wrapSvgText(campaign.label, isMobile ? 56 : 118).slice(0, 2) : [];\n"
    "        const week = weeklyProgressMeta(",
)
html = html.replace(
    "        const campaign = localityCampaignMeta(item.progress, item.rowsForAverage);",
    "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);",
)
html = html.replace(
    "          ? 134 + detailLines.length * 19 + Math.max(0, titleLines.length - 1) * 17\n"
    "          : 66 + detailLines.length * 14 + Math.max(0, titleLines.length - 1) * 13;\n"
    "        return { item, titleLines, detailLines, week, rowHeight };",
    "          ? 134 + detailLines.length * 19 + campaignLines.length * 16 + Math.max(0, titleLines.length - 1) * 17\n"
    "          : 66 + detailLines.length * 14 + campaignLines.length * 13 + Math.max(0, titleLines.length - 1) * 13;\n"
    "        return { item, titleLines, detailLines, campaign, campaignLines, week, rowHeight };",
)
html = html.replace(
    "      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, week, y, rowHeight }) => {",
    "      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, campaign, campaignLines, week, y, rowHeight }) => {",
)
html = html.replace(
    '          const weekY = barY + 38 + Math.max(1, detailLines.length) * 18;\n'
    '          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.9" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n'
    '          const dividerY = y + rowHeight - 22;\n'
    '          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="18" rx="8" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="18" rx="8" fill="${color}"/><text x="18" y="${barY + 36}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}<line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;',
    '          const campaignY = barY + 38 + Math.max(1, detailLines.length) * 18;\n'
    '          const campaignText = campaignLines.map((line, lineIndex) => `<text x="18" y="${campaignY + lineIndex * 16}" font-size="10.2" fill="${campaign.color}" font-weight="800">${escapeHtml(line)}</text>`).join("");\n'
    '          const weekY = campaignY + campaignLines.length * 16;\n'
    '          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.9" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n'
    '          const dividerY = y + rowHeight - 22;\n'
    '          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="18" rx="8" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="18" rx="8" fill="${color}"/><text x="18" y="${barY + 36}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${campaignText}${weekText}<line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;',
)
html = html.replace(
    '        const weekY = y + 22 + Math.max(1, detailLines.length) * 13;\n'
    '        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="11" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n'
    '        return `<text x="22" y="${y}" font-size="13.5" fill="${colors.text}" font-weight="850">${title}</text><rect x="${left}" y="${y - 14}" width="${barW}" height="20" rx="8" fill="#e7edf2"/><rect x="${left}" y="${y - 14}" width="${fillW}" height="20" rx="8" fill="${color}"/><text x="${left}" y="${y + 24}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}`;',
    '        const campaignY = y + 22 + Math.max(1, detailLines.length) * 13;\n'
    '        const campaignText = campaignLines.map((line, lineIndex) => `<text x="${left}" y="${campaignY + lineIndex * 13}" font-size="9.6" fill="${campaign.color}" font-weight="800">${escapeHtml(line)}</text>`).join("");\n'
    '        const weekY = campaignY + campaignLines.length * 13;\n'
    '        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="11" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n'
    '        return `<text x="22" y="${y}" font-size="14.5" fill="${colors.text}" font-weight="850">${title}</text><rect x="${left}" y="${y - 14}" width="${barW}" height="20" rx="8" fill="#e7edf2"/><rect x="${left}" y="${y - 14}" width="${fillW}" height="20" rx="8" fill="${color}"/><text x="${left}" y="${y + 24}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${campaignText}${weekText}`;',
)

mobile_old = """          const ratio = compactAreaRatio(project);
          const deadline = chartDeadline(project);
          const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";
          const week = projectWeeklyMeta(project);
          const zeroReason = chartZeroReason(project);
          const deadlineLines = deadline ? wrapSvgText(`- mốc HT: ${deadline}`, 48).slice(0, 2) : [];
          const deadlineText = deadlineLines.map((line, index) => `<text x="18" y="${metricY + 18 + index * 15}" font-size="10.3" fill="#1d4ed8" font-weight="850">${escapeHtml(line)}</text>`).join("");
          const zeroReasonY = metricY + 18 + deadlineLines.length * 15;
          const zeroReasonLines = zeroReason ? wrapSvgText(zeroReason, 52).slice(0, 2) : [];
          const zeroReasonText = zeroReasonLines.map((line, index) => `<text x="18" y="${zeroReasonY + index * 15}" font-size="10.6" fill="#c2410c" font-weight="850">${escapeHtml(line)}</text>`).join("");
          const weekY = zeroReasonY + zeroReasonLines.length * 15;
          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.8" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";
          const title = nameLines.map((line, index) => `<tspan x="18" dy="${index ? 16 : 0}">${escapeHtml(line)}</tspan>`).join("");
          cursor = metricY + 22 + deadlineLines.length * 15 + zeroReasonLines.length * 15 + (week ? 22 : 0);"""

mobile_new = """          const ratio = compactAreaRatio(project);
          const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";
          const campaign = projectCampaignMeta(project);
          const zeroReason = chartZeroReason(project);
          const campaignLines = campaign ? wrapSvgText(campaign.label, 48).slice(0, 2) : [];
          const campaignText = campaignLines.map((line, index) => `<text x="18" y="${metricY + 18 + index * 15}" font-size="10.3" fill="${campaign.color}" font-weight="850">${escapeHtml(line)}</text>`).join("");
          const zeroReasonY = metricY + 18 + campaignLines.length * 15;
          const zeroReasonLines = zeroReason ? wrapSvgText(zeroReason, 52).slice(0, 2) : [];
          const zeroReasonText = zeroReasonLines.map((line, index) => `<text x="18" y="${zeroReasonY + index * 15}" font-size="10.6" fill="#c2410c" font-weight="850">${escapeHtml(line)}</text>`).join("");
          const title = nameLines.map((line, index) => `<tspan x="18" dy="${index ? 16 : 0}">${escapeHtml(line)}</tspan>`).join("");
          cursor = metricY + 22 + campaignLines.length * 15 + zeroReasonLines.length * 15;"""
html = html.replace(mobile_old, mobile_new).replace("${deadlineText}\n            ${zeroReasonText}\n            ${weekText}", "${campaignText}\n            ${zeroReasonText}")

desktop_old = """        const ratio = compactAreaRatio(project);
        const deadline = chartDeadline(project);
        const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";
        const week = projectWeeklyMeta(project);
        const zeroReason = chartZeroReason(project);
        const deadlineLines = deadline ? wrapSvgText(`- mốc HT: ${deadline}`, 40).slice(0, 2) : [];
        const deadlineText = deadlineLines.map((line, index) => `<text x="${infoX}" y="${y + 18 + index * 14}" font-size="10.2" fill="#1d4ed8" font-weight="850">${escapeHtml(line)}</text>`).join("");
        const zeroReasonY = y + 18 + deadlineLines.length * 14;
        const zeroReasonLines = zeroReason ? wrapSvgText(zeroReason, 37).slice(0, 2) : [];
        const zeroReasonText = zeroReasonLines.map((line, index) => `<text x="${infoX}" y="${zeroReasonY + index * 14}" font-size="10.3" fill="#c2410c" font-weight="850">${escapeHtml(line)}</text>`).join("");
        const weekLines = week ? wrapSvgText(week.label, 42).slice(0, 2) : [];
        const weekStartY = zeroReasonY + zeroReasonLines.length * 14;
        const weekText = weekLines.map((line, index) => `<text x="${infoX}" y="${weekStartY + index * 14}" font-size="10.2" fill="${week.color}" font-weight="800">${escapeHtml(line)}</text>`).join("");"""

desktop_new = """        const ratio = compactAreaRatio(project);
        const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";
        const campaign = projectCampaignMeta(project);
        const zeroReason = chartZeroReason(project);
        const campaignLines = campaign ? wrapSvgText(campaign.label, 40).slice(0, 2) : [];
        const campaignText = campaignLines.map((line, index) => `<text x="${infoX}" y="${y + 18 + index * 14}" font-size="10.2" fill="${campaign.color}" font-weight="850">${escapeHtml(line)}</text>`).join("");
        const zeroReasonY = y + 18 + campaignLines.length * 14;
        const zeroReasonLines = zeroReason ? wrapSvgText(zeroReason, 37).slice(0, 2) : [];
        const zeroReasonText = zeroReasonLines.map((line, index) => `<text x="${infoX}" y="${zeroReasonY + index * 14}" font-size="10.3" fill="#c2410c" font-weight="850">${escapeHtml(line)}</text>`).join("");"""
html = html.replace(desktop_old, desktop_new).replace("${deadlineText}\n          ${zeroReasonText}\n          ${weekText}", "${campaignText}\n          ${zeroReasonText}")

path.write_text(html, encoding="utf-8")
