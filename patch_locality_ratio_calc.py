#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

HELPERS = r'''    function readLocalityNumber(text, unit) {
      const raw = String(text || "").trim();
      if (String(unit || "").toLowerCase() === "m" && /^\d{1,3}(?:\.\d{3})+$/.test(raw)) {
        return Number(raw.replace(/\./g, ""));
      }
      return Number(raw.replace(",", "."));
    }

    function calculateLocalityProgress(clearedText) {
      const match = String(clearedText || "").match(/([\d.,]+)\s*\/\s*([\d.,]+)\s*([a-zA-Z]*)/);
      if (!match) return null;
      const unit = match[3] || "";
      const cleared = readLocalityNumber(match[1], unit);
      const total = readLocalityNumber(match[2], unit);
      if (!Number.isFinite(cleared) || !Number.isFinite(total) || total <= 0) return null;
      return Math.max(0, Math.min(100, cleared / total * 100));
    }

'''


def patch_html(html: str) -> str:
    if "function calculateLocalityProgress" not in html:
        html = html.replace("    function extractLocalityRows() {", HELPERS + "    function extractLocalityRows() {", 1)
    html = html.replace(
        '          const progress = parseFloat(String(match[3]).replace(",", "."));\n          if (!locality || !Number.isFinite(progress)) continue;',
        '          const sourceProgress = parseFloat(String(match[3]).replace(",", "."));\n          const calculatedProgress = calculateLocalityProgress(match[2]);\n          const progress = Number.isFinite(calculatedProgress) ? calculatedProgress : sourceProgress;\n          if (!locality || !Number.isFinite(progress)) continue;',
        1,
    )
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Ưu tiên tự tính tỷ lệ địa phương từ số đã bàn giao/tổng.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã cập nhật cách tính tỷ lệ địa phương từ diện tích/chiều dài.")
    else:
        print("Cách tính tỷ lệ địa phương đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
