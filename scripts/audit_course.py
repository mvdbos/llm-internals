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
        self.tag_counts: Counter[str] = Counter()
        self.hrefs: list[str] = []
        self.anchors: list[tuple[str, str]] = []
        self.glossary_hrefs: list[str] = []
        self.footer_hrefs: list[str] = []
        self.tables: list[dict[str, object]] = []
        self.button_types: list[str | None] = []
        self.quizzes: list[dict[str, object]] = []
        self.script_srcs: list[str] = []
        self.inline_script_parts: list[str] = []
        self.course_nav_wrong_tags: list[str] = []
        self.nav_groups: list[list[str]] = []
        self.unexplained_overflow_waivers = 0
        self.dt_ids: list[str | None] = []
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self._capture_title = False
        self._capture_h1 = False
        self._capture_inline_script = False
        self._anchor_href: str | None = None
        self._anchor_parts: list[str] = []
        self._footer_depth = 0
        self._current_table: dict[str, object] | None = None
        self._quiz_depth = 0
        self._current_quiz: dict[str, object] | None = None
        self._nav_depth = 0
        self._current_nav: list[str] | None = None
        self.is_redirect = False

    @property
    def title_text(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1_text(self) -> str:
        return " ".join("".join(self.h1_parts).split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.tag_counts[tag] += 1
        if "data-overflow-waiver" in values and not (
            values.get("data-overflow-explanation") or ""
        ).strip():
            self.unexplained_overflow_waivers += 1
        if tag == "body" and values.get("data-course-redirect") == "true":
            self.is_redirect = True
        if tag == "script":
            if values.get("src"):
                self.script_srcs.append(values["src"] or "")
            else:
                self._capture_inline_script = True
        if tag == "table":
            self._current_table = {
                "caption": False,
                "thead": False,
                "tbody": False,
                "th_scopes": [],
            }
            self.tables.append(self._current_table)
        elif self._current_table is not None:
            if tag in {"caption", "thead", "tbody"}:
                self._current_table[tag] = True
            elif tag == "th":
                scopes = self._current_table["th_scopes"]
                assert isinstance(scopes, list)
                scopes.append(values.get("scope"))
        classes = set((values.get("class") or "").split())
        if "course-nav" in classes and tag != "nav":
            self.course_nav_wrong_tags.append(tag)
        if self._nav_depth:
            self._nav_depth += 1
        elif tag == "nav":
            self._nav_depth = 1
            self._current_nav = []
            self.nav_groups.append(self._current_nav)
        if tag == "button":
            self.button_types.append(values.get("type"))
        if self._quiz_depth:
            self._quiz_depth += 1
        elif tag == "fieldset" and "data-quiz" in values:
            self._quiz_depth = 1
            self._current_quiz = {"correct": 0, "feedback_live": False}
            self.quizzes.append(self._current_quiz)
        if self._current_quiz is not None:
            if (
                tag == "button"
                and "quiz-option" in classes
                and values.get("data-correct") == "true"
            ):
                correct = self._current_quiz["correct"]
                assert isinstance(correct, int)
                self._current_quiz["correct"] = correct + 1
            if "quiz-feedback" in classes and (
                values.get("role") == "status" or values.get("aria-live") == "polite"
            ):
                self._current_quiz["feedback_live"] = True
        if self._footer_depth:
            self._footer_depth += 1
        elif "terms-footer" in classes:
            self._footer_depth = 1
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "dt":
            self.dt_ids.append(values.get("id"))
        if tag == "title":
            self._capture_title = True
        elif tag == "h1":
            self._capture_h1 = True
        elif tag == "a" and values.get("href"):
            href = values["href"] or ""
            self.hrefs.append(href)
            if "glossary-link" in classes:
                self.glossary_hrefs.append(href)
            if self._footer_depth:
                self.footer_hrefs.append(href)
            if self._current_nav is not None:
                self._current_nav.append(href)
            self._anchor_href = href
            self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self.title_parts.append(data)
        if self._capture_h1:
            self.h1_parts.append(data)
        if self._capture_inline_script:
            self.inline_script_parts.append(data)
        if self._anchor_href is not None:
            self._anchor_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._capture_title = False
        elif tag == "h1":
            self._capture_h1 = False
        elif tag == "script":
            self._capture_inline_script = False
        elif tag == "a" and self._anchor_href is not None:
            text = " ".join("".join(self._anchor_parts).split())
            self.anchors.append((self._anchor_href, text))
            self._anchor_href = None
            self._anchor_parts = []
        if self._footer_depth:
            self._footer_depth -= 1
        if self._quiz_depth:
            self._quiz_depth -= 1
            if self._quiz_depth == 0:
                self._current_quiz = None
        if self._nav_depth:
            self._nav_depth -= 1
            if self._nav_depth == 0:
                self._current_nav = None
        if tag == "table":
            self._current_table = None


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
    index_cards: dict[str, str] = {}
    if index:
        for href, text in index.anchors:
            if href not in index_cards or re.search(
                r"~\s*\d+\s*min", text, flags=re.IGNORECASE
            ):
                index_cards[href] = text
    issues: list[Issue] = []

    lessons = data.get("lessons", [])
    published_lessons = [
        lesson
        for lesson in lessons
        if not (allow_planned_lessons and lesson.get("status") == "planned")
    ]
    for position, lesson in enumerate(published_lessons):
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

        expected_nav_targets = {(root / "index.html").resolve()}
        if position > 0:
            expected_nav_targets.add(
                (root / published_lessons[position - 1]["path"]).resolve()
            )
        if position + 1 < len(published_lessons):
            expected_nav_targets.add(
                (root / published_lessons[position + 1]["path"]).resolve()
            )
        nav_targets = []
        for nav_group in page.nav_groups:
            normalized = {
                target[0]
                for href in nav_group
                if (target := _local_target(lesson_path, href)) is not None
            }
            nav_targets.append(normalized)
        if len(nav_targets) != 2 or any(
            targets != expected_nav_targets for targets in nav_targets
        ):
            issues.append(
                Issue(
                    "lesson-navigation-mismatch",
                    relative_path,
                    "top and bottom navigation must match manifest Previous/Home/Next targets",
                )
            )

    return issues


def audit_workspace(root: Path, *, allow_planned_lessons: bool = False) -> list[Issue]:
    """Return deterministic structural issues for every HTML file below root."""
    root = root.resolve()
    pages = sorted(root.rglob("*.html"))
    parsed_pages = {page.resolve(): _parse_page(page) for page in pages}
    issues: list[Issue] = []

    glossary_path = (root / "reference" / "glossary.html").resolve()
    glossary = parsed_pages.get(glossary_path)
    if glossary:
        for position, term_id in enumerate(glossary.dt_ids, start=1):
            if not term_id:
                issues.append(
                    Issue(
                        "glossary-term-missing-id",
                        Path("reference/glossary.html"),
                        f"glossary <dt> number {position} has no id",
                    )
                )
        for term_id, count in Counter(glossary.dt_ids).items():
            if term_id and count > 1:
                issues.append(
                    Issue(
                        "glossary-anchor-shared",
                        Path("reference/glossary.html"),
                        f"glossary term id {term_id!r} is shared by {count} entries",
                    )
                )

    for source in pages:
        source_resolved = source.resolve()
        page = parsed_pages[source_resolved]
        if not page.is_redirect and page.tag_counts["main"] != 1:
            issues.append(
                Issue(
                    "main-landmark-count",
                    source.relative_to(root),
                    f"expected exactly one <main>, found {page.tag_counts['main']}",
                )
            )
        if not page.is_redirect:
            if page.unexplained_overflow_waivers:
                issues.append(
                    Issue(
                        "overflow-waiver-unexplained",
                        source.relative_to(root),
                        "overflow waiver requires data-overflow-explanation",
                    )
                )
            if page.course_nav_wrong_tags:
                issues.append(
                    Issue(
                        "navigation-not-nav",
                        source.relative_to(root),
                        "course-nav class must be placed on a <nav> element",
                    )
                )
            for number, table in enumerate(page.tables, start=1):
                for part in ("caption", "thead", "tbody"):
                    if not table[part]:
                        issues.append(
                            Issue(
                                f"table-missing-{part}",
                                source.relative_to(root),
                                f"table {number} has no <{part}>",
                            )
                        )
                scopes = table["th_scopes"]
                assert isinstance(scopes, list)
                if any(
                    scope not in {"col", "row", "colgroup", "rowgroup"}
                    for scope in scopes
                ):
                    issues.append(
                        Issue(
                            "table-th-missing-scope",
                            source.relative_to(root),
                            f"table {number} has an unscoped <th>",
                        )
                    )
            if any(button_type != "button" for button_type in page.button_types):
                issues.append(
                    Issue(
                        "button-missing-type",
                        source.relative_to(root),
                        "every <button> must declare type=\"button\"",
                    )
                )
            for number, quiz in enumerate(page.quizzes, start=1):
                if quiz["correct"] != 1:
                    issues.append(
                        Issue(
                            "quiz-correct-count",
                            source.relative_to(root),
                            f"quiz {number} has {quiz['correct']} correct options",
                        )
                    )
                if not quiz["feedback_live"]:
                    issues.append(
                        Issue(
                            "quiz-feedback-not-live",
                            source.relative_to(root),
                            f"quiz {number} feedback lacks role=status or aria-live=polite",
                        )
                    )
            relative_source = source.relative_to(root)
            if relative_source.parts and relative_source.parts[0] == "lessons":
                if page.quizzes and "../assets/quiz.js" not in page.script_srcs:
                    issues.append(
                        Issue(
                            "quiz-shared-script-missing",
                            relative_source,
                            "lesson quizzes must load ../assets/quiz.js",
                        )
                    )
                if "checkAnswer" in "".join(page.inline_script_parts):
                    issues.append(
                        Issue(
                            "quiz-inline-handler",
                            relative_source,
                            "lesson contains an inline checkAnswer implementation",
                        )
                    )
        glossary_targets = [
            target
            for href in parsed_pages[source_resolved].glossary_hrefs
            if (target := _local_target(source_resolved, href)) is not None
        ]
        footer_targets = {
            target
            for href in parsed_pages[source_resolved].footer_hrefs
            if (target := _local_target(source_resolved, href)) is not None
        }
        glossary_term_ids = set(glossary.dt_ids) if glossary else set()
        for target_path, fragment in sorted(
            set(glossary_targets), key=lambda item: (str(item[0]), item[1])
        ):
            if target_path == glossary_path and fragment not in glossary_term_ids:
                issues.append(
                    Issue(
                        "glossary-target-not-term",
                        source.relative_to(root),
                        f"glossary link targets non-term fragment {fragment!r}",
                    )
                )
        missing_footer_targets = set(glossary_targets) - footer_targets
        for target in sorted(missing_footer_targets, key=lambda item: (str(item[0]), item[1])):
            issues.append(
                Issue(
                    "glossary-footer-missing",
                    source.relative_to(root),
                    f"inline glossary target {target[1]!r} is missing from terms footer",
                )
            )
        extra_footer_targets = footer_targets - set(glossary_targets)
        for target in sorted(extra_footer_targets, key=lambda item: (str(item[0]), item[1])):
            issues.append(
                Issue(
                    "glossary-footer-extra",
                    source.relative_to(root),
                    f"terms footer target {target[1]!r} has no inline glossary link",
                )
            )
        for target, count in Counter(glossary_targets).items():
            if count > 1:
                issues.append(
                    Issue(
                        "glossary-link-duplicate",
                        source.relative_to(root),
                        f"glossary target {target[1]!r} is linked {count} times inline",
                    )
                )
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
