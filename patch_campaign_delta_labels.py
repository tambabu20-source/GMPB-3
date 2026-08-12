#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--index", default=None)
args = parser.parse_args()

path = Path(args.index) if args.index else Path("index.html")
if not path.exists():
    path = Path("outputs/dashboard-to-cong-tac-so-3-gpmb.html")

html = path.read_text(encoding="utf-8")

html = html.replace("So với 07/7", "So trước chiến dịch")
html = html.replace("So với trước chiến dịch", "So trước chiến dịch")
html = html.replace("So với trước CĐ", "So trước chiến dịch")
html = html.replace("So trước CĐ", "So trước chiến dịch")

if 'complete: "#2563eb"' not in html:
    html = html.replace(
        '      unknown: "#7b8794",\n',
        '      unknown: "#7b8794",\n      complete: "#2563eb",\n',
        1,
    )

if "function oneLineText(" not in html:
    helper = """
    function oneLineText(text, maxChars = 80) {
      return clipLabel(String(text || "").replace(/\\s+/g, " ").trim(), maxChars);
    }

    function compactCampaignLabel(label) {
      return String(label || "")
        .replace(/^So với trước chiến dịch\\s+/i, "So trước chiến dịch ")
        .replace(/^So trước chiến dịch\\s+/i, "So trước chiến dịch ")
        .replace(/^So trước CĐ\\s+/i, "So trước chiến dịch ")
        .replace(/không thay đổi/i, "không đổi")
        .replace(/\\s+/g, " ")
        .trim();
    }
"""
    html = html.replace(
        "    function compactDeadline(deadline) {",
        helper + "\n    function compactDeadline(deadline) {",
        1,
    )
else:
    replacement = """    function compactCampaignLabel(label) {
      return String(label || "")
        .replace(/^So với trước chiến dịch\\s+/i, "So trước chiến dịch ")
        .replace(/^So trước chiến dịch\\s+/i, "So trước chiến dịch ")
        .replace(/^So trước CĐ\\s+/i, "So trước chiến dịch ")
        .replace(/không thay đổi/i, "không đổi")
        .replace(/\\s+/g, " ")
        .trim();
    }"""
    html = re.sub(
        r"    function compactCampaignLabel\(label\) \{.*?\n    \}",
        lambda _: replacement,
        html,
        count=1,
        flags=re.S,
    )

html = html.replace(
    'const color = progress >= 90 ? colors.public : progress >= 70 ? "#2f855a" : progress > 0 ? "#d97706" : colors.unknown;',
    'const color = progress >= 99.95 ? colors.complete : progress >= 90 ? colors.public : progress >= 70 ? "#2f855a" : progress > 0 ? "#d97706" : colors.unknown;',
)
html = html.replace(
    'const fill = known ? colors.public : colors.unknown;',
    'const fill = known ? (displayProgress >= 99.95 ? colors.complete : colors.public) : colors.unknown;',
)

html = html.replace(
    '          const campaignLines = campaign ? wrapSvgText(campaign.label, 48).slice(0, 2) : [];\n'
    '          const campaignText = campaignLines.map((line, index) => `<text x="18" y="${metricY + 18 + index * 15}" font-size="10.3" fill="${campaign.color}" font-weight="850">${escapeHtml(line)}</text>`).join("");\n'
    '          const zeroReasonY = metricY + 18 + campaignLines.length * 15;',
    '          const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), 58) : "";\n'
    '          const campaignText = campaignLine ? `<text x="18" y="${metricY + 18}" font-size="10.1" fill="${campaign.color}" font-weight="850">${escapeHtml(campaignLine)}</text>` : "";\n'
    '          const zeroReasonY = metricY + 18 + (campaignLine ? 15 : 0);',
)
html = html.replace(
    'cursor = metricY + 22 + campaignLines.length * 15 + zeroReasonLines.length * 15;',
    'cursor = metricY + 22 + (campaignLine ? 15 : 0) + zeroReasonLines.length * 15;',
)
html = html.replace(
    '        const campaignLines = campaign ? wrapSvgText(campaign.label, 40).slice(0, 2) : [];\n'
    '        const campaignText = campaignLines.map((line, index) => `<text x="${infoX}" y="${y + 18 + index * 14}" font-size="10.2" fill="${campaign.color}" font-weight="850">${escapeHtml(line)}</text>`).join("");\n'
    '        const zeroReasonY = y + 18 + campaignLines.length * 14;',
    '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), 58) : "";\n'
    '        const campaignText = campaignLine ? `<text x="${infoX}" y="${y + 18}" font-size="10.1" fill="${campaign.color}" font-weight="850">${escapeHtml(campaignLine)}</text>` : "";\n'
    '        const zeroReasonY = y + 18 + (campaignLine ? 14 : 0);',
)
html = html.replace(
    'const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";',
    'const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";',
)

path.write_text(html, encoding="utf-8")
