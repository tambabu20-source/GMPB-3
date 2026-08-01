#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


SUMMARY_PARAGRAPHS = [
    "Cập nhật ngày {data_date}, Tổ công tác số 3 đang theo dõi 9 dự án; 7 dự án có tiến độ GPMB lớn hơn 0% để so sánh, 01 dự án đang ở mức 0% do chưa đủ cơ sở kiểm đếm thực địa và CT.02 chưa có diện tích thực địa để tính tỷ lệ, được ghi nhận đề xuất bỏ ra Danh mục theo dõi. Tham khảo báo cáo sơ kết 20 ngày đêm cho thấy công tác chỉ đạo đã được triển khai khẩn trương, có họp đôn đốc, kiểm tra hiện trường và yêu cầu các địa phương, chủ đầu tư cập nhật tiến độ hằng ngày trên file trực tuyến.",
    "Nhóm có kết quả GPMB tốt gồm tuyến đường từ Cảng Bãi Gốc kết nối QL1 đi Khu kinh tế Vân Phong đạt 98,74%, tuyến đường bộ ven biển Tuy An - Tuy Hòa đạt 90,05%, tuyến ven biển phía Bắc cầu An Hải đạt 89,44%. Một số dự án có chuyển biến sau 20 ngày chiến dịch như Khu công viên trung tâm, Hạ tầng kỹ thuật khu dân cư phía Nam, KCN Hòa Tâm và Khu nhà ở xã hội An Phú; riêng tuyến Xuân Đài - Tuy An Đông vẫn 0% do chưa đủ cơ sở kiểm đếm thực địa.",
    "Khó khăn nổi bật tập trung ở việc người dân chưa đồng ý nhận tiền bồi thường và chậm bàn giao mặt bằng; công tác xác định, cung cấp thông tin nguồn gốc đất nông nghiệp còn chậm; hạ tầng cấp nước tại khu tái định cư chưa thống nhất tiếp nhận quản lý, vận hành; giá đất bồi thường tại một số đoạn đường khu tái định cư chưa phù hợp; một số đơn vị, địa phương chưa bảo đảm mốc lập, trình thẩm định và phê duyệt phương án bồi thường.",
    "Thời gian tới tiếp tục bám các mốc 30/7, 31/7, 05/8, 15/8, 20/8, 21/8 và 30/8/2026; duy trì họp Tổ công tác, kiểm tra hiện trường các dự án còn khối lượng lớn, tăng cường nhân lực lập phương án, đẩy mạnh vận động đối thoại, chuẩn bị đầy đủ điều kiện pháp lý để cưỡng chế/bảo vệ thi công khi cần thiết và yêu cầu chủ đầu tư đôn đốc nhà thầu thi công ngay trên diện tích đã có mặt bằng sạch.",
]

ZERO_REASON = "Nguyên nhân 0%: sai lệch địa chính, chưa đủ cơ sở kiểm đếm"


def current_data_date(html: str) -> str:
    match = re.search(r'const dataUpdatedDate = "([^"]+)"', html)
    return match.group(1) if match else "30/7/2026"


def patch_summary(html: str) -> str:
    data_date = current_data_date(html)
    paragraphs = [text.format(data_date=data_date) for text in SUMMARY_PARAGRAPHS]
    patterns = [
        r'<p class="hint">Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}, .*?</p>',
        r'<p class="hint">Nhóm có .*?</p>',
        r'<p class="hint">Khó khăn .*?</p>',
        r'<p class="hint">Thời gian tới .*?</p>',
    ]
    for pattern, text in zip(patterns, paragraphs):
        html = re.sub(pattern, f'<p class="hint">{text}</p>', html, count=1, flags=re.S)
    html = re.sub(
        r'<div class="mini-metric"><span>Có tỷ lệ %</span><b>[^<]+</b></div>',
        '<div class="mini-metric"><span>Có tiến độ &gt; 0%</span><b>7/9</b></div>',
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="mini-metric"><span>Có tiến độ &gt; 0%</span><b>[^<]+</b></div>',
        '<div class="mini-metric"><span>Có tiến độ &gt; 0%</span><b>7/9</b></div>',
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>[^<]+</b></div>',
        '<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>2</b></div>',
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="mini-metric"><span>Bình quân [^<]+</span><b>[^<]+</b></div>',
        '<div class="mini-metric"><span>Bình quân 7 dự án có tiến độ</span><b>72,57%</b></div>',
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>[^<]+</b></div>',
        '<div class="mini-metric"><span>0%/chưa tính</span><b>2</b></div>',
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="mini-metric"><span>0%/chưa tính</span><b>[^<]+</b></div>',
        '<div class="mini-metric"><span>0%/chưa tính</span><b>2</b></div>',
        html,
        count=1,
    )
    html = html.replace("Cơ cấu tiến độ 8 dự án có tỷ lệ GPMB", "Cơ cấu tiến độ 7 dự án có GPMB")
    html = html.replace("Biểu đồ cơ cấu tiến độ 8 dự án có tỷ lệ GPMB", "Biểu đồ cơ cấu tiến độ 7 dự án có GPMB")
    return html


