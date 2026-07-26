#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DATA_DATE = "24/7/2026"
SOURCE_NOTE = (
    "Nguồn cập nhật: file “11h30 25.7.2026 TO CONG TAC SO 03 - Theo doi Tien do "
    "giai quyet chi tiet tung du an (3)” - Phụ lục tiến độ kèm Thông báo kết luận "
    "số 326/TB-UBND ngày 17/7/2026 của UBND tỉnh; đối chiếu Báo cáo số 583/BC-SNNMT "
    "ngày 22/7/2026 để rà soát bối cảnh vướng mắc."
)

UPDATES = {
    1: {
        "totalArea": "14,67 km",
        "clearedArea": "13,4136/14,67 km",
        "remainingArea": "1,2564 km",
        "remainingRate": "8,56%",
        "progress": 91.44,
        "deadline": "15/8/2026; 25/7/2026; 27/7/2026; 29/7/2026; 30/7/2026",
        "note": (
            "Địa bàn/tiến độ: xã Tuy An Đông: đã bàn giao 0,2/0,2 km; 100%; chưa bàn giao 0; còn 0% | "
            "xã Tuy An Nam: đã bàn giao 3,93/4,6 km; 85,43%; chưa bàn giao 0,67; còn 14,57% | "
            "xã Ô Loan: đã bàn giao 7,34/7,6 km; 97,58%; chưa bàn giao 0,26; còn 3,42% | "
            "phường Bình Kiến: đã bàn giao 1,9436/2,27 km; 85,62%; chưa bàn giao 0,3264; còn 14,38%\n"
            "Thời gian xử lý xong vướng mắc: xã Tuy An Nam: 25/7/2026; 28/7/2026; 15/8/2026 | "
            "xã Ô Loan: 25/7/2026; 27/7/2026; 29/7/2026; 30/7/2026; 15/8/2026 | "
            "phường Bình Kiến: 27/7/2026; 15/8/2026\n"
            f"{SOURCE_NOTE}"
        ),
        "issues": (
            "xã Tuy An Nam còn vướng 02 hộ không phối hợp kiểm kê; còn 03 trường hợp tiếp tục xem xét điều kiện tái định cư. "
            "xã Ô Loan còn 14 thửa/11 hộ đất nông nghiệp chưa thống nhất giá và mật độ cây trồng; đã cung cấp hồ sơ cưỡng chế cho Công an xã, một số hộ chưa thống nhất sau đối thoại. "
            "phường Bình Kiến còn 08 trường hợp đã phê duyệt chưa đồng ý nhận tiền, bàn giao mặt bằng; 79 trường hợp chưa phê duyệt phương án BTHTTĐC, trong đó có nhóm mới trình thông báo thu hồi đất thay thế và nhóm đã công khai phương án. "
            "BQL dự án ĐTXD Tuy Hòa chưa hoàn tất bàn giao khu tái định cư số 1, 2; một số nội dung liên quan cấp, thoát nước, chính sách bồi thường, hỗ trợ, suất tái định cư tối thiểu còn phát sinh vướng mắc."
        ),
        "proposal": (
            "Kiến nghị:\nBan C, UBND các xã/phường và các đơn vị liên quan hoàn thiện kiểm kê, phương án BTHTTĐC, đối thoại, vận động; trường hợp cần thiết thực hiện quy trình cưỡng chế/bảo vệ thi công theo quy định. "
            "Đề nghị hoàn thành xem xét điều kiện tái định cư, thẩm định, phê duyệt, chi trả và bàn giao mặt bằng theo các mốc 25/7, 27/7, 28/7, 29/7, 30/7 và trước 15/8/2026.\n\n"
            "Kế hoạch thực hiện/Tiến độ thực hiện:\nTập trung hoàn thiện hạ tầng khu tái định cư số 1, 2; xử lý nhóm hộ chưa nhận tiền, chưa thống nhất phương án; phê duyệt các phương án còn lại; tiếp tục đối thoại, vận động, chi trả và bàn giao mặt bằng trước 15/8/2026."
        ),
    },
    2: {
        "totalArea": "7,48 km",
        "clearedArea": "7,14/7,48 km",
        "remainingArea": "0,34 km",
        "remainingRate": "4,55%",
        "progress": 95.45,
        "deadline": "20/8/2026",
        "note": "Địa bàn/tiến độ: xã Tuy An Đông: đã bàn giao 7,14/7,48 km; 95,45%; chưa bàn giao 0,34; còn 4,55%\nThời gian xử lý xong vướng mắc: 15/8/2026; bàn giao mặt bằng 20/8/2026\n" + SOURCE_NOTE,
        "issues": "Hệ thống cấp thoát nước khu tái định cư chưa có đơn vị tiếp nhận quản lý, khó khăn cho việc vận hành, sử dụng; Ban C đã làm việc với Công ty Cổ phần Cấp thoát nước Phú Yên nhưng chưa thống nhất tiếp nhận.",
    },
    3: {
        "totalArea": "3,4 km (21,1443 ha)",
        "clearedArea": "0/3,4 km",
        "remainingArea": "3,4 km",
        "remainingRate": "100%",
        "progress": 0,
        "deadline": "20/8/2026; 30/7/2026; 15/8/2026",
        "note": "Địa bàn/tiến độ: xã Tuy An Đông: đã bàn giao 0/3,4 km; 0%; chưa bàn giao 3,4; còn 100%\nThời gian xử lý xong vướng mắc: 17/7/2026; 20/7/2026; 30/7/2026; 15/8/2026; 20/8/2026\n" + SOURCE_NOTE,
        "issues": "Dự án mới triển khai, tư vấn đã hoàn thành công tác đo đạc; các khu tái định cư thôn Tiên Châu và thôn Xuân Phu đã hoàn thiện kết quả đo đạc hiện trạng, đang quy chủ sử dụng đất và tổ chức kiểm kê.",
    },
    4: {
        "totalArea": "14,59 ha",
        "clearedArea": "13,1/14,59 ha",
        "remainingArea": "1,49 ha",
        "remainingRate": "10,82%",
        "progress": 89.18,
        "deadline": "31/7/2026; 15/8/2026",
        "note": "Địa bàn/tiến độ: phường Phú Yên: đã bàn giao 13,1/14,59 ha; 89,18%; chưa bàn giao 1,49; còn 10,82%\nThời gian xử lý xong vướng mắc: 31/7/2026; 15/8/2026\n" + SOURCE_NOTE,
        "issues": "24 hộ đã phê duyệt phương án chưa đồng ý nhận tiền, chưa đồng ý giao mặt bằng; 17 hộ chưa phê duyệt phương án bồi thường. Đến nay còn 41 hộ, giảm 11 hộ so với thời điểm 07/7/2026.",
    },
    5: {
        "totalArea": "23,79 ha",
        "clearedArea": "18,32/23,79 ha",
        "remainingArea": "5,47 ha",
        "remainingRate": "23,00%",
        "progress": 77.0,
        "deadline": "31/7/2026; 5/8/2026; 15/8/2026",
        "note": "Địa bàn/tiến độ: phường Phú Yên: đã bàn giao 18,32/23,79 ha; 77,00%; chưa bàn giao 5,47; còn 23,00%\nThời gian xử lý xong vướng mắc: 31/7/2026; 5/8/2026; 15/8/2026\n" + SOURCE_NOTE,
        "issues": "16 đối tượng đã phê duyệt phương án chưa đồng ý nhận tiền; 06 hộ chưa phê duyệt phương án bồi thường. Đã vận động, đối thoại được 20 hộ bàn giao mặt bằng; hiện còn 22 hộ, giảm 20 hộ so với thời điểm 07/7/2026.",
    },
    6: {
        "totalArea": "262,25 ha",
        "clearedArea": "40,98/262,25 ha",
        "remainingArea": "221,27 ha",
        "remainingRate": "84,38%",
        "progress": 15.62,
        "deadline": "26/7/2026; 30/7/2026; 20/8/2026",
        "note": "Địa bàn/tiến độ: xã Hòa Xuân: đã bàn giao 40,98/262,25 ha; 15,62%; chưa bàn giao 221,27; còn 84,38%\nThời gian xử lý xong vướng mắc: 26/7/2026; 30/7/2026; 20/8/2026\n" + SOURCE_NOTE,
        "issues": "Nguồn gốc sử dụng đất của nhiều hộ dân phức tạp, hồ sơ pháp lý chưa đầy đủ; giá đất, giá bồi thường và chính sách hỗ trợ còn khác biệt so với kỳ vọng của một bộ phận người dân; còn thiếu thông tin người sử dụng đất do một số địa phương chưa cung cấp kịp thời.",
    },
    7: {
        "totalArea": "41,32 ha (7,40km/7,72km)",
        "clearedArea": "41,07/41,32 ha",
        "remainingArea": "0,25 ha",
        "remainingRate": "0,61%",
        "progress": 99.39,
        "deadline": "30/7/2026; 15/8/2026",
        "note": "Địa bàn/tiến độ: xã Hòa Xuân: đã bàn giao 41,07/41,32 ha; 99,39%; chưa bàn giao 0,25; còn 0,61%\nThời gian xử lý xong vướng mắc: 30/7/2026; 15/8/2026\n" + SOURCE_NOTE,
        "issues": "Còn 03 hộ chưa đồng ý nhận tiền, bàn giao mặt bằng; đã vận động được 04 hộ đồng ý nhận tiền, bàn giao mặt bằng.",
    },
    8: {
        "totalArea": "6,68162 ha",
        "clearedArea": "5,55/6,68162 ha",
        "remainingArea": "1,13162 ha",
        "remainingRate": "16,94%",
        "progress": 82.32,
        "deadline": "26/7/2026; 28/7/2026; 30/7/2026; 15/8/2026",
        "note": "Địa bàn/tiến độ: phường Bình Kiến: đã bàn giao 5,55/6,68162 ha; 82,32%; chưa bàn giao 1,13162; còn 16,94%\nThời gian xử lý xong vướng mắc: 26/7/2026; 28/7/2026; 30/7/2026; 15/8/2026\n" + SOURCE_NOTE,
        "issues": "Còn 01 thửa đã nhận tiền nhưng chưa tháo dỡ nhà để bàn giao mặt bằng; 10 thửa chưa nhận tiền bồi thường, hỗ trợ; 19/97 thửa chưa phê duyệt phương án; còn vướng điều chỉnh hệ số giá đất đối với đoạn đường khu tái định cư.",
    },
    9: {
        "totalArea": "",
        "clearedArea": "",
        "remainingArea": "",
        "remainingRate": "",
        "progress": None,
        "deadline": "",
        "issues": "Chưa có số liệu diện tích thực địa để tính tỷ lệ GPMB.",
        "proposal": "Kiến nghị:\nĐề xuất bỏ ra Danh mục theo dõi.\n\nKế hoạch thực hiện/Tiến độ thực hiện:\nĐang ở bước khảo sát, đề xuất tuyến, chưa có chủ trương đầu tư; đề xuất bỏ ra Danh mục theo dõi do Tổ công tác số 03 phụ trách theo dõi, đôn đốc GPMB các dự án đầu tư trên địa bàn tỉnh.",
        "note": "Đề xuất bỏ ra Danh mục theo dõi.\n" + SOURCE_NOTE,
    },
}

