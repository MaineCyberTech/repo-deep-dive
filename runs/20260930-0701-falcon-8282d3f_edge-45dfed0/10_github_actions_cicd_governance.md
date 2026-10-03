# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repository: `falcon-build` @ `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (`main`; dirty — parallel-session offsite-backup capture in flight) and `falcon-edge-build` @ `f1c5defe6b66887ae49bc44c2cd79b37ad249663` (`main`, clean). Run-named edge SHA `45dfed0` is 5 commits behind; in-flight CI work is now committed (`ba8dce3`…`f1c5def`).
- Generated at: 2026-09-30 (audit session)
- Auditor: repo-deep-dive subagent (prompt 10)
- Area code: CI
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/10_github_actions_cicd_governance.md`
- Scope limitations: GitHub-side settings, run logs and secret values are not readable from the repository; no GitHub API credentials were used (private-repo results marked `unverified`). Live host untouched.

## Scope

Reviewed: both repos' `.github/workflows/`, `.github/dependabot.yml`, `.gitleaks.toml`, in-repo validators (`ci/`), CI evidence captures, doc claims, permissions/pins/concurrency, bypass paths, drift-class coverage, and the scripted deployment/release flow. Not reviewed: GitHub server-side settings (rulesets, environments, secrets, org usage) beyond in-repo documentation; no workflow was executed on GitHub.

## Evidence Reviewed

- falcon-build: `.github/workflows/validate.yml` (job `validate`; commits `6f33a06`, `1dbb86c`, `80d8e8b`), `.github/{dependabot.yml,.gitleaks.toml}`, `ci/validate.py`, `ci/{validate.sh,preflight.sh}`, `automation/validation/{secret_scan.py,build_test_ledger.py,pack_fidelity.py,publish_digests.sh,verify_publication_chain.sh}`; `AGENTS.md` rule 5, `REPOSITORY.md:14`, `README.md` CI section.
- falcon-edge-build: `.github/workflows/{validate,bake-image,boot-smoke,publish-release,dependabot-merge}.yml`, `.github/dependabot.yml`, `.gitleaks.toml`, `ci/validate.sh`, `ci/{check_ledger,check_evidence,check_decisions,lint_openapi,secret_scan}.py`, `automation/validation/{check_upstream_drift.sh,ci_status.sh,fetch_ci_artifact.sh,qemu_boot_smoke.sh}`; `docs/GITHUB_CI.md`; `ledgers/` (R-012, D-009, X-046..X-048, gate ledger); `closeout/OWNER_ACTIONS.md` §9; `evidence/raw/REVIEW-FIX/` CI captures. Prior run: `runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/` (ND-P3-006, ND-P3-011, REV-P3-004/005).

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` (falcon, dirty tree) | Reproduced | Show what falcon CI runs | rc=1: parse/pins/ledger/evidence PASS; secret scan FAIL (2 `long_hex` hits on this run's reports) |
| `bash ci/validate.sh` (edge, clean tree) | Reproduced | Show what edge CI runs | `validation: ALL PASS`; 88 gates, 321 captures, 897 files scanned, OpenAPI 16 paths/30 schemas |
| `evidence/raw/REVIEW-FIX/` captures | Captured API output | Edge CI results after the fact | `validate` success at `45dfed05`; boot smoke run 36695915224 replay green; lab8 full 45/45 verify output |
| Static walk: pins, triggers, permissions, environments, tests | Reproduced | Pin/privilege/approval checks | All actions SHA-pinned (3 edge, 2 falcon); no `pull_request_target`; no `id-token`; no Dockerfile; edge suite = 163 tests |
| Contract vs service routes | Reproduced | Route-parity coverage | `api/openapi/falcon-edge-v1.yaml` (16 paths) lacks `renewals` (`src/falcon_control/service.py:141`) and `ingest/vector` (D-006) |

## Executive Summary

Both repos now have real CI, built within ~24h of this run. `falcon-edge-build` is strong: `validate` runs actionlint, shellcheck (blocking at warning severity), ruff, gitleaks, zizmor, a weekly upstream-drift check, `ci/validate.sh` (88-gate ledger, evidence-vs-index, OpenAPI/models, decisions, secret scan), the 163-test suite on Python 3.12+3.13 with coverage summary, and builds+verifies a review-package artifact; `bake-image` builds the credential-bearing image with a 45/45 verify and SBOM; `boot-smoke` boot-tests a CI-baked image in QEMU; `publish-release` publishes draft releases; `dependabot-merge` merges on green. Strengths: SHA pins, least-privilege permissions, concurrency/timeouts, job summaries, captured run URLs/artifact digests. `falcon-build` added a static pipeline on 2026-09-30, but it is unexercised/unverified, unscheduled, and runs none of that repo's test/publication estate.

Top risks: (1) no enforced branch protection on either `main` (edge documents the GitHub Free limit; falcon does not) — checks are advisory, no bypass audit trail (see `34_branch_protection_required_checks.md`); (2) checks do not cover the requested drift classes: status-vs-source (falcon `evidence_index.csv` unverified; edge gate refs unresolved; gate note "161 tests" vs 163), pin-vs-delivery, docs-vs-records (GITHUB_CI.md "every 20 minutes" vs daily cron), and route-vs-contract; (3) falcon's mandated `ci/validate.py` fails once audit run folders are committed (reproduced); (4) residual supply-chain gaps (unhashed tool downloads, no history scan, no SBOM vulnerability gate). Next: apply the companion branch-protection recommendation (plan upgrade per R-012), capture a falcon run + weekly schedule, and add the missing cross-artifact gates.

## Prior-Run Finding Status

| Prior finding | Status | Evidence |
|---|---|---|
| ND-P3-006 (falcon: no CI/hooks/Makefile) | `partially-fixed` | `validate.yml` + `ci/validate.py` exist (`6f33a06`); no hooks, no run evidence, tests still not in CI |
| ND-P3-011 (edge: CI skips tests; no route parity) | `partially-fixed` | tests job runs the full suite on 3.12/3.13; no route-parity test; live routes still outside spec (ND-P2-012 still-open) |
| REV-P3-004 (P1-G06 cites failing capture) | `still-open` | `evidence/raw/P1-G06/20260929T044104Z_evidence-tooling-verification.out` still ends `validation: FAILURES PRESENT`; gate row has no appended green ref |
| REV-P3-005 (P4-G01 truncated lab7 evidence) | `partially-fixed` | full lab8 45/45 capture exists (`...061721Z_ci-lab8-local-verify.out`); gate row `P4-G01` still cites only `E-P4-G01-282` |

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| falcon CI + validator + dependabot | `.github/workflows/validate.yml`, `ci/validate.py`, `.github/dependabot.yml` | Static validation on push/PR/dispatch; weekly action bumps | Implemented 2026-09-30; unexercised; index not checked despite docstring | P2 | 1 job, py3.12, 20-min timeout; rc=1 on dirty tree (audit docs) |
| edge validate | `.github/workflows/validate.yml` | Tests + static gates; push/PR/weekly | Live, green at `45dfed05` per capture | — | matrix 3.12/3.13; drift check weekly |
| edge validators | `ci/validate.sh`, `ci/*.py` | Ledger/evidence/contract/decisions/secret checks | ALL PASS locally | — | strongest control in both repos |
| edge bake | `.github/workflows/bake-image.yml` | Manual CI image build + verify + SBOM | Live (lab8 run 36676319781) | P2 | `environment: bake`, no reviewers (plan) |
| edge boot smoke | `.github/workflows/boot-smoke.yml` | QEMU healthy-boot check | Verified run 36695915224; manual only | P3 | bounded criteria; serial-log artifact |
| edge release | `.github/workflows/publish-release.yml` | Manual release publisher | Present; draft/prerelease defaults | P2 | no environment approval |
| edge dependabot | `.github/workflows/dependabot-merge.yml` | Merge-on-green sweep (daily) | Live; 3 PRs merged | P2 | bot merge bypasses human review by design |
| edge drift check | `automation/validation/check_upstream_drift.sh` | Pin existence + base image URL | Runs each validate + weekly | P3 | no delivery/pin cross-check |
| Governance docs | `docs/GITHUB_CI.md`, R-012 | CI + plan limits documented | Edge yes; falcon none | P2 | falcon protection state undocumented |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| .github/workflows | 4 | Edge: 5 workflows, pinned/concurrency/timeouts; falcon: 1 | falcon run unproven | Capture a run; keep deploy manual |
| PR validation | 3 | Static checks on PR both; edge tests too | Advisory only; falcon no tests | Enforce via ruleset |
| Lint/typecheck/test/build | 4 | actionlint/shellcheck/ruff/zizmor; 163 tests ×2; package build | falcon: no tests/build; no typecheck | Add falcon CI-able checks |
| Deploy workflows | 2 | `bootstrap/*.sh`; edge `deploy/` | No pipeline/approval (adapted) | Document+approve manual flow |
| Migration workflows | 2 | `index_rename_migration.sh` etc. | Not in CI | Add scripted dry-run check |
| Docker build/push | 3 | Compose pins + `pins/images.lock`; edge image bake | No registry push/build pipeline | Declare scope; add build check if used |
| Releases | 3 | Edge publisher + SHA256SUMS + signed manifest; falcon chain local | Edge releases unapproved; falcon chain not in CI | Env + tag protection; wire falcon check |
| Badge/report generation | 2 | Job summaries; edge digest captures | No badges; falcon no capture | Summarize + ledger-note each release |
| Secrets | 3 | 7 edge secrets staged 0600; tree scans both | No history scan; env approvals blocked | History scan; plan upgrade |
| permissions blocks | 5 | Least privilege verified in all workflows | — | Keep under review |
| OIDC | N/A | no `id-token`/cloud deploy | — | Revisit if cloud target added |
| Environment protection | 1 | `environment: bake` exists | No reviewers (R-012 open) | Upgrade; add reviewers + publish env |

## Detailed Review

### Item: falcon-build `validate` workflow / `ci/validate.py`

- Evidence / behavior: `validate.yml` runs actionlint → shellcheck (errors) → ruff E9/F/B → gitleaks (tree) → zizmor → `ci/validate.py` (YAML/JSON, compose pins, gate-ledger schema, evidence hashes with off-repo skip, secret scan) → summary; `contents: read`, concurrency, 20-min timeout, SHA pins; gaps: no tests/index/pack/publication checks, no schedule/drift, no run capture, and `check_evidence_integrity` never reads `evidence_index.csv`.
- Risk / fix: green CI with drifting tests/records — CI-P2-001/002.

### Item: falcon-edge-build `validate` workflow

- Evidence / behavior: `tests` matrix (3.12 coverage summary / 3.13) + `validate` (actionlint, shellcheck warning-blocking, ruff, gitleaks, zizmor, upstream drift, `ci/validate.sh`, review-package build+verify+upload, summary); weekly cron, cancel-in-progress, least privilege; local ALL PASS (88 gates / 321 captures).
- Gaps / fix: no route parity, vulnerability/container scan, or coverage threshold; gate refs unresolved; no delivery/pin check — CI-P2-004, CI-P3-001/002.

### Item: edge bake / release / merge governance

- Evidence / behavior: `bake-image.yml` (7 secrets, `environment: bake`, 45/45 verify, SBOM); `publish-release.yml` (draft/prerelease defaults); `dependabot-merge.yml` (cron `23 5 * * *`); controls: private repo, SHA pins, zizmor, least privilege, captured digests, R-012 recorded.
- Gaps / fix: env reviewers/rulesets plan-blocked; publish-release has no environment; no tag protection; bot merges bypass review — BP-P1-001/BP-P2-001/002.

### Item: drift classes not covered by required checks

- Evidence / behavior: `ci/check_ledger.py` (format-only refs); falcon `ci/validate.py` (no index read); `check_upstream_drift.sh` (pins exist + URL only); `docs/GITHUB_CI.md:73` vs cron; gate P10-G07 ("161 tests") vs 163; spec vs `src/falcon_control/service.py:141`.
- Classes / risk: status artifacts vs sources, pin vs delivery, docs vs records, route vs contract — a green pipeline can coexist with stale/wrong artifacts (CI-P2-002/004, CI-P3-001).

## Scenario / Control Matrix

| ID | Scenario / control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CI-001 | .github/workflows | both `.github/` | 6 workflows, pinned | falcon unproven | P2 | Capture falcon run |
| CI-002 | PR validation | `validate.yml` both | Static gates on PR | Advisory (no protection) | BP-P1-001 | Ruleset required checks |
| CI-003 | Lint/typecheck/test/build | both workflows | Linters + 163 tests; package build | falcon no tests; no typecheck | P2 | Add falcon checks |
| CI-004 | Deploy workflows | `bootstrap/*.sh`; edge `deploy/` | None (scripted/manual, adapted) | No pipeline/approval | P2 | Document + approve |
| CI-005 | Migration workflows | `index_rename_migration.sh` | None in CI | No migration gate | P3 | Scripted dry-run check |
| CI-006 | Docker build/push | compose pins; image bake | Pins checked; image built in CI | No registry pipeline | P3 | Declare scope |
| CI-007 | Releases | `publish-release.yml`; falcon chain | Manual, draft default, digests | No approval/tag protection | P2 | Env + tag rules |
| CI-008 | Badge/report generation | job summaries; captures | Summary + digest capture | No badges; falcon no capture | P3 | Summary + ledger note |
| CI-009 | Secrets | edge secrets; scanners | 0600 staging; tree scans | No history scan; approvals blocked | P2 | History scan; upgrade |
| CI-010 | permissions blocks | all workflows | Least privilege | — | — | Review on change |
| CI-011 | OIDC | none | N/A | — | — | Revisit later |
| CI-012 | Environment protection | `environment: bake` | Deployment record only | No reviewers | P2 | Upgrade + reviewers |

## Findings

### Finding ID: CI-P2-001 - falcon-build's mandated validation fails on committed audit run folders

- Severity: P2 · Confidence: High · Area: CI
- Evidence: `ci/validate.py` `check_secret_scan` (lines 149-158) and `automation/validation/secret_scan.py` (`long_hex`; the only SHA allowlist is `uses: repo@<40-hex>`); `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/01_repository_inventory.md:6` and `02_architecture_runtime_topology.md:6` (Commit SHA metadata).
- What is happening: Reproduced: `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` exits 1 with `validation_failures=1`; both hits are `long_hex` matches on the 40-hex commit SHA written into this run's report headers.
- Why it matters: profile §7 writes run folders into `docs/audits/`; once committed, `AGENTS.md` rule 5 / `REPOSITORY.md:14` ("must pass before commit") goes red without a real defect.
- User / business impact: audit evidence and the pre-commit gate conflict; maintainers are pushed toward bypassing or weakening the scanner.
- Security / privacy / reliability impact: low direct risk; degrades scanner signal quality.
- Recommended fix: treat `docs/audits/**` like git context in `secret_scan.py` (allow 40-hex commit/revision IDs or path-allowlist run folders); mirror in `.gitleaks.toml` if needed.
- Suggested validation: run `ci/validate.py` with a run folder present → 0 failures; plant a synthetic secret under `docs/audits/` and confirm it still fails.
- Owner suggestion: build-agent · Effort estimate: S · Dependencies: none · Status: open

### Finding ID: CI-P2-002 - falcon CI is unexercised and omits tests, pack/publication checks, and evidence-index verification

- Severity: P2 · Confidence: High · Area: CI
- Evidence: `.github/workflows/validate.yml` (added `6f33a06`, 2026-09-30 06:39Z; fixes `1dbb86c`, `80d8e8b`) has no `schedule`; no repo artifact references a falcon run (grep of `evidence/`, `ledgers/`, `closeout/`; no `ci_status.sh` in `automation/validation/`), unlike edge `evidence/raw/REVIEW-FIX/20260930T061913Z_github-actions-runs.out`. `ci/validate.py:main()` covers parsers, compose pins, gate-ledger schema, evidence hashes and secret scan only; docstring line 9 claims the index is checked but `check_evidence_integrity()` never reads `ledgers/evidence_index.csv`; `automation/validation/` (51 `.sh` checks, `build_test_ledger.py`, `pack_fidelity.py`, `publish_digests.sh`, `verify_publication_chain.sh`) is never invoked; edge counterpart `ci/check_evidence.py` does check index membership/staleness; prior ND-P3-006 (`partially-fixed`), ND-P2-011 class.
- What is happening: The only falcon gate was committed ~20 minutes before this audit began; no run/digest is captured anywhere, index drift is unverifiable in CI, and the test/publication estate still runs only manually.
- Why it matters: "configured" is not "exercised"; "validate PASS" does not mean tests or delivery checks pass; the evidence registry can silently disagree with raw evidence, and pin/URL rot is invisible while idle.
- User / business impact: release/publication records bind to a gate with no evidence trail; reviewers cannot audit CI history or trust the index.
- Security / privacy / reliability impact: unproven gate; publication-chain breakage (prior INTG-P0-001 class) only caught by the operator.
- Recommended fix: run the workflow once and capture run URL/digest via a falcon `ci_status.sh`; add a weekly `schedule` + pin/URL drift step; add a job for host-independent checks (`build_test_ledger.py` check mode, `pack_fidelity.py` where possible, publication-chain verifier); port `ci/check_evidence.py` index semantics into `ci/validate.py`.
- Suggested validation: capture shows success at HEAD; a bogus pin fails the drift check; broken ledger/index/ref fixtures fail CI.
- Owner suggestion: build-agent + owner (scope) · Effort estimate: M · Dependencies: define CI-able checks · Status: open

### Finding ID: CI-P2-004 - edge CI still lacks route parity; live endpoints remain outside the contract

- Severity: P2 · Confidence: High · Area: CI
- Evidence: `api/openapi/falcon-edge-v1.yaml` (16 paths; no `renewals`, `ingest/vector`, `release`); live route `src/falcon_control/service.py:141`; `ledgers/decision_log.md` D-006; `ci/lint_openapi.py` and `api/generate_models.py --check` validate the spec itself; grep of `tests/` shows no service-vs-contract parity test; prior ND-P3-011, ND-P2-012.
- What is happening: The tests job now runs in CI (half of ND-P3-011 fixed), but nothing compares the service route table to the published contract, and the contract is knowingly behind the service.
- Why it matters: clients and new developers code against an "authoritative" spec that omits live endpoints; drift is found only by reading source.
- User / business impact: integration errors, rework; ND-P2-012 remains open.
- Security / privacy / reliability impact: undocumented endpoints (renewals, ingest) bypass contract review.
- Recommended fix: add `tests/phase10/test_route_parity.py` enumerating `service.ROUTES` vs OpenAPI paths/methods; add missing paths/schemas and regenerate models.
- Suggested validation: parity test fails before the spec update, passes after; runs on both Python legs.
- Owner suggestion: build-agent · Effort estimate: S-M · Dependencies: contract update · Status: open

### Finding ID: CI-P3-001 - Declared-vs-actual drift classes remain unguarded (pin↔delivery, docs↔records)

- Severity: P3 · Confidence: High · Area: CI
- Evidence: pin↔delivery — `check_upstream_drift.sh` checks only that pinned action commits resolve and the base image URL is reachable; falcon `ci/validate.py` checks compose pins vs `pins/images.lock` only; `PACKAGE_DIGEST.txt`, `docs/edge/EDGE_RELEASE_PIN.md`, the release manifest and fetched artifact digests are never cross-checked (prior INTG-P0-001 fixed by hand). docs↔records — `docs/GITHUB_CI.md:73` says the Dependabot sweep runs "every 20 minutes" while the cron is `23 5 * * *` (changed in `ba8dce3`); gate `P10-G07` note says "161 tests" while the suite is 163.
- What is happening: The pipeline validates declarative files in isolation; nothing binds declared pins/digests to delivered artifacts, or narrative docs/gate notes to machine-readable sources.
- Why it matters: the highest-impact prior cross-repo class can recur silently; operators act on stale cadence/count claims.
- User / business impact: a wrong artifact may be flashed/published; minor operational confusion.
- Security / privacy / reliability impact: delivery integrity depends on manual verification.
- Recommended fix: add a `verify_pin_vs_delivery` step (falcon: `verify_delivery.sh` + `PACKAGE_DIGEST.txt`; edge: signed release manifest vs fetched artifact digest); fix the stale doc line; add a small cadence/test-count consistency check.
- Suggested validation: mutate a digest or cadence → check fails; current artifacts pass.
- Owner suggestion: build-agent + owner (authoritative pin) · Effort estimate: M · Dependencies: delivery dir / pack build · Status: open

### Finding ID: CI-P3-002 - Residual supply-chain/security-scanning gaps in CI

- Severity: P3 · Confidence: High · Area: CI
- Evidence: tool downloads — falcon and edge `validate.yml` `curl -sL` actionlint 1.7.12 / shellcheck 0.10.0 / ruff 0.16.9 / gitleaks 8.30.1 archives (no checksum verification, no `curl -f`); `pip install "zizmor==1.30.1"` without hashes. History — gitleaks `--no-git` in both; falcon secret scan over the checkout only; prior ND-P2-003 history-scan drift remains manual. SBOM/vuln — edge `bake-image.yml` builds an SBOM but has no scan step; trivy usage is local (`install-trivy.sh`); falcon has no vuln step.
- What is happening: Version pins exist but downloaded tools are unverified; secrets removed from the tree remain invisible in history; SBOMs are produced but never evaluated.
- Why it matters: tool compromise can falsify results; history secrets survive in clones/packages; vulnerable packages ship unnoticed.
- User / business impact: low likelihood, high blast radius on the credential-bearing bake path.
- Security / privacy / reliability impact: supply-chain and secret-management hygiene gaps.
- Recommended fix: verify SHA-256 of each tool archive from a pinned manifest (add `curl -f`); add a scheduled history scan with a reviewed baseline (triage falcon's recorded 20 findings first); add a grype/trivy SBOM scan with a documented waiver policy.
- Suggested validation: corrupted archive fails; planted-and-removed secret fails history scan; vulnerable fixture fails SBOM scan (waivers explicit).
- Owner suggestion: build-agent + owner (scan policy) · Effort estimate: M · Dependencies: history triage; scan policy; Actions minutes · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unprotected `main`; workflow edits can reach secrets/releases | P1 | Medium | High | R-012; BP-P1-001 | Plan upgrade, ruleset, env reviewers |
| Green CI coexists with stale status/delivery record | P2 | Medium | High | CI-P2-002, CI-P3-001 | Cross-artifact checks; derive notes |
| falcon validate red on audit artifacts → bypass habit | P2 | High | Medium | CI-P2-001 (reproduced) | Scanner allowlist for run folders |
| Live endpoints outside contract | P2 | High | Medium | CI-P2-004 | Route-parity test + spec |
| Tool/binary supply-chain compromise; secret in history / vulnerable package missed | P3 | Low–Medium | High–Medium | CI-P3-002 | Hash-verified tooling; history + SBOM scans |

## Recommendations

### Immediate / Release Blocking

- Resolve R-012: enable GitHub Pro/Team and apply `branch_protection_recommendation.md` (ruleset, required checks, environment reviewers).
- Fix CI-P2-001 so committing this run folder cannot fail `ci/validate.py`.

### This Week

- Exercise falcon CI once, capture run evidence, add schedule + drift check (CI-P2-002).
- Add the edge route-parity test + contract update (CI-P2-004); correct `docs/GITHUB_CI.md:73` and the P10-G07 note (CI-P3-001).

### This Month

- Port index-aware evidence checking and CI-able test/pack checks into falcon (CI-P2-002).
- Hash-verify tools, add history scan, add pin↔delivery check, decide the SBOM vulnerability policy (CI-P3-001, CI-P3-002).

### Later / Platform Evolution

- Deployment/approval pipeline once plan permits; OIDC if a cloud target appears; coverage thresholds/type checking if desired.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Allow run folders/40-hex commit IDs in scanner | Unblocks committed audit evidence | `automation/validation/secret_scan.py`, `.gitleaks.toml` | `ci/validate.py` green with run folder |
| Capture one falcon run digest | Turns "configured" into "exercised" | `evidence/raw/REVIEW-FIX/`, new `ci_status.sh` | Capture shows success + digest |
| Fix the "every 20 minutes" line | Docs match records | `docs/GITHUB_CI.md` | doc cadence == cron |
| Add `curl -f` to tool downloads | Fails fast on 404/partial | both `validate.yml` | broken URL fails |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Ruleset + required checks + env reviewers | P1 | owner | S | GitHub Pro/Team (R-012) |
| Falcon run capture + weekly schedule/drift | P2 | build-agent | S | none |
| Falcon index-aware evidence check + CI-able tests | P2 | build-agent | M | scope decision |
| Edge route parity + contract update | P2 | build-agent | S-M | spec update |
| Pin↔delivery + docs consistency checks | P3 | build-agent | M | authoritative pin |
| Hash-pinned tools, history scan, SBOM gate | P3 | owner+build-agent | M | scan policy |

## Suggested Tests

- **CI/unit:** route-parity test; evidence-index tamper test (delete row / stale hash → fail); docs cadence check (cron vs doc); gate-note test-count check.
- **Integration/E2E:** capture a full falcon run + digest; weekly drift workflow against a bogus pin; `fetch_ci_artifact.sh` digest equals the release asset digest.
- **Security/regression:** tool-download tamper test; history secret-scan test; SBOM scan with a known-vulnerable fixture; run-folder fixture proving the CI-P2-001 fix; mutated delivery digest proving the pin↔delivery check.
- **Manual validation:** after the Pro upgrade, confirm a red PR is blocked and a bake waits for environment approval.

## Suggested Documentation Updates

- `docs/GITHUB_CI.md` (edge): cadence fix; state what CI does not cover (drift classes, route parity until fixed).
- New falcon CI section (README/`docs/`): run evidence, schedule, check inventory, bypass policy.
- `AGENTS.md` + `ledgers/risk_register.md` (both): record that branch protection may be absent and who may push/bypass; keep R-012 as the CI credential/plan decision of record and link these findings.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `falcon` private, and on what plan? | Ruleset/env availability | Owner statement; `gh api repos/...` |
| Has falcon `validate.yml` ever run? | Gate unproven | Run URL + conclusion capture |
| Who has write access to either repo? | Bypass exposure | Org member/role list (owner) |
| Which pin is authoritative for edge delivery? | Pin↔delivery design | Owner decision / pin semantics |

## Appendix

### Workflow inventory (current commits)

| Repo | Workflow | Triggers | Jobs | Permissions | Notes |
|---|---|---|---|---|---|
| falcon | `validate` | push main, PR, dispatch | `validate` (py3.12) | contents: read | added 2026-09-30; no schedule |
| edge | `validate` | push main, PR, schedule Mon 06:17, dispatch | `tests` (3.12/3.13), `validate` | contents: read | full suite + review-package artifact |
| edge | `bake-image` + `boot-smoke` + `publish-release` | dispatch | `bake`, `boot`, `publish` | contents: read (bake/boot); contents: write, actions: read (publish) | 7 secrets; `environment: bake` (no reviewers); SBOM; QEMU serial log; draft+prerelease default |
| edge | `dependabot-merge` | daily cron, dispatch | `merge` | contents: write, pull-requests: write | `gh pr checks` then squash merge |

### CI gate map / deployment flow

- falcon `validate`: actionlint → shellcheck (errors) → ruff E9/F/B (`ci automation`) → gitleaks (tree) → zizmor → `ci/validate.py` → job summary. Deployment: `bootstrap/10-…98-*.sh` run manually on the host (`ci/preflight.sh` first); review package + digest publication via `automation/validation/{build_review_package,publish_digests,verify_delivery,verify_publication_chain}.sh`; no deploy workflow.
- edge `validate/tests`: pyyaml → coverage run (3.12) / unittest (3.13). `validate/validate`: actionlint → shellcheck (warning) → ruff → gitleaks → zizmor → upstream drift → `ci/validate.sh` → review-package build+verify+upload → summary. Image bake (CI or `bake_lab_test_image.sh`) → 45/45 verify → flash/onboard (`onboard_lab_side.sh`) → release via `publish-release.yml`; control-plane scripts under `deploy/`; no automated promotion.
