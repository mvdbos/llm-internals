from pathlib import Path
from tempfile import TemporaryDirectory
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


if __name__ == "__main__":
    unittest.main()
