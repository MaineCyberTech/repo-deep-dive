# GitHub Actions, CI/CD, and Governance Audit (re-audit)

- Run: `mainecybertech-20261014-0033-full-main-7dd0402`
- Target: `mainecybertech` @ `7dd0402` (branch `main`, promoted 2026-10-13)
- Area code: CI · Previous full run: `mainecybertech-20261011-0426-full-main-8d299b8`; fast re-check: `mainecybertech-20261013-0126-fast-develop-905ed63`
- Scope: `.github/workflows` (30), `.github/actions` (8 composites), `.github/branch-protection`, CODEOWNERS, dependabot, docs/CI.md, docs/RELEASING.md, release/deploy/migration workflows. Read-only; live GitHub settings not inspectable.

## Executive Summary

The workflow estate is materially hardened and the two regressions from the fast run are resolved: `main` now contains all of `develop` (scheduled jobs can fire; CI-P3-004), `backup-dispatch.yml` is gone from main (CI-P2-010), and the dispatch-input injection surface is closed (CI-P3-013). All 25 previous CI rows plus the fast-run addition were re-checked: **20 verified-fixed, 4 partially-fixed, 2 still-open (operator-gated prod environment), 0 regressed**, plus **2 new findings**.

The new P1 is a real, reproduced release-gate failure: publishing the fast-mode audit run left it out of `docs/audits/README.md` and without its `HISTORICAL.md` marker, so `scripts/check-docs-links.mjs` exits 1 on the current main tree. That script runs inside the required `Test / test (20.x)` job and in the deploy gate (`validate.yml`), so PRs and production deploys fail until a two-file fix lands (CI-P1-004). The remaining P1s are operator provisioning (prod `prod-approval` reviewers and prod secrets), not code defects.

## Verification Performed

