# 10_github_actions_cicd_governance — Prompt 10 - GitHub Actions, CI/CD, and Governance Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `10_github_actions_cicd_governance.md` (area CI, prompt)

## Verification Performed

# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (private, org-owned)
- Branch: `main`
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:31Z
- Auditor: subagent (read-only)
- Area code: CI
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/10_github_actions_cicd_governance.md
- Scope limitations: repository inspection at f5cb7c9 + read-only GitHub API reads (token from `/home/user/.env`, never printed) + read-only local reproduction of the gate scripts. No workflow was dispatched or executed; no file in the target repo or on the host was modified. Org-level runner groups and GitHub billing state were not accessible; runner host configuration (edge-builder/lab-runner-2) is not on this host, so the sudo state could not be re-probed (prior probe 2026-10-04 stands).

## Scope

Reviewed: `.github/workflows/{validate,external-smoke,dependabot-merge}.yml`, `.github/{CODEOWNERS,dependabot.yml,pull_request_template.md,actionlint.yaml}`, `ci/{validate.py,license_check.py,requirements-ci.txt,preflight.sh}`, the `automation/validation/*` gate scripts invoked by CI, `docs/security/{BRANCH_PROTECTION,CI_GOVERNANCE_RECONCILIATION,CI_CD_INCIDENT_PLAYBOOK,CI_TOOL_PINS,CI_SECRET_GATE,SBOM_COVERAGE_AND_PROVENANCE}.md`, and live GitHub state (workflow registry, runs/jobs/check-runs 2026-10-02..10-11, Actions permissions, environments, artifacts, releases/tags). Not reviewed: the `falcon-edge` repository's workflows, org-level runner-group settings, and GitHub billing state.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github/workflows/validate.yml` | workflow | main PR/push/schedule gate | 140 lines; SHA-pinned actions; SHA-256 tool pins; hash-pinned Python; 21 checks + 50 suites |
| `.github/workflows/dependabot-merge.yml` | workflow | Dependabot auto-merge sweep | write scopes; label gate; no head-commit pin |
| `.github/workflows/external-smoke.yml` | workflow | public-surface smoke | runs on lab runner; accepts owner-IP bypass |
| `ci/validate.py` (CHECKS) + `ci/requirements-ci.txt` | gate code | what CI executes | 21 checks; pyyaml 6.0.3 + zizmor 1.30.1 hash-pinned |
| GitHub API: `actions/workflows`, `actions/permissions`, `actions/permissions/workflow`, runs/jobs/check-runs, `environments`, `actions/artifacts`, `releases`, `tags` | live state | server-side truth | read-only GETs on 2026-10-11 |
| Runs 38110410254 (validate@f5cb7c9), 38109809085, 38109789930 (publication-equality failures), 38067043888 (external-smoke), 38047609916 (dependabot-merge), 37460608720/37616708114/37774326519 (queued+cancelled) | run logs | reproduction/verification | logs fetched read-only |
| `docs/security/{CI_CD_INCIDENT_PLAYBOOK,CI_GOVERNANCE_RECONCILIATION,BRANCH_PROTECTION}.md` | docs | declared vs actual | playbook section 8 stale; matrix accurate |
| Local reproduction: `ci/validate.py --only compose-digests,sbom-vuln,sbom-hashes,license,secret-scan,credential-sourcing,digest-binding,publication-equality,lock-age`, `verify_publication_chain.sh` | commands | what the gates actually do | validation_failures=0; publication_chain_failures=0 |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| validate runs and passes at f5cb7c9 | run 38110410254 (push) | supported: completed success, all 16 steps green, runner edge-builder, `validation_failures=0`, 50 suites PASS |
| validate is a real fail-closed gate | run 38109809085 (push @584e1a3) step 12 | supported: `FAIL publication equality ... commits after the declared commit touch only publication/test files (584e1a37:bootstrap/96..., 584e1a37:bootstrap/97..., d70b1216:export_monitor_metrics.sh, d70b1216:90-alerting.sh)` |
| Publication equality was rebound and is green at f5cb7c9 (CI-P2-004) | run 38110410254 step 14 + local `verify_publication_chain.sh` | supported: 0 failures; digest/closeout/package manifests bound to 3c11752; signed-archive guard OK |
| Same-repo PR code runs on the self-hosted lab runner before review | run 38109789930 (pull_request, PR #54 head 1cf1886cd) | supported: job ran on runner `edge-builder`, labels [self-hosted,linux,x64,lab-python] |
| Auto-merge label gate is configured but unexercised | labels API + 54 PRs + run 38047609916 log | supported: no `dependabot-approved` label, 0 Dependabot PRs ever, log line 'no open dependabot PRs' |
| external-smoke passes on the owner-IP bypass | run 38067043888 log | supported: `OK ... -> 302 (owner-IP Access bypass; origin reachable)` for iris/soc; summary still claims Access enforcement |
| Actions defaults remain permissive | API permissions endpoints | supported: allowed_actions=all, sha_pinning_required=false, default write, can_approve_pull_request_reviews=true |
| Scheduled jobs can be silently starved | runs 37460608720/37616708114/37774326519 jobs | supported: runner_name empty, labels [self-hosted,linux,x64,lab], cancelled after ~24h; no notification wiring |
| Stale workflow registrations persist | API workflows vs tree | supported: 3 probe workflows active with no file on any branch |
| Local gate subset green at f5cb7c9 | `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only ...` | supported: validation_failures=0 (9 checks incl. sbom-vuln, sbom-hashes, publication-equality) |

## Executive Summary

The committed CI is small and genuinely hardened: three workflows, all actions pinned by commit SHA, all downloaded tools SHA-256-verified before execution, hash-pinned Python dependencies, gitleaks tree + full-history scans, actionlint, ruff, shellcheck and zizmor, and one `validate` job that runs 21 repository checks and 50 shell suites. The gate demonstrably works and fails closed (the publication-equality failure at 584e1a3 is a real example), and the f5cb7c9 publication rebind closed the CI-P2-004 regression. The CI-P2-004 fix is verified by run 38110410254 (all steps green).

The current risks are unchanged from 2026-10-09 plus two new documentation/implementation gaps. Runner topology remains the top CI risk: same-repo PRs (including workflow-editing Dependabot PRs) execute on the sudo-capable `edge-builder` runner before review (CI-P1-001, owner-accepted). The auto-merge workflow still holds write scopes with a TOCTOU window and no environment protection (CI-P2-001). The external-smoke monitoring gate still passes on an owner-IP bypass while its artifact claims Access enforcement (CI-P2-002). Repository Actions defaults remain permissive (CI-P2-003). Scheduled/queued runs can be silently starved or dead (CI-P3-001: three 24-hour queue cancellations, no notification wiring), stale probe workflows remain registered (CI-P3-002), the CI incident playbook section 8 still describes pre-fix tool pinning (CI-P3-003), and the review package is documented as a CI/release artifact although no CI job builds or publishes it (CI-P3-004).

Immediate actions: fix the auto-merge head-commit pin (small, high-value), fix or rescope external-smoke, and set read-only Actions defaults. Owner-gated: runner hardening for CI-P1-001.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| validate | `.github/workflows/validate.yml` | push/PR/dispatch/weekly static gate | functional, green at f5cb7c9 | Medium (runner) | 21 checks + 50 suites; `contents: read`; SHA-pinned actions/tools |
| dependabot-merge | `.github/workflows/dependabot-merge.yml` | daily Dependabot sweep | configured, unexercised | Medium | write scopes; no `--match-head-commit`; no environment |
| external-smoke | `.github/workflows/external-smoke.yml` | public surface smoke | degraded | Medium | accepts owner-IP bypass; summary stale; runs on lab |
| CI deps | `ci/requirements-ci.txt` | pyyaml + zizmor | hash-pinned (`--require-hashes`) | Low | 10 wheel hashes |
| Tool downloads | validate.yml:45-73 | actionlint/shellcheck/ruff/gitleaks | SHA-256 verified (`sha256sum -c -`) | Low | retry 3; verified before extraction |
| Secret scans | validate.yml:69-85 | tree + history gitleaks | fail-closed | Low | pinned 8.30.1; curl-allowlist regression test |
| SBOM gate | validate.yml:103-106 | coverage + hashes + vuln waivers | enforced (`--require-vuln --vuln-waivers`) | Low | 24/24 covered; 12 vuln pending (waived to 2026-12-31) |
| Publication gate | validate.yml:108-113 | chain + digest/verdict consistency | enforced; green at f5cb7c9 | Low | rebind closed CI-P2-004 |
| Workflow registry | GitHub API | 8 workflows listed | drift | Low | 3 probe workflows have no file on any branch |
| Actions settings | GitHub API | default write; all actions; no SHA requirement | permissive | Medium | latent footgun |
| Environments | GitHub API | 0 environments | absent | Low | no environment protection anywhere |
| CI artifacts/releases | GitHub API | 0 artifacts, 0 releases, 0 tags | absent | Low | contradicts 'published as a CI/release artifact' docs |
| Deploy/migration/docker/release workflows | n/a | host-run bootstrap scripts | absent by design | Low | deployments are not CI-gated (out of CI scope) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| .github/workflows | 4 | 3 workflows; SHA-pinned actions; zizmor/actionlint green | sudo runner for same-repo PRs; stale registrations | runner hardening; registry cleanup |
| PR validation | 3 | validate real and fail-closed (run 38109809085) | no server enforcement; fork fallback dead; same-repo PRs on lab | fix fallback/policy; plan upgrade for required checks |
| Lint/typecheck/test/build | 4 | actionlint, shellcheck, ruff, 21 checks, 50 suites | no dedicated test job (runs inside validate) | keep; optional split for visibility |
| Deploy workflows | 2 | none (bootstrap stages run on host) | no CI deploy gate or approval | document explicitly as out of CI; add preflight job when feasible |
| Migration workflows | 2 | none in CI; host scripts | no CI coverage | document; keep restore assertion in validate |
| Docker build/push | 2 | none in CI; local image build (falcon-opensearch-s3) | no build/push pipeline | consider digest-pinned build job when a registry exists |
| Releases | 2 | no release workflow/tags; publication chain script-driven | release provenance manual | add release job or document manual flow |
| Badge/report generation | 2 | job summary only | no badges/reports | low priority |
| Secrets | 3 | no secrets in workflows; gitleaks tree+history; GH_TOKEN scoped | dependabot-merge write token | minimal scopes; environment |
| permissions blocks | 4 | all workflows declare permissions | permissive repo defaults | set read default |
| OIDC | 0 | absent (no id-token usage) | no keyless cloud auth | not needed today |
| Environment protection | 0 | 0 environments | no required reviewers | plan-gated; add when available |

## Detailed Review

### Item: validate workflow
- Evidence: `.github/workflows/validate.yml:1-140`; run 38110410254.
- What it does: on push(main)/PR/dispatch/weekly cron, runs actionlint, shellcheck, ruff, gitleaks tree + history + allowlist regression, zizmor, `ci/validate.py` (21 checks), SBOM coverage/hashes, publication chain, PowerShell parse, job summary.
- How it appears to work: fail-closed; every download hash-verified; actions pinned by SHA; `contents: read`.
- Current controls: hash pins, SHA pins, zizmor, gitleaks, evidence-optional handling.
- Missing controls: server-side required check (plan-gated), non-sudo PR runner, failure notification.
- Risks: same-repo PR code executes on the sudo-capable runner before review (CI-P1-001, owner-accepted).
- Recommended improvement: add a failure notification step; keep pins current via Dependabot.
- Suggested tests: assert `sudo -n true` fails on the PR runner label; assert the merge command pins the head commit.
- Suggested docs: record the 2026-10-11 green run in the reconciliation doc.

### Item: dependabot-merge workflow
- Evidence: `.github/workflows/dependabot-merge.yml:1-52`; run 38047609916.
- What it does: daily sweep merges `app/dependabot` PRs when checks are green and the owner applied `dependabot-approved`.
- Current controls: author restriction, label gate, concurrency (no cancel).
- Missing controls: `--match-head-commit`, minimal scopes, environment reviewers.
- Risks: TOCTOU merge; broad write token on a self-hosted runner (CI-P2-001); unexercised path (BP-P3-001).
- Recommended improvement: add `--match-head-commit`; reduce scopes; exercise once.
- Suggested tests: regression test on the merge command and permission set.
- Suggested docs: record the first exercised sweep.

### Item: external-smoke workflow
- Evidence: `.github/workflows/external-smoke.yml:1-68`; run 38067043888.
- What it does: daily iris/soc/enroll availability check.
- Current controls: concurrency; token endpoint allows non-5xx.
- Missing controls: a real Access-posture assertion (external vantage).
- Risks: Access regression undetected; artifact misstates verification (CI-P2-002).
- Recommended improvement: restore external vantage or rescope + fix text.
- Suggested tests: canary hostname with Access removed must fail.
- Suggested docs: record where Access posture is verified externally.

### Item: Actions governance settings
- Evidence: permissions endpoints; 0 environments; CODEOWNERS (BP report).
- Current controls: per-workflow permissions; zizmor; manual SHA pins.
- Missing controls: read-only default; PR-approval disable; selected actions; server SHA enforcement; environments.
- Risks: latent privilege for future workflows (CI-P2-003).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CI-001 | PR validation | validate.yml; run 38110410254 | fail-closed validate | no server enforcement; fork fallback dead | P3 | plan upgrade; fix fallback |
| CI-002 | Same-repo PR isolation | run 38109789930 (edge-builder) | none | pre-review code on sudo runner | P1 (owner-accepted) | non-sudo/ephemeral runner |
| CI-003 | Auto-merge integrity | dependabot-merge.yml:46-48 | label + green checks | TOCTOU; write scope | P2 | `--match-head-commit`; minimal scopes |
| CI-004 | Access-posture monitoring | external-smoke.yml:37-42; run 38067043888 | origin reachability only | Access bypass accepted | P2 | external vantage or rescope |
| CI-005 | Default token permissions | API | per-workflow blocks | repo default write | P2 | set read; disable PR approvals |
| CI-006 | Scheduled-run reliability | runs 37460608720 etc. | none | silent queue starvation; no notify | P3 | watchdog + notification |
| CI-007 | Workflow inventory | API 8 vs tree 3 | none | stale registrations | P3 | cleanup + inventory assertion |
| CI-008 | Incident playbook accuracy | playbook:268-272 | documented | stale tool-pin/run claims | P3 | append-only update |
| CI-009 | Delivery artifact publication | REPOSITORY.md:53; API artifacts/releases 0 | none | claim unbacked | P3 | add CI job or fix docs |

## Findings

### CI-P2-001 - Auto-merge workflow holds `contents: write` with no environment protection and no head-commit pin
- Severity: P2; Confidence: High; Area: CI; Status: still-open
- Evidence: dependabot-merge.yml:17-19,27,46-48; environments API 0; BRANCH_PROTECTION.md:95
- What is happening / why it matters / impact: see finding detail in the machine-readable output; the check-then-merge sequence can merge a commit that was never checked; the token is broader than needed and lives on the runner that executes PR code.
- Recommended fix / validation / owner / effort: add `--match-head-commit`; minimize scopes; environment reviewers when available; regression test. Owner: CI owner. Effort: S. Dependencies: none.

### CI-P2-002 - external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass
- Severity: P2; Confidence: High; Area: CI; Status: still-open
- Evidence: external-smoke.yml:3-6,23-26,37-42,64-67; run 38067043888 log
- Impact: an Access regression on iris/soc is undetectable; the artifact contradicts the check.
- Fix: external vantage or honest rescope; correct comments/summary. Owner: CI + Access owner. Effort: S-M.

### CI-P2-003 - Repository Actions settings default to permissive
- Severity: P2; Confidence: High; Area: CI; Status: still-open
- Evidence: API permissions endpoints.
- Fix: read default; disable Actions PR approval; consider selected actions + SHA enforcement. Owner: repo admin. Effort: S.

### CI-P3-001 - Hosted-runner fallback is dead; scheduled/queued workflow failures stay silent
- Severity: P3; Confidence: High; Area: CI; Status: still-open
- Evidence: validate.yml:26-28; external-smoke.yml:26; runs 37460608720/37616708114/37774326519; no notify wiring.
- Fix: remove/replace fallback; add watchdog/notification. Owner: CI owner. Effort: S.

### CI-P3-002 - Three probe workflows remain registered/active with no file on any branch
- Severity: P3; Confidence: High; Area: CI; Status: still-open
- Evidence: API workflow ids 374465077/374566273/374995041; tree.
- Fix: cleanup; inventory assertion. Owner: CI owner. Effort: S.

### CI-P3-003 - CI/CD incident playbook section 8 is stale on tool pinning and captured-run evidence
- Severity: P3; Confidence: High; Area: CI; Status: open (new)
- Evidence: playbook:268-272; validate.yml:45-73; run 38110410254.
- Fix: append-only update. Owner: CI owner. Effort: S.

### CI-P3-004 - Review package is documented as a CI/release artifact but no CI job builds or publishes it
- Severity: P3; Confidence: High; Area: CI; Status: open (new)
- Evidence: REPOSITORY.md:53; README.md:118; grep .github empty; API artifacts/releases 0.
- Fix: add a build/upload job or correct the docs. Owner: CI owner. Effort: S-M.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1 @ 08e20d1, statuses per the 2026-10-11 verification register)

