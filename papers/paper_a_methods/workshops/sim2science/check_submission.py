"""Fail-closed mechanical checks for the final anonymous Sim2Science PDF."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_BYTES = 50 * 1024 * 1024
PLACEHOLDER_PATTERN = re.compile(r"\b(?:PENDING|TODO|TBD)\b", re.IGNORECASE)
LOCAL_PATH_PATTERN = re.compile(r"/(?:Users|home)/[^/\s]+", re.IGNORECASE)
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL_PATTERN = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), check=True, capture_output=True, text=True)


def parse_pdfinfo(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def reference_page(pages: Sequence[str]) -> int | None:
    marker = re.compile(r"(?m)^\s*(?:\d+\s+)?References\s*$")
    for index, page in enumerate(pages, start=1):
        if marker.search(page):
            return index
    return None


def main_text_within_five_pages(pages: Sequence[str]) -> bool:
    marker = re.compile(r"(?m)^\s*(?:\d+\s+)?References\s*$")
    for index, page in enumerate(pages, start=1):
        match = marker.search(page)
        if match is None:
            continue
        if index <= 5:
            return True
        if index == 6:
            return not re.search(r"[A-Za-z0-9]", page[: match.start()])
        return False
    return False


def inspect(pdf: Path, allow_placeholders: bool = False) -> list[Check]:
    if not pdf.is_file():
        return [Check("file exists", False, str(pdf))]
    info = parse_pdfinfo(run(["pdfinfo", str(pdf)]).stdout)
    text = run(["pdftotext", "-layout", str(pdf), "-"]).stdout
    pages = text.split("\f")
    references = reference_page(pages)
    fonts = run(["pdffonts", str(pdf)]).stdout.splitlines()[2:]
    author = info.get("Author", "")
    metadata_anonymous = not author or author.lower().startswith("anonymous")
    placeholders = PLACEHOLDER_PATTERN.findall(text)
    local_paths = LOCAL_PATH_PATTERN.findall(text)
    addresses = IPV4_PATTERN.findall(text)
    emails = EMAIL_PATTERN.findall(text)
    unembedded = [line for line in fonts if re.search(r"\sno\s", line)]
    checks = [
        Check("file size", pdf.stat().st_size < MAX_BYTES, f"{pdf.stat().st_size} bytes"),
        Check("letter page", info.get("Page size", "").startswith("612 x 792 pts"), info.get("Page size", "missing")),
        Check("not encrypted", info.get("Encrypted") == "no", info.get("Encrypted", "missing")),
        Check("anonymous Author metadata", metadata_anonymous, author or "absent"),
        Check(
            "references by page 6 (five-page main-text limit)",
            references is not None and references <= 6,
            str(references),
        ),
        Check(
            "main text ends by page 5",
            main_text_within_five_pages(pages),
            f"references page {references}",
        ),
        Check(
            "no draft placeholders",
            allow_placeholders or not placeholders,
            ", ".join(sorted(set(placeholders))) or "none",
        ),
        Check("no local user paths", not local_paths, ", ".join(local_paths) or "none"),
        Check("no IPv4 addresses", not addresses, ", ".join(addresses) or "none"),
        Check("no email addresses", not emails, ", ".join(emails) or "none"),
        Check("all fonts embedded", not unembedded, f"{len(fonts)} fonts checked"),
    ]
    return checks


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--allow-placeholders", action="store_true", help="draft inspection only")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    checks = inspect(args.pdf, allow_placeholders=args.allow_placeholders)
    print(json.dumps([asdict(check) for check in checks], indent=2))
    if not all(check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
