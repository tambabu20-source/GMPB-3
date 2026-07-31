#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def patch_mobile_chart_scaling(html: str) -> str:
    marker = (
        "    function isMobileChart() {\n"
        "      return window.matchMedia(\"(max-width: 520px)\").matches;\n"
        "    }\n"
    )
    helper = (
        marker
        + "\n"
        "    function fitSvgToViewBox(svg, width, height) {\n"
        "      svg.setAttribute(\"viewBox\", `0 0 ${width} ${height}`);\n"
        "      const renderedWidth = svg.getBoundingClientRect().width || svg.clientWidth || width;\n"
        "      svg.style.height = `${Math.ceil(renderedWidth * height / width)}px`;\n"
        "    }\n"
    )
    if "function fitSvgToViewBox(svg, width, height)" not in html:
        html = html.replace(marker, helper, 1)

    replacements = [
        ('svg.setAttribute("viewBox", "0 0 420 360");', "fitSvgToViewBox(svg, 420, 360);"),
        ('svg.setAttribute("viewBox", "0 0 760 250");', "fitSvgToViewBox(svg, 760, 250);"),
        ('svg.setAttribute("viewBox", `0 0 ${width} ${height}`);', "fitSvgToViewBox(svg, width, height);"),
        ('svg.setAttribute("viewBox", `0 0 420 ${height}`);', "fitSvgToViewBox(svg, 420, height);"),
        ('svg.setAttribute("viewBox", `0 0 900 ${chartHeight}`);', "fitSvgToViewBox(svg, 900, chartHeight);"),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    html = html.replace(
        "    function fitSvgToViewBox(svg, width, height) {\n"
        "      fitSvgToViewBox(svg, width, height);\n",
        "    function fitSvgToViewBox(svg, width, height) {\n"
        "      svg.setAttribute(\"viewBox\", `0 0 ${width} ${height}`);\n",
    )

    mobile_progress_marker = (
        "          const percentText = known ? `${project.progress.toLocaleString(\"vi-VN\", { maximumFractionDigits: 2 })}%` : \"Chưa có %\";\n"
        "          const week = projectWeeklyMeta(project);\n"
    )
    mobile_progress_fix = (
        mobile_progress_marker
        + "          const zeroReason = chartZeroReason(project);\n"
        + "          const zeroReasonText = zeroReason ? `<text x=\"18\" y=\"${metricY + 24}\" font-size=\"10.6\" fill=\"#c2410c\" font-weight=\"850\">${escapeHtml(zeroReason)}</text>` : \"\";\n"
    )
    mobile_block_start = html.find("      if (mobile) {")
    mobile_block_end = html.find("      const rowHeight = 76;", mobile_block_start)
    if mobile_block_start != -1 and mobile_block_end != -1:
        mobile_block = html[mobile_block_start:mobile_block_end]
        if "const zeroReason = chartZeroReason(project);" not in mobile_block:
            html = (
                html[:mobile_block_start]
                + mobile_block.replace(mobile_progress_marker, mobile_progress_fix, 1)
                + html[mobile_block_end:]
            )
        html = html.replace(
            '          const weekText = week ? `<text x="18" y="${metricY + 22}" font-size="10.8" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";',
            '          const weekText = week ? `<text x="18" y="${metricY + (zeroReason ? 42 : 24)}" font-size="10.8" fill="${week.color}" font-weight="800">${escapeHtml(week.label)}</text>` : "";',
        )
    return html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    path.write_text(patch_mobile_chart_scaling(html), encoding="utf-8")


if __name__ == "__main__":
    main()