| Prior finding | Prior status | Current verification (f5cb7c9, 2026-10-11) | Disposition |
|---|---|---|---|
| CI-P1-001 Same-repo PR workflows on passwordless-sudo self-hosted runner | owner-accepted | PR run 38109789930 still ran on `edge-builder`; runner host not reachable for a sudo re-probe; owner decision unchanged | still owner-accepted; not re-filed |
| CI-P2-001 Auto-merge write scope / no environment | open | dependabot-merge.yml unchanged (no `--match-head-commit`; environments 0) | re-filed as CI-P2-001 |
| CI-P2-002 external-smoke accepts bypass | open | run 38067043888 (2026-10-10) passed with 'owner-IP Access bypass'; summary stale | re-filed as CI-P2-002 |
| CI-P2-003 Permissive Actions defaults | open | API unchanged (write default, PR approvals true, allowed all, no SHA requirement) | re-filed as CI-P2-003 |
| CI-P2-004 Publication equality red after post-publication commits | verified-fixed | run 38110410254 step 14 green; local `verify_publication_chain.sh` 0 failures; digest bound to 3c11752 | verified-fixed holds |
| CI-P3-001 Hosted-runner dependency dead; scheduled failures silent | open | fork fallback still in validate.yml:28; three 24h queue cancellations; no notify wiring | re-filed as CI-P3-001 |
| CI-P3-002 Three stale probe workflow registrations | open | API still lists the three active registrations | re-filed as CI-P3-002 |
| Docs-vs-records drift (prior comparison residual: playbook section 8, SBOM doc) | open (documentation) | playbook section 8 still stale; SBOM doc stale (see SBOM report) | re-filed as CI-P3-003 / SBOM-P3-002 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Pre-review PR code on sudo runner | High | Low-Medium | host compromise | run 38109789930; probe SUDO_OK | owner-gated runner hardening |
| Auto-merge TOCTOU / broad write token | Medium | Low | unverified code on main | dependabot-merge.yml:46-48 | `--match-head-commit`; minimal scopes |
| Access regression undetected | Medium | Medium | public exposure regression | external-smoke.yml:37-42 | external vantage |
| Silent gate death / queue starvation | Medium | Medium | false confidence | cancelled runs; no notify | watchdog + notification |
| Permissive Actions defaults | Medium | Low | future workflow privilege | API settings | read default |
| Stale docs mislead incident response | Low | Medium | slower/mistaken response | playbook:268-272 | append-only update |