SUMMARY = {
    "lead": "Cập nhật ngày 24/7/2026, Tổ công tác số 3 đang theo dõi 9 dự án; 8 dự án có tỷ lệ GPMB trong phụ lục mới, CT.02 chưa có diện tích thực địa để tính tỷ lệ và được ghi nhận đề xuất bỏ ra Danh mục theo dõi.",
    "top": "Nhóm có kết quả GPMB tốt gồm tuyến Cảng Bãi Gốc kết nối QL1 đi Khu kinh tế Vân Phong đạt 99,39%, tuyến ven biển phía Bắc cầu An Hải đạt 95,45%, tuyến ven biển Tuy An - Tuy Hòa đạt khoảng 91,44%. Một số dự án đã cải thiện rõ so với kỳ trước như Khu công viên trung tâm đạt 89,18%, Hạ tầng kỹ thuật khu dân cư phía Nam đạt 77,00%, Khu công nghiệp Hòa Tâm tăng lên 15,62% nhưng vẫn còn khối lượng lớn.",
    "issues": "Khó khăn nổi bật vẫn tập trung ở việc hộ dân chưa thống nhất giá đất, mật độ cây trồng và chính sách bồi thường/hỗ trợ; một số hồ sơ còn phải kiểm kê, họp xét tái định cư, phê duyệt phương án, xác định nghĩa vụ tài chính, tiếp nhận hạ tầng cấp thoát nước khu tái định cư, tháo dỡ nhà cửa sau khi nhận tiền và hoàn thiện hồ sơ cưỡng chế/bảo vệ thi công.",
    "next": "Thời gian tới tập trung các mốc 25/7, 26/7, 27/7, 28/7, 29/7, 30/7, 31/7, 05/8, 15/8 và 20/8/2026; tiếp tục đối thoại, vận động, trình thẩm định/phê duyệt phương án, chi trả tiền, xử lý cưỡng chế khi đủ điều kiện và bàn giao mặt bằng sạch theo từng dự án.",
    "known": "8/9",
    "above90": "3",
    "average": "68,80%",
    "unknown": "1",
}


