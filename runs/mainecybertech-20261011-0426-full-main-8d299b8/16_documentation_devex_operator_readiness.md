# 16_documentation_devex_operator_readiness — Prompt 16 - Documentation, Developer Experience, and Operator Readiness Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `16_documentation_devex_operator_readiness.md` (area DOC, prompt)

## Verification Performed

# Documentation, Developer Experience, and Operator Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: MaineCyberTech/mainecybertech (read-only clone at `/tmp/opencode/mct-audit-target`)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (Merge PR #168: promote develop to main)
- Generated at: 2026-10-11
- Auditor: domain subagent `16_documentation_devex_operator_readiness` (area `DOC`)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/16_documentation_devex_operator_readiness.md`
- Scope limitations: read-only; no Node/Docker/pnpm in the audit container (running `scripts/check-docs-counts.mjs` and the quick start was impossible — guards were re-derived by reading their parsers), no `gh` API access, so live GitHub state is unverifiable. Nothing under the target repo was modified.

## Scope

Reviewed: README.md, README.dev.md, AGENTS.md/review.md, CONTRIBUTING.md, SECURITY.md, docs/INDEX.md, docs/ONBOARDING.md, docs/LOCAL_DEVELOPMENT_CHECKLIST.md, docs/testing.md, docs/ENVIRONMENT_VARIABLES.md, docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md, docs/SECRETS_ROTATION.md, docs/MONITORING_AND_ALERTING.md, docs/CI.md, docs/RELEASING.md, docs/ROLLBACK_PROCEDURES.md, docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md, docs/RTO_RPO.md, docs/TROUBLESHOOTING.md, docs/INCIDENT_RESPONSE.md, docs/DATA_BREACH_RESPONSE.md, docs/PLATFORM_FAILURE_RUNBOOKS.md, docs/RELEASE_GATE.md, docs/GAP_ANALYSIS.md, docs/migrations/*, docs/technical-writing/migration-guide.md, docs/API_ENDPOINT_INVENTORY.md, docs/ARCHITECTURE_DIAGRAM.md, docs/adr/README.md, docs/modules|features|runbooks indexes, docs/audits/**, scripts/README.md, prompts/PROVENANCE.md, plus the deploy/backup/alerting workflows and configs the docs describe.

Not reviewed: module feature specs and runbooks content (60+60, sampled via indexes), docs/seo/**, handoff bundle binaries, the 632-file prompt corpus content, and live GitHub/Actions state.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md`, `README.dev.md`, `docs/ONBOARDING.md`, `docs/LOCAL_DEVELOPMENT_CHECKLIST.md` | Onboarding | Quick start, counts, promotion path | Walked literally against scripts/workflows |
| `AGENTS.md` (1,003 lines) + `review.md` (1,009 lines) | Agent reference | Counts, worker model, guardrails | Counts re-derived from the filesystem |
| `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `docs/SECRETS_ROTATION.md`, `docs/ENVIRONMENT_VARIABLES.md` | Env/secret docs | Deploy env delivery, backup/alerting secrets | Compared against deploy-do/db-backup/storage-backup |
| `docs/MONITORING_AND_ALERTING.md`, `infra/digitalocean/{alertmanager.tmpl.yml,prometheus.rules.yml,docker-compose.yml}` | Observability | Metrics wiring, /metrics auth, alert path | Code-level cross-check |
| `docs/INCIDENT_RESPONSE.md`, `docs/DATA_BREACH_RESPONSE.md`, `docs/PLATFORM_FAILURE_RUNBOOKS.md` | Incident docs | Operator readiness | Compared against IR-P0-003 closure |
| `docs/RELEASE_GATE.md`, `docs/RELEASING.md`, `docs/ROLLBACK_PROCEDURES.md`, `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` | Release/ops | Status artifacts vs current pipeline | Register cross-check |
| `docs/CI.md`, `.github/workflows/*` | CI docs | Workflow tables, Slack/ntfy claims | 20 workflows, 3,086 lines |
| `docs/GAP_ANALYSIS.md`, `docs/technical-writing/migration-guide.md`, `docs/API_ENDPOINT_INVENTORY.md` | Historical drafts | Staleness / unresolvable references | INDEX-listed as current |
| `docs/audits/**`, `docs/INDEX.md` | Audit corpus/index | Staleness markers, run index | Committed registers inspected |
| `scripts/README.md`, `scripts/check-docs-counts.mjs`, `scripts/check-docs-links.mjs` | Script docs/guards | Guard coverage, script index | 46 scripts vs index |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline -8`; `git ls-files -s scripts/*.sh` | Command | Commit/exec-bit state | HEAD = `8d299b8d`; scripts are `100755` |
| Filesystem counts: migrations 134, workflows 20, E2E specs 90, seeds 9, scripts (recursive) 81, web pages 319, components 102 | Command | Verify AGENTS.md "File Counts" | All AGENTS.md counts match |
| `find docs/audits -maxdepth 3 -type d`; `diff` committed register vs pack register | Command | Audit corpus staleness | Committed copy == 9c0b88c register; no banner |
| `python3` link check over INDEX/README/README.dev/CONTRIBUTING | Command | Broken references | All links resolve |
| `node scripts/check-docs-counts.mjs` | Command | Count guard | Not executable here (`node: command not found`, exit 127); parser read instead |
| Literal walk of README quick start | Manual | Onboarding | Not executable (no Docker/pnpm); compared `scripts/start-local-stack.sh` line-by-line against README — consistent |
| `grep -rn` NTFY/ALERTMANAGER across `.github`, `docs`, `infra` | Command | Alerting docs vs pipeline | Workflows use ntfy; docs mostly say Slack |
| `grep -rn` metrics record*/set* in `apps/api/src` | Command | Monitoring doc accuracy | All five "not wired" metrics are wired |
| `grep -rn` `DO_SSH_KEY`, `supabase:reset:auto`, `412 paths`, `127 migrations` | Command | Doc-vs-code checks | Each confirmed stale |
| Read of `app.ts:154-171`, `health.ts:16-26`, `field-encryption.ts:43-55` | Code read | Security-behavior claims | /metrics fails closed; PII encryption throws in prod |

