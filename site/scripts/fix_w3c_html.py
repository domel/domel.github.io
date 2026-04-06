#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parent.parent / "_site"
HTML_FILES = SITE_DIR.rglob("*.html")

APPEND_HASH_RE = re.compile(r'(<link\b[^>]*?)\sappend-hash="true"')
NAVBAR_TOGGLER_ROLE_RE = re.compile(
    r'(<button\b[^>]*class="[^"]*\bnavbar-toggler\b[^"]*"[^>]*?)\srole="menu"'
)


def clean_html(html: str) -> tuple[str, int]:
    html, append_hash_count = APPEND_HASH_RE.subn(r"\1", html)
    html, navbar_role_count = NAVBAR_TOGGLER_ROLE_RE.subn(r"\1", html)
    return html, append_hash_count + navbar_role_count


def main() -> int:
    if not SITE_DIR.exists():
        return 0

    total_replacements = 0

    for html_path in HTML_FILES:
        original = html_path.read_text(encoding="utf-8")
        cleaned, replacements = clean_html(original)

        if replacements:
            html_path.write_text(cleaned, encoding="utf-8")
            total_replacements += replacements

    print(f"Fixed {total_replacements} W3C validation issues in rendered HTML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
