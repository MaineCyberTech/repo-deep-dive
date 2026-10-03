# Testing, Quality, and Release Confidence Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab profile v1.0.0, pack v1.2.1)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: falcon-build (`/home/user/falcon-build`, central) + falcon-edge-build (`/home/user/falcon-edge-build`, edge)
- Branch: main (both) · Commit SHA: falcon `8282d3f`; edge `f1c5def` (started at `45dfed0`; +5 commits mid-run, clean)
- Generated at: 2026-09-30 (audit session) · Auditor: testing/quality subagent, read-only
- Area code: TEST
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/09_testing_quality_release_confidence.md`
- Scope limitations: GitHub Actions results could not be fetched (`gh` unavailable, private repo); CI status is verified from workflow definitions + indexed captures and marked `unverified` where a live run would be needed. Root/live tests (docker, nft, wg) were not executed.

## Scope

Reviewed: falcon test estate (`automation/validation/*`, `ledgers/test_execution.csv` = 461 rows, `ci/validate.py`, `.github/workflows/validate.yml`); edge suites (`tests/` 163 tests), `ci/*` checkers, all five workflows, `ledgers/{gate_ledger,test_execution,contradiction_ledger}`, closeout/review docs, evidence captures cited by quality claims. Executed read-only: full edge suite, both static validators, falcon history scan, destructive-helper inspection. Not reviewed: upstream Wazuh/IRIS tests, Pi runtime beyond captures, GitHub-hosted run internals.

## Evidence Reviewed

- Edge: `ci/validate.sh`, `ci/{check_ledger,check_evidence,lint_openapi,secret_scan,check_decisions}.py`, `.github/workflows/*.yml`, `automation/validation/qemu_boot_smoke.sh`
- Edge: `tests/**` (163 `def test_`; suite run locally: `Ran 163 tests in 97.106s — OK`), `src/falcon_agent/queue.py:126-138`, `tests/phase3/test_queue.py:78-84`
- Edge: `ledgers/gate_ledger.csv` (P8-G07:72, P10-G07:88, P10-G02:83), `ledgers/contradiction_ledger.md` C-105, `closeout/REVIEW-2026-09-30.md`, `docs/GITHUB_CI.md:13`
- Edge evidence: `evidence/raw/P10-G02/20260930T022951Z_clean-checkout-replication.out` (FAILED) and `...T025217Z_clean-checkout-replication-v3.out` (green)
- Falcon: `ci/validate.py` + local run (exit 1), `automation/validation/secret_scan_history.sh` + local run (exit 1, 22 findings), `automation/validation/tests/grafana_state_regression.sh`
- Falcon: `ledgers/{test_execution,gate_ledger}.csv` (461/102 rows), `evidence/raw/**/*.meta.json` (462); prior findings `ND-P3-011`, `ND-P2-014`, `ND-P2-003`, `ND-P2-011`, `REV-P3-004/007`, `REV-P2-002`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 -m unittest discover -s tests` (edge) | executed | Suite claim | 163 tests OK, 97.1 s; one ResourceWarning |
| `bash ci/validate.sh` (edge) | executed | "ALL PASS" scope | ALL PASS; no test invocation inside |
| `python3 ci/validate.py` (falcon) | executed | Pre-commit gate | exit 1 — 2 `long_hex` findings in audit run reports |
| `secret_scan_history.sh` (falcon) | executed | History-scan claim | exit 1, 22 findings, `REVIEW_REQUIRED` |
| `/tmp` usage in test ledgers | repo data | Reproducibility | edge 200/313 rows; falcon 66/461 |
| `purge_expired` code+test read | repo | Boundary coverage | No mixed old/fresh test; DELETE uses `now` cutoff |

## Executive Summary