## Executive Summary

The documentation set is unusually large and mostly high-quality: `AGENTS.md` counts are filesystem-accurate, `docs/testing.md` is a guarded canonical reference, `docs/PLATFORM_FAILURE_RUNBOOKS.md` and `docs/INCIDENT_RESPONSE.md` are recent and well structured, and the release/rollback docs correctly describe the `prod-approval` operator gate and the backup S3/encryption contract. The docs-counts guard is real and wired into CI.

The dominant risk is **staleness of "current state" artifacts after the October remediation waves**. Several docs describe the pipeline, alerting path, or status of findings as they were before fixes landed:

- Incident and breach docs still say Alertmanager is not deployed and the dead-man's switch does not exist (`IR-P0-003` was verified-fixed), and still list closed backup findings as open gaps.
- `docs/RELEASE_GATE.md` — referenced by `RELEASING.md` as the consolidated release gate — is bound to an older run and lists closed, release-blocking controls as open.
- The operator handbook and `README.dev.md` still describe push-triggered Terraform applies, cancelled deploys, a non-existent firewall port, and heredoc env delivery.
- The canonical secret matrix and rotation inventory omit every `NTFY_ALERTS_*` and `ALERTMANAGER_*` secret, and CI/RELEASING/breach docs still name Slack as the failure channel, after the ntfy migration.
- Historical drafts (`GAP_ANALYSIS.md`, `technical-writing/migration-guide.md`) are INDEX-listed without markers and contain AWS-era content, missing pnpm scripts, and wrong release/tag instructions.

The verification duty was applied: the single previous DOC row (`DOC-P3-001`) is still open; four documentation-subject rows from other areas were re-verified (`INFRA-P2-005` still-open, `REL-P2-004` partially-fixed, `RES-P3-003` partially-fixed, `SBOM-P2-003` verified-fixed).

