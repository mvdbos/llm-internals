from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

from scripts.audit_course import audit_workspace


class CourseAuditTests(unittest.TestCase):
    def test_skips_private_raw_and_job_html(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("<main><h1>Public</h1></main>")
            for relative in (
                Path("case-study/private/private.html"),
                Path("case-study/raw/raw.html"),
                Path("jobs/job.html"),
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<a href="private-secret.html">private</a>')

            issues = audit_workspace(root)

        self.assertFalse(
            any(
                issue.path.parts[:2] in (("case-study", "private"), ("case-study", "raw"))
                or issue.path.parts[:1] == ("jobs",)
                for issue in issues
            )
        )

    def test_tombstone_is_exempt_from_main_landmark_requirement(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lessons").mkdir()
            (root / "lessons" / "withdrawn.html").write_text(
                '<body data-course-tombstone="true"><h1>Withdrawn</h1></body>',
                encoding="utf-8",
            )

            codes = {issue.code for issue in audit_workspace(root)}

        self.assertNotIn("main-landmark-count", codes)

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

    def test_planned_lesson_does_not_extend_published_navigation_in_migration_mode(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lessons").mkdir()
            (root / "index.html").write_text(
                '<main><h1>Course</h1><a href="lessons/one.html">One · ~5 min</a></main>',
                encoding="utf-8",
            )
            lesson_html = (
                '<title>One</title><nav class="course-nav"><a href="../index.html">Home</a></nav>'
                '<main><h1>One</h1></main>'
                '<nav class="course-nav"><a href="../index.html">Home</a></nav>'
            )
            (root / "lessons" / "one.html").write_text(
                lesson_html, encoding="utf-8"
            )
            (root / "course.json").write_text(
                json.dumps(
                    {
                        "title": "Course",
                        "lessons": [
                            {
                                "number": 1,
                                "path": "lessons/one.html",
                                "title": "One",
                                "minutes": 5,
                            },
                            {
                                "number": 2,
                                "path": "lessons/planned.html",
                                "title": "Planned",
                                "minutes": 8,
                                "status": "planned",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            migration_codes = {
                issue.code
                for issue in audit_workspace(root, allow_planned_lessons=True)
            }
            self.assertNotIn("lesson-navigation-mismatch", migration_codes)

    def test_manifest_duration_uses_course_card_when_path_is_linked_more_than_once(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lessons").mkdir()
            (root / "index.html").write_text(
                '<main><h1>Course</h1>'
                '<a href="lessons/one.html">One · ~5 min</a>'
                '<a href="lessons/one.html">Start lesson</a></main>',
                encoding="utf-8",
            )
            lesson_html = (
                '<title>One</title><nav class="course-nav"><a href="../index.html">Home</a></nav>'
                '<main><h1>One</h1></main>'
                '<nav class="course-nav"><a href="../index.html">Home</a></nav>'
            )
            (root / "lessons" / "one.html").write_text(
                lesson_html, encoding="utf-8"
            )
            (root / "course.json").write_text(
                json.dumps(
                    {
                        "title": "Course",
                        "lessons": [
                            {
                                "number": 1,
                                "path": "lessons/one.html",
                                "title": "One",
                                "minutes": 5,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertNotIn("manifest-duration-mismatch", codes)

    def test_reference_glossary_inventory_rejects_missing_required_terms(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "reference" / "glossary.html").write_text(
                "<dl>"
                '<dt id="artifact">Artifact</dt>'
                '<dt id="inference-engine">Inference Engine</dt>'
                '<dt id="parameter">Parameter</dt>'
                '<dt id="activation">Activation</dt>'
                '<dt id="retained-runtime-state">Retained Runtime State</dt>'
                "</dl>",
                encoding="utf-8",
            )
            (root / "reference" / "tensors-and-layers.html").write_text(
                '<main><p>A parameter and activation are runtime state.</p>'
                '<a class="glossary-link" href="glossary.html#artifact">Artifact</a>'
                '<div class="terms-footer">'
                '<a href="glossary.html#artifact">Artifact</a>'
                "</div></main>",
                encoding="utf-8",
            )

            issues = audit_workspace(root)

        missing = {
            issue.detail
            for issue in issues
            if issue.code == "glossary-required-link-missing"
        }
        self.assertIn("required glossary target 'parameter' has no inline link", missing)
        self.assertIn("required glossary target 'activation' has no inline link", missing)
        self.assertIn(
            "required glossary target 'retained-runtime-state' has no inline link",
            missing,
        )

    def test_requires_reference_pages_to_use_glossary_contract(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            (root / "reference" / "glossary.html").write_text(
                '<main><dl><dt id="tensor">Tensor</dt></dl></main>',
                encoding="utf-8",
            )
            (root / "reference" / "concept.html").write_text(
                "<main><p>A tensor contains values.</p></main>",
                encoding="utf-8",
            )

            codes = {issue.code for issue in audit_workspace(root)}

        self.assertIn("reference-glossary-contract-absent", codes)

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

    def test_requires_exactly_one_main_on_non_redirect_page(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                "<html><body><h1>No main</h1></body></html>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("main-landmark-count", codes)

    def test_requires_semantic_table_structure(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                "<main><table><tr><th>Heading</th><td>Value</td></tr></table></main>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertTrue(
                {
                    "table-missing-caption",
                    "table-missing-thead",
                    "table-missing-tbody",
                    "table-th-missing-scope",
                }
                <= codes
            )

    def test_requires_button_and_quiz_semantics(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                "<main>"
                '<fieldset class="quiz-question" data-quiz>'
                "<legend>Pick one</legend>"
                '<button class="quiz-option" data-correct="true">A</button>'
                '<button class="quiz-option" data-correct="true">B</button>'
                '<p class="quiz-feedback"></p>'
                "</fieldset>"
                "</main>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertTrue(
                {
                    "button-missing-type",
                    "quiz-correct-count",
                    "quiz-feedback-not-live",
                }
                <= codes
            )

    def test_requires_shared_quiz_script_and_forbids_inline_handler(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lessons").mkdir()
            (root / "lessons" / "one.html").write_text(
                "<main>"
                '<fieldset data-quiz><legend>Pick</legend>'
                '<button type="button" class="quiz-option" data-correct="true">A</button>'
                '<p class="quiz-feedback" aria-live="polite"></p>'
                "</fieldset>"
                "<script>function checkAnswer() { return true; }</script>"
                "</main>",
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertTrue(
                {"quiz-shared-script-missing", "quiz-inline-handler"} <= codes
            )

    def test_requires_course_navigation_to_use_nav_element(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<main><div class="course-nav"><a href="index.html">Home</a></div></main>',
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("navigation-not-nav", codes)

    def test_manifest_requires_matching_top_and_bottom_lesson_navigation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lessons").mkdir()
            (root / "index.html").write_text(
                '<main><a href="lessons/one.html">One · ~5 min.</a></main>',
                encoding="utf-8",
            )
            (root / "lessons" / "one.html").write_text(
                "<title>Lesson 1: One</title>"
                '<nav class="course-nav"><a href="../index.html">Home</a></nav>'
                "<main><h1>Lesson 1: One</h1></main>",
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
                                "title": "One",
                                "minutes": 5,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("lesson-navigation-mismatch", codes)

    def test_rejects_unexplained_overflow_waiver(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<main data-overflow-waiver="true">Content</main>',
                encoding="utf-8",
            )
            codes = {issue.code for issue in audit_workspace(root)}
            self.assertIn("overflow-waiver-unexplained", codes)


if __name__ == "__main__":
    unittest.main()
