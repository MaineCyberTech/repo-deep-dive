# GitHub Actions, CI/CD, and Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: MaineCyberTech/mainecybertech (read-only clone at `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (Merge PR #168: promote develop to main)
- Generated at: 2026-10-11
- Auditor: domain subagent `10_github_actions_cicd_governance` (area `CI`)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/10_github_actions_cicd_governance.md`
- Scope limitations: read-only; no `gh` API access, so live branch-protection settings, environment protection rules, secrets, and Actions run history are **not** verifiable from the repo. No node/npm/actionlint/shellcheck/gitleaks binaries in the audit container, so guards that need execution were re-derived by reading the parser/scripts (recorded below). The target repo was never modified.

## Scope

Reviewed: all 20 files in `.github/workflows/`, all 4 composite actions in `.github/actions/`, `.github/branch-protection/{main,develop}.json`, `.github/CODEOWNERS`, `.github/dependabot.yml`, `.github/actionlint.yaml`, `.github/restore-test-baseline.env`, `.gitleaks.toml`, `scripts/check-required-checks.mjs`, `scripts/scan-secrets.sh`, `scripts/ci/verify-gitleaks-config.sh`, `scripts/ci/generate_badges.py`, and the CI/release docs (`docs/CI.md`, `docs/RELEASING.md`, `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, plus README/AGENTS/review workflow tables).

Not reviewed: live GitHub state (branch protection as applied, environment reviewers/secrets, run history, Dependabot PR queue), GHCR image contents, and the workflows' runtime results.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github/workflows/*.yml` (20 files, 3,086 lines) | Workflows | Full trigger/permission/gate inventory | All read in full |
| `.github/actions/*/action.yml` (setup-pnpm, unit-tests, dependency-audit, secret-scan) | Composite actions | Shared PR/deploy gate steps | test.yml and validate.yml share them |
| `.github/branch-protection/main.json`, `develop.json` | Governance config | Required checks, reviews, bypass settings | Committed payload; live application unverifiable |
| `scripts/check-required-checks.mjs` | Guard | Name parity between required checks and emitted check-runs | Wired in `validate.yml:33-39` |
| `.github/CODEOWNERS` | Governance config | Code-owner reviews enforced by branch protection | Teams must exist live |
| `.github/dependabot.yml` | Supply chain | npm/github-actions/docker/terraform update coverage | target-branch develop |
| `.github/actionlint.yaml` | Lint config | actionlint runner labels | Config exists; no CI job runs it |
| `.gitleaks.toml`, `scripts/ci/verify-gitleaks-config.sh`, `secret-history-scan.yml` | Secrets | Full-history scan + allowlist proof | Weekly schedule |
| `docs/CI.md`, `docs/RELEASING.md`, `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` | Docs | Claims to verify against config | Several drift points found |

## Verification Performed

| Evidence / command (read-only) | Type | Why relevant | Observed result |
|---|---|---|---|
| `git log -1` / `git merge-base --is-ancestor 031186ad 8d299b8d` | Git | Main vs develop state (CI-P3-004) | develop tip is ancestor of main → main carries develop work |
| `git log --diff-filter=D -- .github/workflows/wireguard-endpoint.yml` | Git | Firewall workflow removal (CI-P2-001) | `52304944 chore(ci): remove one-time DO firewall workflow` |
| `grep -rn 'pull_request_target\|workflow_run' .github/` | Static | Dangerous trigger check | No matches |
| `grep -rn 'uses:.*@(v[0-9]\|main\|master\|latest)' .github/` | Static | Unpinned action check | No matches — all `uses:` are 40-char SHAs (plus local composites) |
| `grep -c 'timeout-minutes' .github/workflows/*.yml` | Static | Timeout hygiene (CI-P3-010) | 9 workflows have zero; validate.yml's audit/lint/typecheck/prompt-provenance jobs lack one |
| `grep -rn '>> $GITHUB_OUTPUT' .github/workflows` | Static | SC2086 residual (CI-P3-001) | 14 unquoted appends remain (deploy-do.yml:91-99,181; terraform-do.yml:58,60,236,276) |
| `grep -rn 'actions: write' .github/` | Static | Over-broad scope (CI-P3-002) | Only a comment remains |
| `grep -rn 'security-events\|upload-sarif' .github/` | Static | Unused scope (CI-P3-006) | test.yml:18 grants it; Trivy SARIF is artifact-only |
| Manual parity walk of `main.json` contexts vs workflow name/job/matrix | Static | check-required-checks without node | All 5 contexts match emitted names; node not installed so the script was not executed |
| Read `.github/workflows/e2e.yml` triggers vs `main.json` required contexts | Static | Path-filtered required check (new) | E2E required on main but `pull_request` is path-filtered |
| Read `backup-dispatch.yml` + backup workflows triggers vs default branch | Static | Duplicate schedules (new) | Dispatcher and the workflows themselves both scheduled on main |
| Read docs tables vs `ls .github/workflows` | Static | Docs-vs-tree drift (new) | Docs list removed `wireguard-endpoint.yml`; omit `secret-history-scan.yml` |

