# Roadmap — repo-deep-dive

Run: 20261003-0018-main-7bac320 · Gate: **GO WITH CONDITIONS**

## 7 days — remove the P1 blockers

1. **PS-002 Data contract** — align `collect_findings.py` `sourceReports` with `schemas/findings.schema.json`; add `profile`/`scope`/`findings` to the base example manifest; add type-checked schema validation to `self_test.sh`. (DATA-P1-001, DATA-P1-002, TEST-P2-003)
2. **PS-003 CI workflow hardening** — pin+checksum actionlint/gitleaks, remove `curl|bash`/`sudo tar`, mask and remove the PAT from the clone URL, add `.gitleaks.toml`, remove `|| true`. (SEC-P1-001, SEC-P1-002, SEC-P2-003, CI-P2-003, CI-P2-004, SUPPLY-P1-001, SUPPLY-P2-002, OBS-P2-002)
3. **PS-004 Wire audit CI** — move `ci/audit.yml` to `.github/workflows/audit.yml`, set `PACK_DIR: .`, add PR trigger, CODEOWNERS, required checks. (CI-P1-001, CI-P1-002, CI-P2-005, CI-P2-006, TEST-P1-001, TEST-P2-002)
4. **PS-009 Binding** — regenerate `inventory.json`/`INDEX.md` at the audited SHA. (INV-P1-001, INV-P2-002, INV-P3-003)

## 30 days — structural hardening

5. **PS-006 Architecture** — single-source execution order + lint set-equality; make `run_toolchain.py` strict by default. (ARCH-P2-001, ARCH-P2-002)
6. **PS-007 Deterministic integration** — namespace deterministic area codes; provide an import path into the run findings flow; fix line numbers/separator. (API-P2-001, API-P2-002, DATA-P3-003)
7. **PS-005 Change control** — backfill CHANGELOG/VERSION/README/REFERENCE_CARD. (FEAT-P2-001, FEAT-P3-002)
8. **PS-008 Hygiene/standards** — add `.gitattributes`, `.gitignore`, `LICENSE`, `SECURITY.md`; reconcile digest; set sensitive-archive policy. (HYG-P2-001, HYG-P3-002, HYG-P3-003, SUPPLY-P2-003, SUPPLY-P3-004, SEC-P3-004, SEC-P3-005, OBS-P2-001, OBS-P3-003)

## 90 days — assurance and scale

9. **PS-010 Verification/tests** — unit tests for `lib_findings`/`repo_inventory`/`deterministic_checks`; archive CI `self_test.sh` PASS; bind archived verdicts to their commit. (TEST-P3-004, FINAL-P2-001, FINAL-P3-002)
10. **PS-011 Ownership/gate** — CODEOWNERS owner mapping; make the gate cite a machine-validated run. (EXEC-P2-001, EXEC-P3-002)
11. Longer-term: SBOM generation, OIDC/GitHub App token for the org scan, structured tool logging.

## Milestones

| Milestone | Exit criteria |
|---|---|
| M1 (7d) | All P1s fixed; audit CI green on PR; scaffold passes `check_run.sh` |
| M2 (30d) | No P2s open; deterministic findings integrated; standards files present |
| M3 (90d) | Unit tests + archived verification; gate machine-validated; advisory score ≥ 85 |