The edge repository has a genuinely useful test estate: 163 unittest checks across crypto, enrollment, agent lifecycle, update apply/rollback, observability and release artifacts, run in CI on Python 3.12/3.13 with actionlint, shellcheck, ruff, gitleaks, zizmor, upstream drift, and a review-package build+verify. The falcon repository's estate is different in kind: 461 evidence-backed live executions in an append-only ledger, but no unit tests and no CI equivalent. The release-confidence problems are about claims versus what runs: `validation: ALL PASS` excludes the suite and the local commit gate does not run tests; the falcon working-tree validator currently fails because 40-hex commit SHAs in audit reports trip the secret scanner; the history scan ends at exit 1 / `REVIEW_REQUIRED` while P1-G06 says scans pass; `purge_expired()` still deletes non-expired items with no boundary test; and most evidence-backed test procedures are `/tmp/opencode` one-offs (edge 64%, falcon 14%). Recommended: split gate wording and run both commands locally, fix scanner false positives, add destructive-helper boundary tests, and move recurring procedures in-repo.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Edge suite | `tests/**` | 163 checks, discovery | Green at HEAD | Low | CI 3.12/3.13 |
| Edge static gate | `ci/validate.sh` | Parsers/OpenAPI/models/ledger/evidence/secret | Green | Medium | Excludes tests |
| Edge CI | `.github/workflows/validate.yml` | Suite + lints + package + drift | Defined | Low–Med | Live run unverified |
| Falcon static CI | `.github/workflows/validate.yml`, `ci/validate.py` | Lints/parsers/pins/ledger/secret | Defined | Medium | No runtime tests |
| Falcon live ledger | `ledgers/test_execution.csv` | 461 evidence-linked executions | Mixed/curated | Medium | 63 FAIL rows kept by design |
| Destructive helpers | `purge_expired`; `disk_guard.sh`; backup prune | Delete queue/EVE/snapshots/archives | Partial | High | See TEST-P2-003 |
| Evidence integrity | `ci/check_evidence.py`; falcon `validate.py` | Hash + index | Green locally | Medium | 264 falcon paths via legacy symlink |
| Coverage | CI job summary | Informational | No threshold | Low | Subprocess paths excluded |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Unit tests | 4 edge / 1 falcon | 163 OK; falcon none | No falcon unit layer | Factor falcon parsers |
| Integration tests | 4 edge / 3 falcon | in-process suites; live scripts | falcon needs root/live | CI-safe subset |
| API tests | 4 edge | enrollment/RBAC/idempotency/skew | No route parity | Contract↔route test |
| E2E | 2 | boot smoke + lab captures | Manual/bounded | Keep + document |
| Component tests | 3 | phase suites | Boundary depth | Extend |
| Visual regression | 0 | none | N/A | N/A |
| Accessibility | 0 | none | N/A | N/A |
| Contract tests | 3 | openapi lint + model drift | Runtime mismatch | Route parity |
| Migration tests | 3 | update apply/recovery | Slot switch blocked | Re-test on capable HW |
| Security tests | 4 | scanners, tamper/replay, RBAC, firewall | History scan failing | Fix scanner |
| Load/failure | 2 | soak smoke; span scripts live | No CI | Stage drills |
| Smoke tests | 3 | boot smoke, probe, pipeline | Bounded/manual | Document scope |

## Detailed Review

- **What runs where:** edge `ci/validate.sh` = static only while `.github/workflows/validate.yml:43` runs the suite on push/PR; falcon `ci/validate.py` = static only with off-repo evidence skipped via `FALCON_EVIDENCE_OPTIONAL=1`.
- **Quality claims/destructive helpers:** P8-G07/P10-G07 + closeout say 161 tests (suite is 163; C-105 OPEN); P10-G02 first capture FAILED, v3 green, gate BLOCKED; `test_age_purge` covers only all-expired; `disk_guard.sh` has no automated test.
- **Reproducibility/CI:** 200/313 edge and 66/461 falcon test rows run `/tmp/opencode` scripts; 264/462 falcon metas use the `/home/user/monitoring-build` symlink (CI skips); edge CI adds actionlint/shellcheck/ruff/gitleaks/zizmor, py3.13, weekly drift, merge-on-green, bounded boot smoke (plan limits R-012).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| TEST-001 | Unit tests | edge `tests/**` | 163; falcon none | No falcon unit layer | P2 | Factor parsers |
| TEST-002 | Integration | in-process + live | Good edge coverage | falcon live-only | P2 | CI-safe subset |
| TEST-004 | E2E | boot smoke/captures | Bounded | Manual | P2 | Document scope |
| TEST-008 | Contract | lint + models | Drift-checked | No route parity | P3 | Add parity test |
| TEST-009 | Migration | update apply/recovery | Rollback tested | Slot switch blocked | P2 | Re-test on HW |
| TEST-010 | Security | scanners/tamper/RBAC | Strong | History scan failing | P2 | Fix scanner |