## Executive Summary

The CI/CD estate at `8d299b8d` is well above the baseline for a repo of this size: 20 workflows, every external action pinned to a commit SHA, least-privilege `permissions` on every workflow, per-ref concurrency groups (deploys never cancelled mid-flight), composite actions shared between the PR gate and the deploy gate, provenance/SBOM attestations verified fail-closed before deploy, a pre-push migration dry-run plan uploaded as an artifact, and a restore test that asserts integrity floors rather than printing numbers. The branch-protection payload was corrected and is guarded by `check-required-checks.mjs`, which closes the previous P1 class.

The remaining risks are mostly *operator-gated settings* and *drift classes the guards do not cover*:

1. **The prod approval gate is still not in force** (CI-P1-001): the workflow attaches `prod-approval`, but the docs themselves state no reviewers are configured; prod migrations additionally depend on reviewers on `prod`. Combined with the unprovisioned prod secrets (CI-P1-003), production is effectively not deployable by design — safe, but not releasable.
2. **E2E is required on `main` but path-filtered** (new, P2): a docs-only or API-only PR can never satisfy the required check. test/lint/typecheck were fixed for exactly this (BP-P2-004); e2e was missed.
3. **The backup dispatcher now duplicates schedules** (new, P2): the DR-P0-001 fix promoted the backup workflows to main, but `backup-dispatch.yml` still dispatches copies onto develop.
4. **Two smaller verification rows changed state on re-check**: the terraform drift plan is dormant behind `TF_DRIFT_PLAN_ENABLED` (partially-fixed, not fixed), and the actionlint lint fixes are incomplete with no workflow-lint gate (partially-fixed).

Recommended next actions: configure `prod-approval`/`prod` reviewers and prod secrets (operator); remove the e2e `paths:` filter on `pull_request`; retire the backup dispatcher; enable the terraform drift variable after token rotation; and wire a real workflow-lint job.

## Inventory

| Workflow | Triggers | Gate role | Notable controls |
|---|---|---|---|
| `test.yml` | PR main/develop, dispatch | Blocking on PR (required) | unit-tests + guards, dependency audit, license gate, Trivy fs, diff secret scan |
| `lint.yml` / `typecheck.yml` | PR main/develop, dispatch | Blocking on PR (required) | pnpm lint / typecheck; no `paths:` (BP-P2-004) |
| `e2e.yml` | PR main/develop (path-filtered), `workflow_call`, dispatch | Required on main; prod deploy gate | Playwright + axe, local Supabase; **path-filtered on PR** |
| `validate.yml` | `workflow_call` only | Shared deploy gate | audit, tests+guards, secrets-scan, lint, typecheck, prompt provenance, required-check parity |
| `deploy-do.yml` | push main/develop (path-filtered), dispatch | Deploy | 3 image builds + Trivy image scans + SBOM/provenance attestations, `verify-attestations` fail-closed, prod-only e2e/migrate gates, `prod-approval` env, health gate + auto-rollback |
| `supabase-migrations.yml` | push main/develop (`supabase/**`), `workflow_call`, dispatch | Migrate gate (prod) | pre-push dry-run plan artifact, post-push drift gate, `prod`/`dev` env, serialized |
| `terraform-do.yml` | schedule (dormant), dispatch | Manual | plan→apply input, world-open SSH rejection, `prod-approval` apply, fail-on-drift step (gated) |
| `build-push.yml` | dispatch only | Manual | same image scan/SBOM/provenance pipeline |
| `codeql.yml` | push+PR main/develop, weekly, dispatch | SAST | security-and-quality, `security-events: write` |
| `dependency-review.yml` | PR main/develop | Required on main | high severity + license deny list |
| `sbom.yml` | push+PR, weekly, dispatch | Artifact-only | lockfile CycloneDX, commit-bound, validated |
| `chromatic.yml` | push+PR (`packages/ui/**`) | Best-effort | **`continue-on-error: true`** |
| `a11y-breadth.yml` | weekly, dispatch | Triage | calls e2e with `a11y_full` |
| `db-backup.yml` / `storage-backup.yml` / `db-restore-test.yml` | schedules, dispatch | Scheduled DR | encrypted backups, restore integrity floors, ntfy/Slack alerts |
| `backup-dispatch.yml` | 3 schedules, dispatch | Scheduled dispatcher | dispatches backups `--ref develop`; **now duplicates** |
| `secret-history-scan.yml` | weekly, dispatch | Scheduled security | gitleaks full history, pinned+checksummed, allowlist fixture |
| `secret-rotation-reminder.yml` | quarterly, dispatch | Governance | deduplicated rotation issue |