def load_projects(html: str) -> list[dict]:
    match = re.search(r"const projects = (\[[\s\S]*?\n\s*\]);\n\n\s*const dataUpdatedDate", html)
    if not match:
        raise SystemExit("Không tìm thấy mảng projects.")
    return json.loads(match.group(1))


def write_projects(html: str, projects: list[dict]) -> str:
    payload = json.dumps(projects, ensure_ascii=False, indent=6)
    block = "    const projects = " + "\n    ".join(payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    html, count = re.subn(r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate", lambda _m: block, html, count=1)
    if count != 1:
        raise SystemExit("Không thay được mảng projects.")
    return html


def replace_summary(html: str) -> str:
    html = re.sub(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{DATA_DATE}";', html, count=1)
    html = re.sub(r"Cập nhật số liệu: \d{1,2}/\d{1,2}/\d{4}", f"Cập nhật số liệu: {DATA_DATE}", html)
    html = re.sub(r"Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}, .*?</p>", SUMMARY["lead"] + "</p>", html, count=1, flags=re.S)
    html = re.sub(r"Nhóm có kết quả GPMB tốt gồm .*?</p>", SUMMARY["top"] + "</p>", html, count=1, flags=re.S)
    html = re.sub(r"Khó khăn nổi bật .*?</p>", SUMMARY["issues"] + "</p>", html, count=1, flags=re.S)
    html = re.sub(r"Thời gian tới .*?</p>", SUMMARY["next"] + "</p>", html, count=1, flags=re.S)
    html = re.sub(r'<div class="mini-metric"><span>Có tỷ lệ %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Có tỷ lệ %</span><b>{SUMMARY["known"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>{SUMMARY["above90"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Bình quân 8 dự án có %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Bình quân 8 dự án có %</span><b>{SUMMARY["average"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>{SUMMARY["unknown"]}</b></div>', html)
    html = html.replace("ngày 19/7/2026", f"ngày {DATA_DATE}")
    html = html.replace("Báo cáo số 583/BC-SNNMT ngày 24/7/2026", "Báo cáo số 583/BC-SNNMT ngày 22/7/2026")
    return html


def patch_locality_source_preference(html: str) -> str:
    html = html.replace(
        "const progress = Number.isFinite(calculatedProgress) ? calculatedProgress : sourceProgress;",
        "const progress = Number.isFinite(sourceProgress) ? sourceProgress : calculatedProgress;",
    )
    html = html.replace("diện tích đang rà soát - ", "")
    html = html.replace("diện tích đang rà soát", "")
    return html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    projects = load_projects(html)
    by_order = {project.get("order"): project for project in projects}
    for order, updates in UPDATES.items():
        project = by_order.get(order)
        if not project:
            raise SystemExit(f"Thiếu dự án {order}")
        project.update(updates)
    html = write_projects(html, projects)
    html = replace_summary(html)
    html = patch_locality_source_preference(html)
    path.write_text(html, encoding="utf-8")
    print(f"Đã cập nhật dashboard theo phụ lục tiến độ đến ngày {DATA_DATE}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