## Findings

### Finding ID: TEST-P2-001 - "validation: ALL PASS" excludes the test suite; the local commit gate does not run tests
- Severity: P2
- Confidence: High
- Area: TEST / CI execution
- Evidence: `falcon-edge-build/ci/validate.sh` prints `validation: ALL PASS` with no test invocation; `AGENTS.md:16,34` ("`ci/validate.sh` must pass before committing") and `README.md:63-65` list only validate.sh; the suite does run in `.github/workflows/validate.yml:43`; prior ND-P3-011
- What is happening: a local contributor/agent can commit a failing tree; CI catches it only after push.
- Why it matters: release confidence and instructions disagree about what "pass" means; "ALL PASS" captures can be misread as a test pass.
- User / business impact: extra CI round-trips; audit/closeout claims anchored to the wrong command.
- Security / privacy / reliability impact: a red suite can hide behind a green static banner in local captures.
- Recommended fix: add `--with-tests` (or a `make check`) and update AGENTS/README to run validate + suite.
- Suggested validation: run the combined command against a planted failing test; expect non-zero.
- Owner suggestion: edge maintainer
- Effort estimate: S
- Dependencies: none
- Status: partially-fixed (prior ND-P3-011)

### Finding ID: TEST-P2-002 - Falcon secret scanning fails at HEAD: working-tree gate exit 1 and history scan `REVIEW_REQUIRED`
- Severity: P2
- Confidence: High
- Area: TEST / security tests & gate robustness
- Evidence: `python3 ci/validate.py` with the run folder present = exit 1, `FAIL secret scan findings`, 2 `long_hex` (40-hex SHAs) in `docs/audits/.../01_repository_inventory.md:6` and `02_architecture_runtime_topology.md:6`; `secret_scan_history.sh` = exit 1, 22 findings, `REVIEW_REQUIRED` (non-evidence: `automation/wazuh/multi-node/config/wazuh_dashboard/wazuh.yml` empty placeholder, `docs/phase9/review/OWNER_ADOPTION.md`); `ledgers/gate_ledger.csv` P1-G06 claims `history_scan_exit=0, NO_FINDINGS` while `E-P1-G06-612` ends exit 1; `AGENTS.md` rule 5
- What is happening: the repo's gate cannot pass while authorized audit artifacts are present, and the accepted security gate no longer matches the tree.
- Why it matters: the append-only commit flow is blocked or worked around; a failing security test is presented as passing.
- User / business impact: operators cannot run the documented commit flow unchanged.
- Security / privacy / reliability impact: low direct risk (SHAs, empty placeholder), but the gate signal is unreliable and may be ignored.
- Recommended fix: allowlist 40-hex git SHAs in reports and empty redacted assignments; regenerate the history-scan capture; append disposition to P1-G06.
- Suggested validation: scanner fixtures (report SHA, empty placeholder -> PASS; planted secret -> FAIL); validate exits 0.
- Owner suggestion: falcon maintainer
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior ND-P2-003 / REV-P3-004)

### Finding ID: TEST-P2-003 - `purge_expired()` deletes non-expired items and has no mixed-input boundary test
- Severity: P2
- Confidence: High
- Area: TEST / destructive helper coverage
- Evidence: `src/falcon_agent/queue.py:126-138` counts expired rows with `now - max_age_seconds` but DELETEs with `cutoff = iso_now()`; `tests/phase3/test_queue.py:78-84` enqueues only 2020-dated rows so it passes; no caller today (`grep purge_expired` = definition + test); `queue.py` unchanged since 3cdc92b
- What is happening: one call would wipe the whole queue while accounting only expired rows; the missing mixed test hides it.
- Why it matters: the helper is public API and destructive; wiring it into the runner would silently destroy queued telemetry.
- User / business impact: queued telemetry could be destroyed silently once the helper is wired in.
- Security / privacy / reliability impact: potential telemetry data loss (monitoring blind spots).
- Recommended fix: delete with the computed threshold; add empty/all-fresh/mixed/boundary tests incl. loss counters and a concurrency test.
- Suggested validation: `test_purge_expired_keeps_fresh_items` would fail on current code.
- Owner suggestion: edge maintainer
- Effort estimate: S
- Dependencies: none
- Status: still-open (prior ND-P2-014)

