#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def patch_final_chart_guard(html: str) -> str:
    html = html.replace("So với trước chiến dịch", "So trước chiến dịch")
    html = html.replace("So trước CĐ", "So trước chiến dịch")
    html = html.replace(
        '"clearedArea": "13,26/14,59 ha",',
        '"clearedArea": "13,14/14,59 ha",',
    )
    html = html.replace(
        '"clearedArea": "13,14/14,59 ha",',
        '"clearedArea": "13,14/14,59 ha",',
    )
    html = html.replace(
        '"remainingArea": "1,33 ha",\n            "remainingRate": "9,12%",',
        '"remainingArea": "1,45 ha",\n            "remainingRate": "9,94%",',
        1,
    )
    html = html.replace(
        '"remainingArea": "1,45 ha",\n            "remainingRate": "9,94%",',
        '"remainingArea": "1,45 ha",\n            "remainingRate": "9,94%",',
        1,
    )
    html = html.replace(
        '"progress": 90.88',
        '"progress": 90.06',
        1,
    )
    html = html.replace(
        '"clearedArea": "22,69/23,79 ha",',
        '"clearedArea": "22,34/23,79 ha",',
    )
    html = html.replace(
        '"clearedArea": "22,34/23,79 ha",',
        '"clearedArea": "22,34/23,79 ha",',
    )
    html = html.replace(
        '"remainingArea": "1,10 ha",\n            "remainingRate": "4,62%",',
        '"remainingArea": "1,45 ha",\n            "remainingRate": "6,09%",',
        1,
    )
    html = html.replace(
        '"remainingArea": "1,45 ha",\n            "remainingRate": "6,09%",',
        '"remainingArea": "1,45 ha",\n            "remainingRate": "6,09%",',
        1,
    )
    html = html.replace(
        '"progress": 95.38',
        '"progress": 93.91',
        1,
    )
    html = html.replace("Hạ tầng kỹ thuật khu dân cư phía Nam đạt 95,38%", "Hạ tầng kỹ thuật khu dân cư phía Nam đạt 93,91%")
    html = html.replace("Khu công viên trung tâm đạt 90,88%", "Khu công viên trung tâm đạt 90,06%")
    html = html.replace("Hạ tầng kỹ thuật khu dân cư phía Nam đạt 95,38%", "Hạ tầng kỹ thuật khu dân cư phía Nam đạt 93,91%")
    html = html.replace("Khu công viên trung tâm đạt 90,88%", "Khu công viên trung tâm đạt 90,06%")
    html = html.replace(
        '<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>89,67%</b></div>',
        '<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>89,35%</b></div>',
    )
    html = html.replace(
        '<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>89,58%</b></div>',
        '<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>89,35%</b></div>',
    )
    if "function weightedLocalityProgress(rows)" not in html:
        html = html.replace(
            """    function calculateLocalityProgress(clearedText) {
      const match = String(clearedText || "").match(/([\\d.,]+)\\s*\\/\\s*([\\d.,]+)\\s*([a-zA-Z]*)/);
      if (!match) return null;
      const unit = match[3] || "";
      const cleared = readLocalityNumber(match[1], unit);
      const total = readLocalityNumber(match[2], unit);
      if (!Number.isFinite(cleared) || !Number.isFinite(total) || total <= 0) return null;
      return Math.max(0, Math.min(100, cleared / total * 100));
    }
""",
            """    function calculateLocalityProgress(clearedText) {
      const match = String(clearedText || "").match(/([\\d.,]+)\\s*\\/\\s*([\\d.,]+)\\s*([a-zA-Z]*)/);
      if (!match) return null;
      const unit = match[3] || "";
      const cleared = readLocalityNumber(match[1], unit);
      const total = readLocalityNumber(match[2], unit);
      if (!Number.isFinite(cleared) || !Number.isFinite(total) || total <= 0) return null;
      return Math.max(0, Math.min(100, cleared / total * 100));
    }

    function parseLocalityAreaParts(clearedText) {
      const match = String(clearedText || "").match(/([\\d.,]+)\\s*\\/\\s*([\\d.,]+)\\s*([a-zA-Z]*)/);
      if (!match) return null;
      const unit = (match[3] || "").toLowerCase();
      const cleared = readLocalityNumber(match[1], unit);
      const total = readLocalityNumber(match[2], unit);
      if (!Number.isFinite(cleared) || !Number.isFinite(total) || total <= 0) return null;
      return { cleared, total, unit };
    }

    function weightedLocalityProgress(rows) {
      const usable = rows.filter(row => row.progress > 0);
      const basis = usable.length ? usable : rows;
      const areaRows = basis.map(row => row.areaParts).filter(Boolean);
      const units = new Set(areaRows.map(row => row.unit));
      if (areaRows.length === basis.length && units.size === 1) {
        const cleared = areaRows.reduce((sum, row) => sum + row.cleared, 0);
        const total = areaRows.reduce((sum, row) => sum + row.total, 0);
        if (total > 0) return Math.max(0, Math.min(100, cleared / total * 100));
      }
      return basis.reduce((sum, row) => sum + row.progress, 0) / basis.length;
    }
""",
            1,
        )
    html = html.replace(
        "            progress: Math.max(0, Math.min(100, progress)),\n            cleared: compactLocalityArea(match[2])",
        "            progress: Math.max(0, Math.min(100, progress)),\n            cleared: compactLocalityArea(match[2]),\n            areaParts: parseLocalityAreaParts(match[2])",
    )
    html = html.replace(
        "        const avg = rowsForAverage.reduce((sum, row) => sum + row.progress, 0) / rowsForAverage.length;\n        return { locality, rows, rowsForAverage, progress: Math.max(0, Math.min(100, avg)) };",
        "        const progress = weightedLocalityProgress(rows);\n        return { locality, rows, rowsForAverage, progress: Math.max(0, Math.min(100, progress)) };",
    )
    if "function oneLineText(" not in html:
        label_helpers = """
    function oneLineText(text, maxChars = 80) {
      return clipLabel(String(text || "").replace(/\s+/g, " ").trim(), maxChars);
    }

    function compactCampaignLabel(label) {
      return String(label || "")
        .replace(/^So với trước chiến dịch\s+/i, "So trước chiến dịch ")
        .replace(/^So trước chiến dịch\s+/i, "So trước chiến dịch ")
        .replace(/^So trước CĐ\s+/i, "So trước chiến dịch ")
        .replace(/không thay đổi/i, "không đổi")
        .replace(/\s+/g, " ")
        .trim();
    }

    function compactDetailLabel(text) {
      return String(text || "")
        .replace(/Tuyến đường bộ ven biển,?\s*/gi, "Ven biển ")
        .replace(/Ven biển\s+đoạn\s+/gi, "Ven biển ")
        .replace(/Tuyến đường giao thông từ\s+/gi, "")
        .replace(/Khu công nghiệp Hòa Tâm - Giai đoạn 1/gi, "KCN Hòa Tâm")
        .replace(/Khu công viên trung tâm thuộc KĐT mới Nam/gi, "Công viên trung tâm KĐT mới Nam")
        .replace(/Hạ tầng kỹ thuật khu dân cư phía Nam thuộc KĐT mới Nam/gi, "HTKT KDC phía Nam")
        .replace(/Thành phố Tuy Hòa/gi, "TP Tuy Hòa")
        .replace(/Khu kinh tế Vân Phong/gi, "KKT Vân Phong")
        .replace(/\s+/g, " ")
        .trim();
    }
"""
        html = html.replace(
            "    function compactDeadline(deadline) {",
            label_helpers + "\n    function compactDeadline(deadline) {",
            1,
        )
    elif "function compactDetailLabel(" not in html:
        detail_helper = """
    function compactDetailLabel(text) {
      return String(text || "")
        .replace(/Tuyến đường bộ ven biển,?\s*/gi, "Ven biển ")
        .replace(/Ven biển\s+đoạn\s+/gi, "Ven biển ")
        .replace(/Tuyến đường giao thông từ\s+/gi, "")
        .replace(/Khu công nghiệp Hòa Tâm - Giai đoạn 1/gi, "KCN Hòa Tâm")
        .replace(/Khu công viên trung tâm thuộc KĐT mới Nam/gi, "Công viên trung tâm KĐT mới Nam")
        .replace(/Hạ tầng kỹ thuật khu dân cư phía Nam thuộc KĐT mới Nam/gi, "HTKT KDC phía Nam")
        .replace(/Thành phố Tuy Hòa/gi, "TP Tuy Hòa")
        .replace(/Khu kinh tế Vân Phong/gi, "KKT Vân Phong")
        .replace(/\s+/g, " ")
        .trim();
    }
"""
        html = html.replace(
            "    function compactDeadline(deadline) {",
            detail_helper + "\n    function compactDeadline(deadline) {",
            1,
        )
    if "function projectCampaignMeta(project)" not in html:
        helper_anchor = """    function localityAreaDeltaText(currentByUnit, baselineByUnit) {
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
"""
        campaign_helpers = helper_anchor + """
    function campaignAreaTextFromCurrent(currentArea) {
      const current = parseClearedAmount(currentArea);
      if (!current) return "";
      return `(${formatAreaValue(Math.max(0, current.amount))} ${current.unit})`;
    }

    function campaignAreaTextByUnit(currentByUnit) {
      const parts = Object.entries(currentByUnit || {})
        .filter(([, amount]) => Number.isFinite(amount) && amount > 0)
        .sort(([unitA], [unitB]) => unitA.localeCompare(unitB))
        .map(([unit, amount]) => `${formatAreaValue(Math.max(0, amount))} ${unit}`);
      return parts.length ? `(${parts.join("; ")})` : "";
    }

    const campaignProjectDelta = {
      1: { text: "tăng 3,2% (0,4 km)", color: colors.weekUp },
      2: { text: "tăng 8% (0,6 km)", color: colors.weekUp },
      3: { text: "chưa phát sinh tăng (0 km)", color: colors.weekFlat },
      4: { text: "tăng 15,08% (2,20 ha)", color: colors.weekUp },
      5: { text: "tăng 26,40% (6,28 ha)", color: colors.weekUp },
      6: { text: "tăng 14% (69,3055 ha)", color: colors.weekUp },
      7: { text: "tăng 1,26% (0,52 ha)", color: colors.weekUp },
      8: { text: "tăng 11,4% (0,7939 ha)", color: colors.weekUp }
    };

    const campaignLocalityDelta = {
      "xã Ô Loan": { text: "không thay đổi (0 km)", color: colors.weekFlat },
      "xã Tuy An Nam": { text: "tăng 2,2% (0,1 km)", color: colors.weekUp },
      "phường Bình Kiến": { text: "tăng 11,97% (0,2741 km; 0,7939 ha)", color: colors.weekUp },
      "phường Phú Yên": { text: "tăng 22,09% (8,48 ha)", color: colors.weekUp },
      "xã Tuy An Đông": { text: "tăng 4% (0,6 km)", color: colors.weekUp },
      "xã Hòa Xuân": { text: "tăng 7,63% (69,8255 ha)", color: colors.weekUp }
    };

    function campaignProgressMeta(current, areaText = "") {
      if (!Number.isFinite(current)) return null;
      const safeCurrent = Math.max(0, current);
      const suffix = areaText ? ` ${areaText}` : "";
      const color = safeCurrent > 0.05 ? colors.weekUp : colors.weekFlat;
      return {
        label: `So trước chiến dịch tăng ${formatPct(safeCurrent)}%${suffix}`,
        color
      };
    }

    function projectCampaignMeta(project) {
      const delta = campaignProjectDelta[project.order];
      if (delta) return { label: `So trước chiến dịch ${delta.text}`, color: delta.color };
      return campaignProgressMeta(project.progress, campaignAreaTextFromCurrent(project.clearedArea));
    }

    function localityCampaignMeta(locality, current, rows) {
      const delta = campaignLocalityDelta[locality];
      if (delta) return { label: `So trước chiến dịch ${delta.text}`, color: delta.color };
      return campaignProgressMeta(current, campaignAreaTextByUnit(aggregateClearedByUnit(rows)));
    }
"""
        html = html.replace(helper_anchor, campaign_helpers)
    html = html.replace(
        "        const campaign = localityCampaignMeta(item.locality);\n",
        "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n",
    )
    html = html.replace(
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const campaignLines = campaignLine ? [campaignLine] : [];\n"
        "        const week = weeklyProgressMeta(\n",
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const week = weeklyProgressMeta(\n",
    )
    html = html.replace(
        "        const detail = localityDetail(item.rows);\n"
        "        const titleLines = wrapSvgText(item.locality, isMobile ? 44 : 42).slice(0, 2);\n"
        "        const detailLines = wrapSvgText(`(${detail})`, isMobile ? 50 : 96).slice(0, isMobile ? 6 : 5);\n"
        "        const week = weeklyProgressMeta(\n",
        "        const detail = compactDetailLabel(localityDetail(item.rows));\n"
        "        const titleLines = wrapSvgText(item.locality, isMobile ? 44 : 42).slice(0, 2);\n"
        "        const detailLine = oneLineText(`(${detail})`, isMobile ? 58 : 138);\n"
        "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n"
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const week = weeklyProgressMeta(\n",
    )
    html = html.replace(
        "        const detailLine = oneLineText(`(${detail})`, isMobile ? 58 : 138);\n"
        "        const detailLines = detailLine ? [detailLine] : [];\n"
        "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n"
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const campaignLines = campaignLine ? [campaignLine] : [];\n",
        "        const detailLine = oneLineText(`(${detail})`, isMobile ? 58 : 138);\n"
        "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n"
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n',
    )
    html = html.replace(
        "        const rowHeight = isMobile\n"
        "          ? 134 + detailLines.length * 19 + campaignLines.length * 16 + Math.max(0, titleLines.length - 1) * 17\n"
        "          : 66 + detailLines.length * 14 + campaignLines.length * 13 + Math.max(0, titleLines.length - 1) * 13;\n"
        "        return { item, titleLines, detailLines, campaign, campaignLines, week, rowHeight };\n",
        "        const rowHeight = isMobile\n"
        "          ? 126 + Math.max(0, titleLines.length - 1) * 17\n"
        "          : 76 + Math.max(0, titleLines.length - 1) * 13;\n"
        "        return { item, titleLines, detailLine, campaign, campaignLine, week, rowHeight };\n",
    )
    html = html.replace(
        "      svg.innerHTML = positioned.map(({ item, titleLines, detailLines, campaign, campaignLines, week, y, rowHeight }) => {\n",
        "      svg.innerHTML = positioned.map(({ item, titleLines, detailLine, campaign, campaignLine, week, y, rowHeight }) => {\n",
    )
    html = html.replace(
        '          const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="7" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="18" dy="17" font-size="9.8" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");\n'
        "          const weekY = barY + 38 + Math.max(1, detailLines.length) * 18;\n"
        '          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.9" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n'
        "          const dividerY = y + rowHeight - 12;\n"
        '          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="18" rx="8" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="18" rx="8" fill="${color}"/><text x="18" y="${barY + 36}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${weekText}<line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;\n',
        '          const detailText = detailLine ? `<tspan dx="6" font-size="8.9" fill="${colors.muted}" font-weight="700">${escapeHtml(detailLine)}</tspan>` : "";\n'
        "          const campaignY = barY + 58;\n"
        '          const campaignText = campaignLine ? `<text x="18" y="${campaignY}" font-size="9.6" fill="${campaign.color}" font-weight="800">${escapeHtml(campaignLine)}</text>` : "";\n'
        "          const weekY = campaignY + (campaignLine ? 15 : 0);\n"
        '          const weekText = week ? `<text x="18" y="${weekY}" font-size="10.9" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n'
        "          const dividerY = y + rowHeight - 22;\n"
        '          return `<text x="18" y="${y}" font-size="12.8" fill="${colors.text}" font-weight="850">${title}</text><rect x="18" y="${barY}" width="372" height="18" rx="8" fill="#e7edf2"/><rect x="18" y="${barY}" width="${Math.max(4, progress / 100 * 372)}" height="18" rx="8" fill="${color}"/><text x="18" y="${barY + 36}" font-weight="800"><tspan font-size="14.2" fill="${color}">${percent}</tspan>${detailText}</text>${campaignText}${weekText}<line x1="18" x2="402" y1="${dividerY}" y2="${dividerY}" stroke="#e7edf2" stroke-width="1"/>`;\n',
    )
    html = html.replace(
        '        const detailText = detailLines.map((line, lineIndex) => lineIndex === 0 ? `<tspan dx="6" font-size="10.3" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>` : `<tspan x="${left}" dy="15" font-size="9.6" fill="${colors.muted}" font-weight="700">${escapeHtml(line)}</tspan>`).join("");\n'
        "        const campaignY = y + 22 + Math.max(1, detailLines.length) * 13;\n"
        '        const campaignText = campaignLines.map((line, lineIndex) => `<text x="${left}" y="${campaignY + lineIndex * 13}" font-size="9.6" fill="${campaign.color}" font-weight="800">${escapeHtml(line)}</text>`).join("");\n'
        "        const weekY = campaignY + campaignLines.length * 13;\n"
        '        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="11" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n',
        '        const detailText = detailLine ? `<tspan dx="6" font-size="9.6" fill="${colors.muted}" font-weight="700">${escapeHtml(detailLine)}</tspan>` : "";\n'
        "        const campaignY = y + 40;\n"
        '        const campaignText = campaignLine ? `<text x="${left}" y="${campaignY}" font-size="9.9" fill="${campaign.color}" font-weight="800">${escapeHtml(campaignLine)}</text>` : "";\n'
        "        const weekY = campaignY + (campaignLine ? 13 : 0);\n"
        '        const weekText = week ? `<text x="${left}" y="${weekY}" font-size="11" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";\n',
    )
    html = html.replace(
        "Tổng diện tích/chiều dài phải GPMB 7 dự án</span>\n              <b>29,62 km + 578,25 ha</b>",
        "Tổng diện tích/chiều dài phải GPMB 7 dự án</span>\n              <b>578,25 ha + 25,55 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài phải GPMB 7 dự án</span>\n              <b>578,25 ha + 29,62 km</b>",
        "Tổng diện tích/chiều dài phải GPMB 7 dự án</span>\n              <b>578,25 ha + 25,55 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>28,18 km + 381,77 ha</b>",
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>381,77 ha + 20,89 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>381,77 ha + 28,18 km</b>",
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>381,77 ha + 20,89 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>382,24 ha + 28,18 km</b>",
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>381,77 ha + 20,89 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>382,24 ha + 20,89 km</b>",
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>381,77 ha + 20,89 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>1,00 km + 77,21 ha</b>",
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,10 ha + 0,99 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>77,21 ha + 1,00 km</b>",
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,10 ha + 0,99 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>77,68 ha + 1,00 km</b>",
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,10 ha + 0,99 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,57 ha + 1,00 km</b>",
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,10 ha + 0,99 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,57 ha + 0,99 km</b>",
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>79,10 ha + 0,99 km</b>",
    )
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Chốt lỗi biểu đồ và thứ tự đơn vị trước khi xuất bản.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_final_chart_guard(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã chốt lỗi biểu đồ và thứ tự đơn vị tổng hợp.")
    else:
        print("Biểu đồ và thứ tự đơn vị tổng hợp đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