17 findings: 8 × P2, 9 × P3 (12 new, 5 verification rows). No P0/P1. Recommended next action: one "truth-up" docs PR per artifact class (incident/breach, release gate, handbook/README.dev, secret matrix), plus extending `check-docs-counts.mjs` to the files it misses.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| README | `README.md` | Overview/quick start | Current except migration count | Low | `:45` 127 vs 134 |
| Dev onboarding | `README.dev.md`, `docs/ONBOARDING.md` | Setup/promotion | Partly stale | Medium | Terraform push claims, counts, container names |
| Agent reference | `AGENTS.md` / `review.md` | Agent contract | Counts accurate; worker section stale | Low | Compose table omits alertmanager |
| Testing docs | `docs/testing.md` | Canonical test guide | Current, guarded | None | a11y 25/68 matches spec |
| Env docs | `docs/ENVIRONMENT_VARIABLES.md` | App vars | Current for app vars; alerting secrets missing | Medium | `METRICS_TOKEN` "Required: No" |
| Secret matrix | `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` | Canonical secret list | Missing NTFY/ALERTMANAGER | High | Slack-only backup row |
| Rotation | `docs/SECRETS_ROTATION.md` | Rotation policy | Good; inventory incomplete | Medium | 48 entries, no alerting secrets |
| Monitoring | `docs/MONITORING_AND_ALERTING.md` | Observability | Alert path current; metrics status stale | Medium | "defined, not wired" x5 |
| CI | `docs/CI.md` | Workflow reference | Mostly current | Low | SBOM row fixed; Slack-only claims |
| Release | `docs/RELEASING.md` | Promotion | Current | Low | Slack-only backup line |
| Release gate | `docs/RELEASE_GATE.md` | Go-live gate | Stale (older run) | High | Contradicts register |
| Rollback | `docs/ROLLBACK_PROCEDURES.md` | Rollback | Approval fixed; Terraform push stale | Medium | §4 |
| Operator handbook | `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` | Operator manual | Stale pipeline details | High | Concurrency/terraform/firewall/counts |
| Incident | `docs/INCIDENT_RESPONSE.md` | IR plan | Stale alerting gaps | High | IR-P0-003 closed |
| Breach | `docs/DATA_BREACH_RESPONSE.md` | Breach plan | Stale detection gaps | High | Same + backup findings |
| Platform runbooks | `docs/PLATFORM_FAILURE_RUNBOOKS.md` | Failure modes | Current | None | `prod.tfvars` path nit |
| Gap analysis | `docs/GAP_ANALYSIS.md` | Known gaps | AWS-era historical draft | Medium | INDEX-listed as current |
| Migration docs | `docs/migrations/naming-guide.md`, `docs/SUPABASE_MIGRATION_WORKFLOW.md`, `docs/technical-writing/migration-guide.md` | DB changes | Contradictory/stale | Medium | ISO vs 5302xxx |
| API inventory | `docs/API_ENDPOINT_INVENTORY.md` | Endpoint list | Marked historical; count stale | Low | 412 vs 418 |
| Audit corpus | `docs/audits/**` | Point-in-time audits | No staleness markers; index incomplete | Medium | Machine paths committed |
| Script docs | `scripts/README.md` | Script index | Missing 14 scripts | Low | Guards absent |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| README | 3 | Accurate quick start, CI table, security model | Stale migration count (`:45`) | Fix count + guard it |
| Local setup | 3 | `start-local-stack.sh` matches README; dev-setup exists | ONBOARDING Windows-only env sync; `dev-setup.sh:332` missing script | Fix sync step + script |
| Env docs | 3 | Thorough per-service tables; guarded app vars | Alerting secrets missing; METRICS_TOKEN requirement | Add NTFY/ALERTMANAGER; fix metrics note |
| Architecture/API docs | 2 | `ARCHITECTURE_DIAGRAM.md`, ADR index current | `GAP_ANALYSIS.md` AWS-era; endpoint count stale | Mark/rewrite gap analysis |
| DB/migration docs | 2 | Workflow + rollback paths accurate | Naming conventions contradict; technical guide stale | Pick one convention; fix guide |
| Testing docs | 4 | Canonical, counts guarded in CI, a11y counts accurate | Minor: none material | Keep |
| Deploy/rollback docs | 2 | RELEASING/ROLLBACK approval sections current | Handbook + README.dev describe retired Terraform flow | Truth-up both docs |
| Incident/security docs | 2 | Comprehensive IR/breach plans; good structure | Alerting/backup gaps stale; on-call rota unassigned | Update gaps; assign rota |
| Contribution/coding standards | 3 | CONTRIBUTING + AGENTS patterns; review.md mirrored | Script index gaps | Regenerate script index |
| PR/release process | 2 | RELEASING current | RELEASE_GATE stale; tag process contradicts | Regenerate gate |
| Operator manuals | 2 | Handbook rich but stale | Multiple pipeline contradictions | One truth-up PR |
| Troubleshooting | 2 | PLATFORM_FAILURE_RUNBOOKS current | TROUBLESHOOTING wrong secret/containers/limits | Fix 4 items |

## Detailed Review

### Item: Release-gate status artifact

