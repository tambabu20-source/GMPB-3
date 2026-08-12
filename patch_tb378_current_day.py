#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


PLAN_START = date(2026, 7, 7)
PLAN_DAYS = 45


def vn_date(day: date) -> str:
    return f"{day.day:02d}/{day.month}/{day.year}"


def plan_day(day: date) -> int:
    return max(1, min(PLAN_DAYS, (day - PLAN_START).days + 1))


def current_stage(day_number: int) -> int:
    if day_number <= 10:
        return 1
    if day_number <= 30:
        return 2
    return 3


def extract_projects(html: str) -> tuple[list[dict], int, int]:
    marker = "    const projects = "
    start = html.index(marker) + len(marker)
    match = re.search(r";\s*const dataUpdatedDate", html[start:])
    if not match:
        raise SystemExit("Không tìm thấy điểm kết thúc dữ liệu dự án.")
    end = start + match.start()
    return json.loads(html[start:end]), start, end


def append_once(value: str, addition: str) -> str:
    if addition in value:
        return value
    if not value:
        return addition
    return value.rstrip() + "\n\n" + addition


def patch_projects(html: str) -> str:
    projects, start, end = extract_projects(html)

    coastal_note = (
        "Cập nhật TB 378/TB-UBND ngày 11/8/2026: UBND phường Bình Kiến, "
        "xã Tuy An Nam, xã Ô Loan, xã Tuy An Đông và Ban C khẩn trương hoàn thiện, "
        "phê duyệt PA BTHTTĐC các trường hợp còn lại; vận động, đối thoại, chuẩn bị "
        "phương án cưỡng chế/bảo vệ thi công để bàn giao mặt bằng trước ngày 15/8/2026."
    )
    phu_yen_note = (
        "Cập nhật TB 378/TB-UBND ngày 11/8/2026: UBND phường Phú Yên phối hợp các đơn vị "
        "liên quan tiếp tục vận động, đối thoại, hoàn thiện phương án cưỡng chế nếu cần, "
        "bàn giao mặt bằng trước ngày 15/8/2026."
    )
    hoa_tam_note = (
        "Cập nhật TB 378/TB-UBND ngày 11/8/2026: yêu cầu Ban Quản lý dự án đầu tư xây dựng "
        "Tuy Hòa phối hợp UBND xã Hòa Xuân lập kế hoạch theo từng ngày, đẩy nhanh thẩm định, "
        "phê duyệt phương án BTHTTĐC, chi trả và bàn giao; phấn đấu bàn giao trên 90% diện tích "
        "mặt bằng chậm nhất trước ngày 21/8/2026, xử lý phần còn lại trong tháng 8/2026."
    )
    xuandai_note = (
        "Cập nhật TB 378/TB-UBND ngày 11/8/2026: Sở Xây dựng rà soát, giải quyết thủ tục lĩnh vực "
        "xây dựng liên quan dự án chậm nhất ngày 11/8/2026; 02 khu tái định cư chậm nhất ngày "
        "21/8/2026. Dự án tiếp tục thuộc nhóm ven biển cần bàn giao mặt bằng trước ngày 15/8/2026."
    )
    cang_note = (
        "Cập nhật TB 378/TB-UBND ngày 11/8/2026: Ban Quản lý Khu kinh tế Phú Yên làm việc với "
        "nhà thầu, tăng nhân công, máy móc để tập trung thi công hoàn thành dự án trong tháng 9/2026."
    )
    an_phu_note = (
        "Cập nhật TB 378/TB-UBND ngày 11/8/2026: UBND phường Bình Kiến và các đơn vị liên quan "
        "khẩn trương vận động, đối thoại; trường hợp không đồng ý thì chuẩn bị phương án cưỡng chế, "
        "bảo vệ thi công để bàn giao mặt bằng trước ngày 15/8/2026."
    )

    for project in projects:
        name = project.get("name", "")
        if "Xuân Đài" in name:
            project["proposal"] = append_once(project.get("proposal", ""), xuandai_note)
            project["note"] = append_once(project.get("note", ""), xuandai_note)
            continue
        if "đoạn kết nối huyện Tuy An" in name or "phía Bắc cầu An Hải" in name:
            project["proposal"] = append_once(project.get("proposal", ""), coastal_note)
            project["note"] = append_once(project.get("note", ""), coastal_note)
            continue
        if "Khu công viên trung tâm" in name or "Hạ tầng kỹ thuật khu dân cư phía Nam" in name:
            project["proposal"] = append_once(project.get("proposal", ""), phu_yen_note)
            project["note"] = append_once(project.get("note", ""), phu_yen_note)
            continue
        if "Khu công nghiệp Hòa Tâm" in name:
            project["proposal"] = append_once(project.get("proposal", ""), hoa_tam_note)
            project["note"] = append_once(project.get("note", ""), hoa_tam_note)
            project["deadline"] = "21/8/2026; mục tiêu trên 90%; 30/8/2026"
            continue
        if "Cảng Bãi Gốc" in name:
            project["proposal"] = append_once(project.get("proposal", ""), cang_note)
            project["note"] = append_once(project.get("note", ""), cang_note)
            continue
        if "An Phú" in name:
            project["proposal"] = append_once(project.get("proposal", ""), an_phu_note)
            project["note"] = append_once(project.get("note", ""), an_phu_note)

    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    return html[:start] + payload + html[end:]


