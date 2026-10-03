# Patch Plan — repo-deep-dive

Run: 20261003-0018-main-7bac320 · 41 findings · No P0 (PS-001 empty by design).
Every finding lands in exactly one patch set.

## PS-001 — P0 only (immediate)

_Empty: there are no P0 findings._ No dependencies.

## PS-002 — Data contract alignment

- Findings: DATA-P1-001, DATA-P1-002, TEST-P2-003
- Files: `tools/collect_findings.py`, `schemas/findings.schema.json`, `examples/audit_manifest.example.json`, `examples/audit_manifest.falcon-lab.example.json`, `tools/new_run.py`, `tools/self_test.sh`
- Dependencies: none · Effort: S
- Verification: `python3 tools/new_run.py --run t --root $TMP && tools/check_run.sh $TMP/repo-deep-dive/t` prints `PASS`; schema type validation green.

## PS-003 — CI workflow hardening

- Findings: SEC-P1-001, SEC-P1-002, SEC-P2-003, CI-P2-003, CI-P2-004, SUPPLY-P1-001, SUPPLY-P2-002, OBS-P2-002
- Files: `.github/workflows/deep-dive-deterministic.yml`, `.gitleaks.toml`, `.github/dependabot.yml`
- Dependencies: none · Effort: M
- Verification: every `uses:` pinned to a commit SHA; tool downloads versioned+sha256; clone failure logs contain no token; fixture secret fails the job.

## PS-004 — Wire the audit CI

- Findings: CI-P1-001, CI-P1-002, CI-P2-005, CI-P2-006, TEST-P1-001, TEST-P2-002
- Files: `.github/workflows/audit.yml` (moved from `ci/audit.yml`), `ci/audit.yml`, `.github/CODEOWNERS`
- Dependencies: PS-002 · Effort: M
- Verification: PR runs `lint_pack.sh` + `self_test.sh`; a P0 fixture run fails the P0 gate; required checks block merge.

## PS-005 — Change control and docs

- Findings: FEAT-P2-001, FEAT-P3-002
- Files: `CHANGELOG.md`, `VERSION`, `README.md`, `REFERENCE_CARD.md`, example/profile manifests
- Dependencies: none · Effort: S
- Verification: `lint_pack.sh` version-sync green; new capabilities named in CHANGELOG.

## PS-006 — Architecture: single source + strict gate

- Findings: ARCH-P2-001, ARCH-P2-002
- Files: `tools/run_toolchain.py`, `tools/lint_pack.sh`, `examples/*.json`, `profiles/falcon-lab.manifest.json`
- Dependencies: none · Effort: M
- Verification: execution-order set equals prompt-number set; run without bash fails unless `--no-check`.

## PS-007 — Deterministic findings integration

- Findings: API-P2-001, API-P2-002, DATA-P3-003
- Files: `tools/deterministic_checks.py`, `tools/collect_findings.py`
- Dependencies: PS-002 · Effort: M
- Verification: deterministic + domain reports coexist without duplicate IDs; deterministic findings counted by `collect_findings.py`; real line numbers; ASCII separator.

## PS-008 — Hygiene and standards

- Findings: HYG-P2-001, HYG-P3-002, HYG-P3-003, SUPPLY-P2-003, SUPPLY-P3-004, SEC-P3-004, SEC-P3-005, OBS-P2-001, OBS-P3-003
- Files: `.gitattributes`, `.gitignore`, `LICENSE`, `SECURITY.md`, `PACK_DIGEST.txt`, `runs/**`
- Dependencies: none · Effort: M
- Verification: digest covers the tracked tree; portability check green; sensitive-archive policy documented.

## PS-009 — Run binding and inventory

- Findings: INV-P1-001, INV-P2-002, INV-P3-003
- Files: `inventory.json`, `INDEX.md`, `audit_manifest.json`
- Dependencies: none · Effort: S
- Verification: `inventory.json.git.sha == git rev-parse --short HEAD`.

## PS-010 — Verification and tests

- Findings: TEST-P3-004, FINAL-P2-001, FINAL-P3-002
- Files: `tests/`, `.github/workflows/`, `runs/INDEX.md`
- Dependencies: PS-004 · Effort: M
- Verification: unit tests green; archived `self_test.sh` PASS log at the audited SHA; each archived run states its generating SHA.

## PS-011 — Ownership and gate

- Findings: EXEC-P2-001, EXEC-P3-002
- Files: `.github/CODEOWNERS`, `RELEASE_GATE.md`
- Dependencies: PS-002, PS-004 · Effort: S
- Verification: every finding maps to an owner; gate cites a machine-validated run.

## Coverage

PS-002 (3) · PS-003 (8) · PS-004 (6) · PS-005 (2) · PS-006 (2) · PS-007 (3) · PS-008 (9) · PS-009 (3) · PS-010 (3) · PS-011 (2) = **41 findings**, no overlaps.
