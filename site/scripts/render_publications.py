#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "_partials" / "generated-publications.qmd"

ACCENT_MARKS = {
    '"': "\u0308",
    "'": "\u0301",
    "~": "\u0303",
    "`": "\u0300",
    "^": "\u0302",
}

SPECIAL_LATEX = {
    r"\i": "i",
    r"\l": "l",
}


def split_top_level(text: str, separator: str = ",") -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    brace_depth = 0
    quote_open = False

    for char in text:
        if char == '"' and brace_depth == 0:
            quote_open = not quote_open
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)

        if char == separator and brace_depth == 0 and not quote_open:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)

    return parts


def strip_wrapping(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    if not value:
        return ""

    if (value[0], value[-1]) in {("{", "}"), ('"', '"')}:
        value = value[1:-1]

    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)
    value = decode_latex(value)
    value = value.replace("{", "").replace("}", "")
    return value.strip()


def decode_latex(value: str) -> str:
    value = re.sub(r"\\url\{([^{}]+)\}", r"\1", value)

    for source, target in SPECIAL_LATEX.items():
        value = value.replace(source, target)

    value = value.replace(r"\_", "_")
    value = value.replace("{-}", "-")

    accent_pattern = re.compile(r"""\\(["'~`^])\s*\{?\s*(\\[A-Za-z]+|[A-Za-z])\s*\}?""")

    def replace_accent(match: re.Match[str]) -> str:
        accent = match.group(1)
        base = SPECIAL_LATEX.get(match.group(2), match.group(2))
        return unicodedata.normalize("NFC", f"{base}{ACCENT_MARKS[accent]}")

    return accent_pattern.sub(replace_accent, value)


def parse_entries(raw_text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    chunks = re.split(r"(?=@)", raw_text)

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk.startswith("@"):
            continue

        header, _, remainder = chunk.partition("{")
        entry_type = header[1:].strip().lower()
        body = remainder.rsplit("}", 1)[0].strip()
        if not body:
            continue

        key, _, fields_blob = body.partition(",")
        fields: dict[str, str] = {
            "entry_type": entry_type,
            "key": key.strip(),
        }

        for field in split_top_level(fields_blob):
            if "=" not in field:
                continue
            name, value = field.split("=", 1)
            fields[name.strip().lower()] = strip_wrapping(value)

        entries.append(fields)

    return entries


def format_author(name: str) -> str:
    name = name.strip()
    if "," in name:
        family, given = [part.strip() for part in name.split(",", 1)]
        return f"{given} {family}".strip()
    return name


def format_authors(raw_authors: str) -> str:
    authors = [format_author(part) for part in raw_authors.split(" and ") if part.strip()]
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    return f"{', '.join(authors[:-1])}, and {authors[-1]}"


def publication_venue(entry: dict[str, str]) -> str:
    if entry.get("journal"):
        venue = f"*{entry['journal']}*"
        volume = entry.get("volume")
        number = entry.get("number")
        if volume and number:
            venue += f" {volume}({number})"
        elif volume:
            venue += f" {volume}"
        return venue

    if entry.get("booktitle"):
        venue = f"In *{entry['booktitle']}*"
        if entry.get("publisher"):
            venue += f", {entry['publisher']}"
        return venue

    if entry.get("publisher"):
        return entry["publisher"]

    return ""


def publication_pages(entry: dict[str, str]) -> str:
    pages = entry.get("pages", "").replace("--", "-")
    return f"pp. {pages}" if pages else ""


def publication_link(entry: dict[str, str]) -> str:
    doi = entry.get("doi", "").strip()
    url = entry.get("url", "").strip()

    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        return f"[DOI]({doi_url})"

    if url:
        return f"[URL]({url})"

    return ""


def sort_key(entry: dict[str, str]) -> tuple[int, str, str]:
    year = entry.get("year", "0")
    try:
        numeric_year = int(year)
    except ValueError:
        numeric_year = 0

    return (-numeric_year, entry.get("author", ""), entry.get("title", ""))


def year_anchor(year: str) -> str:
    safe_year = re.sub(r"[^0-9A-Za-z_-]+", "-", year.strip().lower()).strip("-")
    if not safe_year:
        safe_year = "unknown"
    return f"publication-year-{safe_year}"


def format_entry(entry: dict[str, str], anchor_id: str | None = None) -> str:
    year = entry.get("year", "n.d.")
    authors = format_authors(entry.get("author", ""))
    title = entry.get("title", "Untitled")
    venue = publication_venue(entry)
    pages = publication_pages(entry)
    link = publication_link(entry)

    details = ". ".join(part for part in [venue, pages, link] if part)
    citation = f"{authors}. \"{title}.\""
    if details:
        citation = f"{citation} {details}."

    entry_block = "::: {.publication-entry}"
    if anchor_id:
        entry_block = f"::: {{#{anchor_id} .publication-entry}}"

    return "\n".join(
        [
            entry_block,
            f"[{year}]{{.publication-year}}",
            "",
            f"{citation}",
            ":::",
        ]
    )


def render_year_nav(years: list[str]) -> str:
    if not years:
        return ""

    links = " ".join(
        f"[{year}](#{year_anchor(year)}){{.publication-year-link}}" for year in years
    )

    return "\n".join(
        [
            "::: {.publication-year-nav}",
            f"[Jump to year]{{.publication-year-nav-label}} {links}",
            ":::",
            "",
        ]
    )


def render(entries: list[dict[str, str]]) -> str:
    ordered = sorted(entries, key=sort_key)
    seen_years: set[str] = set()
    years: list[str] = []
    rendered_entries: list[str] = []

    for entry in ordered:
        year = entry.get("year", "n.d.")
        anchor_id = None

        if year not in seen_years:
            seen_years.add(year)
            years.append(year)
            anchor_id = year_anchor(year)

        rendered_entries.append(format_entry(entry, anchor_id=anchor_id))

    blocks: list[str] = []
    nav = render_year_nav(years).strip()
    if nav:
        blocks.append(nav)

    blocks.extend(
        [
            "::: {.publication-list}",
            "\n\n".join(rendered_entries),
            ":::",
        ]
    )

    return "\n\n".join(blocks) + "\n"


def bibliography_source() -> Path:
    candidates = sorted(path for path in ROOT.parent.glob("*.bib") if path.is_file())
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one bibliography file in {ROOT.parent}, found {len(candidates)}."
        )
    return candidates[0]


def main() -> None:
    raw = bibliography_source().read_text(encoding="utf-8")
    entries = parse_entries(raw)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(render(entries), encoding="utf-8")


if __name__ == "__main__":
    main()