def patch_current_day(html: str, today: date) -> str:
    day_number = plan_day(today)
    stage = current_stage(day_number)
    today_text = vn_date(today)

    html = re.sub(
        r"Ngày \d{2}/\d{1,2}/\d{4} là ngày thứ \d+/45, thuộc giai đoạn \d+",
        f"Ngày {today_text} là ngày thứ {day_number}/45, thuộc giai đoạn {stage}",
        html,
    )
    html = re.sub(
        r"Theo ngày hiện tại \d{2}/\d{1,2}/\d{4}, chiến dịch đang ở ngày thứ \d+/45, thuộc Giai đoạn \d+",
        f"Theo ngày hiện tại {today_text}, chiến dịch đang ở ngày thứ {day_number}/45, thuộc Giai đoạn {stage}",
        html,
    )
    html = re.sub(
        r'<span class="current-badge">Mốc hiện nay · Ngày thứ \d+/45</span>',
        f'<span class="current-badge">Mốc hiện nay · Ngày thứ {day_number}/45</span>',
        html,
    )
    html = html.replace('class="card card-pad phase current-phase"', 'class="card card-pad phase"')
    html = re.sub(
        r'(<article class="card card-pad phase">\s*)<span class="current-badge">[^<]+</span>\s*(<strong>Ngày 31-45 · Hoàn thành</strong>)',
        r'\1\2',
        html,
    )
    html = re.sub(
        r'(<article class="card card-pad phase">\s*)(<strong>Ngày 31-45 · Hoàn thành</strong>)',
        rf'\1<span class="current-badge">Mốc hiện nay · Ngày thứ {day_number}/45</span>\n          \2',
        html,
        count=1,
    )
    html = html.replace(
        f'<article class="card card-pad phase">\n          <span class="current-badge">Mốc hiện nay · Ngày thứ {day_number}/45</span>\n          <strong>Ngày 31-45 · Hoàn thành</strong>',
        f'<article class="card card-pad phase current-phase">\n          <span class="current-badge">Mốc hiện nay · Ngày thứ {day_number}/45</span>\n          <strong>Ngày 31-45 · Hoàn thành</strong>',
    )
    return html