- Evidence: `docs/RELEASE_GATE.md:3-6,31-36,45-49`; committed register `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md`.
- What it does: consolidates release exit criteria and operator actions for the 20261003 run.
- Current controls: referenced by `RELEASING.md:136-137`; statuses are per-finding and dated.
- Missing controls: no run/commit binding refresh, no staleness marker, no link to the latest register.
- Risks: operators treat closed controls as open (or lose trust in the gate).
- Recommended improvement: regenerate from the 9c0b88c/8d299b8d register or replace with a pointer to the latest run + `AGENTS.md` Known Debt.
- Suggested tests: a docs guard that asserts any "release gate" artifact's run id matches the newest committed register.
- Suggested docs: keep one authoritative gate; archive old ones.

### Item: Incident/breach gap lists

- Evidence: `docs/INCIDENT_RESPONSE.md:124-127`; `docs/DATA_BREACH_RESPONSE.md:143-147,412,446-455`; `infra/digitalocean/docker-compose.yml:244`; `alertmanager.tmpl.yml:12-14,144-155`; `deploy-do.yml:739-746`.
- What it does: tells responders what detection is missing.
- Current controls: Alertmanager deployed with an external watchdog receiver; restore test asserts integrity/freshness.
- Missing controls: the docs were not updated when IR-P0-003/DR-P0-001/DR-P0-002/IR-P1-004/IR-P1-005 closed.
- Risks: wrong incident decisions and breach timelines.
- Recommended improvement: update the gap lists; keep only genuinely open gaps.
- Suggested tests: tabletop read-through against the current register each quarter.
- Suggested docs: add "last verified against register" line.

### Item: Alert-delivery secret documentation

- Evidence: `db-backup.yml:51-62`, `deploy-do.yml:622-631,647,709-715`, `GITHUB_SECRETS_AND_VARIABLES_MATRIX.md:83-93`, `SECRETS_ROTATION.md:9-58`, `CI.md:23-25`.
- What it does: defines the secret inventory and notification channels.
- Current controls: workflows fail closed and post to ntfy.
- Missing controls: matrix/rotation omit NTFY/ALERTMANAGER; prose still says Slack.
- Risks: alert delivery lost during rebuild/rotation; audit trail wrong.
- Recommended improvement: add the 10 secret names; update prose.
- Suggested tests: a script that extracts `secrets.*` from workflows and diffs against the matrix.
- Suggested docs: matrix + rotation + CI/RELEASING/breach.

### Item: Operator handbook pipeline details

- Evidence: `FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:54,99,104,135,137,144`; `deploy-do.yml:40-43,667-722,771,831-862`; `terraform-do.yml:3-21`; `firewall.tf:22-57`; `variables.tf` (13).
- What it does: operator manual for deploy/rollback/infra.
- Current controls: many sections (approval gate, rollback SHA) are accurate.
- Missing controls: concurrency/terraform/firewall/secret-count/env-delivery sections stale.
- Risks: operators expect wrong behavior during incidents.
- Recommended improvement: one truth-up PR with the evidence above.
- Suggested tests: doc lint comparing workflow trigger/concurrency strings.
- Suggested docs: handbook + README.dev.

### Item: Historical drafts presented as current

- Evidence: `GAP_ANALYSIS.md:7,23,24,27,149`; `technical-writing/migration-guide.md:15,25-33,206-232,275`; `API_ENDPOINT_INVENTORY.md:5`.
- What it does: INDEX-listed guidance for gaps/migrations/endpoints.
- Current controls: `API_ENDPOINT_INVENTORY.md` has a historical banner (good pattern).
- Missing controls: `GAP_ANALYSIS.md` and the migration guide have none.
- Risks: wrong architecture/counts/commands for developers and agents.
- Recommended improvement: reuse the banner pattern or rewrite.
- Suggested tests: `check-docs-links`-style lint for "historical" markers on dated docs.
- Suggested docs: INDEX entries should carry `(historical)`.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DOC-001 | README | `README.md` | Accurate quick start/CI table | 127 vs 134 migrations | P3 | Fix + guard |
| DOC-002 | Local setup | `start-local-stack.sh` | Script matches README | ONBOARDING sync step Windows-only | P3 | Document cross-platform path |
| DOC-003 | Env docs | `ENVIRONMENT_VARIABLES.md` | Per-service tables | Alerting secrets; METRICS_TOKEN note | P2 | Add secrets; fix note |
| DOC-004 | Architecture/API docs | `ARCHITECTURE_DIAGRAM.md`, `GAP_ANALYSIS.md` | Diagram current | Gap analysis AWS-era | P2 | Mark historical |
| DOC-005 | DB/migration docs | `SUPABASE_MIGRATION_WORKFLOW.md` | Reverse-migration path accurate | Naming contradiction; stale guide | P3 | Align conventions |
| DOC-006 | Testing docs | `docs/testing.md` | Canonical + guarded | — | — | Keep |
| DOC-007 | Deploy/rollback docs | `RELEASING.md`, handbook | Approval gate accurate | Handbook/README.dev Terraform + concurrency | P2 | Truth-up |
| DOC-008 | Incident/security docs | `INCIDENT_RESPONSE.md`, breach doc | Plans complete | Stale alerting/backup gaps | P2 | Update gaps |
| DOC-009 | Contribution/coding standards | `CONTRIBUTING.md`, AGENTS patterns | Adequate | Script index gaps | P3 | Regenerate index |
| DOC-010 | PR/release process | `RELEASING.md`, `RELEASE_GATE.md` | Branch model accurate | Stale release gate | P2 | Regenerate gate |
| DOC-011 | Operator manuals | Handbook, `PLATFORM_FAILURE_RUNBOOKS.md` | Failure runbooks current | Handbook stale | P2 | Truth-up |
| DOC-012 | Troubleshooting | `TROUBLESHOOTING.md` | Symptom/fix structure | Wrong secret/containers/limits | P3 | Fix four items |

