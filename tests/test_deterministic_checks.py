"""Tests for tools/deterministic_checks.py: CRLF detection, checks, ID stability."""

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import deterministic_checks as det  # noqa: E402


def _collect(fn, root):
    findings = []
    fn(root, lambda area, sev, title, detail, evidence: findings.append(
        {"area": area, "severity": sev, "title": title,
         "detail": detail, "evidence": list(evidence)}))
    return findings


class CrlfDetectionTest(unittest.TestCase):
    def setUp(self):
        if shutil.which("git") is None:
            self.skipTest("git not available")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(["git", "-C", self.root, "config", "user.email", "t@t"],
                       check=True)
        subprocess.run(["git", "-C", self.root, "config", "user.name", "t"],
                       check=True)
        # Commit a CRLF file into the index (as a Windows author would).
        with open(os.path.join(self.root, "a.txt"), "wb") as fh:
            fh.write(b"line1\r\nline2\r\n")
        subprocess.run(["git", "-C", self.root, "add", "a.txt"], check=True)
        subprocess.run(["git", "-C", self.root, "commit", "-qm", "init"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_crlf_in_index_flagged(self):
        findings = _collect(det.check_portability, self.root)
        crlf = [f for f in findings if f["area"] == "PORT"
                and f["severity"] == "P2"]
        self.assertTrue(crlf, "CRLF index file was not flagged: %r" % findings)
        self.assertIn("a.txt", crlf[0]["evidence"])

    def test_missing_gitattributes_flagged(self):
        findings = _collect(det.check_portability, self.root)
        attrs = [f for f in findings if f["area"] == "PORT"
                 and "gitattributes" in f["title"]]
        self.assertTrue(attrs)


class CheckUnitsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_workflows(self):
        findings = _collect(det.check_ci, self.root)
        self.assertEqual([f["area"] for f in findings], ["CI"])
        self.assertIn("No GitHub Actions workflows", findings[0]["title"])

    def test_no_readme(self):
        findings = _collect(det.check_docs, self.root)
        self.assertEqual(findings[0]["area"], "DOC")

    def test_no_license(self):
        findings = _collect(det.check_hygiene, self.root)
        self.assertTrue(any("LICENSE" in f["title"] for f in findings))

    def test_unpinned_action_flagged(self):
        wf = pathlib.Path(self.root) / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text(
            "name: ci\non: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - uses: actions/checkout@v4\n",
            encoding="utf-8")
        findings = _collect(det.check_supply_chain, self.root)
        unpinned = [f for f in findings if "not pinned" in f["title"]]
        self.assertTrue(unpinned, findings)

    def test_pinned_action_ok(self):
        wf = pathlib.Path(self.root) / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text(
            "name: ci\non: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - uses: actions/checkout@"
            "11bd71901bbe5b1630ceea73d27597364c9af683\n",
            encoding="utf-8")
        findings = _collect(det.check_supply_chain, self.root)
        self.assertFalse([f for f in findings if "not pinned" in f["title"]])


class RunChecksTest(unittest.TestCase):
    ID_RE = re.compile(r"^[A-Z]+-P[0-3]-\d{3}$")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_ids_are_well_formed_and_unique(self):
        findings = det.run_checks(self.root)
        self.assertTrue(findings)
        ids = [f["id"] for f in findings]
        self.assertEqual(len(ids), len(set(ids)), "duplicate finding IDs")
        for fid in ids:
            self.assertRegex(fid, self.ID_RE)

    def test_counts_match(self):
        findings = det.run_checks(self.root)
        c = det.counts(findings)
        self.assertEqual(c["total"], len(findings))
        self.assertEqual(sum(c["bySeverity"].values()), len(findings))

    def test_run_is_deterministic(self):
        self.assertEqual(det.run_checks(self.root), det.run_checks(self.root))


if __name__ == "__main__":
    unittest.main()
