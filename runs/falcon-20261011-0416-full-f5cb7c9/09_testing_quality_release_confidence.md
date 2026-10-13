# 09_testing_quality_release_confidence — Prompt 09 - Testing, Quality, and Release Confidence Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `09_testing_quality_release_confidence.md` (area TEST, prompt)

## Verification Performed

# Testing, Quality, and Release Confidence Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: falcon-20261011-0416-full-f5cb7c9
- Repository: falcon @ f5cb7c9 (branch main), live lab host `falcon`
- Generated at: 2026-10-11T04:40:00Z
- Auditor: subagent (repo-deep-dive full, area TEST)
- Area code: TEST
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/09_testing_quality_release_confidence.md
- Scope limitations: read-only. The full local gate was executed on a copy of the audited tree (no writes to the target repository). Live root/docker-only suites were not re-executed (they run via host timers); the private-repo CI state was read via the GitHub API (read-only).

## Scope

Reviewed at f5cb7c9: `ci/validate.py` (21 checks) and `ci/validate.sh`, the 50 offline shell regression suites under `automation/validation/tests/`, the live-only validators under `automation/validation/` (81 scripts), the three GitHub workflows (validate, external-smoke, dependabot-merge), the ledgers (gate, phase9 gate, test execution, evidence index), the release/publication checks (digest binding, publication equality, SBOM hashes, restore assertion), and the stress/load harness.

Not reviewed: live root/docker suites were not re-executed (read-only role); edge-repository tests; console-level QA; visual/accessibility testing (no UI in this repository).

