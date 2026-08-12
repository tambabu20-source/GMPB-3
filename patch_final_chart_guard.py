#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def patch_final_chart_guard(html: str) -> str:
    html = html.replace("So với trước chiến dịch", "So trước chiến dịch")
    html = html.replace("So trước CĐ", "So trước chiến dịch")
    html = html.replace(
        "        const campaign = localityCampaignMeta(item.locality);\n",
        "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n",
    )
    html = html.replace(
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const week = weeklyProgressMeta(\n",
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const campaignLines = campaignLine ? [campaignLine] : [];\n"
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
        "        const detailLines = detailLine ? [detailLine] : [];\n"
        "        const campaign = localityCampaignMeta(item.locality, item.progress, item.rowsForAverage);\n"
        '        const campaignLine = campaign ? oneLineText(compactCampaignLabel(campaign.label), isMobile ? 58 : 118) : "";\n'
        "        const campaignLines = campaignLine ? [campaignLine] : [];\n"
        "        const week = weeklyProgressMeta(\n",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài phải GPMB 7 dự án</span>\n              <b>29,62 km + 578,25 ha</b>",
        "Tổng diện tích/chiều dài phải GPMB 7 dự án</span>\n              <b>578,25 ha + 29,62 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>28,18 km + 381,77 ha</b>",
        "Tổng diện tích/chiều dài đã GPMB đến nay 7 dự án</span>\n              <b>381,77 ha + 28,18 km</b>",
    )
    html = html.replace(
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>1,00 km + 77,21 ha</b>",
        "Tổng diện tích/chiều dài đã GPMB trong chiến dịch</span>\n              <b>77,21 ha + 1,00 km</b>",
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