## Recommendations

### Immediate / Release Blocking
- None new (no P0/P1 current). CI-P1-001 remains owner-accepted.

### This Week
- CI-P2-001: add `--match-head-commit`; minimize token scopes.
- CI-P2-002: fix or rescope external-smoke; correct the summary text.
- CI-P2-003: set read-only default token permissions; disable Actions PR approval.

### This Month
- CI-P3-001: failure/queue watchdog for scheduled workflows; document the fork-PR policy.
- CI-P3-002: clean up stale workflow registrations; add an inventory assertion.
- CI-P3-003: append the current pin/run state to the incident playbook.
- CI-P3-004: add a package build/upload job or correct the delivery docs.

### Later / Platform Evolution
- Org runner groups restricted to selected workflows; ephemeral runners; `allowed_actions: selected` + `sha_pinning_required: true`; plan upgrade for required checks/environments.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `--match-head-commit` in the merge step | removes the TOCTOU window | dependabot-merge.yml | grep/regression test |
| Read-only default workflow permissions | default-deny for future workflows | repo settings (API/UI) | API returns read |
| Fix external-smoke summary text | artifact stops contradicting the check | external-smoke.yml:64-67 | run log matches assertion |
| Playbook section 8 update note | incident docs match reality | CI_CD_INCIDENT_PLAYBOOK.md | doc review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Non-sudo/ephemeral PR runners | P1 | platform | M | org runner group |
| Required checks + environments after plan upgrade | P2 | owner | S | GitHub Pro |
| Workflow inventory API-vs-tree check | P3 | CI owner | S | none |
| CI package build/upload job | P3 | CI owner | M | artifact storage |