### Finding ID: TEST-P2-004 - Most evidence-backed test executions are ephemeral `/tmp/opencode` procedures, not repo tests
- Severity: P2
- Confidence: High
- Area: TEST / reproducibility
- Evidence: edge `ledgers/test_execution.csv` 200/313 rows reference `/tmp/...` (178 distinct, e.g. `/tmp/opencode/lab7_delivery_update.sh`); falcon 66/461 rows (114 distinct, e.g. `/tmp/opencode/lab_update_drill.sh`); `evidence/raw/REVIEW-FIX/20260930T011352Z_maintenance-timers.meta.json` records an ephemeral installer
- What is happening: the release-gating "tests" are largely un-runnable history; only in-repo scripts + the edge suite can be re-executed.
- Why it matters: reviewers/successors cannot reproduce program claims without the machines that held the scripts.
- User / business impact: reviewer trust and handover quality degrade.
- Security / privacy / reliability impact: audit conclusions rest on unverifiable procedures.
- Recommended fix: move recurring procedures into `automation/validation/`; mark one-off captures `observation` via a CI check.
- Suggested validation: CI flags any test-ledger row whose command runs `bash /tmp/...`.
- Owner suggestion: both maintainers
- Effort estimate: M
- Dependencies: none
- Status: still-open (prior REV-P2-002 / ND-P3-006)

### Finding ID: TEST-P2-005 - Falcon evidence portability: 264/462 captures bind to a legacy symlink; CI skips them
- Severity: P2
- Confidence: High
- Area: TEST / evidence binding
- Evidence: `evidence/raw/**/*.meta.json` = 462 metas, 198 current-path, 264 under `/home/user/monitoring-build/...` (symlink -> falcon-build, resolves only here); `ci/validate.py:27-28` + `.github/workflows/validate.yml` set `FALCON_EVIDENCE_OPTIONAL=1` so off-repo artifacts are skipped; prior ND-P2-011 unchanged
- What is happening: local integrity passes only because of the symlink; clean clones/reviewer packages cannot verify those hashes.
- Why it matters: the delivered evidence set is not self-contained; CI PASS excludes 57% of captures.
- User / business impact: a reviewer cannot verify most falcon captures from the package.
- Security / privacy / reliability impact: evidence-binding gap for audit/integrity claims.
- Recommended fix: rewrite meta paths to package-relative form at index/publication time; add a package-time resolution check.
- Suggested validation: `ci/validate.py` in a clean clone without the symlink; expect 0 skips.
- Owner suggestion: falcon maintainer
- Effort estimate: M
- Dependencies: none
- Status: still-open (prior ND-P2-011)

### Finding ID: TEST-P3-001 - Quality-claim drift: "161 tests" counts and an unannotated failing P10-G02 capture
- Severity: P3
- Confidence: High
- Area: TEST / claim accuracy & citations
- Evidence: suite at `f1c5def` = `Ran 163 tests in 97.106s - OK` while `ledgers/gate_ledger.csv:72,88` and `closeout/REVIEW-2026-09-30.md:31,178,216,337` say "161 tests" and `docs/GITHUB_CI.md:13` says 163 (commit 824f701 added 2 portability tests; C-105 OPEN); `evidence/raw/P10-G02/20260930T022951Z_clean-checkout-replication.out` = `Ran 161 tests ... FAILED (failures=1, skipped=7)` + `validation: FAILURES PRESENT`, while the v3 capture is green and `gate_ledger.csv:83` P10-G02 stays BLOCKED (review F3 resolved; annotation optional/unmade)
- What is happening: counts frozen at the closeout commit were not refreshed after CI-hygiene commits, and the failing replication capture stays indexed without a superseded marker.
- Why it matters: release artifacts no longer describe the tested tree, and a red capture sits in the accepted evidence chain.
- User / business impact: reviewer confusion; wrong scope statements.
- Security / privacy / reliability impact: low; claim-integrity only.
- Recommended fix: append-only C-105 note refresh + annotate the superseded capture with the v3 id.
- Suggested validation: CI count check; evidence-index disposition audit.
- Owner suggestion: edge maintainer
- Effort estimate: S
- Dependencies: C-105 disposition
- Status: still-open (count class regressed; P10-G02 annotation outstanding)

