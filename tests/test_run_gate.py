"""Tests for tools/run_gate.py: the changed-run gate blocks only UNRESOLVED findings.

Regression for EXEC-P1-001-class bug in CI: a run with a historical, now
verified-fixed P0/P1 must be able to pass; a live open P0/P1 must still block.
"""

import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import run_gate  # noqa: E402


def _write_run(tmp, findings):
    d = pathlib.Path(tempfile.mkdtemp(dir=tmp))
    (d / "findings.json").write_text(
        json.dumps({"run": "demo", "counts": {}, "findings": findings}),
        encoding="utf-8")
    return str(d)


class GateBlockersTest(unittest.TestCase):
    def test_resolved_statuses_do_not_block(self):
        for status in ("verified-fixed", "owner-accepted", "false-positive"):
            f = [{"id": "OBS-P0-001", "severity": "P0", "status": status}]
            self.assertEqual(run_gate.gate_blockers(f, ["P0"]), [], status)

    def test_unresolved_statuses_block(self):
        for status in ("open", "still-open", "partially-fixed", "regressed", ""):
            f = [{"id": "OBS-P0-001", "severity": "P0", "status": status}]
            self.assertEqual(len(run_gate.gate_blockers(f, ["P0"])), 1, status)

    def test_severity_outside_the_gate_is_ignored(self):
        f = [{"id": "X-P2-001", "severity": "P2", "status": "open"}]
        self.assertEqual(run_gate.gate_blockers(f, ["P0", "P1"]), [])


class GateMainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _run(self, findings, severities="P0,P1"):
        return run_gate.main([_write_run(self.tmp.name, findings),
                              "--severities", severities])

    def test_verified_fixed_p0_passes(self):
        self.assertEqual(self._run(
            [{"id": "OBS-P0-001", "severity": "P0", "status": "verified-fixed"}]), 0)

    def test_open_p0_fails(self):
        self.assertEqual(self._run(
            [{"id": "OBS-P0-001", "severity": "P0", "status": "open"}]), 1)

    def test_owner_accepted_p1_passes(self):
        self.assertEqual(self._run(
            [{"id": "ARCH-P1-001", "severity": "P1", "status": "owner-accepted"}]), 0)

    def test_partially_fixed_p1_fails(self):
        self.assertEqual(self._run(
            [{"id": "API-P1-001", "severity": "P1", "status": "partially-fixed"}]), 1)

    def test_mixed_run_blocks_on_the_live_finding(self):
        self.assertEqual(self._run([
            {"id": "OBS-P0-001", "severity": "P0", "status": "verified-fixed"},
            {"id": "API-P1-001", "severity": "P1", "status": "partially-fixed"},
        ]), 1)

    def test_missing_findings_json_fails_closed(self):
        missing = str(pathlib.Path(self.tmp.name) / "does-not-exist")
        self.assertEqual(run_gate.main([missing]), 2)

    def test_gate_severities_can_be_narrowed_to_p0(self):
        self.assertEqual(self._run(
            [{"id": "API-P1-001", "severity": "P1", "status": "open"}],
            severities="P0"), 0)


if __name__ == "__main__":
    unittest.main()