Composite actions: `setup-pnpm` (node+corepack+cache+install), `unit-tests` (coverage + 8 guards), `dependency-audit` (audit+license+untracked-artifact guard+Trivy fs), `secret-scan` (diff + tracked-secret-file guard).

Other governance files: 2 branch-protection JSONs (5 required checks on main, 3 on develop; enforce_admins, code-owner reviews), CODEOWNERS with 7 teams, Dependabot (npm + github-actions + docker×5 + terraform, target develop), `.gitleaks.toml`, restore-test baseline, actionlint config.

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| .github/workflows | 4 | 20 workflows, SHA-pinned actions, per-workflow permissions, concurrency, composites | No workflow-lint job; 9 workflows lack timeouts | Add actionlint job; add timeouts |
| PR validation | 4 | Required checks on both branches; shared composites; no paths filter on test/lint/typecheck | E2E path-filtered while required on main | Remove e2e paths filter on `pull_request` |
| Lint/typecheck/test/build | 4 | `pnpm lint`/`typecheck`/`test:coverage` + 8 schema/docs guards in both gates | Guards not run for workflow YAML/shell | actionlint + shellcheck job |
| Deploy workflows | 4 | Fail-closed gate, attestation verification, health gate + auto-rollback, queued concurrency | Prod approval + secrets not provisioned (operator) | Operator provisioning; verify with a dispatch |
| Migration workflows | 4 | Dry-run plan artifact, post-push drift gate, serialized, pinned CLI | Prod runs under `prod` env without reviewers | Add reviewers or move to `prod-approval` |
| Docker build/push | 4 | Trivy image scan CRITICAL/HIGH, digest-bound SBOM + provenance, verified pre-deploy | `postgres:16-alpine` in restore test unpinned | Pin by digest |
| Releases | 2 | SHA-as-release documented; SBOM commit binding | No tag/release workflow or artifact | Add release workflow or record decision |
| Badge/report generation | 1 | `generate_badges.py` stub only; README badges static | Not wired; stub cannot run (no `dashboards/`) | Delete stub or implement real report step |
| Secrets | 4 | diff scan with event.before, full-history gitleaks weekly, tracked-file guard, rotation reminder | Diff scanner lacks platform token formats; history scan weekly | Extend patterns; document coverage |
| permissions blocks | 4 | Workflow-level least privilege; job-level re-scope in verify-attestations | `security-events: write` (test), `pull-requests: write` (terraform-do) unused | Drop unused scopes |
| OIDC | 3 | `id-token: write` used for attestations; no cloud OIDC trust configured | Cloud auth still long-lived DO/CF tokens | Consider OIDC for cloud providers (later) |
| Environment protection | 3 | `prod-approval` on deploy + terraform apply; `prod`/`dev` env separation; fail-closed deploy | Reviewers/secrets not configured (operator); no drift check | Configure environments; add live drift check |

## Detailed Review

### Item: Required-check gate map (what each check executes)

- Evidence: `.github/branch-protection/main.json:4-10`, `develop.json:4-8`; `test.yml:26-65`; `lint.yml:21-37`; `typecheck.yml:21-32`; `e2e.yml:39-182`; `dependency-review.yml:10-30`; `.github/actions/unit-tests/action.yml:21-63`.
- What it does: `Test / test (20.x)` runs the coverage suite plus OpenAPI validation/audit, docs counts/links, DB-type freshness, RLS hygiene, membership-predicate lint and review.md mirror, plus audit/license/Trivy/secrets jobs. `Lint` and `TypeCheck` run the workspace commands. `E2E / e2e (20.x)` boots local Supabase + API + web and runs Playwright/axe. `Dependency Review / review` blocks high-severity and denied licenses on the PR diff.
- Drift classes the required checks do **not** cover: path-filtered workflows that never report (E2E — new finding); committed-vs-live branch protection drift (BP-P2-003, owned by the branch-protection domain); workflow YAML/shell lint (no actionlint job); docs-vs-tree drift (new finding).
- Bypass analysis: `enforce_admins: true`, `allow_force_pushes: false`, `allow_deletions: false`, `required_conversation_resolution: true` in both JSONs. There is no `pull_request_target`/`workflow_run` anywhere, and `[skip ci]` on a PR leaves required checks pending (blocks, not bypasses). The remaining bypass vector is repo-admin mutation of the protection payload itself, which has no in-repo audit (BP-P2-002/003 domain).

### Item: Deploy flow (deployment flow)

