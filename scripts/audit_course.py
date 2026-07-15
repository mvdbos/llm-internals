"""Dependency-free structural audit for the static course."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    detail: str


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")


def _parse_page(path: Path) -> _PageParser:
    parser = _PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def _local_target(source: Path, href: str) -> tuple[Path, str] | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:", "javascript:")):
        return None
    target = source if not parsed.path else source.parent / unquote(parsed.path)
    if target.is_dir():
        target /= "index.html"
    return target.resolve(), unquote(parsed.fragment)


def audit_workspace(root: Path) -> list[Issue]:
    """Return deterministic structural issues for every HTML file below root."""
    root = root.resolve()
    pages = sorted(root.rglob("*.html"))
    parsed_pages = {page.resolve(): _parse_page(page) for page in pages}
    issues: list[Issue] = []

    for source in pages:
        source_resolved = source.resolve()
        for element_id, count in Counter(parsed_pages[source_resolved].ids).items():
            if count > 1:
                issues.append(
                    Issue(
                        "duplicate-id",
                        source.relative_to(root),
                        f"id {element_id!r} occurs {count} times",
                    )
                )
        for href in parsed_pages[source_resolved].hrefs:
            target_info = _local_target(source_resolved, href)
            if target_info is None:
                continue
            target, fragment = target_info
            if not target.exists():
                issues.append(
                    Issue(
                        "broken-file",
                        source.relative_to(root),
                        f"{href!r} targets missing file",
                    )
                )
                continue
            if target not in parsed_pages:
                continue
            if fragment and fragment not in parsed_pages[target].ids:
                issues.append(
                    Issue(
                        "broken-fragment",
                        source.relative_to(root),
                        f"{href!r} targets missing fragment {fragment!r}",
                    )
                )

    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.detail))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit static course structure")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args(argv)
    issues = audit_workspace(args.root)
    for issue in issues:
        print(f"{issue.path}: {issue.code}: {issue.detail}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
