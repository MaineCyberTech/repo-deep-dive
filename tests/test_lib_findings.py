"""Tests for tools/lib_findings.py: report parsing, register merge, counts."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import lib_findings  # noqa: E402


class ScanReportTest(unittest.TestCase):
    def _report(self, text, name="01_domain.md"):
        d = pathlib.Path(self.tmp.name)
        p = d / name
        p.write_text(text, encoding="utf-8")
        return p

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_heading_hyphen(self):
        p = self._report("### Finding ID: TEST-P1-001 - No CI job runs lint\n")
        found = lib_findings.scan_report(p)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["id"], "TEST-P1-001")
        self.assertEqual(found[0]["severity"], "P1")
        self.assertEqual(found[0]["title"], "No CI job runs lint")
        self.assertEqual(found[0]["line"], 1)

    def test_full_heading_en_dash(self):
        p = self._report("### Finding ID: DATA-P2-002 \u2013 Schema omits types\n")
        found = lib_findings.scan_report(p)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["id"], "DATA-P2-002")
        self.assertEqual(found[0]["title"], "Schema omits types")

    def test_table_row(self):
        p = self._report("| TEST-P3-004 | P3 | No unit tests for parsing |\n")
        found = lib_findings.scan_report(p)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["id"], "TEST-P3-004")
        self.assertEqual(found[0]["severity"], "P3")
        self.assertEqual(found[0]["title"], "No unit tests for parsing")

    def test_non_finding_lines_ignored(self):
        p = self._report("# Heading\n\nSome prose mentioning TEST-P1-001 inline.\n")
        self.assertEqual(lib_findings.scan_report(p), [])


class RunReportsTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.run = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_run_reports_selection(self):
        (self.run / "01_repository_inventory.md").write_text("x", encoding="utf-8")
        (self.run / "lens_security_adversary.md").write_text("x", encoding="utf-8")
        (self.run / "INDEX.md").write_text("x", encoding="utf-8")
        (self.run / "notes.md").write_text("x", encoding="utf-8")
        names = [p.name for p in lib_findings.run_reports(self.run)]
        self.assertEqual(names, ["01_repository_inventory.md",
                                 "lens_security_adversary.md"])

    def test_collect_with_dupes_first_wins(self):
        (self.run / "01_a.md").write_text(
            "### Finding ID: TEST-P1-001 - First\n", encoding="utf-8")
        (self.run / "02_b.md").write_text(
            "### Finding ID: TEST-P1-001 - Second\n"
            "### Finding ID: TEST-P2-002 - Other\n", encoding="utf-8")
        _run, findings, dupes = lib_findings.collect_with_dupes(self.run)
        self.assertEqual({f["id"] for f in findings}, {"TEST-P1-001", "TEST-P2-002"})
        self.assertEqual(dupes["TEST-P1-001"], ["01_a.md", "02_b.md"])
        first = next(f for f in findings if f["id"] == "TEST-P1-001")
        self.assertEqual(first["title"], "First")


class RegisterTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.run = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_fields_by_name(self):
        (self.run / "follow_up_register.md").write_text(
            "| Finding | Owner | Target | Status | Post-audit note |\n"
            "|---|---|---|---|---|\n"
            "| TEST-P3-004 | maintainer | v1.1 | open | add unit tests |\n",
            encoding="utf-8")
        fields = lib_findings.register_fields(self.run)
        self.assertEqual(fields["TEST-P3-004"]["owner"], "maintainer")
        self.assertEqual(fields["TEST-P3-004"]["target"], "v1.1")
        self.assertEqual(fields["TEST-P3-004"]["status"], "open")
        self.assertEqual(fields["TEST-P3-004"]["note"], "add unit tests")

    def test_register_absent_returns_empty(self):
        self.assertEqual(lib_findings.register_fields(self.run), {})

    def test_merge_register_attaches_fields(self):
        (self.run / "follow_up_register.md").write_text(
            "| Finding | Owner | Target | Status | Post-audit note |\n"
            "|---|---|---|---|---|\n"
            "| TEST-P3-004 | maintainer | v1.1 | open | note |\n",
            encoding="utf-8")
        findings = [{"id": "TEST-P3-004", "severity": "P3", "title": "t",
                     "report": "r.md", "line": 1}]
        lib_findings.merge_register(findings, self.run)
        self.assertEqual(findings[0]["status"], "open")
        self.assertEqual(findings[0]["owner"], "maintainer")


class CountsTest(unittest.TestCase):
    def test_counts_by_severity_and_area(self):
        findings = [
            {"id": "TEST-P1-001", "severity": "P1"},
            {"id": "TEST-P1-002", "severity": "P1"},
            {"id": "DATA-P2-001", "severity": "P2"},
        ]
        c = lib_findings.counts(findings)
        self.assertEqual(c["total"], 3)
        self.assertEqual(c["bySeverity"], {"P1": 2, "P2": 1})
        self.assertEqual(c["byArea"], {"DATA": 1, "TEST": 2})


class ComputeGateTest(unittest.TestCase):
    def test_p0_is_never_go(self):
        # EXEC-P1-001: a P0 must yield NO-GO (the shared gate, not just a label).
        self.assertEqual(lib_findings.compute_gate({"bySeverity": {"P0": 1}}), "NO-GO")
        self.assertEqual(lib_findings.compute_gate({"bySeverity": {"P0": 1, "P2": 3}}), "NO-GO")

    def test_p1_is_go_with_conditions_and_clean_is_go(self):
        self.assertEqual(lib_findings.compute_gate({"bySeverity": {"P1": 1}}),
                         "GO WITH CONDITIONS")
        self.assertEqual(lib_findings.compute_gate({"bySeverity": {"P2": 4, "P3": 1}}), "GO")
        self.assertEqual(lib_findings.compute_gate({}), "GO")

    def test_override_wins_but_unknown_fails_closed(self):
        self.assertEqual(lib_findings.compute_gate({"bySeverity": {"P0": 1}}, "GO"), "GO")
        with self.assertRaises(ValueError):
            lib_findings.compute_gate({"bySeverity": {}}, "MAYBE")


if __name__ == "__main__":
    unittest.main()
