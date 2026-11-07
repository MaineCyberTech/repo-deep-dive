# G2 — CI / infra / testing / product verify pass

- Target: `MaineCyberTech/chat` @ `develop` `49bf4243ae02a9cd5c6ca090417d12c3696429ea` (repo HEAD dated 2026-10-15)
- Verification date: 2026-11-07
- Previous audit: `chat-20261004-full-develop-a62e44a` (2026-10-04)
- Method: read-only clone (`git fetch && git checkout -f origin/develop`), source inspection with file:line evidence, plus read-only GitHub API/DNS checks for live state. No app-code changes.

## Counts

| Measure | Count |
|---|---:|
| Re-verified previous IDs | 42 |
| New findings | 7 |
| **Total entries** | **49** |
| verified-fixed | 5 |
| partially-fixed | 4 |
| open | 40 |
| regressed | 0 |
| owner-accepted | 0 |
| P1 / P2 / P3 (all entries) | 3 / 17 / 29 |

Re-verified subset (42): 5 verified-fixed, 4 partially-fixed, 33 open.
New subset (7): 1 P1, 6 P2.

## Regressions

None. No previously fixed G2 item reverted between `a62e44a` and `49bf424`.

## What changed since the audit (relevant to G2)

- `2358666` (#107) made `infra-development` manual/plan-only → **CI-P2-001 fixed**.
- `95764fd` (#106) removed the six stale root reconciliation artifacts → **INV-P2-001 and DOC-P3-002 fixed**.
- `214e5c8` added the org gitleaks pre-commit baseline and `check-no-dotenv.sh`; `1a06708` removed the demo-JWT fallback from the E2E job. Both are improvements, but the gitleaks control is local-only (see new `SC-P2-005`).
- PR #108 (draft, open) contains the code half of the `develop` branch-protection fix; it is **not merged**.

## Re-verified findings

| ID | Sev | Status | Evidence (current commit) | Remediation |
|---|---|---|---|---|
| CI-P2-001 | P2 | verified-fixed | `infra-development.yml:7-14` dispatch-only, `apply` default false; `:118-132` plan; `:134-136` apply gated | None; optionally add reviewers to `development` env |
| CI-P2-002 | P2 | open | `audit-ci-autocommit.yml:17-18,46-49`; `audit-badges-autocommit.yml:10-11,23-26` — `contents: write` + direct push | PR-based updates / scoped bot token |
| CI-P2-003 | P2 | open | `validate.yml:273-288` hard-codes `main`; live `rules/branches/develop` = `[]`; default branch `develop` | Merge #108 + server-side ruleset |
| CI-P3-001 | P3 | open | 13/22 workflows lack `permissions:` (e.g. `ci.yml:1-14`, `validate.yml:1-10`, `audit-ci.yml:1-13`) | Least-privilege permissions per job |
| BP-P2-001 | P2 | open | Same as CI-P2-003; `BRANCH_PROTECTION_SETUP.md:5-7` still omits `develop` | Protect `develop`, update runbook |
| BP-P3-001 | P3 | open | Live API: only `development` env, `protection_rules: []`, no `production`; no committed snapshot | Commit dated settings evidence |
| SC-P2-004 | P2 | open | `.pnpm-audit-exceptions.json:2` expires `2027-01-04`; gate at `validate.yml:236-241` | Track expiry / remediate |
| SC-P3-001 | P3 | partially-fixed | No archives in HEAD tree; `infra.zip` (52.6 MB) and `docs-prompts-archive.zip` (602 KB) still in git history; `.git` 54 MB | Purge history or accept size |
| SBOM-P3-001 | P3 | open | SBOMs generated `build-push.yml:99-133`, `deploy-production.yml:214-238`; no cosign/attest | Sign images + SBOMs (OIDC) |
| SBOM-P3-002 | P3 | open | No dependency-review/license job; `docs/supply-chain.md:12` says license compliance missing; LICENSE is MIT | dependency-review + license allow-list |
| CTR-P3-001 | P3 | open | `docker-compose.prod.yml:28-46,118-142` only `mem_limit`; no `cap_drop`/`no-new-privileges`/`read_only`/seccomp | Apply container hardening |
| CTR-P3-002 | P3 | open | `docker-compose.prod.yml:29,49,119` `:latest`; dev compose `chat-*:dev`; deploy re-tags `latest` (`deploy-production.yml:338-343`) | Deploy by digest |
| SECRET-P3-001 | P3 | open | `docs/security/secrets-rotation.md` has procedures but no owner/last-rotated/expiry or alert | Inventory + overdue alert |
| SECRET-P3-002 | P3 | partially-fixed | Examples diverge (57/20/11/19/15/5 keys); `WEBHOOK_ENCRYPTION_KEY` now in `.env.example:77` and `.env.prod.example:33`, absent dev | Generate from one schema |
| INFRA-P2-001 | P2 | open | `main.tf:12-19` one droplet per env; `versions.tf:4-13` one state; `environment-model.md:65-69` same Supabase project | Separate state/hosts/projects |
| INFRA-P3-001 | P3 | open | Only manual `infra-development.yml:7-14`; no plan-on-PR or scheduled drift check | Add plan/drift jobs |
| DET-P3-001 | P3 | open | `trivy` absent from audit environment; CI uses `trivy-action` only | Install/pin trivy in audit tooling |
| DET-P3-002 | P3 | open | Still 9 unpinned refs (all first-party): prod `:29,:49,:119`, devremote `:26,:69,:106`, dev `:29,:61,:99` | Deploy by digest |
| DET-P3-003 | P3 | open | `hadolint` absent; no invocation anywhere | Add hadolint |
| RES-P2-001 | P2 | open | All services on one host `docker-compose.prod.yml:11-215`; `backup-strategy.md:16-22` | Failure domains / warm standby |
| RES-P3-001 | P3 | verified-fixed | Weekly schedules already present: `chaos-tests.yml:5-6`, `load-test.yml:6-7`, `ci.yml:22-26` | None (alert on failures) |
| OBS-P2-001 | P2 | open | `trace-context.ts:1-13` helpers only; no OTel SDK/exporter/collector; `tracing.md:11` admits gap | OTLP exporter + collector |
| OBS-P3-001 | P3 | partially-fixed | Sentry optional `sentry.ts:23-30`; durable buffer exists `error-buffer.ts:19-27` but `SENTRY_DSN`/`ERROR_LOG_FILE` not set in prod compose/deploy | Require DSN + persistent error log |
| PERF-P3-001 | P3 | partially-fixed | k6 thresholds `smoke-test.js:7-10`, `load-test.js:11-14`; weekly smoke only `load-test.yml:6-7,16-22`; no PR budget/trend | Add PR/nightly budget + dashboard |
| DR-P3-001 | P3 | open | `backup-strategy.md:6-7` targets not measured; no dated drill result under `docs/operations` | Run/record restore drill |
| IR-P3-001 | P3 | open | `incident_tabletop_scenarios.md:3-4` says no dated artifact; no participant record | Run/record tabletop |
| DOC-P3-001 | P3 | open | `deployment-policy.md:33-37` forbids DB changes in deploys, but `deploy-development.yml:87-93` runs `supabase db push`; hotfix input documented but absent `deploy-production.yml:10-16` | Reconcile policy/workflow |
| DOC-P3-002 | P3 | verified-fixed | `95764fd` (#106) removed all six stale root artifacts; none in `git ls-files` | None |
| UX-P3-001 | P3 | open | `scripts/accessibility-audit.sh:20-45` ad-hoc pa11y/axe; no CI reference | Add blocking axe/pa11y job |
| MOB-P3-001 | P3 | open | `apps/web/public/sw.js:1-40`; no SW test or cache-policy doc | Document policy + update test |
| USE-P3-001 | P3 | open | Invite modal exists; no invite/accept E2E in `tests/e2e/*.spec.ts` | Add invite/accept E2E |
| ARCH-P2-001 | P2 | open | One compose host `docker-compose.prod.yml:11-215`; one droplet `main.tf:12-19` | RTO/RPO + managed services/warm standby |
| ARCH-P3-001 | P3 | open | Shared `METRICS_TOKEN` for api/worker/prometheus `docker-compose.prod.yml:57,131,160` | Per-consumer tokens |
| INV-P2-001 | P2 | verified-fixed | #106 removed root artifacts; root tree clean | None |
| INV-P3-001 | P3 | open | 1108 tracked files; `docs/audits` 126 files (~984 KB), `docs/hardening_super_bundle` 47 (~264 KB), plus edition mirrors | Keep one canonical run; externalize mirrors |
| INV-P3-002 | P3 | verified-fixed | `README.md:7` correct em dash; no mojibake in workflows/scripts/operational docs | None |
| HYGIENE-P3-002 | P3 | open | Duplicate `requireAdmin` `workspaces/routes.ts:169-176` vs `middleware/require-admin.ts:12-60`; duplicate migration basenames; one-off scripts | Consolidate / relocate |
| REL-P3-001 | P3 | open | `CHANGELOG.md:8` last release 2026-07-06; no commitlint/changesets/release job | Adopt changesets/commitlint |
| EVOL-P3-001 | P3 | open | SDK exists, versioning doc `docs/api/versioning.md:22-27` + `deprecation.ts:18`; no extension contract; advertised `Accept-Version` is unimplemented | Publish contract; implement/remove claim |
| EXEC-P1-001 | P1 | open | `RELEASE_GATE.md:5-6` remains `GO WITH CONDITIONS`; 33 re-verified P2/P3 open in G2 + new P1/P2 issues | Keep gate conditional; re-run domains |
| FINAL-P1-001 | P1 | open | `22_final_risk_register_roadmap.md:16-18`; structural P2s remain | Close P2s before unconditional GO |
| FINAL-P2-001 | P2 | open | Same 2027-01-04 expiry (`.pnpm-audit-exceptions.json:2`, `.trivyignore:13`) | Track expiry |

## New findings

| ID | Sev | Title | Evidence | Remediation |
|---|---|---|---|---|
| INFRA-P1-001 | P1 | Development and production share one Terraform state key and resource address | `versions.tf:4-7` single key `infra/terraform.tfstate`; `main.tf:12-14` single `digitalocean_droplet.chat`; `infra-development.yml:58` and `deploy-production.yml:71-73` init the same backend; no workspaces | Separate backend keys/workspaces per environment + separate credentials and state locks |
| CI-P2-005 | P2 | PRs targeting `develop` skip validate/test | `ci.yml:6-7` PRs only to `main`; default branch `develop`; `deploy-development.yml:5-6` auto-deploys it; PRs to develop only get `audit-pr-gate.yml:2-4` + `build-push.yml:15-17` | Run validate on every PR to `develop`; make jobs required |
| CI-P2-006 | P2 | Development deploy is ungated and accepts cancelled CI as success | `deploy-development.yml:28-33` no `environment:` (contrast `deploy-production.yml:58,154`); `:47-50` treats `cancelled` as success; `:87-93` then runs DB migrations | Fail closed on cancelled/skipped; add protected `development` env; remove DB push |
| CI-P2-007 | P2 | Scheduled validate pipeline is persistently red on `develop` | `ci.yml:8-9`; failed jobs defined at `validate.yml:11-62` (test), `:122-143` (lint), `:207-271` (security-audit), `:325-434` (migration-test), `ci.yml:22-26` (k6); runs `42237471839` (11-06), `42052857311`, `41855419957`, `41658125088`, `41485750511` (11-02..06) all failed on `49bf424`; Load Test `41466298046` failed 11-02 | Triage/fix failures; alert on scheduled-run failure; keep release blocked |
| CI-P2-008 | P2 | Two workflows apply the same migrations concurrently on `develop` | `supabase-migrations.yml:4-8,34-35` and `deploy-development.yml:7-13,87-93` both trigger on `supabase/migrations/**` and both run `supabase db push --include-all` without a shared concurrency group | Make `supabase-migrations` the only applier; add a concurrency lock |
| SC-P2-005 | P2 | Org gitleaks baseline is local-only and not enforced in CI | `214e5c8` added `.pre-commit-config.yaml:12-20`; `.husky/pre-commit` does not call it; `verify-gitleaks-allowlist.sh:18-20` exits 0 without the binary; no workflow runs gitleaks | Add blocking CI gitleaks detect + allowlist verification; wire hook into husky |
| INFRA-P2-002 | P2 | Production approval/deploy path is not configured: no `main`, no `production` environment | `deploy-production.yml:16-17` triggers on `main`, which does not exist (`git ls-remote`); environment only `development` (live API, no protection); production DNS absent while dev returns 200 | Create `main` + protected `production` env, or disable/document the prod workflow |

## Top new findings

1. **INFRA-P1-001 (P1) — shared Terraform state.** Both environments use the same state key and the same `digitalocean_droplet.chat` address. A development `apply` can plan replacement of the production droplet (and vice versa) because only `var.environment` changes. This is the highest-impact new issue in G2.
2. **CI-P2-007 (P2) — default-branch CI is red.** Five consecutive scheduled Validate runs on the audited SHA failed (lint, test, security-audit, migration-test, k6), and the weekly Load Test also failed. The release gate has no trustworthy green signal.
3. **CI-P2-008 (P2) — duplicate migration appliers.** Every migration push to `develop` triggers two `supabase db push --include-all` runs against the same project, with no shared concurrency lock.
4. **SC-P2-005 (P2) — gitleaks is advisory-only.** The new org baseline only runs if a developer manually installs `pre-commit`; CI never scans for secrets.
5. **CI-P2-005 / CI-P2-006 (P2) — develop is weakly gated.** PRs to the default branch skip validate, and the auto-deploy job has no environment gate and treats cancelled CI as success.

## Verification limits

- Live GitHub API/DNS checks were read-only and unauthenticated; job logs were not downloadable (`403 Must have admin rights`), so CI failure causes are inferred from job names, not logs.
- Server-side secret scoping is not inspectable: the repo references `secrets.SUPABASE_*` from repo level, and `docs/environments/environment-model.md:65-69` states both environments share one Supabase project. Live secret values were not accessed.
- `production` may be intentionally not deployed; the finding records the mismatch between the checked-in production workflow/docs and the live state.

## Outputs

- `g2_ci_infra_product.json` — machine-readable findings with full evidence and remediation.
- `g2_ci_infra_product.md` — this report.