def patch_summary_and_sources(html: str, today: date) -> str:
    day_number = plan_day(today)
    stage = current_stage(day_number)
    today_text = vn_date(today)
    html = re.sub(
        r'(<strong>Tóm tắt tiến độ chung</strong>\s*<p class="hint">[^<]*?</p>)',
        (
            '<strong>Tóm tắt tiến độ chung</strong>\n'
            '          <p class="hint">Cập nhật ngày 10/8/2026, Tổ công tác số 3 đang theo dõi 9 dự án; '
            '7 dự án có tiến độ GPMB lớn hơn 0% để so sánh, 01 dự án đang ở mức 0% do chưa bàn giao mặt bằng '
            'và CT.02 chưa có diện tích thực địa để tính tỷ lệ, được ghi nhận đề xuất bỏ ra Danh mục theo dõi. '
            f'Theo ngày hiện tại {today_text}, chiến dịch đang ở ngày thứ {day_number}/45, thuộc Giai đoạn {stage}. '
            'Đối chiếu TB 378/TB-UBND ngày 11/8/2026, mốc 21/8/2026 là mốc đánh giá kết quả thực hiện, '
            'các địa phương và chủ đầu tư phải rà soát từng dự án, cam kết tiến độ chi tiết và xử lý ngay vướng mắc phát sinh.</p>'
        ),
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'(<p class="hint">Thời gian tới tập trung bám[^<]*?</p>)',
        (
            '<p class="hint">Thời gian tới tập trung bám các mốc 15/8, 20/8, 21/8, 30/8 và 15/9/2026; '
            'trọng tâm là hoàn thành bàn giao nhóm dự án ven biển, Công viên trung tâm, Hạ tầng kỹ thuật khu dân cư phía Nam '
            'và An Phú trước ngày 15/8; riêng Hòa Tâm phấn đấu trên 90% trước ngày 21/8. '
            'Tiếp tục kiểm tra hiện trường, đôn đốc chủ đầu tư và địa phương cập nhật tiến độ hằng ngày, hoàn thiện phương án bồi thường, '
            'tổ chức vận động đối thoại, chuẩn bị điều kiện pháp lý để cưỡng chế/bảo vệ thi công khi cần thiết và yêu cầu nhà thầu thi công ngay trên phần mặt bằng sạch.</p>'
        ),
        html,
        count=1,
        flags=re.S,
    )
    html = html.replace(
        "Các biểu đồ dùng dữ liệu từ file “TO CONG TAC SO 03 - Theo doi Tien do giai quyet chi tiet tung du an.xlsx” và phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày 17/7/2026.",
        "Các biểu đồ dùng dữ liệu từ file “TO CONG TAC SO 03 - Theo doi Tien do giai quyet chi tiet tung du an.xlsx”, phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày 17/7/2026 và nội dung chỉ đạo liên quan tại TB 378/TB-UBND ngày 11/8/2026.",
    )
    html = html.replace(
        "Dashboard đã cập nhật số liệu, vướng mắc, kiến nghị, kế hoạch thực hiện và thời hạn bàn giao mặt bằng theo file nguồn ngày 10/8/2026.",
        "Dashboard đã cập nhật số liệu, vướng mắc, kiến nghị, kế hoạch thực hiện và thời hạn bàn giao mặt bằng theo file nguồn ngày 10/8/2026; bổ sung chỉ đạo TB 378/TB-UBND ngày 11/8/2026, mốc đánh giá 21/8/2026 và các yêu cầu bàn giao/đôn đốc liên quan.",
    )
    return html


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="outputs/dashboard-to-cong-tac-so-3-gpmb.html")
    parser.add_argument("--today", help="Ngày hiện tại dạng YYYY-MM-DD; mặc định theo giờ Việt Nam.")
    args = parser.parse_args()
    today = date.fromisoformat(args.today) if args.today else datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()

    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    html = patch_projects(html)
    html = patch_current_day(html, today)
    html = patch_summary_and_sources(html, today)
    html = patch_final_chart_guard(html)
    path.write_text(html, encoding="utf-8")
    print("Đã cập nhật TB 378/TB-UBND và ngày hiện tại của chiến dịch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
