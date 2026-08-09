#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


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
PHASES = [
    ("Ngày 1-10", 1, date(2026, 7, 7), date(2026, 7, 16)),
    ("Ngày 11-30", 2, date(2026, 7, 17), date(2026, 8, 5)),
    ("Ngày 31-45", 3, date(2026, 8, 6), date(2026, 8, 20)),
]
PLAN_START = date(2026, 7, 7)
PLAN_DAYS = 45


def current_phase(today: date) -> tuple[str, int]:
    for label, stage, start, end in PHASES:
        if start <= today <= end:
            return label, stage
    if today < PHASES[0][2]:
        return PHASES[0][0], PHASES[0][1]
    return PHASES[-1][0], PHASES[-1][1]


def plan_day(today: date) -> int:
    return max(1, min(PLAN_DAYS, (today - PLAN_START).days + 1))


def mark_current_phase(html: str, phase_label: str, day_number: int) -> str:
    html = re.sub(r"\s*<span class=\"current-badge\">[^<]*</span>\n", "\n", html)
    html = html.replace('class="card card-pad phase current-phase"', 'class="card card-pad phase"')
    pattern = re.compile(
        rf'(<article class="card card-pad phase">\n)(\s*<strong>{re.escape(phase_label)}[^<]*</strong>)',
        re.MULTILINE,
    )
    replacement = (
        '<article class="card card-pad phase current-phase">\n'
        f'          <span class="current-badge">Mốc hiện nay · Ngày thứ {day_number}/45</span>\n'
        r"\2"
    )
    html, count = pattern.subn(replacement, html, count=1)
    if count != 1:
        raise SystemExit(f"Không tìm thấy mốc {phase_label} để tô nổi.")
    return html


def patch(html: str, today: date) -> str:
    if STYLE_MARKER not in html:
        if STYLE_ANCHOR not in html:
            raise SystemExit("Không tìm thấy vị trí CSS của khung điều hành 45 ngày.")
        html = html.replace(STYLE_ANCHOR, STYLE_ANCHOR + STYLE_BLOCK, 1)
    phase_label, stage = current_phase(today)
    day_number = plan_day(today)
    html = re.sub(
        r"Từ ngày ban hành Kế hoạch 295/KH-UBND, thực hiện liên tục kể cả ngày nghỉ khi cần thiết(?:\. Ngày \d{2}/\d{1,2}/\d{4} là ngày thứ \d+/45, thuộc giai đoạn \d+)?\.",
        f"Từ ngày ban hành Kế hoạch 295/KH-UBND, thực hiện liên tục kể cả ngày nghỉ khi cần thiết. Ngày {today.strftime('%d/%-m/%Y')} là ngày thứ {day_number}/45, thuộc giai đoạn {stage}.",
        html,
        count=1,
    )
    html = re.sub(
        r"Báo cáo chung Tổ 3 kỳ đến ngày 07/8/2026 cho thấy chiến dịch đã bước sang ngày thứ \d+, thuộc Giai đoạn \d+\.",
        f"Theo ngày hiện tại {today.strftime('%d/%-m/%Y')}, chiến dịch đang ở ngày thứ {day_number}/45, thuộc Giai đoạn {stage}.",
        html,
        count=1,
    )
    return mark_current_phase(html, phase_label, day_number)


def parse_today(value: str | None) -> date:
    if value:
        return date.fromisoformat(value)
    return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()


def main() -> int:
    parser = argparse.ArgumentParser(description="Tô nổi mốc hiện nay trong khung điều hành 45 ngày.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--today", help="Ngày kiểm tra dạng YYYY-MM-DD; mặc định theo giờ Việt Nam.")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    updated = patch(html, parse_today(args.today))
    path.write_text(updated, encoding="utf-8")
    print("Đã làm nổi mốc hiện nay trong khung điều hành 45 ngày.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
