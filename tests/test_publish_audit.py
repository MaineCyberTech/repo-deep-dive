"""Tests for tools/publish_audit.py: pre-publish secret scan (repo-deep-dive-SEC-002)."""

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import publish_audit as pub  # noqa: E402


class ScanSecretsTest(unittest.TestCase):
    def test_detects_high_confidence_secrets(self):
        files = {
            "FINDINGS.md": "\n".join([
                "aws: AKIAIOSFODNN7EXAMPLE",
                "gh: ghp_" + "A" * 36,
                "-----BEGIN RSA PRIVATE KEY-----",
                'password = "correcthorsebattery123"',
            ]),
        }
        rules = {h[2] for h in pub.scan_secrets(files)}
        self.assertIn("aws-access-key-id", rules)
        self.assertIn("github-token", rules)
        self.assertIn("private-key", rules)
        self.assertIn("generic-assigned-secret", rules)

    def test_never_leaks_the_value(self):
        files = {"findings.json": '{"token": "ghp_' + "B" * 36 + '"}'}
        hits = pub.scan_secrets(files)
        self.assertTrue(hits)
        for _, _, _, red in hits:
            self.assertNotIn("B" * 10, red)
            self.assertIn("redacted", red)

    def test_allows_documented_placeholders_and_false_positives(self):
        files = {"pr_body.md": "\n".join([
            "token=abcdef1234567890",
            "value = <YOUR_LOCAL_PRIVATE_KEY>",
            "gitleaks generic-api-key false positive",
            "manifest digest sha256: " + "a" * 64,
        ])}
        self.assertEqual(pub.scan_secrets(files), [])

    def test_manifest_digest_keys_are_not_generic_secrets(self):
        files = {"pkg.json": '"repo-deep-dive/abc1234/x.md": "%s"' % ("c" * 64)}
        self.assertEqual(pub.scan_secrets(files), [])


class PublishFailClosedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = pathlib.Path(self.tmp.name) / "src"
        self.src.mkdir()
        self.pack = pathlib.Path(self.tmp.name) / "runs"
        self.pack.mkdir()

    def _argv(self):
        return ["publish_audit.py", "--repo", "demo", "--branch", "main",
                "--sha", "a" * 40, "--source-dir", str(self.src),
                "--pack-dir", str(self.pack), "--no-pr"]

    def _write_source(self, findings):
        (self.src / "findings.json").write_text(
            json.dumps({"findings": findings}), encoding="utf-8")

    def test_refuses_when_evidence_contains_a_secret(self):
        self._write_source([{
            "id": "x", "severity": "P2", "area": "SEC", "title": "leak",
            "evidence": ["config shows AKIAIOSFODNN7EXAMPLE"],
        }])
        with mock.patch.object(sys, "argv", self._argv()):
            rc = pub.main()
        self.assertEqual(rc, 2)
        # Fail closed: nothing was written into the pack runs dir.
        self.assertEqual(list(self.pack.iterdir()), [])

    def test_publishes_clean_run_and_records_scan(self):
        self._write_source([{
            "id": "x", "severity": "P3", "area": "DOC", "title": "docs",
            "evidence": ["README.md:1"],
        }])
        with mock.patch.object(sys, "argv", self._argv()):
            rc = pub.main()
        self.assertEqual(rc, 0)
        dest = next(self.pack.glob("demo-*"))
        manifest = json.loads((dest / "audit_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["secretScan"]["result"], "pass")


class PublishGateTest(unittest.TestCase):
    """EXEC-P1-001: the release gate must be able to return NO-GO for a P0."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = pathlib.Path(self.tmp.name) / "src"
        self.src.mkdir()
        self.pack = pathlib.Path(self.tmp.name) / "runs"
        self.pack.mkdir()

    def _publish(self, findings):
        (self.src / "findings.json").write_text(
            json.dumps({"findings": findings}), encoding="utf-8")
        argv = ["publish_audit.py", "--repo", "demo", "--branch", "main",
                "--sha", "a" * 40, "--source-dir", str(self.src),
                "--pack-dir", str(self.pack), "--no-pr"]
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(pub.main(), 0)
        dest = next(self.pack.glob("demo-*"))
        return (dest / "RELEASE_GATE.md").read_text(encoding="utf-8")

    def test_p0_yields_no_go(self):
        gate = self._publish([{"id": "x", "severity": "P0", "area": "SEC",
                               "title": "critical", "evidence": ["README.md:1"]}])
        self.assertIn("NO-GO", gate)
        self.assertNotIn("Verdict: **GO", gate)

    def test_p1_yields_go_with_conditions(self):
        gate = self._publish([{"id": "x", "severity": "P1", "area": "SEC",
                               "title": "high", "evidence": ["README.md:1"]}])
        self.assertIn("GO WITH CONDITIONS", gate)


if __name__ == "__main__":
    unittest.main()
