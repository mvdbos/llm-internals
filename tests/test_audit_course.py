from pathlib import Path
from tempfile import TemporaryDirectory
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


if __name__ == "__main__":
    unittest.main()