## Suggested Tests

- CI regression: assert dependabot-merge.yml contains `--match-head-commit` and no unused write scope.
- Runner isolation test: a PR job asserts `sudo -n true` fails on the PR runner label.
- external-smoke canary: a known bypass URL must fail the strong assertion.
- Scheduled-workflow watchdog: force a failed/queued run and assert a notification/metric.
- Workflow inventory assertion: API workflow list equals the tree set.

## Suggested Documentation Updates

- `docs/security/CI_CD_INCIDENT_PLAYBOOK.md` section 8: append the 2026-10-11 state (tool pins applied; green validate runs captured; queue-starvation observation).
- `docs/security/CI_GOVERNANCE_RECONCILIATION.md`: append the 2026-10-11 run/permission/registry state.
- `REPOSITORY.md`/`README.md`: state the actual review-package delivery path (manual lab build) or implement the CI publication.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was sudo removed from `edge-builder` after 2026-10-04? | severity of CI-P1-001 today | runner host config or a re-probe |
| Which runner group(s) can access this repo's runners? | blast radius | org runner-group settings |
| Is the review package meant to be published by CI at all? | CI-P3-004 fix direction | owner statement |
| Does the weekly validate cron have an owner watching its result? | CI-P3-001 | alerting config/decision |

## Limitations

