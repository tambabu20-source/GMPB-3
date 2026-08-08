#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


WEEKLY_BASELINE_LABEL = "tuần trước (30/7/2026)"

PROJECT_PROGRESS = """{
      1: 92.16,
      2: 95.59,
      3: 0,
      4: 89.72,
      5: 81.72,
      6: 19.41,
      7: 99.91,
      8: 83.06,
      9: null
    }"""

PROJECT_CLEARED = """{
      1: "13,5193/14,67 km",
      2: "7,15/7,48 km",
      3: "0/3,4 km",
      4: "13,09/14,59 ha",
      5: "19,44/23,79 ha",
      6: "50,89/262,25 ha",
      7: "41,283/41,32 ha",
      8: "5,55/6,6816 ha",
      9: ""
    }"""

LOCALITY_PROGRESS = """{
      "xã Tuy An Đông": 63.15,
      "xã Tuy An Nam": 85.43,
      "xã Ô Loan": 97.58,
      "phường Bình Kiến": 81.61,
      "phường Phú Yên": 71.36,
      "xã Hòa Xuân": 53.84
    }"""

LOCALITY_CLEARED = """{
      "xã Tuy An Đông": { km: 6.89 },
      "xã Tuy An Nam": { km: 3.93 },
      "xã Ô Loan": { km: 7.34 },
      "phường Bình Kiến": { km: 1.774, ha: 5.78532 },
      "phường Phú Yên": { ha: 27.05 },
      "xã Hòa Xuân": { ha: 63.54 }
    }"""


def replace_const(html: str, name: str, value: str) -> str:
    return re.sub(
        rf"const {name} = [\s\S]*?;\n",
        f"const {name} = {value};\n",
        html,
        count=1,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Cập nhật mốc so sánh tuần qua theo kỳ dữ liệu thực tế trước đó.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = html
    new_html = replace_const(new_html, "weeklyBaselineDate", f'"{WEEKLY_BASELINE_LABEL}"')
    new_html = replace_const(new_html, "weeklyProjectProgress", PROJECT_PROGRESS)
    new_html = replace_const(new_html, "weeklyProjectCleared", PROJECT_CLEARED)
    new_html = replace_const(new_html, "weeklyLocalityProgress", LOCALITY_PROGRESS)
    new_html = replace_const(new_html, "weeklyLocalityCleared", LOCALITY_CLEARED)

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã cập nhật mốc tuần qua theo tuần trước thực tế.")
    else:
        print("Mốc tuần qua đã đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