## Findings

IDs are assigned by the aggregator. Severity/status per the run JSON.

1. **Dated point-in-time audit reports are mixed with current runbooks with no archive/staleness marker** — P3, still-open (verification). Evidence: `docs/audits/README.md:30-37` (index omits every repo-deep-dive run), committed 9c0b88c register without banner, `REAUDIT_REPORT_20261004.md:8-9` machine-local paths, `INCIDENT_RESPONSE.md:114-135` referencing audit-folder-only runbooks. Fix: banner + index + path hygiene.
2. **Operations documentation contradicts the current pipeline and configuration** — P2, still-open (verification of INFRA-P2-005). Evidence: handbook `:54,99,104,135,137,144`; `README.dev.md:393,403,411,432`; `deploy-do.yml:40-43,667-722`; `terraform-do.yml:3-21`; `firewall.tf:22-57`. Fix: update both docs.
3. **Rollback documentation is stale (Terraform push flow) and repeats the false approval claim** — P2, partially-fixed (verification of REL-P2-004). `ROLLBACK_PROCEDURES.md:199-203` still says push triggers terraform-do; `:239-253` approval section corrected. Fix: replace §4.
4. **`AGENTS.md` documents the worker consumer incorrectly and omits the queue backend divergence** — P3, partially-fixed (verification of RES-P3-003). `AGENTS.md:17` fixed; `:326-328` still "SQS-based"/"142 lines"; actual dispatcher `consumer-sqs.ts:80-96`, prod `QUEUE_BACKEND=bullmq` (compose `:138`).
5. **`docs/CI.md` documents the SBOM workflow as "Blocking" but it gates nothing** — P2, verified-fixed (verification of SBOM-P2-003). `docs/CI.md:29` now "Artifact-only (not a gate)".
6. **Incident-response and breach docs still describe the alerting dead-man's switch as undeployed and list closed gaps** — P2, open. Evidence: `INCIDENT_RESPONSE.md:124-127`; `DATA_BREACH_RESPONSE.md:143-147,412,446-455`; deployed alertmanager (`compose:244`, `alertmanager.tmpl.yml:144-155`, `deploy-do.yml:739-746`).
7. **docs/RELEASE_GATE.md is a stale status artifact contradicting the current verified-fixed register** — P2, open. `RELEASE_GATE.md:3-6,31-36,45-49` vs register verified-fixed rows; referenced as the gate by `RELEASING.md:136-137`.
8. **Alert-delivery secrets (NTFY_ALERTS_*, ALERTMANAGER_*) are missing from the canonical secret docs, which still name Slack as the only channel** — P2, open. `db-backup.yml:51-62`; matrix `:83-93`; rotation inventory `:9-58`; `CI.md:23-25`; `RELEASING.md:130`; `DATA_BREACH_RESPONSE.md:140`.
9. **docs/GAP_ANALYSIS.md is an AWS-era historical draft presented as current** — P2, open. `GAP_ANALYSIS.md:7,23,24,27,149`; INDEX `:31`.
10. **docs/technical-writing/migration-guide.md documents commands and a release process that do not exist** — P2, open. Missing pnpm scripts (`:15,210,274-279`), timestamp naming (`:25-33`), web `/api/health` (`:206-207`), tag release (`:216-232`); `dev-setup.sh:332`.
11. **Migration/workflow/OpenAPI counts drift and the count guard does not cover them** — P3, open. `README.md:45`; `ONBOARDING.md:51,55,305`; `check-docs-counts.mjs:9-29,145-171`.
12. **docs/MONITORING_AND_ALERTING.md contradicts the now-wired metrics and the fail-closed /metrics gate** — P3, open. `:117,130-134,253`; `app.ts:154-171`; `health.ts:16-26`; `prometheus.yml:22-28`.
13. **docs/TROUBLESHOOTING.md and docs/ONBOARDING.md name wrong deploy secrets/containers and stale memory limits** — P3, open. `TROUBLESHOOTING.md:39,50`; `ONBOARDING.md:288-290`.
14. **docs/audits/README.md index omits the committed repo-deep-dive runs and its naming contract does not match them** — P3, open. `:13,30-37`.
15. **scripts/README.md omits 14 scripts, including every CI guard script** — P3, open. `:19-48` vs filesystem.
16. **AGENTS.md production compose table omits the alertmanager service** — P3, open. `AGENTS.md:190-198` vs `compose:244`.
17. **Migration naming docs contradict each other and the repo's actual 5302xxx sequence** — P3, open. `naming-guide.md:95` vs `SUPABASE_MIGRATION_WORKFLOW.md:30` vs tree.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Responders act on a stale alerting/backup gap list | High | High | Wrong incident decisions, delayed breach detection | Findings 6, 16 | Update IR/breach docs; quarterly register read-through |
| Release gate blocks or misleads promotion | High | Medium | Release friction, eroded trust | Finding 7 | Regenerate gate from register |
| Alert delivery lost during secret rotation/rebuild | High | Medium | Silent backup/monitoring failures | Finding 8 | Add secrets to matrix/rotation; add workflow-vs-matrix guard |
| Operator follows stale Terraform/concurrency steps | Medium | High | Wasted incident time, wrong expectations | Findings 2, 3 | Truth-up handbook/README.dev/rollback |
| Developer/agent follows AWS-era or missing commands | Medium | High | Wasted time, broken local setup | Findings 9, 10, 15 | Mark historical; fix commands; index scripts |
| Counts drift silently (guard blind spots) | Low | High | Wrong scale assumptions | Finding 11 | Extend `check-docs-counts.mjs` |

