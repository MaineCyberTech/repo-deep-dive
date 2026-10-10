# 09_testing_quality_release_confidence — Prompt 09 - Testing, Quality, and Release Confidence Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `09_testing_quality_release_confidence.md` (area TEST, prompt)

## Verification Performed

# Testing, Quality, and Release Confidence Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261009-2117-full-08e20d1
- Repository: falcon @ 08e20d1 (branch main), live lab host `falcon`
- Generated at: 2026-10-09T21:44:07Z
- Auditor: subagent (repo-deep-dive full, area TEST)
- Area code: TEST
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/09_testing_quality_release_confidence.md
- Scope limitations: read-only; the full local gate was executed on the audit clone, and CI results were read via the GitHub API. No live-only root/docker suite was re-run.

## Scope

Reviewed: ci/validate.py (21 checks) and ci/validate.sh, the 50 shell regression suites under automation/validation/tests/, the live-only validators under automation/validation/ (container drift, pipeline e2e, port matrix, firewall negative tests, backup/recovery drills, load), the three GitHub workflows (validate, external-smoke, dependabot-merge), the ledgers (gate, phase9 gate, test execution, evidence index), and the release/publication checks (restore assertion, digest binding, publication equality, SBOM hashes).

Not reviewed: live root/docker suites were not re-executed (read-only role); edge-repository tests; console-level QA.