Companion artifacts: test inventory + critical-workflow coverage matrix + release-confidence scorecard + manual QA checklist are in the sections below.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| ci/validate.py | gate | single local/CI entry point | 21 checks; --fast subset |
| automation/validation/tests/*.sh | tests | offline regression suites | 50 suites; 1 test-requires marker |
| automation/validation/*.sh | live validators | root/docker/live checks | 81 scripts; timers/host |
| .github/workflows/validate.yml | CI | static + gate + gitleaks + zizmor + pwsh | runs on self-hosted lab for same-repo |
| .github/workflows/external-smoke.yml | CI | public-surface posture | daily; lab runner; accepts owner-IP bypass |
| ledgers/gate_ledger.csv | ledger | gate claims | 102 gates |
| ledgers/test_execution.csv | ledger | test evidence rows | 1127 rows; last row 2026-10-03 |
| ledgers/evidence_index.csv | ledger | capture index | 1134 entries |
| automation/validation/lab_stress_test.sh | load test | weekly stress harness | ran 2026-10-11 04:20Z, exit 0 |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py` on a copy of f5cb7c9 | gate | reproduce "all checks pass" | EXIT=0; 21 checks + 50 suites; no skips |
| GitHub API: validate runs on main | CI | head-of-main status | f5cb7c9 validate = success (2026-10-11T04:04Z) |
| Meta-file scan | repo | CI evidence-integrity coverage | 1134 metas; 0 reference in-repo artifacts |
| `bash automation/validation/tests/validate_gate_test.sh` | test | marker behavior | runs and passes 12/12 as uid 1000 (no skip) |
| `systemctl status falcon-stress.service` | live | load test evidence | weekly run completed exit 0; metrics written |
| external-smoke.yml inspection | CI | vantage/claim check | runs-on [self-hosted, lab]; accepts any 302 |

## Executive Summary

Release confidence at this commit is good but not complete. The local gate reproduces cleanly: `python3 ci/validate.py` on a copy of f5cb7c9 exits 0 with 21 checks and all 50 offline shell suites passing (322 shell scripts syntax-checked, 194 shellcheck-clean), and the GitHub `validate` workflow on the same commit succeeded. The live-only validators (container drift, image pin, pipeline e2e, boot checks, firewall negatives, backup drills, weekly stress) run via host timers and the weekly stress harness completed successfully on 2026-10-11.

Three carried findings remain, all in the "claim vs actual coverage" class: the external-smoke workflow runs on the lab runner and accepts the owner-IP Access bypass, so it cannot detect an Access-policy regression for non-owner clients (TEST-P2-001); the CI evidence-integrity check verifies zero captures because all 1134 meta files reference off-repo paths that are skipped under FALCON_EVIDENCE_OPTIONAL=1 (TEST-P3-001); and the `test-requires` skip marker is only honored in the first 15 lines, making `validate_gate_test.sh`'s marker at line 26 dead (TEST-P3-002). No new test failures were found, and no flakiness was observed in the gate run.

What "all checks pass" does NOT cover: live root/docker suites (firewall negative tests, container drift, pipeline e2e, backup/restore drills), the external-vantage Access posture, image vulnerability scans, and the CI-only tool steps (actionlint, shellcheck download, ruff, gitleaks, zizmor, pwsh) which were not re-executed locally.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Gate | ci/validate.py | 21 checks | passes locally + CI green on head | Low | --fast subset exists |
| Offline suites | automation/validation/tests/*.sh | regression | 50/50 pass | Low | 1 marker (dead) |
| Live validators | automation/validation/*.sh | live checks | 81 scripts; timer-driven | Medium | not in CI by design |
| external-smoke | .github/workflows/external-smoke.yml | public posture | daily on lab runner | Medium | bypass accepted |
| Evidence integrity | ci/validate.py:195-216 | capture hashes | 0 verified in CI | Medium | off-repo paths skipped |
| Test ledger | ledgers/test_execution.csv | test evidence | 1127 rows; frozen 2026-10-03 | Low | newest fixes not recorded |
| Stress harness | automation/validation/lab_stress_test.sh | load | weekly; passed 04:20Z | Low | falcon-stress.timer |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Unit tests | 3 | 50 shell suites, fixtures for validators | shell-level only | continue |
| Integration tests | 3 | pipeline e2e, container drift, backup drills (live) | not in CI | document + keep timers |
| API tests | N/A | no API surface in this repo | - | - |
| E2E | 3 | pipeline_e2e_check.sh + restore drills | live-only | keep + evidence |
| Component tests | N/A | no UI components | - | - |
| Visual regression | N/A | no UI | - | - |
| Accessibility | N/A | no UI | - | - |
| Contract tests | 3 | compose pins/digest checks, port matrix, mapping drift | - | - |
| Migration tests | 3 | index_rename_migration + rollback drill | live-only | keep evidence |
| Security tests | 4 | gitleaks static+history, fw negatives, secret scan, phase7 | - | - |
| Load/failure tests | 3 | weekly stress + disk pressure drill | no OOM failure-injection (RES-P3-001) | add failure injection |
| Smoke tests | 4 | opensearch_smoke, central_health, boot checks | - | - |

## Detailed Review

### Item: Gate and offline suites
- Evidence: local gate run at f5cb7c9: EXIT=0; "PASS shell tests (50 suite(s))"; "PASS shellcheck (194 scripts)"; "PASS evidence integrity (1134 captures)" locally.
- What it does: single entry point for local and CI validation.
- Current controls: fail-closed checks, --fast subset, timeout per suite.
- Missing controls: none material; coverage is shell-level (appropriate for an infra repo).
- Risks: the CI variant of evidence integrity verifies nothing (TEST-P3-001).
- Recommended improvement: split the evidence check (CI manifest vs lab hashes) as previously recommended.
- Suggested tests: keep the suites; add a fixture for the 9-key owner env.
- Suggested docs: README gate section.

### Item: external-smoke
- Evidence: .github/workflows/external-smoke.yml:3 (claims GitHub's network), :23-26 (runs on [self-hosted, lab]), :37-45 (accepts any 302 with an "owner-IP Access bypass" branch).
- What it does: daily public-surface check.
- Missing controls: an external vantage; a real Access assertion for non-owner clients.
- Risks: an Access-policy regression is not detected by this gate.
- Recommended improvement: run from an external host (owner DO) or treat bypass as a warning with a recorded residual; narrow the workflow claim.
- Suggested tests: negative test that a non-Access 302 fails the check.
- Suggested docs: update the workflow header.

### Item: Evidence integrity and ledgers
- Evidence: ci/validate.py:195-216 (skip when off-repo and FALCON_EVIDENCE_OPTIONAL=1); 1134/1134 metas reference off-repo artifacts; CI log line "0 captures, N external skipped".
- What it does: verifies captured artifact hashes.
- Missing controls: in-repo captures for CI verification.
- Risks: CI passes while verifying nothing; the claim gap is documented but easy to misread.
- Recommended improvement: state the skip explicitly and split the check (CI verifies the committed manifest; the lab verifies meta hashes).
- Suggested tests: evidence_index_check_test.sh exists; add a CI-mode assertion on the output text.
- Suggested docs: ci/README or gate docs.

### Item: test-requires marker
- Evidence: ci/validate.py:434-441 (readlines()[:15]); automation/validation/tests/validate_gate_test.sh:26 (`# test-requires: root`).
- What it does: skips suites that need root/docker.
- Missing controls: header-window independence.
- Risks: a root/docker-requiring suite placed later would run instead of skipping.
- Recommended improvement: scan the header comment block (or whole file) for the marker.
- Suggested tests: a fixture suite with the marker after line 15.
- Suggested docs: validate.py docstring.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| TEST-001 | Unit tests | 50 suites pass | offline shell regression | - | - | - |
| TEST-002 | Integration tests | live validators + timers | host-run | not in CI | P3 | document |
| TEST-003 | API tests | n/a | - | - | - | - |
| TEST-004 | E2E | pipeline_e2e + restore drills | live | evidence cadence | P3 | keep captures |
| TEST-005 | Component tests | n/a | - | - | - | - |
| TEST-006 | Visual regression | n/a | - | - | - | - |
| TEST-007 | Accessibility | n/a | - | - | - | - |
| TEST-008 | Contract tests | pins/digest/port/mapping checks | CI gate | - | - | - |
| TEST-009 | Migration tests | index rename + rollback drill | live | - | - | - |
| TEST-010 | Security tests | gitleaks/fw/secret/phase7 | CI + live | - | - | - |
| TEST-011 | Load/failure tests | weekly stress + disk drill | live | no OOM injection | P3 | add |
| TEST-012 | Smoke tests | opensearch/central/boot | live | - | - | - |

## Findings

### TEST-P2-001 - external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass

- Severity: P2
- Confidence: High
- Area: TEST
- Evidence:
  - `.github/workflows/external-smoke.yml:3` ("from GitHub's network") vs `:23-26` (runs-on [self-hosted, lab]; comment says it "stays on hosted" but the runner list is the lab)
  - `.github/workflows/external-smoke.yml:37-45` (any 302 accepted; non-cloudflareaccess location labeled "owner-IP Access bypass; origin reachable")
  - Live: iris/soc return 302 from the lab vantage; the workflow cannot distinguish owner-IP bypass from Access enforcement for other clients
- What is happening: the only automated Access-posture check runs from the lab and accepts the bypass branch.
- Why it matters: an Access-policy regression for non-owner clients would not be detected.
- User / business impact: admin consoles could silently become reachable without the intended Access gate.
- Security / privacy / reliability impact: detection gap on a security control (composition with ADMIN-P2-002).
- Recommended fix: run the check from an external vantage (owner DO host or another external runner), or treat the bypass as a warning with a recorded residual and narrow the workflow's claim.
- Suggested validation: a negative test that a non-Access 302 fails; a run from an external host.
- Owner suggestion: CI/platform
- Effort estimate: S-M
- Dependencies: external runner availability (GitHub-hosted is billing-blocked per the workflow comment)
- Status: still-open
- Endpoint / data path: https://iris|soc.mainecybertech.us -> Cloudflare edge -> origin
- Attack path: Access misconfig -> anonymous origin reachability (CHAIN-P3-001 leg)

### TEST-P3-001 - CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `ci/validate.py:195-216` (skip when `FALCON_EVIDENCE_OPTIONAL=1` and the artifact is outside the repo)
  - Independent scan: 1134 meta files; 0 reference an in-repo artifact (paths under /home/user/falcon-build or /home/user/monitoring-build)
  - Local gate: "PASS evidence integrity (1134 captures)" (host paths resolve); CI (validate.yml:96 sets FALCON_EVIDENCE_OPTIONAL=1): "0 captures, N external skipped"
- What is happening: the CI variant of the check verifies no capture hashes.
- Why it matters: the check's name implies integrity verification that CI does not perform.
- User / business impact: low; the committed manifest and evidence-index cross-check still bind the tree.
- Security / privacy / reliability impact: claim/precision gap only.
- Recommended fix: state the skip explicitly and/or split the check (CI verifies the committed manifest; the lab verifies meta hashes).
- Suggested validation: an assertion on the CI output text; keep the local full run.
- Owner suggestion: CI coordinator
- Effort estimate: S
- Dependencies: none
- Status: still-open

### TEST-P3-002 - The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead

- Severity: P3
- Confidence: High
- Area: TEST
- Evidence:
  - `ci/validate.py:434-441` (`readlines()[:15]`)
  - `automation/validation/tests/validate_gate_test.sh:26` (`# test-requires: root`)
  - Local gate log: "PASS shell tests: .../validate_gate_test.sh (0.3s)" with no SKIP; suite passes 12/12 as uid 1000
- What is happening: the marker outside the 15-line window is ignored; the suite runs instead of skipping.
- Why it matters: a genuinely root/docker-requiring suite whose marker is placed later would run in the gate instead of skipping.
- User / business impact: low; the affected suite happens to pass unprivileged.
- Security / privacy / reliability impact: gate correctness gap.
- Recommended fix: scan the header comment block (or whole file) for the marker and move or remove the dead marker.
- Suggested validation: a fixture suite with the marker after line 15.
- Owner suggestion: CI coordinator
- Effort estimate: S
- Dependencies: none
- Status: still-open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Access regression undetected | P2 | Medium | High | external-smoke bypass branch | external vantage |
| CI evidence check misread as verification | P3 | Medium | Low | 0 in-repo metas | split check |
| Root/docker suite mis-run | P3 | Low | Low | marker at line 26 | widen scan |
| Live-only coverage invisible in CI | P3 | Medium | Medium | timers | record captures |

## Recommendations

### Immediate / Release Blocking
- None (gate green at the audited commit).

### This Week
- Fix the external-smoke vantage or narrow its claim and record the residual (TEST-P2-001).

### This Month
- Split/label the evidence-integrity check (TEST-P3-001).
- Widen the test-requires scan and fix the dead marker (TEST-P3-002).
- Add a lightweight failure-injection case for the aggregator OOM class (RES-P3-001).

### Later / Platform Evolution
- Record live-validator runs into the test ledger on each timer run so release evidence stays current.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Move the marker to line 2-5 | removes dead marker | validate_gate_test.sh | gate log shows SKIP or intended run |
| Print "CI mode: external captures skipped" | removes ambiguity | ci/validate.py | CI log |
| Add `location` assertion when bypass seen | makes the bypass visible | external-smoke.yml | next run log |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| External-vantage Access check | P2 | CI/platform | M | external runner |
| Evidence-check split | P3 | CI coordinator | S | - |
| Marker scan fix | P3 | CI coordinator | S | - |
| Failure-injection coverage | P3 | resilience | M | - |

## Suggested Tests

- Unit: marker-position fixture; owner-env 9-key fixture.
- Integration: keep the 50 suites; add an external-smoke negative test.
- E2E: keep pipeline e2e + restore drills on timers; capture results.
- CI: keep gitleaks/actionlint/zizmor/shellcheck/ruff/pwsh steps; consider SHA-pinning already done.
- Security: keep the firewall negative tests and phase7 checks.
- Manual: quarterly walkthrough of the live validators.

## Suggested Documentation Updates

- external-smoke.yml header (vantage claim).
- ci/validate.py docstring (evidence-integrity CI behavior).
- docs/runbooks/AUDIT_RUN_LIFECYCLE.md (test evidence cadence).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is an external runner available for the smoke? | decides the fix path | owner/CI decision |
| Should the test ledger be updated by timers? | release-evidence freshness | owner preference |
| Which live validators are the release-critical set? | manual QA checklist scope | platform decision |

## Appendix

- Gate run (copy of f5cb7c9, 2026-10-11): EXIT=0; 21 checks; 50/50 suites; evidence integrity 1134 captures (local); publication equality PASS; lock freshness 20d <= 30d.
- CI (GitHub API): validate on f5cb7c9 = success; earlier commits after a publication bind failed the repository-validation step until the rebind (expected fail-closed behavior, CI-P2-004).
- Live: falcon-stress weekly run 2026-10-11T04:20Z exit 0 (OpenSearch bulk 5,000 docs; 200 sequential queries 17.4s; VPN RTT 45.9ms avg).
- Ledger note: ledgers/test_execution.csv has 1127 rows and its last entry is 2026-10-03; the newest remediation verification (Oct 9-11) is not recorded there (evidence-index rows exist for the Oct 9 captures).

## Findings

| ID | Severity | Title |
|---|---|---|
| TEST-P2-001 | P2 | external-smoke no longer verifies Cloudflare Access from an external vantage; it accepts the owner-IP bypass |
| TEST-P3-001 | P3 | CI evidence-integrity check verifies zero captures; all meta files reference off-repo artifact paths |
| TEST-P3-002 | P3 | The test-requires skip marker is only honored in the first 15 lines; validate_gate_test.sh's marker is dead |