- Evidence: `deploy-do.yml:16-43` (push to main/develop + dispatch), `:101-182` (resolve-ip from DO API → TF state → var), `:184-380` (3 builds + Trivy image scan + digest-bound SBOM + provenance attestation), `:391-515` (`verify-attestations` fail-closed incl. reviewed legacy rollback allow-list), `:517-535` (validate always; e2e+migrate prod-only), `:537-571` (fail-closed `needs` expression, `prod-approval`), `:575-935` (SSH deploy, `.env` via printf, health gate, auto-rollback, host-key-pinned health check).
- Deployment flow: push/merge to `main` (or dispatch `deploy_target=prod`) → setup → resolve-ip (`prod` env) → build×3 ∥ validate → e2e+migrate (prod only) → verify attestations → deploy (`prod-approval`, health-gated, auto-rollback). Dev (`develop`) skips e2e/migrate and uses the `dev` environment.
- Missing controls: the approval pause itself depends on GitHub environment settings (CI-P1-001); prod secrets are unprovisioned (CI-P1-003).

### Item: Migration flow

- Evidence: `supabase-migrations.yml:21-25` (serialized per ref), `:30-34` (`prod` env on main), `:57-60` (CLI pinned 2.107.0), `:67-83` (pre-push `db push --dry-run` teed + artifact before the real push), `:90-127` (post-push `db diff` gate, ANSI-stripped, `allow_drift=1` only on reviewed dispatch).
- Assessment: this is a strong flow (IR-P2-006/IR-P1-002/DATA-P2-004 fixes verified). Residual: approval depends on reviewers configured on the `prod` environment, which the matrix says are not set.

### Item: Secrets handling

- Evidence: `secret-scan/action.yml:14` (provider pattern list), `:15-27` (event.before on push, base.sha on PR), `:43-62` (tracked local-secret-file guard); `secret-history-scan.yml:27-51` (gitleaks 8.30.1 pinned + SHA-256 verified, full history, redacted, allowlist negative test); `.gitleaks.toml` (scoped allowlists only); `secret-rotation-reminder.yml` (quarterly issue); deploy secrets forwarded via `envs:`/`printf` and never interpolated into remote shell text (`deploy-do.yml:644-716`).
- Residual: diff-scanner formats are a fixed provider list; full-history scan is weekly, not per-commit.

### Item: Permissions, OIDC, concurrency, caching, artifacts

- Permissions: least-privilege at workflow level; `verify-attestations` re-scopes to read (`deploy-do.yml:399-406`). Unused `security-events: write` (test.yml:18) and `pull-requests: write` (terraform-do.yml:26) remain.
- OIDC: `id-token: write` only for attestations (`deploy-do.yml:34`, `build-push.yml:15`); no cloud OIDC trust (DO/CF still token-based).
- Concurrency: per-ref groups everywhere it matters; deploys (`cancel-in-progress: false`) and migrations/terraform are serialized; PR runs cancel superseded (`test/lint/typecheck/e2e/sbom/chromatic/codeql`).
- Caching: pnpm store keyed on lockfile (`setup-pnpm/action.yml:38-47`), Playwright browser cache (`e2e.yml:55-62`), buildx `type=gha` caches.
- Artifacts: dry-run plan before push, Trivy SARIF (7d), SBOMs (30d), Playwright reports on failure (7d), tfplan (1d); retention set on all.

### Item: Branch protection, CODEOWNERS, Dependabot

- Evidence: `main.json`/`develop.json` (above); `check-required-checks.mjs` wired into `validate.yml:33-39`; `CODEOWNERS:1-44`; `dependabot.yml:1-102` (npm/github-actions/docker×5/terraform, weekly, target develop).
- Recommendations: apply the JSON (repo-admin) and add a scheduled live-vs-committed drift check; consider `github-actions` grouped updates to keep SHA pins fresh.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| CI-001 | Workflow inventory/triggers | 20 workflows; `pull_request_target`/`workflow_run` absent | SHA-pinned, least privilege | No workflow-lint gate | P3 | actionlint job |
| CI-002 | PR validation / required checks | `branch-protection/*.json`, `check-required-checks.mjs` | 5 contexts on main, 3 on develop; parity guard | E2E path-filtered (new) | P2 | Remove e2e paths filter |
| CI-003 | Lint/typecheck/test/build | `test.yml`, `validate.yml`, composites | Shared gates, 8 repo guards | No YAML/shell lint; timeouts missing | P3 | Add actionlint + timeouts |
| CI-004 | Deploy workflows | `deploy-do.yml` | Fail-closed, attestation-verified, auto-rollback | Approval/reviewers unset | P1 | Configure `prod-approval` |
| CI-005 | Migration workflows | `supabase-migrations.yml` | Dry-run artifact + drift gate | `prod` env reviewers unset | P1 | Configure `prod` |
| CI-006 | Docker build/push | `deploy-do.yml`, `build-push.yml` | Trivy + SBOM + provenance | Restore-test image unpinned | P3 | Pin digest |
| CI-007 | Releases | 20 workflows, none release/tag | SHA-as-release documented | No tag/release artifact | P3 | Add release workflow or record decision |
| CI-008 | Badge/report generation | `generate_badges.py` stub | None (static badges) | Not wired; stub broken | P3 | Delete or implement |
| CI-009 | Secrets | `secret-scan`, `secret-history-scan` | diff scan + weekly full history | Formats gap; weekly cadence | P3 | Extend patterns |
| CI-010 | Permissions blocks | grep results | Workflow-level least privilege | 2 unused write scopes | P3 | Drop unused scopes |
| CI-011 | OIDC | `id-token: write` for attestations | Attestation signing | No cloud OIDC trust | P3 | Evaluate later |
| CI-012 | Environment protection | `deploy-do.yml:571`, `terraform-do.yml:202` | `prod-approval` attached | Reviewers unset (operator) | P1 | Configure reviewers |
| CI-013 | Backup scheduling | `backup-dispatch.yml` + backup workflows | Dispatcher + native schedules | Duplicate runs (new) | P2 | Keep one trigger source |

