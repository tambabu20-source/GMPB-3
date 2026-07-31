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