def patch_progress_data_chart(html: str) -> str:
    html = html.replace(
        "      const known = projects.filter(p => Number.isFinite(p.progress));\n"
        "      const segments = [\n"
        "        { label: \"Từ 90% trở lên\", count: known.filter(p => p.progress >= 90).length, color: colors.public },\n"
        "        { label: \"Từ 70% đến dưới 90%\", count: known.filter(p => p.progress >= 70 && p.progress < 90).length, color: \"#2f855a\" },\n"
        "        { label: \"Dưới 70%\", count: known.filter(p => p.progress > 0 && p.progress < 70).length, color: \"#d97706\" },\n"
        "        { label: \"0%\", count: known.filter(p => p.progress === 0).length, color: colors.unknown }\n"
        "      ];\n"
        "      const total = known.length || 1;",
        "      const known = projects.filter(p => Number.isFinite(p.progress) && p.progress > 0);\n"
        "      const notCounted = projects.length - known.length;\n"
        "      const segments = [\n"
        "        { label: \"Từ 90% trở lên\", count: known.filter(p => p.progress >= 90).length, color: colors.public },\n"
        "        { label: \"Từ 70% đến dưới 90%\", count: known.filter(p => p.progress >= 70 && p.progress < 90).length, color: \"#2f855a\" },\n"
        "        { label: \"Dưới 70%\", count: known.filter(p => p.progress < 70).length, color: \"#d97706\" },\n"
        "        { label: \"0%/chưa tính\", count: notCounted, color: colors.unknown }\n"
        "      ];\n"
        "      const total = projects.length || 1;",
    )
    html = html.replace(
        '<text x="${cx}" y="${cy + 17}" font-size="11.5" fill="${colors.muted}" font-weight="700" text-anchor="middle">dự án có %</text>',
        '<text x="${cx}" y="${cy + 17}" font-size="11.5" fill="${colors.muted}" font-weight="700" text-anchor="middle">dự án &gt; 0%</text>',
    )
    return html


def patch_zero_reason_helper(html: str) -> str:
    if "function chartZeroReason(project)" in html:
        return html
    marker = (
        "    function isMobileChart() {\n"
        "      return window.matchMedia(\"(max-width: 520px)\").matches;\n"
        "    }\n"
    )
    helper = (
        marker
        + "\n"
        "    function chartZeroReason(project) {\n"
        f"      return project.order === 3 ? \"{ZERO_REASON}\" : \"\";\n"
        "    }\n"
    )
    return html.replace(marker, helper, 1)


def patch_project_chart(html: str) -> str:
    if "const zeroReason = chartZeroReason(project);" not in html:
        html = html.replace(
            "          const week = projectWeeklyMeta(project);\n"
            "          const weekText = week ? `<text x=\"18\" y=\"${metricY + 24}\" font-size=\"10.8\" fill=\"${week.color}\" font-weight=\"800\">${escapeHtml(week.label)}</text>` : \"\";\n",
            "          const week = projectWeeklyMeta(project);\n"
            "          const zeroReason = chartZeroReason(project);\n"
            "          const zeroReasonText = zeroReason ? `<text x=\"18\" y=\"${metricY + 24}\" font-size=\"10.6\" fill=\"#c2410c\" font-weight=\"850\">${escapeHtml(zeroReason)}</text>` : \"\";\n"
            "          const weekText = week ? `<text x=\"18\" y=\"${metricY + (zeroReason ? 42 : 24)}\" font-size=\"10.8\" fill=\"${week.color}\" font-weight=\"800\">${escapeHtml(week.label)}</text>` : \"\";\n",
            1,
        )
        html = html.replace(
            "          cursor = metricY + (week ? 46 : 24);\n",
            "          cursor = metricY + (zeroReason ? 64 : (week ? 46 : 24));\n",
            1,
        )
        html = html.replace(
            "            ${weekText}\n"
            "          `;\n"
            "        }).join(\"\");",
            "            ${zeroReasonText}\n"
            "            ${weekText}\n"
            "          `;\n"
            "        }).join(\"\");",
            1,
        )

    if "const zeroReason = chartZeroReason(project);\n        return `" not in html:
        html = html.replace(
            "        const week = projectWeeklyMeta(project);\n"
            "        return `\n"
            "          <text x=\"22\" y=\"${y}\" font-size=\"12\" fill=\"${colors.text}\" font-weight=\"700\">${escapeHtml(chartProjectName(project.name))}</text>",
            "        const week = projectWeeklyMeta(project);\n"
            "        const zeroReason = chartZeroReason(project);\n"
            "        return `\n"
            "          <text x=\"22\" y=\"${y}\" font-size=\"12\" fill=\"${colors.text}\" font-weight=\"700\">${escapeHtml(chartProjectName(project.name))}</text>",
            1,
        )
        html = html.replace(
            "          ${week ? `<text x=\"740\" y=\"${y + 19}\" font-size=\"10.5\" fill=\"${week.color}\" font-weight=\"800\">${escapeHtml(week.label)}</text>` : \"\"}\n"
            "        `;",
            "          ${zeroReason ? `<text x=\"740\" y=\"${y + 19}\" font-size=\"10.5\" fill=\"#c2410c\" font-weight=\"850\">${escapeHtml(zeroReason)}</text>` : \"\"}\n"
            "          ${week ? `<text x=\"740\" y=\"${y + (zeroReason ? 36 : 19)}\" font-size=\"10.5\" fill=\"${week.color}\" font-weight=\"800\">${escapeHtml(week.label)}</text>` : \"\"}\n"
            "        `;",
            1,
        )
    return html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    html = patch_summary(html)
    html = patch_progress_data_chart(html)
    html = patch_zero_reason_helper(html)
    html = patch_project_chart(html)
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()