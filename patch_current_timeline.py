#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


STYLE_MARKER = ".phase.current-phase"
STYLE_BLOCK = """
    .phase.current-phase {
      border-left-color: #f59e0b;
      border-color: rgba(245, 158, 11, 0.55);
      background: linear-gradient(180deg, #fff7ed 0%, #ffffff 82%);
      box-shadow: 0 16px 32px rgba(245, 158, 11, 0.18);
      position: relative;
    }

    .phase.current-phase strong {
      color: #9a3412;
    }

    .phase.current-phase .date-chip {
      background: #ffedd5;
      color: #c2410c;
      border: 1px solid #fdba74;
    }

    .current-badge {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      margin-bottom: 8px;
      padding: 5px 9px;
      border-radius: 999px;
      background: #f97316;
      color: #fff;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0;
    }
"""

STYLE_ANCHOR = "    .phase:nth-child(4) { border-left-color: var(--accent-3); }\n"
OLD_PHASE = """        <article class=\"card card-pad phase\">
          <strong>Ngày 11-30 · Tập trung xử lý</strong>"""
NEW_PHASE = """        <article class=\"card card-pad phase current-phase\">
          <span class=\"current-badge\">Mốc hiện nay</span>
          <strong>Ngày 11-30 · Tập trung xử lý</strong>"""


def patch(html: str) -> str:
    if STYLE_MARKER not in html:
        if STYLE_ANCHOR not in html:
            raise SystemExit("Không tìm thấy vị trí CSS của khung điều hành 45 ngày.")
        html = html.replace(STYLE_ANCHOR, STYLE_ANCHOR + STYLE_BLOCK, 1)

    if "current-badge">" in html:
        return html
    if OLD_PHASE not in html:
        raise SystemExit("Không tìm thấy mốc Ngày 11-30 để tô nổi.")
    return html.replace(OLD_PHASE, NEW_PHASE, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tô nổi mốc hiện nay trong khung điều hành 45 ngày.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    updated = patch(html)
    path.write_text(updated, encoding="utf-8")
    print("Đã làm nổi mốc hiện nay trong khung điều hành 45 ngày.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