## Prior-Run Finding Status (verified at current commits)

| Prior ID | Status | Evidence |
|---|---|---|
| ND-P3-011 CI validates contract, not service surface; ALL PASS ≠ tests | partially-fixed | Suite runs in CI (`validate.yml:43`); banner and AGENTS/README flow still exclude tests (TEST-P2-001); no OpenAPI route-parity test |
| ND-P2-014 `purge_expired` deletes non-expired | still-open | `queue.py:126-138` unchanged; no boundary test (TEST-P2-003) |
| ND-P2-003 / REV-P3-004 history-scan claims | still-open | 22 findings / `REVIEW_REQUIRED`; P1-G06 claims pass; latest capture exit 1 (TEST-P2-002) |
| ND-P2-011 evidence index doesn't resolve in package | still-open | 264/462 legacy symlink metas; CI skips (TEST-P2-005) |
| REV-P3-007 stale test counts | regressed | "161" vs 163 at HEAD (TEST-P3-001); infra prior findings in `12_infra_deployment_environment_drift.md` |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Release judged on static "ALL PASS"; reviewer cannot reproduce evidence | High | Medium | Faulty decision / trust erosion | TEST-P2-001/002/004/005 | Label scopes; in-repo scripts; portable paths |
| Latent queue data loss if helper wired in | Medium | Low | Telemetry loss | TEST-P2-003 | Fix + boundary tests |
| Security gate signal ignored as noisy | Medium | Medium | Missed real secret | TEST-P2-002 | Fix false positives; keep negatives |

## Recommendations

### Immediate / This Week
- Split gate wording (TEST-P2-001); fix scanner false positives (TEST-P2-002); fix `purge_expired` + boundary tests (TEST-P2-003); annotate the P10-G02 superseded capture (TEST-P3-001).

### This Month / Later
- Move `/tmp` procedures in-repo (TEST-P2-004); portable evidence paths (TEST-P2-005); add the OpenAPI route-parity test (ND-P3-011 residual); coverage ratchet + falcon live-drift job later.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Print "static validation" in edge validate | Ends ambiguity | edge `ci/validate.sh` | output grep in CI |
| Add suite command to edge README/AGENTS | One-command check | `README.md`, `AGENTS.md` | docs lint |
| Allowlist report SHAs + empty placeholders | Restores falcon gate | `automation/validation/secret_scan.py` | validate exits 0 |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| In-repo tests for falcon parsers/helpers | P2 | falcon | M | none |
| Portable evidence meta paths | P2 | falcon | M | none |
| Route-parity contract test | P3 | edge | S | none |

## Suggested Tests

- Unit: `purge_expired` mixed/empty/boundary + concurrent enqueue/purge.
- Integration: OpenAPI spec→route parity; disk_guard fixture dry-run.
- CI: label `/tmp`-executed captures `observation`; metas resolve inside the package.

## Suggested Documentation Updates

- Edge `docs/GITHUB_CI.md` + `AGENTS.md`/`README.md`: validate exclusions + run tests; C-105 counts.
- Falcon `REPOSITORY.md`: evidence path policy + scanner allowlist rules.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are the GitHub validate runs green at f1c5def? / other red captures besides P10-G02? | CI claim / evidence-chain trust | authenticated run statuses; index-vs-exit audit |
| Does anything test the Pi-side suite end-to-end? | Hardware claim | boot-smoke scope (bounded only) |

## Appendix

Falcon at `8282d3f`: 461 test rows (392 PASS | 63 FAIL | 5 FAILED_OBSERVATION | 1 TOOL_FALSE_NEGATIVE); 66 rows reference `/tmp`; 2 PASS rows with non-zero raw exits (documented notes T-P0-G02-006, T-P0-G08-012); 462 metas (198 current, 264 legacy symlink). Edge at `f1c5def`: 163 tests OK / 97.1 s; `ci/validate.sh` PASS (openapi 16/16/30, 88 gates, 321 captures, secret scan 897 files 0 findings); 313 test rows, 200 with `/tmp`, 0 PASS rows with non-zero exits.