Companion artifacts: test inventory + critical-workflow coverage matrix + release-confidence scorecard + manual QA checklist are in the sections below.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| ci/validate.py | gate | single local/CI entry point | 21 checks; --fast subset |
| automation/validation/tests/*.sh | tests | offline regression suites | 50 suites; 1 marker |
| automation/validation/*.sh | live validators | root/docker/live checks | run by timers or manually |
| .github/workflows/validate.yml | CI | static + gate + gitleaks + zizmor + pwsh | self-hosted lab for trusted refs |
| .github/workflows/external-smoke.yml | CI | public-surface smoke | lab runner + bypass acceptance |
| ledgers/gate_ledger.csv + phase9_gate_ledger.csv | ledgers | gate aggregates | 102 + 14 rows verified |
| ledgers/test_execution.csv | ledger | raw execution observations | 1127 rows |
| ledgers/evidence_index.csv + evidence/ | evidence | binding | index cross-check |
| CI runs 276-280, external-smoke 15 | CI artifacts | actual outcomes | read via API |
| automation/validation/restore_assertion.sh + tests | tests | offline restore proof | FINAL-P1-001 |
| automation/validation/selfcheck_edge_pin.py + tests | tests | pairing contract | API-P1-001 |

## Verification Performed

| Check | Command / artifact | Result |
|---|---|---|
| Full local gate | `python3 ci/validate.py` on the audit clone | validation_failures=0; 21 checks PASS; 50/50 suites PASS |
| Bounded smoke | `python3 ci/validate.py --fast` | PASS in 1.77s (5 checks) |
| CI on audited commit | GitHub API run 37985725668 (push, main, 08e20d1) | success in 1.4 min on the edge-builder self-hosted runner |
| CI on the live lineage | runs 37986216737 / 37986933263 (ops branch) | FAIL: evidence index cross-check (6 meta files without index rows) |
| External smoke | run 37985746101 (08e20d1) | success, but both hostnames hit the owner-IP bypass branch |
| Gate aggregates | gate_ledger (102: 101 PASS/1 NA) + phase9_gate_ledger (14: 13 PASS/1 NA) | matches README/CURRENT_STATE claims |
| Test execution ledger | 1127 rows: 981 PASS, 140 FAIL, 5 FAILED_OBSERVATION, 1 TOOL_FALSE_NEGATIVE | FAIL rows are captured observations/negative tests through 2026-10-03; latest gate statuses are PASS |
| Evidence integrity in CI | CI log line | '0 captures, 1133 external skipped in CI' (vacuous) |
| Evidence integrity on the lab | local gate | '1127 captures' verified (paths resolve to /home/user/falcon-build) |
| Marker handling | validate_gate_test.sh run as uid 1000 | 12/12 passed although it declares test-requires: root (marker at line 26 > 15-line window) |

## Executive Summary

Strengths: this repository has an unusually strong offline gate for an infra repo — one entry point (ci/validate.py) with 21 checks covering parsing, image pinning/digests, SBOM/vuln coverage, shell syntax, shellcheck, credential sourcing, gate-ledger integrity, evidence integrity/index, digest binding, SBOM hashes, generated drift, license gate, secret scan, edge-pin pairing (with a signed offline self-check), the end-to-end restore assertion, 50 offline shell suites, publication equality, lock freshness, and event-time consistency. The full gate reproduces green locally at 08e20d1 and in CI (1.4 min). Aggregates match their ledgers, and prior TEST findings (ledger provenance, bounded gate, restore e2e) are demonstrably fixed.

Risks: what the gate does NOT cover is where the residual risk sits. The external-smoke check no longer exercises its stated Access-posture assertion (it runs on the lab and accepts the owner-IP bypass). The CI evidence-integrity step verifies zero captures because every meta file references off-repo paths. The only test-requires marker is outside the header window the gate scans, so the skip mechanism silently does not apply. Live-only suites (firewall negative test, port matrix, container drift, pipeline e2e, backup/recovery drills, load) run outside CI and their failures (e.g., the daily backup) are not release-gating.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Gate | ci/validate.py | static + regression gate | 21 checks; green at 08e20d1 | low | --fast subset for iteration |
| Shell suites | automation/validation/tests/ | offline regressions | 50 suites, all pass | low | stubbed, no root/network |
| Live validators | automation/validation/*.sh | root/docker/live checks | run by timers/manual | medium | not in CI |
| validate workflow | .github/workflows/validate.yml | CI gate | green on main; lab runners | low | fork jobs billing-blocked |
| external-smoke | .github/workflows/external-smoke.yml | public surface | green but bypass path | medium | vantage regression |
| dependabot-merge | .github/workflows/dependabot-merge.yml | label-gated merge | success | low | CI domain |
| Gate ledger | ledgers/gate_ledger.csv | P0-8 gates | 101 PASS/1 NA | low | verified |
| Phase9 ledger | ledgers/phase9_gate_ledger.csv | phase 9 gates | 13 PASS/1 NA | low | verified |
| Test ledger | ledgers/test_execution.csv | raw observations | 1127 rows incl. negative captures | low | append-only |
| Evidence index | ledgers/evidence_index.csv | evidence binding | cross-check green at 08e20d1 | low | 6 rows missing on the live lineage |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Unit tests | 4 | 50 offline suites (stubbed units) | no coverage metric | add optional kcov for shell helpers |
| Integration tests | 3 | offline restore/backup/offsite suites | live integration not gated | keep timers; add drift metrics |
| API tests | N/A | no application API | edge pairing tested offline | n/a |
| E2E | 3 | restore_assertion (offline), pipeline_e2e (live timer) | live e2e not in CI | expose result metric to release gate |
| Component tests | 3 | compose/compose digest/shell checks | no live container recreate test | lab-only recreate drill |
| Visual regression | N/A | no UI built here | n/a | n/a |
| Accessibility | N/A | no UI built here | n/a | n/a |
| Contract tests | 4 | edge pin + selfcheck + mutation test | clean-clone path covered | keep |
| Migration tests | 3 | mapping drift + event-time + rename/rollback drills | rollback drill live-only | schedule |
| Security tests | 4 | secret scan + gitleaks + exposure edges + guards | adopted-stack checks (CTR) | extend compose tests |
| Load/failure tests | 2 | phase9_span_load (live, manual) | not scheduled in CI | periodic lab run + metric |
| Smoke tests | 3 | --fast, service probe, external-smoke | external vantage weakened | restore external vantage |

## Detailed Review

### Item: The gate and what "all checks pass" does not cover

- Evidence: ci/validate.py:1-646; local full run; CI run 278.
- Covers: static/offline checks and offline regression suites; the lab's evidence tree when present.
- Does NOT cover: container rebuilds/recreate, live firewall/DOCKER-USER, live pipeline delivery, live backup/restore rehearsal, load, third-party console checks, and any root/docker-requiring validator. CI additionally skips evidence hashes for off-repo artifacts and does not run actionlint/ruff/zizmor/pwsh locally (CI-only steps).

### Item: external-smoke vantage

- Evidence: external-smoke.yml:23-26,37-45; run 37985746101 log.
- Current: runs on [self-hosted, lab]; accepts any 302 as OK, labeling the non-Access location as an owner-IP bypass.

### Item: CI evidence integrity

- Evidence: ci/validate.py:195-216; CI log; meta scan.
- Current: 0/1127 metas reference in-repo artifacts, so the CI step is a no-op; the committed tree is still bound by generated-drift and the index check.

### Item: test-requires marker

- Evidence: ci/validate.py:434-441 (head 15 lines); validate_gate_test.sh:26; local run.
- Current: marker outside the window; suite runs (and passes) instead of being skipped.

### Item: Aggregates

- Evidence: ledgers; README/CURRENT_STATE.
- Result: gate_ledger 102 (101/1) and phase9_gate_ledger 14 (13/1) match the published claims; test_execution 1127 rows include intentional negative/observation FAILs (latest 2026-10-03) — no contradiction with gate statuses.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| TEST-001 | Unit tests | 50 suites | offline, stubbed | no coverage metric | P3 | optional coverage |
| TEST-002 | Integration tests | restore/backup/offsite suites | offline | live path not gated | P2 | metrics to gate |
| TEST-003 | API tests | edge pin contract | offline selfcheck | n/a | - | keep |
| TEST-004 | E2E | restore assertion + pipeline e2e | offline + timer | live not gating | P2 | surface live metric |
| TEST-005 | Component tests | compose checks | static | no recreate test | P3 | lab drill |
| TEST-006 | Visual regression | n/a | n/a | n/a | - | n/a |
| TEST-007 | Accessibility | n/a | n/a | n/a | - | n/a |
| TEST-008 | Contract tests | edge pin + mutation | strong | none | - | keep |
| TEST-009 | Migration tests | mapping/event-time/rename | offline + drills | rollback live-only | P3 | schedule |
| TEST-010 | Security tests | scanners + guards | strong | adopted-stack gap | P2 | extend |
| TEST-011 | Load/failure tests | phase9_span_load | manual | not scheduled | P2 | periodic run |
| TEST-012 | Smoke tests | --fast + external-smoke | fast; vantage weakened | Access assertion dead | P2 | external vantage |

## Findings

### TEST-P2-001 - external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence: .github/workflows/external-smoke.yml:23-26 (comment: 'Must run from GitHub's network ... stays on hosted'), :26 (runs-on [self-hosted, lab]), :37-45 (any 302 accepted; non-cloudflareaccess location labeled 'owner-IP Access bypass; origin reachable'); CI run 37985746101 log ('OK https://iris.mainecybertech.us/ -> 302 (owner-IP Access bypass; origin reachable)', same for soc); commit 08e20d1 message.
- What is happening: the daily public-surface check now runs from the lab's own vantage and treats the owner-IP bypass as success, so it cannot detect an Access-policy regression for other clients — the assertion in the workflow header is not exercised.
- Why it matters: the only automated public-Access gate has become self-confirming; the repo's follow-up register treats public-router origin auth as still-open (ADMIN-P2-001/SEC-P2-001), and this check would not catch a widening.
- User / business impact: a policy drift that exposes consoles to non-owner clients would go unnoticed until manual review.
- Security / privacy / reliability impact: external posture regression undetected.
- Recommended fix: keep the check on an external vantage (GitHub-hosted is billing-blocked; use the owner DO host or another vantage), treat the bypass as a WARN with a recorded residual, or rename/narrow the check's claim and track the Access posture elsewhere.
- Suggested validation: run the check from two vantages; assert that a non-owner client still receives a cloudflareaccess.com redirect.
- Owner suggestion: CI/owner.
- Effort estimate: S-M
- Dependencies: an external host to run from (DO server exists).
- Status: open
- Attack path: Access policy weakened -> consoles reachable -> admin abuse (CHAIN-P3-001 context).

### TEST-P3-001 - CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence: ci/validate.py:195-216 (skip when artifact is outside REPO under FALCON_EVIDENCE_OPTIONAL=1); independent scan of 1127 meta files (0 in-repo; 863 -> /home/user/falcon-build/..., 264 -> /home/user/monitoring-build/...); CI run 37985725668 log 'PASS evidence integrity (0 captures, 1133 external skipped in CI)'; local gate 'PASS evidence integrity (1127 captures)'.
- What is happening: in CI the check passes vacuously; only a lab run (where the absolute paths resolve) verifies meta-vs-artifact hashes. The committed evidence tree is still bound by the generated-drift check (evidence/MANIFEST.sha256) and the evidence-index cross-check, so this is a precision/claim gap rather than an unbound tree.
- Why it matters: the README claim 'hash checks still run for in-repo artifacts' is vacuous; a reviewer may over-trust the CI step.
- Recommended fix: state the skip explicitly, or split the check (CI verifies the committed manifest; the lab verifies meta hashes) and record which runs which.
- Suggested validation: negative test — tamper a committed evidence artifact in a fixture and confirm CI fails via generated-drift.
- Owner suggestion: CI/coordinator.
- Effort estimate: S
- Status: open

### TEST-P3-002 - The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence: ci/validate.py:434-441 (reads only the first 15 lines for `# test-requires: root|docker`); automation/validation/tests/validate_gate_test.sh:26 (marker at line 26); `bash automation/validation/tests/validate_gate_test.sh` -> 12/12 passed as uid 1000; full gate log 'PASS shell tests: .../validate_gate_test.sh (0.3s)' and 'PASS shell tests (50 suite(s))' with no skip.
- What is happening: the suite runs despite declaring root; the gate's own self-test demonstrates the skip mechanism is positional and can silently fail to skip a genuinely root-requiring suite whose marker is placed later.
- Why it matters: a future root/docker suite with a misplaced marker would execute in CI instead of skipping (potentially failing or mutating state).
- Recommended fix: scan the leading comment block (or whole file) for the marker, and move or remove the dead marker in validate_gate_test.sh.
- Suggested validation: extend validate_gate_test.sh with a fixture whose marker sits at line 20+ and assert it is skipped.
- Owner suggestion: CI/coordinator.
- Effort estimate: S
- Status: open

## Prior-Run Comparison

- Prior TEST-P1-001 (ledger pointed at an out-of-repo pre-rename tree): verified-fixed — check_evidence_index + ledger provenance run in the gate and pass at 08e20d1.
- Prior TEST-P1-002 (full gate not bounded / suites not portable): verified-fixed — `--fast` completes in 1.77s; the full gate completes locally and in CI in ~1.4 min; suites are offline/stubbed.
- Prior TEST-P2-001 (no backup/offsite/restore e2e in the standard gate): verified-fixed — restore_assertion.sh is a first-class check and a shell suite, with corrupt-object/wrong-key negative cases; backup/offsite suites exist.
- No active prior TEST finding carries forward; the current findings are new gaps in CI coverage/vantage.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Access regression undetected | Medium | Medium | High | external-smoke bypass | TEST-P2-001 |
| Over-trusted CI evidence claim | Low | Medium | Low | vacuous check | TEST-P3-001 |
| Skip mechanism positional | Low | Low | Medium | marker at line 26 | TEST-P3-002 |
| Live failures not release-gating | Medium | Medium | Medium | backup failed; live suites manual | surface metrics to gate |

## Recommendations

### Immediate / Release Blocking
- None: the gate is green at the audited commit.

### This Week
- Restore an external vantage (or downgrade the claim) for external-smoke.
- Clarify the evidence-integrity skip and the marker convention.

### This Month
- Wire key live-only validator results (container drift, pipeline e2e, backup freshness) into the release view as metrics.
- Add a scheduled load/failure run with captured evidence.

### Later / Platform Evolution
- Optional coverage instrumentation for shell helpers; periodic full-vs-fast divergence check.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the marker scan | skip logic works as documented | ci/validate.py | new fixture test |
| Annotate the CI skip | claims match behavior | ci/validate.py, README.md | gate run |
| Record the external-smoke residual | makes the weakened assertion explicit | external-smoke.yml, exception register | workflow run |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| External vantage smoke | P2 | CI/owner | S-M | DO host |
| Live metrics into release gate | P2 | platform | M | metrics exporter |
| Marker/header fix + test | P3 | coordinator | S | none |
| Evidence-check clarification | P3 | coordinator | S | none |

## Suggested Tests

- external-smoke: two-vantage assertion (non-owner client must be Access-gated).
- ci/validate.py: fixture with the marker beyond line 15 must be skipped.
- generated-drift negative: tamper a committed artifact in a throwaway clone and assert CI fails.
- Live metric contract tests for the drift/pipeline/backup exporters.

## Suggested Documentation Updates

- README.md continuous-integration section: state exactly what CI verifies vs what is lab-only.
- docs/security/CI_GOVERNANCE_RECONCILIATION.md: record the external-smoke vantage decision.
- automation/validation/tests/README (if present): document the marker convention.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which external vantage will run the Access check? | restores the only public gate | owner decision |
| Should live validator metrics be release-gating? | closes the delivery-vs-configuration gap | owner decision |
| Is coverage instrumentation wanted for shell? | effort vs value | owner decision |

## Limitations

- Live root/docker suites were not re-run; their last evidence captures were not exhaustively dated.
- CI logs were read from the GitHub API; job logs are truncated to the steps inspected.
- The test ledger FAIL rows are observations (including deliberate negative captures) and were not individually reconciled beyond the latest dates.

## Appendix

Critical-workflow coverage matrix (gate vs live):

| Workflow | Offline gate | Live validator | Last known live state |
|---|---|---|---|
| Backup/restore | restore_assertion, backup_e2e, offsite suites | falcon-backup.timer, restore_rehearsal | backup failed Oct 8-9 (INFRA-P2-003) |
| Alerts/notifications | alert suites, relay auth, deadman | alert-canary timer, alert-relay | canary last Mon; relay running |
| Container runtime | compose digest/cap tests | container_drift_check timer | 0 drift (2026-10-09) |
| Firewall | credential/exposure suites | post_reboot_verify, fw_negative_test | policy drop; wg0 drift (INFRA-P1-001) |
| Pipeline | event-time/mapping tests | pipeline_e2e timer | green 21:26Z (transient OOM failures earlier) |
| Secrets | scanners, rotation register | rotation_status, owner_env (manual) | 20/20 pending; owner-env FAIL (SECRET) |
| Release/publication | digest binding, publication equality | verify_publication_chain | green |

## Findings

| ID | Severity | Title |
|---|---|---|
| TEST-P2-001 | P2 | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass |
| TEST-P3-001 | P3 | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths |
| TEST-P3-002 | P3 | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead |
