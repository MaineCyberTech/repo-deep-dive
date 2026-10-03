# Final Risk Register, Roadmap, and Patch Plan

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: FINAL
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/22_final_risk_register_roadmap.md
- Scope limitations: synthesis of the domain reports; no new external evidence.

## Scope

Aggregate all findings into one risk register, roadmap, patch plan, validation plan, and definition of done. Duplicates were merged; each finding is placed in exactly one patch set.

## Evidence Reviewed

- All domain reports in this run (INV, ARCH, FEAT, SEC, DATA, API, TEST, CI, SUPPLY, OBS, HYG, EXEC).
- `audit_manifest.json`, `risk_register.md`, `roadmap.md`, `patch_plan.md`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| all report findings | synthesis | aggregate counts | 41 findings, no P0 |
| `tools/risk_score.py` formula | rule | advisory score | 100 − (P1×10 + P2×3) = 100 − 150 → 0 |
| `check_run.sh` | rule | gate inputs | final PASS depends on DATA-P1-002 fix |

## Executive Summary

There is no P0: the pack holds no production data and no runtime service. Nine P1 issues cluster around CI safety (remote root execution, PAT leakage), the data contract (schema + scaffold), CI being unwired, and supply-chain pinning. Twenty P2 and twelve P3 items cover architecture duplication, docs drift, observability, and hygiene. The advisory score floors at 0 because P1 findings dominate; the human gate is **GO WITH CONDITIONS**. The run itself cannot self-certify as complete until the base-manifest defect (DATA-P1-002) is fixed, because `check_run.sh` rejects the scaffolded manifest.

## Inventory

| Severity | Count | Areas |
|---|---:|---|
| P0 | 0 | — |
| P1 | 9 | INV 1, SEC 2, DATA 2, TEST 1, CI 2, SUPPLY 1 |
| P2 | 20 | INV 1, ARCH 2, FEAT 1, SEC 1, API 2, TEST 2, CI 4, SUPPLY 2, OBS 2, HYG 1, FINAL 1, EXEC 1 |
| P3 | 12 | INV 1, FEAT 1, SEC 2, DATA 1, TEST 1, SUPPLY 1, OBS 1, HYG 2, FINAL 1, EXEC 1 |
| **Total** | **41** | |

## Findings

### Finding ID: FINAL-P2-001 - No evidence the toolchain/self-test ran at the audited commit

- Severity: P2
- Confidence: Medium
- Area: FINAL
- Evidence:
  - `tools/self_test.sh` — the end-to-end harness; no CI invokes it (TEST-P1-001)
  - no CI log, `verification_log.md`, or capture for the pack itself at `6cada03`
  - `PACK_DIGEST.txt` regenerated, but that is not an exercise of the tools
- What is happening: The pack's tools are not demonstrably exercised at the current commit.
- Why it matters: "Validation PASS" claims in `runs/INDEX.md` refer to falcon-lab target runs, not to the pack's own tools.
- User / business impact: Consumers cannot tell whether the new deterministic tools work.
- Security / privacy / reliability impact: Unverified tooling.
- Recommended fix: Run `self_test.sh` in CI at the audited SHA and archive the log with the run.
- Suggested validation: A CI artifact shows `RESULT: PASS` at `6cada03`.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: TEST-P1-001
- Status: open

### Finding ID: FINAL-P3-002 - Archived run verdicts and register statuses were not re-verified after two tooling commits

- Severity: P3
- Confidence: Medium
- Area: FINAL
- Evidence:
  - `runs/INDEX.md` line 6 — archived run "verification pass ... 50 verified-fixed / 38 partially-fixed / 176 open"
  - `git log 7bac320..6cada03` — two commits changed tools after the archive
  - no `verification_log.md` at `6cada03` for the pack
- What is happening: Archive statuses predate the newest tooling; no re-verification occurred.
- Why it matters: Verification discipline requires status changes to cite an artifact at the current commit.
- User / business impact: Stale confidence in fixed findings.
- Security / privacy / reliability impact: Low.
- Recommended fix: Mark the archive as bound to its own commit; do not inherit statuses across tooling changes.
- Suggested validation: Archive states its generating SHA.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Findings | Mitigation |
|---|---|---|---|---|---|
| CI supply-chain RCE | P1 | Medium | High | SEC-001, SUPPLY-001, CI-003 | pin + checksum |
| PAT leak via CI logs | P1 | Medium | High | SEC-002 | mask + header auth |
| Run contract invalid | P1 | High | Medium | DATA-001, DATA-002 | align schema/scaffold |
| No enforced QA gate | P1 | High | Medium | CI-001, CI-002, TEST-001 | wire CI + fix path |
| Gate bypass without bash | P2 | High | Medium | ARCH-002 | Python gate/strict default |
| Coverage drift | P2 | Medium | High | ARCH-001 | single-source order |
| Sensitive host export committed | P3 | Medium | Medium | HYG-003 | redact/relocate |
| Silent pipeline failure | P2 | High | Medium | OBS-002, CI-003 | fail closed + alert |

## Recommendations

### Immediate / Release Blocking
- Fix the data contract (DATA-P1-001, DATA-P1-002).
- Pin/checksum CI tools; stop root remote-script execution and token-in-URL (SEC-P1-001/002, SUPPLY-P1-001).

### This Week
- Wire the audit workflow at `.github/workflows/` with `PACK_DIR: .` (CI-P1-001/002).
- Make `run_toolchain.py` strict by default (ARCH-P2-002).

### This Month
- Single-source execution order (ARCH-P2-001); integrate deterministic findings (API-P2-001/002); add standards files (HYG).

### Later / Platform Evolution
- Structured tool logging, SBOM, OIDC/App token, unit tests.

## Patch Plan

No P0 exists, so the P0-only immediate set is empty by design.

| Patch set | Findings | Files | Dependencies | Effort | Verification |
|---|---|---|---|---|---|
| PS-001 (P0 only) | none | — | — | — | — |
| PS-002 Data contract | DATA-P1-001, DATA-P1-002, TEST-P2-003 | `tools/collect_findings.py`, `schemas/findings.schema.json`, `examples/audit_manifest*.json`, `tools/new_run.py`, `tools/self_test.sh` | none | S | schema validate + scaffold `check_run.sh` PASS |
| PS-003 CI workflow hardening | SEC-P1-001, SEC-P1-002, SEC-P2-003, CI-P2-003, CI-P2-004, SUPPLY-P1-001, SUPPLY-P2-002, OBS-P2-002 | `.github/workflows/deep-dive-deterministic.yml`, `.gitleaks.toml`, `.github/dependabot.yml` | none | M | pinned refs; clone-failure log has no token; fixture secret fails |
| PS-004 Wire audit CI | CI-P1-001, CI-P1-002, CI-P2-005, CI-P2-006, TEST-P1-001, TEST-P2-002 | `.github/workflows/audit.yml`, `ci/audit.yml`, `.github/CODEOWNERS` | PS-002 | M | lint/self-test run on PR; P0 fixture fails |
| PS-005 Change control/docs | FEAT-P2-001, FEAT-P3-002 | `CHANGELOG.md`, `VERSION`, `README.md`, `REFERENCE_CARD.md`, manifests | none | S | lint version sync |
| PS-006 Architecture | ARCH-P2-001, ARCH-P2-002 | `tools/run_toolchain.py`, `tools/lint_pack.sh`, manifest examples | none | M | order-set lint; no-bash run fails |
| PS-007 Deterministic integration | API-P2-001, API-P2-002, DATA-P3-003 | `tools/deterministic_checks.py`, `tools/collect_findings.py` | PS-002 | M | dupe gate green; deterministic findings counted |
| PS-008 Hygiene/standards | HYG-P2-001, HYG-P3-002, HYG-P3-003, SUPPLY-P2-003, SUPPLY-P3-004, SEC-P3-004, SEC-P3-005, OBS-P2-001, OBS-P3-003 | `.gitattributes`, `.gitignore`, `LICENSE`, `SECURITY.md`, `PACK_DIGEST.txt`, `runs/**` | none | M | digest complete; portability check |
| PS-009 Binding/inventory | INV-P1-001, INV-P2-002, INV-P3-003 | `inventory.json`, `INDEX.md`, `audit_manifest.json` | none | S | inventory SHA == HEAD |
| PS-010 Verification/tests | TEST-P3-004, FINAL-P2-001, FINAL-P3-002 | `tests/`, CI, `runs/INDEX.md` | PS-004 | M | unit tests + archived PASS log |
| PS-011 Ownership/gate | EXEC-P2-001, EXEC-P3-002 | `.github/CODEOWNERS`, `RELEASE_GATE.md` | PS-002, PS-004 | S | owners resolve; gate cites validated run |

Coverage check: every one of the 41 findings appears in exactly one set.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Seed manifest keys | scaffold passes gate | `examples/audit_manifest.example.json` | `check_run.sh` PASS |
| `PACK_DIR: .` + move workflow | CI runs | `.github/workflows/audit.yml` | green run |
| `sourceReports` integer | schema conformance | `collect_findings.py` | jsonschema pass |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Condition: P0 gate in CI | P1 | CI owner | M | PS-004 |
| Python port of check_run | P2 | maintainer | M | PS-006 |
| SBOM + license gate | P2 | maintainer | M | PS-008 |

## Suggested Tests

- Schema conformance (types), scaffold round-trip, no-bash gate failure, pinned-ref lint, secret fixture failure, deterministic+domain duplicate-ID test, inventory SHA binding.

## Suggested Documentation Updates

- `README.md` (tools, CI, binding), `CHANGELOG.md`, `CONTRIBUTING.md`, `REFERENCE_CARD.md`, add `SECURITY.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is deterministic checks in scope for base edition? | docs/manifests | maintainer intent |
| Is the repo intended public? | license/sensitivity | maintainer intent |

## Appendix

Advisory score: `max(0, 100 − (0×40 + 9×10 + 20×3)) = max(0, 100 − 150) = 0/100` → advisory NO-GO because the formula's P0 rule does not apply but the score floor triggers "GO WITH CONDITIONS" per `risk_score.py` (`P0==0`, score<85). The authoritative gate is `RELEASE_GATE.md`.