| Evidence | Type | Why relevant | Result |
|---|---|---|---|
| `scripts/check-required-checks.mjs` (executed) | Guard | Required contexts must resolve and not be path-filtered | **PASS** — 8 main / 6 develop contexts resolve |
| `scripts/check-docs-links.mjs` (executed) | Guard | Docs/CI table + audit-run index + markers | **FAIL** — fast-run dir unindexed and unmarked (CI-P1-004) |
| `scripts/check-env-parity.mjs`, `actions-inventory.mjs --check`, `check-codeowners.sh`, `check-branch-protection-audit.sh`, `check-required-checks.sh`, `check-migration-transactions.sh`, `check-circular-deps.mjs` (executed) | Guards | Adjacent CI gates | all **PASS** |
| `.github/workflows/*` inventory (30 workflows: triggers, permissions, jobs, timeouts, environments) | Config | Gate/permission/timeout claims | verified |
| `docs/CI.md` File column vs `.github/workflows` (replicated) | Cross-check | Workflow documentation drift | exact match |
| `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `docs/RELEASING.md` | Docs | Operator-gated prod gaps | still open |
| `git rev-list origin/main..origin/develop` = 0 | Git | Branch promotion state | fixed |

## Findings

| ID | Sev | Title | Status | Evidence (at 7dd0402) |
|---|---|---|---|---|
| CI-P1-001 | P1 | Production application deploys have no working manual-approval gate | still-open | Code attaches `prod-approval` (deploy-do.yml:648, supabase-migrations.yml:38, terraform-do.yml:204, load-test.yml:61); docs state no reviewers configured (matrix:12-14, RELEASING.md:128-133) — operator action |
| CI-P1-002 | P1 | Branch-protection-as-code mismatched check / admin bypass | verified-fixed | guard PASS; `enforce_admins:true` + code-owner reviews in both payloads |
| CI-P1-003 | P1 | Production deploy path cannot run; prod env lacks secrets/protection | still-open | matrix:187-220; RELEASING.md:170-182 (prod-approval secrets absent, DO_API_TOKEN 401) |
| **CI-P1-004** | **P1** | **NEW: fast-run publish fails the docs-links gate on main** | **open** | `node scripts/check-docs-links.mjs` → exit 1; dir `…20261013-0126-fast-develop-905ed63` not in `docs/audits/README.md` (last row :95) and no `HISTORICAL.md`; runs in required test job (unit-tests action.yml:72-74) and deploy gate (validate.yml:88) |
| CI-P2-001 | P2 | World-open DO firewall mutation workflow | verified-fixed | no firewall workflow; terraform-do rejects world-open allowlists (:102-113) |
| CI-P2-002 | P2 | Deploy-gate secret scan no-op on main pushes | verified-fixed | secret-scan action.yml:15-28 (`github.event.before` + zero-SHA fallback) |
| CI-P2-003 | P2 | Prod approval env documented with no reviewers | verified-fixed | docs state the truth; tracked by CI-P1-001/003 |
| CI-P2-004 | P2 | DB restore test asserts nothing | verified-fixed | db-restore-test.yml:196-330 floors |
| CI-P2-005 | P2 | Infra changes not gated in CI | partially-fixed | terraform-do manual-dispatch only; drift plan dormant until `TF_DRIFT_PLAN_ENABLED` (:40) |
| CI-P2-006 | P2 | Chromatic permanently non-blocking | verified-fixed | no continue-on-error; `exitZeroOnChanges:false`; residual docs staleness → CI-P3-014 |
| CI-P2-007 | P2 | Admin bypass / CODEOWNERS ignored | verified-fixed | both payloads enforce admins + owner reviews |
| CI-P2-008 | P2 | Terraform apply manual; drift not automated | partially-fixed | weekly plan-only drift check wired but dormant (:14-15, :160-172) |
| CI-P2-009 | P2 | E2E required but path-filtered | verified-fixed | e2e.yml:19-23 no paths; guard enforces |
| CI-P2-010 | P2 | Backup dispatcher duplicates workflows | verified-fixed | dispatcher removed from main; token documented retired |
| CI-P3-001 | P3 | actionlint/shellcheck lint issues | partially-fixed | shellcheck gate wired; actionlint still config-only |
| CI-P3-002 | P3 | Over-broad token permissions | verified-fixed | no `actions: write`; least privilege |
| CI-P3-003 | P3 | `StrictHostKeyChecking=no` | verified-fixed | deploy-do.yml:1128-1141 pinned known_hosts |
| CI-P3-004 | P3 | `main` behind `develop`; crons can't fire | verified-fixed | main contains develop (0 behind); was regressed at 905ed63 |
| CI-P3-005 | P3 | Scanner misses platform token formats | partially-fixed | patterns still lack dop_v1_/sbp_/glpat_/sk-proj-/npm_ |
| CI-P3-006 | P3 | Unused permission grants | verified-fixed | permissions minimal and consumed |
| CI-P3-007 | P3 | Unpinned postgres in restore test | verified-fixed | db-restore-test.yml:177 digest pin |
| CI-P3-008 | P3 | No release/tagging workflow | verified-fixed | release.yml tags + Release + SBOM |
| CI-P3-009 | P3 | E2E flakiness vs hard gate | verified-fixed | CI.md:196-211 policy + flake summary |
| CI-P3-010 | P3 | Missing job timeouts | verified-fixed | all jobs have timeouts |
| CI-P3-011 | P3 | Workflow docs drift | verified-fixed | docs/CI.md table exact match; guard |
| CI-P3-012 | P3 | Badge generator stub | verified-fixed | stubs removed; real reports documented |
| CI-P3-013 | P3 | Dispatch inputs interpolated into `run:` | verified-fixed | env indirection at 7dd0402 (commit 07e9ce09) |
| **CI-P3-014** | **P3** | **NEW: Storybook pin landed but docs/comments still say build broken** | **open** | package.json overrides webpack 5.101.2; docs/CI.md:149-157 + chromatic.yml:28-43 stale |

## New Findings Detail

### CI-P1-004 — Published fast-mode run breaks the docs-links gate (P1, open)

- **Evidence**: `docs/audits/repo-deep-dive/mainecybertech-20261013-0126-fast-develop-905ed63/audit_manifest.json` exists but is absent from `docs/audits/README.md` (newest row :95 = the 20261011 run) and has no `HISTORICAL.md`; `scripts/check-docs-links.mjs:128-153` (index) and `:155-177` (marker) both `exit 1`. Reproduced: `node scripts/check-docs-links.mjs` → exit 1 with `audit runs missing from docs/audits/README.md (1)`.
- **Why it matters**: the script runs in the shared `unit-tests` composite (action.yml:72-74) called by the required `Test / test (20.x)` job (test.yml:41) and by the deploy gate (validate.yml:88). The current main tree therefore fails a required check and the deploy gate — every PR is red and `deploy-do` cannot pass `validate`.
- **Fix**: add the run row to `docs/audits/README.md` (repo-deep-dive table) and add `HISTORICAL.md` to the run directory (copy the marker shape from the 20261011 run). Introduced by publish commit `62a09bac`; promoted to main.
- **Validation**: `node scripts/check-docs-links.mjs` → exit 0.

### CI-P3-014 — Stale Storybook/Chromatic state in CI docs (P3, open)

- **Evidence**: `package.json` `pnpm.overrides.webpack = "5.101.2"` (mirrored `pnpm-lock.yaml:32`) and commit `673d76cb` state the pin greens the Storybook/Chromatic build; `docs/CI.md:149-157` still describes the break as current and `chromatic.yml:28-43` still says the build "still fails". The two statements cannot both be current.
- **Fix**: re-run the Chromatic job (or `pnpm storybook:build`) on main and update `docs/CI.md` + the workflow comment to the measured result; keep `continue-on-error` off either way. Underlying build fix owned by TEST-P3-001.
- **Validation**: Chromatic run conclusion + `pnpm storybook:build` exit 0.

## Recommendations

- **Immediate (this week)**: fix CI-P1-004 (docs/audits/README.md row + HISTORICAL.md) — it blocks every required check and the deploy gate. Operator: configure `prod-approval` required reviewers and prod secrets (CI-P1-001/003).
- **This month**: enable `TF_DRIFT_PLAN_ENABLED` after rotating `DO_API_TOKEN` (CI-P2-005/008); add platform token formats to the diff secret scanner (CI-P3-005).
- **This quarter**: wire an actionlint CI job (CI-P3-001); reconcile Chromatic docs after re-verifying the build (CI-P3-014).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are the committed branch-protection payloads applied to live GitHub? | The red required-check/gate state may already have allowed merges | `gh api .../protection` comparison (needs `BRANCH_PROTECTION_READ_TOKEN`) |
| Did PR #279 merge with a red required check? | Signals live protection drift | GitHub PR checks page / audit log |
| Is the Chromatic job green after the webpack pin? | Decides CI-P3-014 wording and required-check promotion | Chromatic run result |
