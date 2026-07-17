#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def replace_once(pattern: str, repl: str, text: str, flags: int = 0) -> str:
    new_text, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"Không tìm thấy đúng 01 vùng cần thay: {pattern[:80]}")
    return new_text


def insert_after_once(pattern: str, insert: str, text: str, flags: int = 0) -> str:
    new_text, count = re.subn(pattern, lambda match: match.group(0) + insert, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"Không tìm thấy đúng 01 vùng cần chèn: {pattern[:80]}")
    return new_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Cập nhật dashboard GPMB từ JSON tiến độ đã chuẩn hóa.")
    parser.add_argument("--index", default="index.html")
    parser.add_argument("--data", default="work/latest_progress_data.json")
    args = parser.parse_args()

    index_path = Path(args.index)
    data_path = Path(args.data)
    html = index_path.read_text(encoding="utf-8")
    data = json.loads(data_path.read_text(encoding="utf-8"))

    projects_payload = json.dumps(data["projects"], ensure_ascii=False, indent=6)
    projects_block = "    const projects = " + "\n    ".join(projects_payload.splitlines()) + ";\n\n    const dataUpdatedDate"
    pattern = r"    const projects = \[[\s\S]*?\n\s*\];\n\n    const dataUpdatedDate"
    html, count = re.subn(pattern, lambda _m: projects_block, html, count=1)
    if count != 1:
        raise SystemExit("Không tìm thấy đúng 01 vùng mảng projects để thay.")
    html = replace_once(r'const dataUpdatedDate = "[^"]+";', f'const dataUpdatedDate = "{data["dataUpdatedDate"]}";', html)
    html = re.sub(r"Cập nhật số liệu: \d{1,2}/\d{1,2}/\d{4}", f'Cập nhật số liệu: {data["dataUpdatedDate"]}', html)

    summary = data["summary"]
    html = replace_once(r"Cập nhật ngày \d{1,2}/\d{1,2}/\d{4}, .*?</p>", summary["lead"] + "</p>", html, flags=re.S)
    html = replace_once(r"Nhóm có kết quả GPMB tốt gồm .*?</p>", summary["top"] + "</p>", html, flags=re.S)
    html = replace_once(r"Khó khăn nổi bật tập trung ở .*?</p>", summary["issues"] + "</p>", html, flags=re.S)
    html = replace_once(r"Thời gian tới .*?</p>", summary["next"] + "</p>", html, flags=re.S)

    html = re.sub(r'<div class="mini-metric"><span>Có tỷ lệ %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Có tỷ lệ %</span><b>{summary["known"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Đạt từ 90% trở lên</span><b>{summary["above90"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Bình quân 8 dự án có %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Bình quân 8 dự án có %</span><b>{summary["average"]}</b></div>', html)
    html = re.sub(r'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>[^<]+</b></div>', f'<div class="mini-metric"><span>Chưa có tỷ lệ %</span><b>{summary["unknown"]}</b></div>', html)

    if ".pill.deadline-pill" not in html:
        html = insert_after_once(
            r'\n    \.pill\.private-fund \{[\s\S]*?\n    \}\n',
            '''
    .pill.deadline-pill {
      border-color: #5b8def;
      background: #eef5ff;
      color: #1d4ed8;
      font-weight: 800;
    }
''',
            html,
        )

    if ".progress-deadline" not in html:
        html = insert_after_once(
            r'\n    \.progress-row \.area-ratio \{[\s\S]*?\n    \}\n',
            '''
    .progress-deadline {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 5px 7px;
      width: 100%;
      margin: 4px 0 8px;
      padding: 6px 8px;
      border: 1px solid #70a5ff;
      border-radius: 8px;
      background: #eef5ff;
      color: #1d4ed8;
      font-size: 12px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }

    .progress-deadline span {
      font-weight: 700;
    }

    .progress-deadline strong {
      color: #1d4ed8;
      font-size: 12.5px;
      white-space: normal;
    }
''',
            html,
        )

    for old, new in {
        "#e3a12c": "#5b8def",
        "#fff3cc": "#eef5ff",
        "#7a3300": "#1d4ed8",
        "#e2a336": "#70a5ff",
        "#fff2c2": "#eef5ff",
        "#713200": "#1d4ed8",
        "#a23c00": "#1d4ed8",
        "Dự kiến hoàn thành GPMB": "Dự kiến hoàn thành",
        "Mốc HT GPMB:": "- mốc HT:",
        "Mốc HT:": "- mốc HT:",
    }.items():
        html = html.replace(old, new)

    html = html.replace(
        "      .chart.progress-percent-chart {\n        height: 820px;\n      }",
        "      .chart.progress-percent-chart {\n        height: 980px;\n      }",
    )
    html = html.replace(
        "    .chart.progress-percent-chart {\n      height: 340px;\n    }",
        "    .chart.progress-percent-chart {\n      height: 430px;\n    }",
    )
    html = html.replace(
        "    .chart.progress-percent-chart {\n      height: 560px;\n    }",
        "    .chart.progress-percent-chart {\n      height: 430px;\n    }",
    )

    html = html.replace(
        '${project.deadline ? `<span class="pill">Hoàn thành: ${project.deadline}</span>` : ""}',
        '${project.deadline ? `<span class="pill deadline-pill">Dự kiến hoàn thành: ${project.deadline}</span>` : ""}',
    )
    html = html.replace(
        '${project.deadline ? `<span class="pill deadline-pill">Dự kiến hoàn thành GPMB: ${project.deadline}</span>` : ""}',
        '${project.deadline ? `<span class="pill deadline-pill">Dự kiến hoàn thành: ${project.deadline}</span>` : ""}',
    )
    html = html.replace(
        '<div class="progress-row"><span class="progress-label">Tiến độ GPMB</span><strong>${percent}</strong>${areaRatio ? `<span class="area-ratio">Đã GPMB ${areaRatio}</span>` : ""}</div>\n            <div class="bar">',
        '<div class="progress-row"><span class="progress-label">Tiến độ GPMB</span><strong>${percent}</strong>${areaRatio ? `<span class="area-ratio">Đã GPMB ${areaRatio}</span>` : ""}</div>\n            ${project.deadline ? `<div class="progress-deadline"><span>Dự kiến hoàn thành</span><strong>${project.deadline}</strong></div>` : ""}\n            <div class="bar">',
    )
    html = html.replace(
        '<div class="progress-row"><span class="progress-label">Tiến độ GPMB</span><strong>${percent}</strong>${areaRatio ? `<span class="area-ratio">Đã GPMB ${areaRatio}</span>` : ""}</div>\n            ${project.deadline ? `<div class="progress-deadline"><span>Dự kiến hoàn thành GPMB</span><strong>${project.deadline}</strong></div>` : ""}\n            <div class="bar">',
        '<div class="progress-row"><span class="progress-label">Tiến độ GPMB</span><strong>${percent}</strong>${areaRatio ? `<span class="area-ratio">Đã GPMB ${areaRatio}</span>` : ""}</div>\n            ${project.deadline ? `<div class="progress-deadline"><span>Dự kiến hoàn thành</span><strong>${project.deadline}</strong></div>` : ""}\n            <div class="bar">',
    )

    if "function compactDeadline" not in html:
        html = insert_after_once(
            r'    function clipLabel\(text, max = 34\) \{\n      return text\.length > max \? `\$\{text\.slice\(0, max - 3\)\}\.\.\.` : text;\n    \}\n',
            '''

    function chartProjectName(name) {
      const cleaned = name
        .replace(/^Dự án\\s+/i, "")
        .replace(/\\s*\\(.*?\\)/g, "")
        .replace(/ tỉnh Đắk Lắk| tỉnh Phú Yên| thành phố Tuy Hòa| thành phố Tuy Hoà/g, "")
        .trim();
      return cleaned.charAt(0).toLocaleUpperCase("vi-VN") + cleaned.slice(1);
    }

    function wrapSvgText(text, maxChars = 52) {
      const words = text.split(/\\s+/).filter(Boolean);
      const lines = [];
      let line = "";
      words.forEach(word => {
        const next = line ? `${line} ${word}` : word;
        if (next.length > maxChars && line) {
          lines.push(line);
          line = word;
        } else {
          line = next;
        }
      });
      if (line) lines.push(line);
      return lines;
    }

    function compactDeadline(deadline) {
      if (!deadline) return "";
      const dates = deadline.match(/\\d{1,2}\\/\\d{1,2}(?:\\/\\d{4})?/g);
      if (!dates) return deadline.replace(/^Trước\\s+/i, "").trim();
      const unique = [...new Set(dates.map(date => date.replace(/\\/2026$/, "")))];
      return unique.join("; ");
    }

    function chartDeadline(project) {
      const deadline = compactDeadline(project.deadline);
      if (!deadline) return "";
      const summaries = {
        1: "15/8(HT);25/7(TĐC);30/7(PA);10/8(BV);5/8(GP)",
        3: "20/8",
        4: "30/7(PA);15/8(HT)",
        5: "30/7(PA);15/8(HT)",
        6: "21/8(95%)"
      };
      if (summaries[project.order]) return summaries[project.order];
      const normalized = deadline.replace(/\\/2026/g, "");
      return normalized.includes(";")
        ? normalized.split(";").map(item => `${item.trim()}(HT)`).join(";")
        : normalized;
    }
''',
            html,
        )

    if "function chartProjectName" not in html:
        html = insert_after_once(
            r'    function shortName\(name\) \{[\s\S]*?\n    \}\n',
            '''

    function chartProjectName(name) {
      const cleaned = name
        .replace(/^Dự án\\s+/i, "")
        .replace(/\\s*\\(.*?\\)/g, "")
        .replace(/ tỉnh Đắk Lắk| tỉnh Phú Yên| thành phố Tuy Hòa| thành phố Tuy Hoà/g, "")
        .trim();
      return cleaned.charAt(0).toLocaleUpperCase("vi-VN") + cleaned.slice(1);
    }

    function wrapSvgText(text, maxChars = 52) {
      const words = text.split(/\\s+/).filter(Boolean);
      const lines = [];
      let line = "";
      words.forEach(word => {
        const next = line ? `${line} ${word}` : word;
        if (next.length > maxChars && line) {
          lines.push(line);
          line = word;
        } else {
          line = next;
        }
      });
      if (line) lines.push(line);
      return lines;
    }
''',
            html,
        )

    if "function chartDeadline" not in html:
        html = insert_after_once(
            r'    function compactDeadline\(deadline\) \{[\s\S]*?\n    \}\n',
            '''

    function chartDeadline(project) {
      const deadline = compactDeadline(project.deadline);
      if (!deadline) return "";
      const summaries = {
        1: "15/8(HT);25/7(TĐC);30/7(PA);10/8(BV);5/8(GP)",
        3: "20/8",
        4: "30/7(PA);15/8(HT)",
        5: "30/7(PA);15/8(HT)",
        6: "21/8(95%)"
      };
      if (summaries[project.order]) return summaries[project.order];
      const normalized = deadline.replace(/\\/2026/g, "");
      return normalized.includes(";")
        ? normalized.split(";").map(item => `${item.trim()}(HT)`).join(";")
        : normalized;
    }
''',
            html,
        )

    chart_deadline = '''    function chartDeadline(project) {
      const deadline = compactDeadline(project.deadline);
      if (!deadline) return "";
      const summaries = {
        1: "15/8(HT);25/7(TĐC);30/7(PA);10/8(BV);5/8(GP)",
        3: "20/8",
        4: "30/7(PA);15/8(HT)",
        5: "30/7(PA);15/8(HT)",
        6: "21/8(95%)"
      };
      if (summaries[project.order]) return summaries[project.order];
      const normalized = deadline.replace(/\\/2026/g, "");
      return normalized.includes(";")
        ? normalized.split(";").map(item => `${item.trim()}(HT)`).join(";")
        : normalized;
    }'''
    html = replace_once(r'    function chartDeadline\(project\) \{[\s\S]*?\n    \}', chart_deadline, html)

    progress_chart = '''    function drawProgressPercentChart() {
      const svg = document.getElementById("progressPercentChart");
      const mobile = isMobileChart();
      const sorted = [...projects].sort((a, b) => {
        const aKnown = Number.isFinite(a.progress);
        const bKnown = Number.isFinite(b.progress);
        if (aKnown && bKnown) return b.progress - a.progress || a.order - b.order;
        if (aKnown) return -1;
        if (bKnown) return 1;
        return a.order - b.order;
      });
      if (mobile) {
        let cursor = 24;
        const rows = sorted.map(project => {
          const nameLines = wrapSvgText(chartProjectName(project.name), 52);
          const y = cursor;
          const barY = y + nameLines.length * 16 + 10;
          const metricY = barY + 43;
          const known = Number.isFinite(project.progress);
          const barW = 384;
          const w = known ? Math.max(4, project.progress / 100 * barW) : barW;
          const fill = known ? colors.public : colors.unknown;
          const ratio = compactAreaRatio(project);
          const deadline = chartDeadline(project);
          const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";
          const title = nameLines.map((line, index) => `<tspan x="18" dy="${index ? 16 : 0}">${escapeHtml(line)}</tspan>`).join("");
          cursor = metricY + 24;
          return `
            <text x="18" y="${y}" font-size="12.3" fill="${colors.text}" font-weight="700">${title}</text>
            <rect x="18" y="${barY}" width="${barW}" height="20" rx="7" fill="#e7edf2"/>
            <rect x="18" y="${barY}" width="${w}" height="20" rx="7" fill="${fill}"/>
            <text x="18" y="${metricY}" font-size="8.8" font-weight="800">
              <tspan fill="${colors.text}">${percentText}</tspan>
              ${ratio ? `<tspan dx="4" fill="${colors.ratio}">(${escapeHtml(ratio)})</tspan>` : ""}
              ${deadline ? `<tspan dx="5" fill="#1d4ed8">- mốc HT: ${escapeHtml(deadline)}</tspan>` : ""}
            </text>
          `;
        }).join("");
        const height = Math.max(420, cursor + 8);
        svg.setAttribute("viewBox", `0 0 420 ${height}`);
        svg.innerHTML = `<rect x="0" y="0" width="420" height="${height}" fill="transparent"/>${rows}`;
        return;
      }
      svg.setAttribute("viewBox", "0 0 900 430");
      const rows = sorted.map((project, i) => {
        const y = 32 + i * 45;
        const known = Number.isFinite(project.progress);
        const barW = 250;
        const w = known ? Math.max(4, project.progress / 100 * barW) : barW;
        const fill = known ? colors.public : colors.unknown;
        const ratio = compactAreaRatio(project);
        const deadline = chartDeadline(project);
        const percentText = known ? `${project.progress.toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%` : "Chưa có %";
        return `
          <text x="22" y="${y}" font-size="11.2" fill="${colors.text}" font-weight="700">${escapeHtml(clipLabel(chartProjectName(project.name), 58))}</text>
          <rect x="382" y="${y - 14}" width="${barW}" height="18" rx="7" fill="#e7edf2"/>
          <rect x="382" y="${y - 14}" width="${w}" height="18" rx="7" fill="${fill}"/>
          <text x="650" y="${y}" font-size="9.3" font-weight="800">
            <tspan fill="${colors.text}">${percentText}</tspan>
            ${ratio ? `<tspan dx="4" fill="${colors.ratio}">(${escapeHtml(ratio)})</tspan>` : ""}
            ${deadline ? `<tspan dx="5" fill="#1d4ed8">- mốc HT: ${escapeHtml(deadline)}</tspan>` : ""}
          </text>
        `;
      }).join("");
      svg.innerHTML = `<rect x="0" y="0" width="900" height="430" fill="transparent"/>${rows}`;
    }'''
    html = replace_once(r'    function drawProgressPercentChart\(\) \{[\s\S]*?\n    \}', progress_chart, html)

    chart_hint = (
        f'Các biểu đồ dùng dữ liệu từ file “PL Tien do (TB ket luan 326TB-UBND).xlsx” '
        f'và phụ lục tiến độ kèm Thông báo kết luận số 326/TB-UBND ngày {data["dataUpdatedDate"]}.'
    )
    html = replace_once(r'Các biểu đồ dùng dữ liệu từ .*?</p>', chart_hint + '</p>', html, flags=re.S)

    html = replace_once(r'<span class="hint">Nguồn .*?</span>', f'<span class="hint">{data["sourceNote"]}</span>', html, flags=re.S)

    index_path.write_text(html, encoding="utf-8")
    print(f'Đã cập nhật dashboard theo dữ liệu ngày {data["dataUpdatedDate"]}.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
