"""Dependency-free structural audit for the static course."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
import json
from pathlib import Path
import re
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
        self.anchors: list[tuple[str, str]] = []
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self._capture_title = False
        self._capture_h1 = False
        self._anchor_href: str | None = None
        self._anchor_parts: list[str] = []

    @property
    def title_text(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1_text(self) -> str:
        return " ".join("".join(self.h1_parts).split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "title":
            self._capture_title = True
        elif tag == "h1":
            self._capture_h1 = True
        elif tag == "a" and values.get("href"):
            href = values["href"] or ""
            self.hrefs.append(href)
            self._anchor_href = href
            self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self.title_parts.append(data)
        if self._capture_h1:
            self.h1_parts.append(data)
        if self._anchor_href is not None:
            self._anchor_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._capture_title = False
        elif tag == "h1":
            self._capture_h1 = False
        elif tag == "a" and self._anchor_href is not None:
            text = " ".join("".join(self._anchor_parts).split())
            self.anchors.append((self._anchor_href, text))
            self._anchor_href = None
            self._anchor_parts = []


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


def _audit_manifest(
    root: Path,
    parsed_pages: dict[Path, _PageParser],
    *,
    allow_planned_lessons: bool,
) -> list[Issue]:
    manifest_path = root / "course.json"
    if not manifest_path.exists():
        return []

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    index = parsed_pages.get((root / "index.html").resolve())
    index_cards = dict(index.anchors) if index else {}
    issues: list[Issue] = []

    for lesson in data.get("lessons", []):
        if allow_planned_lessons and lesson.get("status") == "planned":
            continue
        relative_path = Path(lesson["path"])
        lesson_path = (root / relative_path).resolve()
        if lesson_path not in parsed_pages:
            issues.append(
                Issue(
                    "manifest-lesson-missing",
                    Path("course.json"),
                    f"lesson {lesson['number']} targets missing {relative_path}",
                )
            )
            continue

        expected_title = str(lesson["title"])
        page = parsed_pages[lesson_path]
        if expected_title not in page.title_text or expected_title not in page.h1_text:
            issues.append(
                Issue(
                    "manifest-title-mismatch",
                    relative_path,
                    f"expected {expected_title!r} in both <title> and <h1>",
                )
            )

        card_text = index_cards.get(relative_path.as_posix(), "")
        duration = re.search(r"~\s*(\d+)\s*min", card_text, flags=re.IGNORECASE)
        if duration is None or int(duration.group(1)) != int(lesson["minutes"]):
            issues.append(
                Issue(
                    "manifest-duration-mismatch",
                    Path("index.html"),
                    f"{relative_path} should show ~{lesson['minutes']} min",
                )
            )

    return issues


def audit_workspace(root: Path, *, allow_planned_lessons: bool = False) -> list[Issue]:
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

    issues.extend(
        _audit_manifest(
            root,
            parsed_pages,
            allow_planned_lessons=allow_planned_lessons,
        )
    )
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.detail))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit static course structure")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--allow-planned-lessons", action="store_true")
    args = parser.parse_args(argv)
    issues = audit_workspace(
        args.root,
        allow_planned_lessons=args.allow_planned_lessons,
    )
    for issue in issues:
        print(f"{issue.path}: {issue.code}: {issue.detail}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