## Findings

Statuses: 25 findings — 3 P1 (1 verified-fixed, 2 still-open), 10 P2 (5 verified-fixed, 2 partially-fixed, 1 still-open, 2 new/open), 12 P3 (3 verified-fixed, 2 partially-fixed, 5 still-open, 2 new/open). Full evidence, impact and recommendation text for every row is in `10_github_actions_cicd_governance.json`; the blocks below summarize the P1/P2 rows and the new findings, then tabulate the P3 verification rows.

### CI-P1-001 (carried) — Production application deploys have no working manual-approval gate

- Severity: P1 · Confidence: high · Status: still-open · Owner: platform/CI owner · Target: this week
- Evidence: `deploy-do.yml:565-571` attaches `prod-approval`; `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:16-19` "none are configured yet"; `docs/RELEASING.md:96-105` "no working manual-approval gate"; `supabase-migrations.yml:28-34` prod migrations depend on reviewers on `prod`.
- Why it matters: without the environment reviewers, a merge to main reaches production (and prod migrations) with no human pause.
- Recommended fix: operator configures 1+ reviewers on `prod-approval` and `prod`, then dispatches a prod deploy and confirms the pause.

### CI-P1-002 (carried) — Branch-protection-as-code has a likely-mismatched required check and permits admin bypass

- Severity: P1 · Confidence: high · Status: verified-fixed · Owner: platform/CI owner · Target: this week
- Evidence: `main.json:4-17`, `develop.json:4-19`; `validate.yml:33-39` runs `scripts/check-required-checks.mjs`; manual walk confirms all 5 contexts match emitted check-runs; `enforce_admins: true`.
- Residual: live application is a repo-admin action; no live drift check (owned by the branch-protection domain).

### CI-P1-003 (carried) — Production deploy path cannot run; prod environment lacks secrets and protection rules

- Severity: P1 · Confidence: high · Status: still-open · Owner: @owner · Target: this week
- Evidence: `docs/RELEASING.md:140-147`; `deploy-do.yml:577-637` consumes ~50 environment secrets; matrix checklist `:142-151`.
- Why it matters: production is intentionally not deployable until the operator provisions environments; safe but release-blocking.

### CI-P2-001 (carried) — World-open DigitalOcean firewall mutation with no approval and unvalidated udp_port

- Severity: P2 · Confidence: high · Status: verified-fixed
- Evidence: no wireguard/firewall workflow in the 20-file workflow dir; removal commit `52304944`. Residual doc drift is the new docs finding.

### CI-P2-002 (carried) — Deploy-gate secret scan is a no-op on pushes to main

- Severity: P2 · Confidence: high · Status: verified-fixed
- Evidence: `secret-scan/action.yml:15-27` now diffs `github.event.before` with a zero-SHA fallback; used by both `validate.yml:57-70` and `test.yml:54-65`.

### CI-P2-003 (carried) — Production approval environment documented as having no required reviewers

- Severity: P2 · Confidence: high · Status: verified-fixed
- Evidence: matrix `:16-19` and `RELEASING.md:96-105` now state the truth; the operational gap is tracked under the two P1s.

### CI-P2-004 (carried) — DB restore test reports success without asserting restore integrity

- Severity: P2 · Confidence: high · Status: verified-fixed
- Evidence: `db-restore-test.yml:135-232` fails on table/migration/row/freshness/RLS floors; baseline committed at `.github/restore-test-baseline.env`.

### CI-P2-005 (carried) — Infrastructure changes are no longer gated in CI (terraform-do is manual-dispatch only)

- Severity: P2 · Confidence: high · Status: partially-fixed
- Evidence: `terraform-do.yml:3-21` manual-only; `:99-110` rejects world-open SSH; `:198-236` prod apply behind `prod-approval`. Residual: PR/push plan triggers remain off pending DO token rotation + environment protection.