## Recommendations

### Immediate / Release Blocking

None. (No P0/P1 in this domain.)

### This Week

- Update `docs/INCIDENT_RESPONSE.md` §8 and `docs/DATA_BREACH_RESPONSE.md` detection/gap lists to the deployed alerting and backup state (finding 6).

### This Month

- Regenerate `docs/RELEASE_GATE.md` from the current register (finding 7).
- Truth-up the operator handbook + `README.dev.md` Terraform/concurrency/env-delivery sections (finding 2) and `ROLLBACK_PROCEDURES.md` §4 (finding 3).
- Add `NTFY_ALERTS_*` and `ALERTMANAGER_*` to the secret matrix and rotation inventory; switch CI/RELEASING/breach prose to ntfy-primary (finding 8).
- Mark `GAP_ANALYSIS.md` historical and rewrite/mark `technical-writing/migration-guide.md` (findings 9, 10).
- Add staleness banners to `docs/audits/**` and complete `docs/audits/README.md` (findings 1, 14).

### Later / Platform Evolution

- Extend `check-docs-counts.mjs` to README/ONBOARDING (finding 11); add a workflow-secrets-vs-matrix diff script (finding 8); add a historical-marker lint (findings 9, 10).
- Align migration naming conventions and add a filename-pattern guard (finding 17).
- Fix remaining P3 doc accuracy items (findings 4, 12, 13, 15, 16).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix 127→134 / 16→20 / 412→418 | Stops obvious drift | `README.md`, `docs/ONBOARDING.md`, `docs/API_ENDPOINT_INVENTORY.md` | `grep` counts vs filesystem |
| Add alertmanager row to AGENTS compose table | Prevents "not deployed" misreading | `AGENTS.md` | Diff vs compose services |
| Correct `DO_SSH_KEY`→`CI_SSH_PRIVATE_KEY` and prune order | Operator accuracy | `docs/TROUBLESHOOTING.md` | Read vs `deploy-do.yml` |
| Add "historical" banner to GAP_ANALYSIS | One-line protection | `docs/GAP_ANALYSIS.md` | Pattern matches API inventory |
| Add NTFY/ALERTMANAGER rows to matrix | Audit/rotation completeness | matrix + rotation docs | Diff workflow `secrets.*` vs matrix |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Register-driven doc refresh for IR/breach | P2 | platform lead | S | Finding 6 |
| Release gate regeneration + run binding | P2 | release owner | S | Finding 7 |
| Secret inventory completion + guard | P2 | platform/security | M | Finding 8 |
| Handbook/README.dev truth-up | P2 | infra | M | Findings 2, 3 |
| Historical-draft marking + audit index | P3 | docs | S | Findings 1, 9, 10, 14 |
| Count-guard extension | P3 | repo maintainer | S | Finding 11 |
| Monitoring/metrics doc refresh | P3 | observability | S | Finding 12 |
| Migration naming alignment + guard | P3 | DB lead | S | Finding 17 |

