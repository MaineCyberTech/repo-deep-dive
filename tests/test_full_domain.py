"""Tests for tools/full_domain.py: domain registry, emit, and aggregate."""

import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import full_domain as fd  # noqa: E402


class RegistryTest(unittest.TestCase):
    def test_fast_is_deterministic_plus_security_supply_chain_ci(self):
        domains = fd.select("fast")
        self.assertEqual(domains[0]["domain"], "deterministic")
        areas = [d["area"] for d in domains]
        self.assertEqual(areas, ["DET", "SEC", "CI", "SC"])

    def test_full_covers_every_master_prompt(self):
        self.assertEqual(len(fd.select("full")), len(fd.master_order()) + 1)


class AggregateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run = str(pathlib.Path(self.tmp.name) / "run")

    def _emit(self, domain, findings):
        src = pathlib.Path(self.tmp.name) / ("%s.json" % domain)
        src.write_text(json.dumps({"findings": findings}), encoding="utf-8")
        self.assertEqual(fd.main(["emit", "--run", self.run, "--domain", domain,
                                  "--input", str(src)]), 0)

    def test_end_to_end_writes_a_consistent_run(self):
        self.assertEqual(fd.main(["init", "--repo", "demo", "--branch", "main",
                                  "--sha", "a" * 40, "--out", self.run,
                                  "--mode", "fast"]), 0)
        self._emit("deterministic", [
            {"id": "DET-P3-001", "severity": "P3", "title": "[SEC] sample",
             "detail": "x"},
        ])
        self._emit("06_security_authz_tenancy_audit.md", [
            {"id": "SEC-P1-001", "severity": "P1", "title": "explicit id",
             "status": "open", "owner": "@sec", "target": "SEC"},
            {"severity": "P2", "title": "assigned id", "status": "open"},
        ])
        self.assertEqual(fd.main(["aggregate", "--run", self.run]), 0)

        run = pathlib.Path(self.run)
        doc = json.loads((run / "findings.json").read_text(encoding="utf-8"))
        ids = [f["id"] for f in doc["findings"]]
        self.assertEqual(ids, ["SEC-P1-001", "SEC-P2-001", "DET-P3-001"])
        self.assertEqual(doc["counts"]["total"], 3)
        self.assertEqual(doc["counts"]["byArea"], {"SEC": 2, "DET": 1})
        # Registers mirror the findings 1:1 and carry the subagent statuses.
        reg = (run / "risk_register.md").read_text(encoding="utf-8")
        for fid in ids:
            self.assertIn("| %s |" % fid, reg)
        # A P1 finding makes the computed gate conditional.
        self.assertIn("GO WITH CONDITIONS",
                      (run / "RELEASE_GATE.md").read_text(encoding="utf-8"))
        for name in ("INDEX.md", "EXECUTIVE_SUMMARY.md", "RELEASE_GATE.md",
                     "risk_register.md", "roadmap.md", "patch_plan.md",
                     "coverage.md", "audit_manifest.json"):
            self.assertTrue((run / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