### CI-P2-006 (carried) — Chromatic visual-regression job is permanently non-blocking

- Severity: P2 · Confidence: high · Status: still-open
- Evidence: `chromatic.yml:20-28` job-level `continue-on-error: true`; not in any required-check list; `AGENTS.md:635` falsely claims the opposite.

### CI-P2-007 (carried) — Branch protection permits admin bypass and ignores CODEOWNERS

- Severity: P2 · Confidence: high · Status: verified-fixed
- Evidence: both JSONs set `enforce_admins: true`, `require_code_owner_reviews: true`, `allow_force_pushes/deletions: false`.

### CI-P2-008 (carried) — Terraform apply is manual and drift detection is not automated

- Severity: P2 · Confidence: high · Status: partially-fixed (downgraded from the register's verified-fixed)
- Evidence: `terraform-do.yml:36-38` skips the scheduled plan unless `vars.TF_DRIFT_PLAN_ENABLED == 'true'`; `:161-172` fails on a non-empty plan when it does run; `docs/CI.md:104-107` confirms dormancy. Residual: enable the variable after token rotation.

### NEW — E2E is a required check on main but path-filtered, so PRs that miss its paths can never satisfy branch protection

- Severity: P2 · Confidence: medium · Status: open · Owner: platform/CI owner · Target: this month
- Evidence: `main.json:8` requires `E2E / e2e (20.x)`; `e2e.yml:12-22` path-filters `pull_request`; `test.yml:10-12` records the same class (BP-P2-004) fixed for test/lint/typecheck only — this is the concrete residual for e2e.yml (BP-P2-004 is also tracked by the branch-protection domain).
- Why it matters: docs-only or API-only PRs to main stay blocked on a check that will never report.
- Recommended fix: drop the `paths:` filter on `pull_request` (or make E2E non-required / add a reporting companion job); extend the required-check guard to flag path-filtered required workflows.

### NEW — Backup dispatcher duplicates the backup workflows now that they exist on the default branch

- Severity: P2 · Confidence: medium · Status: open · Owner: platform/CI owner · Target: this month
- Evidence: `backup-dispatch.yml:21-25,85-93` schedules + dispatches `--ref develop`; `db-backup.yml:3-4`, `storage-backup.yml:19-20`, `db-restore-test.yml:3-4` have the same schedules and are all on main; the dispatcher header (`:3-9`) explains it predates the promotion (DR-P0-001, PR #93).
- Why it matters: each DR job now runs twice (main + dispatched develop), duplicating dumps/mirrors/restore tests; an unset `SCHEDULE_DISPATCH_TOKEN` produces daily red runs while the real backup may succeed.
- Recommended fix: keep one trigger source — delete the dispatcher or the three schedule blocks; document the choice.

### P3 verification rows (tabulated)

| Previous row | Title | Status at 8d299b8d | Key evidence / residual |
|---|---|---|---|
| CI-P3-001 | actionlint/shellcheck workflow lint issues | partially-fixed | `actionlint.yaml` exists; 14 unquoted `>> $GITHUB_OUTPUT` remain; no actionlint job in CI |
| CI-P3-002 | Over-broad workflow token permissions (unused write scopes) | verified-fixed | no `actions: write` remains; residual scopes tracked in CI-P3-006 |
| CI-P3-003 | StrictHostKeyChecking=no in the deploy health check | verified-fixed | `deploy-do.yml:883-891` uses `StrictHostKeyChecking=yes` + pinned known_hosts |
| CI-P3-004 | `main` far behind `develop`; schedules only from default branch | verified-fixed | develop tip is ancestor of main; backup workflows present on main; new dispatcher duplication finding |
| CI-P3-005 | Secret scanner misses platform formats; diffs only | partially-fixed | weekly full-history gitleaks added; diff scanner provider list unchanged |
| CI-P3-006 | Unused permission grants across deploy/test workflows | still-open | `test.yml:18` `security-events: write`; `terraform-do.yml:26` `pull-requests: write` + unreachable PR-comment step |
| CI-P3-007 | DB restore test uses unpinned `postgres:16-alpine` | still-open | `db-restore-test.yml:116` |
| CI-P3-008 | No release/tagging workflow and no post-merge release artifact | still-open | 20 workflows, none release/tag; `RELEASING.md:47-53` SHA-as-release |
| CI-P3-009 | e2e required on main but flaky | still-open | `main.json:8`; `AGENTS.md:93`; `RELEASING.md:148-150` |
| CI-P3-010 | Missing per-job timeouts and minor hygiene gaps | still-open | 9 workflows with zero timeouts; validate.yml's audit/lint/typecheck/prompt-provenance lack one |
| NEW | Workflow documentation drift (removed/omitted/misstated workflows) | open | README/AGENTS/review/docs/CI list `wireguard-endpoint.yml`; `secret-history-scan.yml` omitted; a11y/Chromatic claims wrong |
| NEW | Badge/report generation is a stub and not wired into CI | open | `scripts/ci/generate_badges.py:1-8`; no `dashboards/`; no workflow reference |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unattended prod change (no reviewer gate) | P1 | Medium (requires merge-capable account) | Prod deploy/migrations without human pause | `deploy-do.yml:571`, matrix:16-19 | Configure `prod-approval` + `prod` reviewers |
| Prod release blocked on unprovisioned secrets | P1 | High | Cannot release | `RELEASING.md:140-147` | Provision environments |
| Docs-only PR to main blocked forever | P2 | High | Merge friction, possible unsafe workarounds | `e2e.yml:12-22`, `main.json:8` | Remove e2e paths filter |
| Duplicate DR jobs / false failure signal | P2 | Medium | Wasted runs; alert fatigue on backup path | `backup-dispatch.yml` + backups | Retire one trigger source |
| Visual regressions never gate | P2 | Medium | UI regressions ship | `chromatic.yml:28` | Fix Storybook, then require |
| Drift undetected (infra, branch protection) | P2 | Medium | Silent divergence from as-code | `terraform-do.yml:38`; no live BP check | Enable drift var; add live BP check |
| Workflow YAML/shell errors unguarded | P3 | Low | Broken workflow lands on default branch | no actionlint job | Add workflow-lint job |

## Recommendations

### Immediate / Release Blocking

- Configure 1+ required reviewers on `prod-approval` **and** `prod`, then verify a prod deploy pauses (CI-P1-001).
- Provision prod/prod-approval secrets per the matrix so the documented promotion path can run (CI-P1-003).

### This Week

- Remove the `paths:` filter from `e2e.yml`'s `pull_request` trigger (or add a reporting companion job) so the required check always reports.
- Decide the backup trigger source and retire `backup-dispatch.yml` or the duplicate schedule blocks.
- Rotate `DO_API_TOKEN`, set `TF_DRIFT_PLAN_ENABLED=true`, set `ADMIN_IP_RANGES`, then re-enable plan-only PR runs for terraform.

### This Month

- Add an actionlint (+ shellcheck) job and quote the remaining 14 `GITHUB_OUTPUT` appends.
- Drop `security-events: write` from `test.yml` and `pull-requests: write` from `terraform-do.yml` (or make them real).
- Update the workflow tables in docs/CI.md, README.md, AGENTS.md and review.md; add a docs-vs-tree workflow check.
- Pin `postgres:16-alpine` by digest in `db-restore-test.yml`.
- Add explicit `timeout-minutes` to the 9 workflows/jobs lacking them.

### Later / Platform Evolution

- Release/tag workflow (annotated tag + SBOM + release-notes body) or a recorded owner decision for SHA-only releases.
- Extend the diff secret scanner to platform token formats or run gitleaks on the diff.
- Evaluate cloud OIDC (DigitalOcean/Cloudflare) to retire long-lived tokens.
- Replace or delete the badge/report stub.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Remove e2e PR paths filter | Unblocks required check for all PRs | `e2e.yml:12-22` | Open a docs-only PR; check E2E reports |
| Delete `security-events: write` | Least privilege | `test.yml:16-18` | actionlint/review; Trivy artifact still uploads |
| Delete unreachable terraform PR-comment step + scope | Removes dead code and unused grant | `terraform-do.yml:23-26,138-152` | actionlint |
| Quote GITHUB_OUTPUT appends | Clears SC2086 residual | `deploy-do.yml:91-99,181`; `terraform-do.yml:58,60,236,276` | shellcheck |
| Update stale doc rows | Operators stop chasing removed workflow | `docs/CI.md`, `README.md:326`, `AGENTS.md:300,635`, `review.md:306`, `RELEASING.md:149` | Docs review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Enable required reviewers on `prod-approval`/`prod` and verify pause | P1 | platform/CI owner | S | GitHub admin |
| Provision prod environment secrets | P1 | @owner | M | Operator access |
| Remove e2e paths filter | P2 | platform/CI owner | S | None |
| Retire backup dispatcher or duplicate schedules | P2 | platform/CI owner | S | Confirm preferred trigger source |
| Enable terraform drift plan + rotate token | P2 | platform/CI owner | S/M | DO token rotation |
| actionlint/shellcheck CI job | P3 | platform/CI owner | S | None |
| Drop unused permission scopes | P3 | platform/CI owner | S | None |
| Pin restore-test postgres digest | P3 | platform/CI owner | S | None |
| Per-job timeouts | P3 | platform/CI owner | S | None |
| Release/tag workflow | P3 | platform/CI owner | M | Owner decision |
| Live branch-protection drift check | P3 | repo admin | M | Admin token |
| Badge/report step or deletion | P3 | platform/CI owner | S/M | None |

## Suggested Tests

- **CI/regression:** a synthetic PR that touches only `docs/**` must still produce the `E2E / e2e (20.x)` check-run (proves the paths fix).
- **CI/regression:** run `node scripts/check-required-checks.mjs` in validate (already) and extend it with a test fixture containing a path-filtered workflow + required context, expecting failure.
- **CI/security:** a synthetic secret pushed directly to a scratch branch must fail the deploy-gate secret scan; a platform-format token (e.g. `mct_`-style) must fail the diff scanner.
- **CI/supply chain:** `gh attestation verify` on each built digest must fail for an image built by a different workflow (negative test of the signer-workflow pin).
- **CI/DR:** assert the backup dispatcher does not create a second run for a workflow already scheduled on the default branch (or remove the dispatcher and assert single-run cadence from run history).
- **CI/hygiene:** actionlint + shellcheck over `.github/` with zero findings; assert every job declares `timeout-minutes` via a small script.

## Suggested Documentation Updates

- `docs/CI.md`: regenerate the workflow table (remove `wireguard-endpoint.yml`, add `secret-history-scan.yml`); correct the a11y `continue-on-error` claim; document the e2e path-filter decision and the backup trigger decision.
- `README.md:326`, `AGENTS.md:300,635`, `review.md:306`: remove the removed workflow and fix the Chromatic claim.
- `docs/RELEASING.md:149`: drop the stale "main is far behind develop" line; add the backup-trigger and drift-var decisions when made.
- `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`: add a "last verified" date column for the environment reviewer/secret checklist.
- New: `docs/CI_GATE_MAP.md` (or a section in `docs/CI.md`) mapping each required check to the exact steps it executes and the drift classes it does not cover.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the live branch protection identical to the committed JSON (enforce_admins, contexts, code-owner reviews)? | The repo only proves the intended payload | `gh api repos/.../branches/main/protection` output |
| Are `prod`/`prod-approval` required reviewers and prod secrets configured? | Decides whether prod deploys can run/pause | GitHub Environments settings screenshot/API |
| Is `SCHEDULE_DISPATCH_TOKEN` set, and which backup runs actually fire on main vs develop? | Confirms/denies duplicate DR runs | Actions run history for the 3 backup workflows |
| Is the default branch really `main` (docs claim it; origin HEAD says main)? | Scheduled-trigger semantics depend on it | Repo settings |
| Was the e2e path filter on `pull_request` intentional? | Determines fix (remove filter vs companion job) | PR/commit discussion |
| Does `@mainecybertech/*` team membership still satisfy code-owner reviews? | CODEOWNERS is only advisory if teams are empty | Org team membership |

## Appendix

### A. Command log (read-only)

```
git log -1 --format='%H %ci %s'                     # 8d299b8d ... Merge PR #168
git merge-base --is-ancestor 031186ad 8d299b8d      # true (develop tip in main)
git log --oneline --diff-filter=D --all -- .github/workflows/wireguard-endpoint.yml
                                                    # 52304944 chore(ci): remove one-time DO firewall workflow
grep -rn 'pull_request_target|workflow_run' .github/            # no matches
grep -rn 'uses:.*@(v[0-9]|main|master|latest)' .github/         # no matches (all SHA-pinned)
grep -rn '>> \$GITHUB_OUTPUT' .github/workflows                 # 14 unquoted appends
grep -rn 'actions: write' .github/                              # comment only
grep -rn 'security-events|upload-sarif|sarif' .github/          # test.yml:18 grant; artifact-only SARIF
grep -c 'timeout-minutes' .github/workflows/*.yml               # 9 workflows with 0
ls .github/workflows/                                           # 20 workflows, no release/tag, no firewall
node scripts/check-required-checks.mjs                          # not run: node not installed (EXIT 127)
```

### B. Required-check → execution map (main)

| Required context | Workflow | Steps executed | Path-filtered? |
|---|---|---|---|
| `Test / test (20.x)` | `test.yml` | unit-tests composite (coverage + 8 guards) | No |
| `Lint / lint (20.x)` | `lint.yml` | `pnpm lint` | No |
| `TypeCheck / typecheck` | `typecheck.yml` | `pnpm typecheck` | No |
| `E2E / e2e (20.x)` | `e2e.yml` | Supabase + API + web + Playwright/axe | **Yes (PR)** |
| `Dependency Review / review` | `dependency-review.yml` | high-severity + license deny list | No |

### C. Note on verification duty

All 21 previous CI rows were re-checked at `8d299b8d`; 4 statuses changed from the previous register: CI-P2-008 verified-fixed→partially-fixed, CI-P3-001 verified-fixed→partially-fixed, CI-P3-005 open→partially-fixed, CI-P3-004 partially-fixed→verified-fixed. Four new findings were added from the extended verification checks (path-filtered required check, dispatcher duplication, docs drift, badge stub).