## Suggested Tests

- **CI/docs guard:** extend `scripts/check-docs-counts.mjs` to README.md, docs/ONBOARDING.md and docs/API_ENDPOINT_INVENTORY.md (migrations/workflows/paths); fail on drift.
- **Secret-inventory guard:** extract `secrets.*`/`vars.*` names from `.github/workflows/**` and assert each appears in `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md` (ignore-list for computed values).
- **Historical-marker lint:** every `docs/audits/<pack>/<run>/` directory and any doc whose title/banner states a commit must contain a "historical" marker; every INDEX entry for a dated audit carries `(historical)`.
- **Status-artifact consistency check:** a script that parses `docs/RELEASE_GATE.md` finding ids and compares statuses against the newest `follow_up_register.md`; fail on contradiction.
- **Doc-command smoke test:** assert every `pnpm <script>` mentioned in docs exists in a package.json; assert referenced shell scripts exist and are executable.
- **Manual quarterly walk:** run the README quick start on a clean Linux box and the ONBOARDING path on Windows; record failures.

## Suggested Documentation Updates

- `docs/INCIDENT_RESPONSE.md` — §8 gap list; §7 playbook references to audit-folder-only files.
- `docs/DATA_BREACH_RESPONSE.md` — detection gaps; Slack→ntfy; closed backup findings.
- `docs/RELEASE_GATE.md` — regenerate or replace with a pointer to the latest run.
- `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md` — concurrency, terraform, firewall, variables count, env delivery, secret list.
- `README.dev.md` — terraform promotion path.
- `docs/ROLLBACK_PROCEDURES.md` — §4 terraform rollback command.
- `docs/GITHUB_SECRETS_AND_VARIABLES_MATRIX.md`, `docs/SECRETS_ROTATION.md` — NTFY/ALERTMANAGER entries.
- `docs/CI.md`, `docs/RELEASING.md` — ntfy-primary backup notifications; backup-dispatch 05:00 cron.
- `docs/MONITORING_AND_ALERTING.md` — metrics statuses, fail-closed /metrics, memory table.
- `docs/GAP_ANALYSIS.md`, `docs/technical-writing/migration-guide.md` — historical banner or rewrite.
- `docs/ONBOARDING.md`, `README.md`, `docs/API_ENDPOINT_INVENTORY.md` — counts; cross-platform env sync; container names.
- `docs/audits/README.md` + run directories — index + staleness banners.
- `scripts/README.md` — regenerate index.
- `docs/migrations/naming-guide.md` vs `docs/SUPABASE_MIGRATION_WORKFLOW.md` — one convention.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which artifact is the single authoritative "current state" — the latest run register, `AGENTS.md`, or `docs/RELEASE_GATE.md`? | Deciding which to refresh and what to archive | Owner decision; then bind artifacts to it |
| Is the on-call rota still unassigned (INCIDENT_RESPONSE §8)? | IR plan "not operational until names recorded" | GitHub/team confirmation (not in repo) |
| Is `prod-approval` reviewer configuration now live? | Docs correctly say it cannot live in the repo | `gh api repos/.../environments` (not accessible here) |
| Should migration naming be ISO-date (guide) or sequential (practice)? | Prevents mis-ordered migrations | Owner decision; then align docs + guard |
| Are the alerting secrets (`NTFY_ALERTS_*`, `ALERTMANAGER_*`) actually set in both environments? | Docs cannot confirm provisioning | GitHub environment listing (not accessible here) |

## Appendix

### Commands run (read-only)

