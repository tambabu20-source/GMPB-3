#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DATA_DATE = "07/8/2026"

REPORT_SUMMARY = [
    (
        "Cập nhật ngày 07/8/2026, Tổ công tác số 3 đang theo dõi 9 dự án; 7 dự án có tiến độ GPMB lớn hơn 0% để so sánh, "
        "01 dự án đang ở mức 0% do chưa bàn giao mặt bằng và CT.02 chưa có diện tích thực địa để tính tỷ lệ, được ghi nhận đề xuất bỏ ra Danh mục theo dõi. "
        "Báo cáo chung Tổ 3 kỳ đến ngày 07/8/2026 cho thấy chiến dịch đã bước sang ngày thứ 31, thuộc Giai đoạn 2."
    ),
    (
        "Nhóm có kết quả GPMB tốt gồm tuyến đường Cảng Bãi Gốc kết nối QL1 đi Khu kinh tế Vân Phong đạt 100%, "
        "tuyến ven biển phía Bắc cầu An Hải đạt 97,46%, Hạ tầng kỹ thuật khu dân cư phía Nam đạt 93,91%, "
        "tuyến ven biển Tuy An - Tuy Hòa đạt 92,72%, Khu nhà ở xã hội An Phú đạt 90,5% và Khu công viên trung tâm đạt 90,06%. "
        "KCN Hòa Tâm đã tăng lên 60,77%, còn tuyến Xuân Đài - Tuy An Đông vẫn 0% nhưng đã hoàn thành đo đạc, ký bản đồ và kiểm kê các khu tái định cư."
    ),
    (
        "Khó khăn nổi bật tập trung ở các trường hợp người dân chưa đồng ý nhận tiền, chưa bàn giao mặt bằng; việc phê duyệt, trình thẩm định phương án BTHTTĐC còn chậm; "
        "hạ tầng cấp thoát nước khu tái định cư chưa thống nhất tiếp nhận vận hành; một số khu tái định cư còn thiếu điện, nước, khu cải táng và nhân lực hỗ trợ địa phương. "
        "Riêng KCN Hòa Tâm có khối lượng còn lớn, khả năng hoàn thành mục tiêu chiến dịch không cao nếu không tăng tốc phê duyệt, chi trả và bàn giao."
    ),
    (
        "Thời gian tới tập trung bám các mốc 10/8, 15/8, 20/8, 21/8, 30/8 và 15/9/2026; tiếp tục họp Tổ công tác, kiểm tra hiện trường, "
        "đôn đốc chủ đầu tư và địa phương cập nhật tiến độ hằng ngày, hoàn thiện phương án bồi thường, tổ chức vận động đối thoại, "
        "chuẩn bị điều kiện pháp lý để cưỡng chế/bảo vệ thi công khi cần thiết và yêu cầu nhà thầu thi công ngay trên phần mặt bằng sạch."
    ),
]

DEADLINES_BY_ORDER = {
    1: "15/8/2026; 20/8/2026; 15/9/2026",
    2: "15/8/2026",
    3: "20/8/2026",
    4: "15/8/2026; 30/8/2026",
    5: "15/8/2026",
    6: "21/8/2026; 30/8/2026",
    7: "Đã hoàn thành",
    8: "15/8/2026; 20/8/2026; 10/9/2026; 15/9/2026",
    9: "",
}

PROJECT_METRICS = {
    1: {"progress": 92.72, "clearedArea": "13,6024/14,67 km", "remainingArea": "1,0676 km", "remainingRate": "7,28%"},
    2: {"progress": 97.46, "clearedArea": "7,29/7,48 km", "remainingArea": "0,19 km", "remainingRate": "2,54%"},
    3: {"progress": 0, "clearedArea": "0/3,4 km", "remainingArea": "3,4 km", "remainingRate": "100%"},
    4: {"progress": 90.06, "clearedArea": "13,14/14,59 ha", "remainingArea": "1,45 ha", "remainingRate": "9,94%"},
    5: {"progress": 93.91, "clearedArea": "22,34/23,79 ha", "remainingArea": "1,45 ha", "remainingRate": "6,09%"},
    6: {"progress": 60.77, "clearedArea": "298,9255/491,87 ha", "remainingArea": "192,9445 ha", "remainingRate": "39,23%"},
    7: {"progress": 100, "clearedArea": "41,32/41,32 ha", "remainingArea": "0 ha", "remainingRate": "0%"},
    8: {"progress": 90.5, "clearedArea": "6,0469/6,6816 ha", "remainingArea": "0,6348 ha", "remainingRate": "9,5%"},
}


def format_percent(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",") + "%"


def extract_projects(html: str) -> list[dict]:
    match = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not match:
        raise SystemExit("Không tìm thấy dữ liệu dự án trong dashboard.")
    return json.loads(match.group(1))


def replace_projects(html: str, projects: list[dict]) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    return re.sub(
        r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate",
        lambda _m: block,
        html,
        count=1,
    )


def patch_summary(html: str, projects: list[dict]) -> str:
    known_positive = [p for p in projects if isinstance(p.get("progress"), (int, float)) and float(p["progress"]) > 0]
    above_90 = [p for p in known_positive if float(p["progress"]) >= 90]
    avg = sum(float(p["progress"]) for p in known_positive) / len(known_positive)

    summary_html = "\n".join(f'          <p class="hint">{paragraph}</p>' for paragraph in REPORT_SUMMARY)
    html = re.sub(
        r'          <p class="hint">Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}, .*?</p>\s*'
        r'          <p class="hint">Nhóm có .*?</p>\s*'
        r'          <p class="hint">Khó khăn .*?</p>\s*'
        r'          <p class="hint">Thời gian tới .*?</p>',
        summary_html,
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(r'<div class="mini-metric"><span>Có tiến độ &gt; 0%</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Có tiến độ &gt; 0%</span><b>{len(known_positive)}/9</b></div>', html, count=1)
    html = re.sub(r'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>{len(above_90)}</b></div>', html, count=1)
    html = re.sub(r'<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>{format_percent(avg)}</b></div>', html, count=1)
    html = re.sub(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{DATA_DATE}";', html, count=1)
    html = re.sub(r"Cập nhật số liệu: \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật số liệu: {DATA_DATE}", html)
    html = re.sub(r"Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật ngày {DATA_DATE}", html)
    html = re.sub(r"file nguồn ngày \d{1,2}/\d{1,2}/\d{4}", f"file nguồn ngày {DATA_DATE}", html)
    return html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    projects = extract_projects(html)
    for project in projects:
        order = int(project.get("order", 0))
        if order in PROJECT_METRICS:
            project.update(PROJECT_METRICS[order])
        if order in DEADLINES_BY_ORDER:
            project["deadline"] = DEADLINES_BY_ORDER[order]
        if order == 3:
            project["zeroReason"] = "Đã hoàn thành đo đạc, ký bản đồ và kiểm kê các khu tái định cư; tuyến chính đang hoàn thiện hồ sơ quy chủ, kiểm kê, xác nhận nguồn gốc đất để lập phương án bồi thường."
    html = replace_projects(html, projects)
    html = patch_summary(html, projects)
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
