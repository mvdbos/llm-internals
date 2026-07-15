from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

from scripts.audit_course import audit_workspace


class CourseAuditTests(unittest.TestCase):
    def test_reports_missing_local_fragment(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<a href="reference.html#missing">broken</a>',
                encoding="utf-8",
            )
            (root / "reference.html").write_text(
                '<h1 id="present">Reference</h1>',
                encoding="utf-8",
            )
            issues = audit_workspace(root)
            self.assertTrue(any(i.code == "broken-fragment" for i in issues))

    def test_reports_missing_local_file(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<a href="missing.html">broken</a>',
                encoding="utf-8",
            )
            issues = audit_workspace(root)
            self.assertTrue(any(i.code == "broken-file" for i in issues))

    def test_reports_duplicate_id(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<h1 id="same">One</h1><h2 id="same">Two</h2>',
                encoding="utf-8",
            )
            issues = audit_workspace(root)
            self.assertTrue(any(i.code == "duplicate-id" for i in issues))

    def test_cli_prints_issues_and_exits_one(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<a href="missing.html">broken</a>',
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-m", "scripts.audit_course", str(root)],
                cwd=Path(__file__).parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("broken-file", result.stdout)

    def test_manifest_reports_missing_lesson_title_and_duration(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lessons").mkdir()
            (root / "lessons" / "one.html").write_text(
                "<title>Wrong title</title><h1>Wrong heading</h1>",
                encoding="utf-8",
            )
            (root / "index.html").write_text(
                '<a href="lessons/one.html">One lesson · ~3 min.</a>',
                encoding="utf-8",
            )
            (root / "course.json").write_text(
                json.dumps(
                    {
                        "title": "Course",
                        "lessons": [
                            {
                                "number": 1,
                                "path": "lessons/one.html",
                                "title": "Expected title",
                                "minutes": 8,
                            },
                            {
                                "number": 2,
                                "path": "lessons/missing.html",
                                "title": "Missing lesson",
                                "minutes": 8,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertTrue(
                {
                    "manifest-lesson-missing",
                    "manifest-title-mismatch",
                    "manifest-duration-mismatch",
                }
                <= codes
            )

    def test_manifest_allows_planned_lessons_only_with_explicit_flag(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("<h1>Course</h1>", encoding="utf-8")
            (root / "course.json").write_text(
                json.dumps(
                    {
                        "title": "Course",
                        "lessons": [
                            {
                                "number": 3,
                                "path": "lessons/planned.html",
                                "title": "Planned",
                                "minutes": 8,
                                "status": "planned",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            strict_codes = {issue.code for issue in audit_workspace(root)}
            migration_codes = {
                issue.code
                for issue in audit_workspace(root, allow_planned_lessons=True)
            }
            self.assertIn("manifest-lesson-missing", strict_codes)
            self.assertNotIn("manifest-lesson-missing", migration_codes)

    def test_reports_glossary_term_without_id(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "reference" / "glossary.html").write_text(
                "<dl><dt>Tensor</dt><dd>A grid of numbers.</dd></dl>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("glossary-term-missing-id", codes)

    def test_reports_shared_glossary_term_anchor(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "reference" / "glossary.html").write_text(
                '<dl><dt id="T">Tensor</dt><dt id="T">Token</dt></dl>',
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("glossary-anchor-shared", codes)

    def test_reports_duplicate_inline_glossary_target(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "lessons").mkdir()
            (root / "reference" / "glossary.html").write_text(
                '<dl><dt id="tensor">Tensor</dt></dl>',
                encoding="utf-8",
            )
            (root / "lessons" / "one.html").write_text(
                '<a class="glossary-link" href="../reference/glossary.html#tensor">Tensor</a>'
                '<a class="glossary-link" href="../reference/glossary.html#tensor">tensor</a>',
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("glossary-link-duplicate", codes)

    def test_reports_inline_glossary_target_missing_from_footer(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "lessons").mkdir()
            (root / "reference" / "glossary.html").write_text(
                '<dl><dt id="tensor">Tensor</dt></dl>',
                encoding="utf-8",
            )
            (root / "lessons" / "one.html").write_text(
                '<a class="glossary-link" href="../reference/glossary.html#tensor">Tensor</a>'
                '<div class="terms-footer"></div>',
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("glossary-footer-missing", codes)

    def test_reports_footer_glossary_target_missing_inline(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "lessons").mkdir()
            (root / "reference" / "glossary.html").write_text(
                '<dl><dt id="tensor">Tensor</dt></dl>',
                encoding="utf-8",
            )
            (root / "lessons" / "one.html").write_text(
                '<div class="terms-footer">'
                '<a href="../reference/glossary.html#tensor">Tensor</a>'
                "</div>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("glossary-footer-extra", codes)

    def test_reports_glossary_link_to_letter_heading_instead_of_term(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "lessons").mkdir()
            (root / "reference" / "glossary.html").write_text(
                '<h2 id="T">T</h2><dl><dt id="tensor">Tensor</dt></dl>',
                encoding="utf-8",
            )
            (root / "lessons" / "one.html").write_text(
                '<a class="glossary-link" href="../reference/glossary.html#T">Tensor</a>'
                '<div class="terms-footer">'
                '<a href="../reference/glossary.html#T">Tensor</a>'
                "</div>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("glossary-target-not-term", codes)


if __name__ == "__main__":
    unittest.main()