```bash
cd /tmp/opencode/mct-audit-target
git log --oneline -8
ls supabase/migrations/*.sql | wc -l                    # 134
ls .github/workflows/*.yml | wc -l                      # 20
find apps/web/e2e -name '*.spec.ts' | wc -l             # 90
find docs -name '*.md' | wc -l                          # 342
python3  # filesystem counts + link checks + page counts
grep -rn "NTFY_ALERTS\|ALERTMANAGER_" .github docs infra
grep -rn "record\|setActive" apps/api/src/lib/metrics.ts apps/api/src/routes apps/api/src/services
grep -rn "DO_SSH_KEY\|supabase:reset:auto\|412 paths\|127 migrations" docs README.md
node scripts/check-docs-counts.mjs                      # node not found (exit 127) — parser read instead
```

### New-developer journey (literal walk)

1. `git clone` → `pnpm install` — documented, consistent.
2. `./scripts/start-local-stack.sh` — script exists, executable, checks docker/node/pnpm, runs `pnpm install`, `supabase start`, `db reset`, writes `apps/*/.env.local`, starts API+web. README matches. **Not executable in the audit container** (no Docker/Node) — marked not reproducible.
3. ONBOARDING alternative: `pnpm supabase:env:sync` runs `powershell ... sync_supabase_env.auto.v2.ps1 -EnvFile .env.local` → writes the repo-root `.env.local`, which compose does not consume (`docker-compose.yml:8,25,43` read `apps/*/.env.local`); Linux/macOS only get the `.ps1` pointer. Gap recorded (finding 11/13 class).
4. Test commands in README/testing.md all exist in package.json.
5. Promotion path: README/README.dev correctly describe develop→main and prod-approval, but README.dev's Terraform lines are stale (finding 2).

### Documentation set recommendation

Keep: `AGENTS.md`/`review.md`, `docs/INDEX.md`, `docs/testing.md`, `docs/PLATFORM_FAILURE_RUNBOOKS.md`, `docs/RELEASING.md`, `docs/RTO_RPO.md`, `docs/MONITORING_AND_ALERTING.md` (§9), `docs/SECRETS_ROTATION.md` (procedure quality), ADRs, module/feature/runbook indexes. Add: a `docs/CURRENT_STATE.md` (or a banner convention) naming the newest run register and commit; a docs-accuracy CI guard; staleness banners on all dated audits.

## Findings

| ID | Severity | Title |
|---|---|---|
| DOC-P3-001 | P3 | Dated point-in-time audit reports are mixed with current runbooks with no archive/staleness marker |
| DOC-P2-001 | P2 | Operations documentation contradicts the current pipeline and configuration |
| DOC-P2-002 | P2 | Rollback documentation is stale (Terraform push flow) and repeats the false approval claim |
| DOC-P3-002 | P3 | `AGENTS.md` documents the worker consumer incorrectly and omits the queue backend divergence |
| DOC-P2-003 | P2 | `docs/CI.md` documents the SBOM workflow as "Blocking" but it gates nothing |
| DOC-P2-004 | P2 | Incident-response and breach docs still describe the alerting dead-man's switch as undeployed and list closed gaps |
| DOC-P2-005 | P2 | docs/RELEASE_GATE.md is a stale status artifact contradicting the current verified-fixed register |
| DOC-P2-006 | P2 | Alert-delivery secrets (NTFY_ALERTS_*, ALERTMANAGER_*) are missing from the canonical secret docs, which still name Slack as the only channel |
| DOC-P2-007 | P2 | docs/GAP_ANALYSIS.md is an AWS-era historical draft presented as current |
| DOC-P2-008 | P2 | docs/technical-writing/migration-guide.md documents commands and a release process that do not exist |
| DOC-P3-003 | P3 | Migration/workflow/OpenAPI counts drift in README.md, docs/ONBOARDING.md and the endpoint inventory, and the count guard does not cover them |
| DOC-P3-004 | P3 | docs/MONITORING_AND_ALERTING.md contradicts the now-wired metrics and the fail-closed /metrics gate |
| DOC-P3-005 | P3 | docs/TROUBLESHOOTING.md and docs/ONBOARDING.md name wrong deploy secrets/containers and stale memory limits |
| DOC-P3-006 | P3 | docs/audits/README.md index omits the committed repo-deep-dive runs and its naming contract does not match them |
| DOC-P3-007 | P3 | scripts/README.md omits 14 scripts, including every CI guard script |
| DOC-P3-008 | P3 | AGENTS.md production compose table omits the alertmanager service |
| DOC-P3-009 | P3 | Migration naming docs contradict each other and the repo's actual 5302xxx sequence |