- Read-only audit: no workflow was dispatched or executed; runner host configuration (edge-builder/lab-runner-2) was not reachable from this host, so the sudo state could not be re-probed (prior probe 2026-10-04 stands).
- Org-level runner groups and billing state were not accessible.
- Workflow logs are untrusted data; only their factual content was used as evidence.

## Appendix

- Local reproduction commands (read-only): `PYTHONDONTWRITEBYTECODE=1 FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only compose-digests,sbom-vuln,sbom-hashes,license,secret-scan,credential-sourcing,digest-binding,publication-equality,lock-age` -> `validation_failures=0`; `bash automation/validation/verify_publication_chain.sh` -> `publication_chain_failures=0`.
- Validate run at f5cb7c9: 75 PASS lines, 0 FAIL, 50 suites, runner `edge-builder`.

## Findings

| ID | Severity | Title |
|---|---|---|
| CI-P2-001 | P2 | Auto-merge workflow holds `contents: write` with no environment protection and no head-commit pin |
| CI-P2-002 | P2 | external-smoke no longer asserts Cloudflare Access posture and passes on an owner-IP bypass |
| CI-P2-003 | P2 | Repository Actions settings default to permissive (write token, PR approvals, any action, no SHA-pin requirement) |
| CI-P3-001 | P3 | Hosted-runner fallback is dead; scheduled/queued workflow failures stay silent |
| CI-P3-002 | P3 | Three probe workflows remain registered/active with no file on any branch |
| CI-P3-003 | P3 | CI/CD incident playbook section 8 is stale on tool pinning and captured-run evidence |
| CI-P3-004 | P3 | Review package is documented as a CI/release artifact but no CI job builds or publishes it |
