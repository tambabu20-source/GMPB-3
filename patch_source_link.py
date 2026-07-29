#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

SOURCE_URL = "https://docs.google.com/spreadsheets/d/1MjJcE8f93HyrpNP1Ik6QBdpQIulJLd4y/edit?pli=1&gid=1092138269#gid=1092138269"
SOURCE_URL_HTML = SOURCE_URL.replace("&", "&amp;")

CSS = """

    .source-link-card {
      grid-column: 1 / -1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-left-color: var(--accent);
    }

    .source-link-card a {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      padding: 8px 12px;
      border: 1px solid rgba(20, 126, 132, 0.24);
      border-radius: 999px;
      color: var(--accent);
      background: rgba(20, 126, 132, 0.08);
      font-weight: 800;
      text-decoration: none;
      white-space: nowrap;
    }
"""

MOBILE_CSS = """

      .source-link-card {
        align-items: stretch;
        flex-direction: column;
      }

      .source-link-card a {
        width: 100%;
        white-space: normal;
        text-align: center;
      }
"""

CARD = f'''        <article class="card source-item source-link-card">
          <div>
            <strong>Link nguồn Google Drive cập nhật tiến độ</strong>
            <span class="hint">Sử dụng link này để xem bảng nguồn đang được dùng để cập nhật dashboard.</span>
          </div>
          <a href="{SOURCE_URL_HTML}" target="_blank" rel="noopener">Mở nguồn Google Drive</a>
        </article>
'''


def patch_html(html: str) -> str:
    html = re.sub(r"\n\s*\.source-link-card \{[\s\S]*?\n\s*\.source-link-card a \{[\s\S]*?\n\s*\}\n", "\n", html, count=1)
    html = re.sub(r"\n\s*\.source-link-card \{\n\s*align-items: stretch;[\s\S]*?\.source-link-card a \{[\s\S]*?\n\s*\}\n", "\n", html, count=1)
    html = html.replace("    .empty {", CSS + "\n    .empty {", 1)
    html = html.replace("\n      .toolbar {", MOBILE_CSS + "\n      .toolbar {", 1)
    html = re.sub(r"\n\s*<article class=\"card source-item source-link-card\">[\s\S]*?</article>\n", "\n", html)
    marker = "        </article>\n      </div>\n    </section>\n  </main>"
    replacement = "        </article>\n" + CARD + "      </div>\n    </section>\n  </main>"
    if marker not in html:
        raise SystemExit("Không tìm thấy cuối mục Nguồn để chèn link Google Drive.")
    return html.replace(marker, replacement, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bổ sung link nguồn Google Drive ở cuối dashboard.")
    parser.add_argument("--index", default="index.html")
    args = parser.parse_args()
    path = Path(args.index)
    html = path.read_text(encoding="utf-8")
    new_html = patch_html(html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        print("Đã bổ sung link nguồn Google Drive.")
    else:
        print("Link nguồn Google Drive đã có.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
