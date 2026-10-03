# Remediation PR — PATCH-013

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PATCH-013` — hygiene / inventory / CI / test / observability batch.
The audit ran on a stale clone at `2295958d`; every finding was re-checked against
the current base `origin/fix/p2-batch-31 @ 11746adc`, and only what still
reproduced was changed.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d`
- Repo / base: `mainecybertech` @ branch `fix/p2-batch-31` (`11746adc`)
- Branch: `remediation/patch-013-20261003-0018-fix-p2-batch-31-2295958d`
- Commit: `1c62862a0aa2fe90facb1a60942398871bb63073`
- Evidence: `remediation/PATCH-013/{verify.log,diff.patch,manifest.json,guard-check.sh,gitleaks-changed.sh}`

## Findings addressed

| Finding | Severity | Status | Change |
|---|---|---|---|
| `INV-P2-002` | P2 | addressed | Docs hand-off bootstrap SQL is stamped historical/don't-edit with a pointer to the live migrations. |
| `INV-P3-002` | P3 | addressed | `AGENTS.md` + regenerated `review.md` use the canonical repo slug instead of `C:\temp\mainecybertech-portal`. |
| `SUPPLY-P3-002` | P3 | addressed | `test.yml` rejects tracked `supabase/.temp/**` and non-example `.env` files (fail-closed proven). |
| `CI-P2-002` | P2 | addressed (pending token rotation) | Weekly plan-only drift run; skipped until `TF_DRIFT_PLAN_ENABLED=true`, fails on a non-empty plan. |
| `TEST-P2-002` | P2 | addressed | Static router-mount guard: mutating routers must mount `requireAuth`; tenant routers `requireOrgAccess`. |
| `TEST-P3-001` | P3 | addressed (ratchet) | api thresholds 30/50/55/58 → 45/70/74/70; web 38/38/45/46 → 39/39/47/47. |
| `DATA-P2-002` | P2 | addressed | PostgREST `.in()` reference lookup chunked at 200 keys/request; fail-closed behaviour preserved. |
| `ARCH-P2-001` | P2 | addressed (runbook) | Single-host loss/recovery runbook with snapshot + Terraform restore path. |
| `OBS-P2-002` | P2 | addressed | `docs/SLO.md` (objectives + error budget) and `infra/digitalocean/dashboards/mct-overview.json`. |
| `OBS-P3-001` | P3 | addressed (partial) | Failure-mode runbooks (Redis, Supabase, failed deploy, webhook backlog) + drill table; tabletop still to run. |
| `SEC-P3-001` | P3 | addressed | Dropped deprecated `X-XSS-Protection`; removed `'unsafe-inline'` from the JSON API `style-src`. |
| `SEC-P3-002` | P3 | addressed | M365 webhook `clientState` compared with a shared `timingSafeCompare`. |
| `DATA-P2-001` | P2 | already fixed at base | `encrypted_pii` written by `profiles.ts` + backfill; `generate-db-types --check` in CI. No change. |
| `ARCH-P2-003` | P2 | already fixed at base | Prometheus `alerting:` block + Alertmanager service/template already present. No change. |

## Open questions (not guessed)

Product / org / ops decisions the runner did **not** make:

- `HYG-P2-001` — externalize the committed `prompts/` + audit corpus to a separate repo/artifact store (org decision).
- `HYG-P2-002` — reconcile the two divergent `products.json` catalogs. `review.md` already documents the divergence as intentional pending a catalog content workflow; force-merging user-visible copy needs a store/commerce call.
- `CI-P3-001` — promote/rename the default branch (`main` behind `develop`); repo-admin decision.
- `OBS-P2-003` — a green scheduled `db-restore-test` on the deployed branch needs Spaces credentials + an ops drill (the workflow already asserts table/migration/row/RLS/age floors).
- `OBS-P3-001` (tabletop) — runbooks added; a recorded tabletop exercise still needs to be run.
- `ARCH-P2-001` (topology) — splitting Redis / adding an API replica is an infra/budget decision.

## Verification Performed

All commands ran on the Proxmox `ci-runner` (lab) at commit `1c62862a`; full raw output + exit codes in `remediation/PATCH-013/verify.log`.

| Command | Exit | Evidence |
|---|---|---|
| `corepack pnpm install --frozen-lockfile` | 0 | lockfile up to date |
| `corepack pnpm --filter api typecheck` | 0 | clean |
| `corepack pnpm --filter worker typecheck` | 0 | clean |
| `corepack pnpm --filter api test:coverage` | 0 | 124 suites / 1411 tests; 72.86/49.71/75.30/78.65 vs thresholds 70/45/70/74 |
| `corepack pnpm --filter web test:coverage` | 0 | 271 suites / 1832 tests; 48.93/41.29/40.38/49.65 vs thresholds 47/39/39/47 |
| `corepack pnpm --filter worker test` | 0 | 12 suites / 125 tests (incl. chunking test) |
| `node scripts/check-docs-links.mjs` | 0 | docs links OK |
| `node scripts/check-docs-counts.mjs` | 0 | docs counts OK |
| `node scripts/generate-db-types.js --check` | 0 | types current |
| `node scripts/sync-review-md.mjs --check` | 0 | mirror in sync |
| `actionlint .github/workflows/test.yml` | 0 | no findings |
| `actionlint -shellcheck= .github/workflows/{terraform-do,test}.yml` | 0 | syntax/expressions OK |
| `yq -e . infra/digitalocean/dashboards/mct-overview.json` | 0 | valid JSON |
| `bash guard-check.sh` (secret-files guard) | 0 | passes on tree; detects synthetic `supabase/.temp` + `.env` |
| `gitleaks detect --no-git --redact` (changed files) | 0 | no leaks found |

Note: bare `actionlint` on `terraform-do.yml` exits 1 on four **pre-existing**
SC2086 shellcheck info findings; the base `11746adc` fails identically and no
workflow runs actionlint in CI. This change adds no new findings.

## Diff summary

21 files, +552/−47: two workflows, two jest configs, three API source/test files,
one worker task + test, `AGENTS.md`/`review.md`, the docs bootstrap header,
`docs/CI.md`, two new platform docs, the runbooks index, and a dashboard JSON.

## Rollback

Revert `1c62862a` (or drop the branch). No migrations, no schema, no dependency
changes; the workflow/test/docs changes are independently revertible.

## Review checklist

- [ ] `SUPPLY-P3-002` guard allowlist is correct (`.github/restore-test-baseline.env` is a non-secret floor file).
- [ ] `CI-P2-002` is acceptable as a dormant schedule gated on `TF_DRIFT_PLAN_ENABLED` (no failing runs before token rotation).
- [ ] Coverage ratchet levels leave adequate headroom.
- [ ] Open questions above are assigned owners.
