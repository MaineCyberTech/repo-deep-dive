# Release Notes and Changelog Generator

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (MaineCyberTech portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11
- Auditor: domain subagent `40_release_notes_changelog_generator` (area `REL`)
- Area code: REL
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/40_release_notes_changelog_generator.md`
- Scope limitations: read-only audit. Node.js/pnpm/docker are not installed in the audit
  environment, so `scripts/generate-sbom.mjs`, the audit gates and `pnpm audit` were **read, not
  executed**. There is no network access, so live GitHub Releases/tags on the remote and the
  `prod`/`prod-approval` environment settings are **not verifiable from the repo**; tag/release
  evidence comes from the local clone (`refs/tags` = 0) plus the workflow inventory. Live ntfy /
  Prometheus / deploy behavior was not exercised.

## Scope

Reviewed at `8d299b8d`:

- **Delta since the previous run**: `git log/diff 9c0b88c..8d299b8d` — 113 commits, 99 files,
  +8,955/-620 lines (26 of the commits touch `CHANGELOG.md`).
- **Release artifacts**: `CHANGELOG.md` (468 lines), `VERSION`, `templates/RELEASE_NOTES_TEMPLATE.md`,
  `templates/release_scorecard.md`, `templates/pr_comment.md`, `.github/PULL_REQUEST_TEMPLATE.md`.
- **Release process docs**: `docs/RELEASING.md`, `docs/ROLLBACK_PROCEDURES.md`, `docs/SBOM_PROCESS.md`,
  `AGENTS.md` (Known Debt), `docs/RELEASE_GATE.md`.
- **Version/package identity**: `package.json` + `apps/*/package.json` + `packages/*/package.json`,
  `apps/web/scripts/generate-version.js`, `scripts/generate-sbom.mjs`, `.github/workflows/{deploy-do,sbom}.yml`.
- **Migrations**: `supabase/migrations/` (134 files) and the delta's migration set.
- **Committed audit outputs**: `docs/audits/repo-deep-dive/**` (registers, findings.json) and the
  register-reconciliation commits.
- **Verification of the previous REL register rows** (`mainecybertech-20261004-full-main-9c0b88c`).

Not reviewed: live GitHub Releases/tags/settings, runtime deploy behavior, prod secrets, the
contents of `docs/audits` corpora older than the last two runs.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline 9c0b88c..8d299b8d` | Git history | Delta to summarise | 113 commits; merge-based PRs #94–#168 |
| `CHANGELOG.md` (468 lines) | Changelog | Delta accuracy + breaking-change section | +112 lines added by 26 delta commits |
| `VERSION` = `0.1.0` | Version file | Product version source of truth | Touched by exactly one commit (`6757a478`); never bumped |
| `templates/RELEASE_NOTES_TEMPLATE.md` | Template | Release notes / GitHub Release body | Version+sha+date header, migrations, operator actions |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template | Changelog/artifact checkboxes | CHANGELOG checkbox at line 17; no versioned-artifact box |
| `docs/RELEASING.md` | Process doc | Versioning, changelog, approval gate, prod caveats | Accurate except the "main behind develop" claim (line 149) |
| `docs/ROLLBACK_PROCEDURES.md` | Process doc | Rollback / migration steps | §3 hard-delete; §4 Terraform flow stale (line 203) |
| `scripts/generate-sbom.mjs` | Code | Commit/version binding of generated artifacts | `readProductVersion()` + `mct:commit` property |
| `.github/workflows/deploy-do.yml` | CI/CD | Image tags, approval env, web version arg | SHA-tagged images; `prod-approval`; `main-<run>` badge |
| `supabase/migrations/` | SQL | Breaking/upgrade manifest inputs | 134 migrations; none added in this delta |
| `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/` | Audit output | Aggregate/binding check | Header bound to `9c0b88c`; rows reconciled later |

## Verification Performed

| Command | Observed result |
|---|---|
| `git log --oneline 9c0b88c..8d299b8d \| wc -l` | 113 commits (the delta since the last run) |
| `git diff --stat 9c0b88c 8d299b8d` | 99 files changed, 8,955 insertions(+), 620 deletions(−) |
| `git for-each-ref refs/tags \| wc -l` | 0 tags |
| `git log --oneline --follow -- VERSION` | 1 commit (`6757a478`) — `VERSION` never bumped |
| `git log --oneline 9c0b88c..8d299b8d -- CHANGELOG.md \| wc -l` | 26 commits, including the last non-merge commit `00cb3da6` |
| `git diff --stat 9c0b88c 8d299b8d -- CHANGELOG.md` | 112 insertions, all inside `### Fixed` (lines 137–327) |
| `git diff --name-only --diff-filter=A 9c0b88c 8d299b8d -- supabase/migrations/` | empty — no new migrations in the delta |
| `grep -n "5302432\|5302434" CHANGELOG.md` | no hits — column drop + anon-grant removal not in the changelog |
| `git rev-list --count 8d299b8d..origin/develop` | 0 (develop fully contained in main) |
| `git log develop..8d299b8d \| wc -l` | 87 (main is ahead of develop, contradicting `docs/RELEASING.md:149`) |
| `grep -rn "CHANGELOG" .github/ scripts/` | only `.github/PULL_REQUEST_TEMPLATE.md:17` — no CI enforcement |
| `grep -rn "softprops/action-gh-release\|semantic-release\|gh release" .github/ package.json` | no hits — no release/tag automation |
| `grep -n "handlebars" CHANGELOG.md` | no hits — `ea427954` (CRITICAL advisory override) undocumented |
| `which node npm pnpm` | not installed — SBOM/audit scripts read-only, `pnpm audit` not run |
| Sampled CHANGELOG claims vs code | 18 of 18 sampled entries matched the code (below) |

**Sampled CHANGELOG claims (all `supported`):**

| CHANGELOG entry | Code evidence at `8d299b8d` |
|---|---|
| Deploy SSH verifies the host key (CI-P3-003) | `.github/workflows/deploy-do.yml:642,761,875-891` (`fingerprint:` pin + known_hosts from `DO_SSH_HOST_KEY`, `StrictHostKeyChecking=yes`) |
| Worker `unhandledRejection` + shutdown watchdog | `apps/worker/src/main.ts:42`, `apps/worker/src/shutdown.ts:14`, tests at `apps/worker/src/__tests__/shutdown.test.ts:68` |
| CSV formula-injection guard + mandatory tenant scope | `apps/api/src/lib/csv.ts:9-38` (`escapeCsvValue`), used by export routes (e.g. `client-onboarding-command-center.ts:97`) |
| Raw-body webhook signatures | `apps/api/src/lib/webhook-signature.ts:32`, `apps/api/src/routes/webhooks.ts:377,479` |
| M365 replay window | `apps/api/src/routes/webhooks.ts:24,56,620` (atomic digest claim) |
| Search `?limit` default 5 / cap 25 + counts | `apps/api/src/routes/search.ts:28`, `:223` |
| e2e service profile-gated | `docker-compose.yml:58-65` (`profiles: ["e2e"]`, explicit `E2E_ADMIN_PASSWORD`) |
| Secret history scan workflow | `.github/workflows/secret-history-scan.yml:1-40` (pinned gitleaks 8.30.1 + SHA-256) |
| Inline email bounded retry (NOTIF-P2-006) | `apps/api/src/lib/email.ts:13-57` (`EMAIL_MAX_ATTEMPTS` loop + backoff) |
| Migration dry-run artifact (IR-P2-006) | `.github/workflows/supabase-migrations.yml:67-82` (`--dry-run` tee + upload-artifact) |
| Prometheus scrape auth (METRICS_TOKEN) | `apps/api/src/app.ts:154-165` (404 unauthenticated), `infra/digitalocean/docker-compose.yml:214`, `prometheus.yml:22` |
| ntfy backup notifications | `.github/workflows/db-backup.yml:51-62`, `storage-backup.yml:61-63`, `db-restore-test.yml` |
| Alertmanager ntfy basic auth | `infra/digitalocean/alertmanager.tmpl.yml:112-133` |
| SSE org assertion (MT-P2-004) | `apps/api/src/routes/notifications.ts:31-42,120-155` (`notificationInScope`) |
| Sensitive-export audit events (ADMIN-P2-001) | `apps/api/src/routes/{tickets.ts:84,projects.ts:81,audit.ts:96}` |
| Webhook retry accounting (WH-P2-002/003) | `apps/api/src/lib/webhook-dispatcher.ts:36-97` (actual `attempts`) |
| Atomic scheduled notification emails (NOTIF-P2-004) | `apps/worker/src/tasks/scheduled-notifications.ts:172-207,282-314` (`claimNotificationEmail`) |
| Web prod env fail-fast (SECRET-P3-002) | `apps/web/lib/env.ts:84-90` (throws in production without `NEXT_PUBLIC_API_URL`) |

## Executive Summary

The release-notes/changelog machinery is materially better than the previous run recorded. The
`CHANGELOG.md` `[Unreleased]` section was refreshed during the delta (26 commits, +112 lines), every
sampled entry matches the code, a `Breaking Changes` section and an upgrade/rollback pointer exist,
and `templates/RELEASE_NOTES_TEMPLATE.md` gives a complete GitHub Release body shape. The previous
register's P2 "changelog stale" and "no release-notes template" rows are now verified-fixed.

The remaining risks are concentrated in **accuracy and completeness**, not absence:

1. **Breaking-change coverage is incomplete for the release window.** The upgrade manifest lists
   migrations `5302420`–`5302428`, but the `[Unreleased]` window includes `5302430`–`5302436`,
   including `5302432` (drops `deleted_at`/`deleted_by` from `tickets`/`projects`/`documents`) and
   `5302434` (removes the blanket `anon` DML grant). Neither appears anywhere in the changelog.
2. **One security fix is missing from the changelog** — the handlebars `>=4.7.10` override that
   cleared new CRITICAL advisories (`ea427954`), while the `### Security` section still asserts
   "0 critical/high".
3. **Version identity is split.** `VERSION` is `0.1.0` and has never been bumped; images are
   SHA-tagged; the web badge/`version.json` uses `<branch>-<run_number>` (`main-168`), not `VERSION`.
   No git tags and no GitHub Releases exist.
4. **Release docs carry a stale repo-state claim** (`main` is far behind `develop` — the opposite is
   true: `origin/develop` is an ancestor of `main`), and the rollback doc still describes a
   Terraform push/PR trigger that no longer exists.

Delta-level risk to production: low. This delta contains **no migrations** and no OpenAPI spec
change, so the release notes can honestly say "no breaking schema/API changes"; the operator-facing
deltas are the new `METRICS_TOKEN` requirement for `/metrics`, the ntfy alert routing secrets, and the
production `QUEUE_BACKEND=inline` refusal.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Changelog | `CHANGELOG.md` | Release-facing change log | Refreshed for the delta; all new entries under `Fixed` | Medium | 112 lines added; 18/18 sampled claims correct |
| Breaking changes | `CHANGELOG.md:12-25` | Behavior-affecting changes | Present, incomplete manifest (`5302420–5302428`) | Medium | `5302432`/`5302434` unmentioned |
| Product version | `VERSION` | Version source of truth | `0.1.0`, never bumped | Medium | SBOM binds `<VERSION>+sha`; web badge diverges |
| Release notes template | `templates/RELEASE_NOTES_TEMPLATE.md` | GitHub Release body | Complete; referenced by `docs/RELEASING.md:70-74` | Low | Never exercised (no Release exists) |
| Release scorecard | `templates/release_scorecard.md` | Readiness scorecard | 1-line placeholder, unreferenced | Low | Dead template |
| PR template | `.github/PULL_REQUEST_TEMPLATE.md:17` | Changelog checkbox | Present; unenforced; no versioned-artifact box | Low | `grep` shows no CI check |
| Release process | `docs/RELEASING.md` | Promotion/versioning/approval | Accurate except line 149 (`main` behind `develop`) | Medium | Approval caveat is honest |
| Rollback notes | `docs/ROLLBACK_PROCEDURES.md` | Docker/DB/infra rollback | §3 hard-delete accurate; §4 Terraform trigger stale | Medium | Line 203 contradicts `terraform-do.yml` |
| SBOM binding | `scripts/generate-sbom.mjs:300-306,444-459` | Commit/version binding | Present (`mct:commit`, serialNumber) | Low | Read, not executed (no node) |
| Image tagging | `.github/workflows/deploy-do.yml:38` | Release identity | SHA-tagged (or `rollback_sha`) | Low | Documented in `docs/RELEASING.md:51-61` |
| Web version badge | `deploy-do.yml:334`, `apps/web/scripts/generate-version.js` | UI version display | `<branch>-<run_number>` (e.g. `main-168`) | Low | Not `VERSION` |
| Migrations | `supabase/migrations/` (134) | Schema changes | None added in the delta | Low | Manifest gap only |
| Audit outputs | `docs/audits/.../mainecybertech-20261004-full-main-9c0b88c/` | Prior-run evidence | Reconciled in place at later commits | Low | Matches the pack's reconciliation workflow |
| Release automation | — | Tags/Releases/notes publication | Absent (0 tags, no release workflow) | Medium | Owner decision documented as SHA-authoritative |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Git history | 4 | Conventional `fix/feat/ci/docs` subjects in the delta; PR merges traceable | `Merge PR #N` subjects non-conventional; one human author | Keep conventional subjects; note merge-commit filtering in the notes tooling |
| PR templates | 3 | `.github/PULL_REQUEST_TEMPLATE.md:17` CHANGELOG checkbox | No versioned-artifact/release-notes checkbox; nothing enforces it | Add a release-artifact line; make the checkbox a required check or drop the pretence |
| Changelog/release notes templates | 4 | `CHANGELOG.md` refreshed; template complete | Entries all under `Fixed`; handlebars fix missing | Re-file entries; add the missing entry |
| Version files | 2 | `VERSION` exists; SBOM binds it | Static `0.1.0`; web badge uses a different identity | Bump `VERSION` per release and pass it to the web build |
| Package versions | 3 | All app/package manifests `private: true`; no npm publishing | No versions at all | Fine for a private monorepo; keep SHA image identity |
| Migrations | 4 | 134 migrations, listed in changelog where relevant | Upgrade manifest stops at `5302428` | Complete the manifest in `Breaking Changes` |
| API/UI/security/bug/dependency/infra/docs changes | 4 | 18/18 sampled delta entries match code | handlebars entry absent | Add the dependency entry |
| Breaking changes | 2 | `CHANGELOG.md:12-25` + template section | Column drop (`5302432`) and anon-grant removal (`5302434`) unflagged | Add both; state "no migrations in this delta" explicitly |
| Known issues | 3 | Template `Known Issues` section; `AGENTS.md` Known Debt | Changelog has no known-issues pointer for the release | Link the Known Debt entries in the release notes |
| Operator actions | 3 | Template `Operator Actions`; delta actions documented in `Fixed` | No consolidated operator list for the delta | Add an Operator Actions block to `[Unreleased]` |
| Migration steps | 3 | Upgrade note + `docs/ROLLBACK_PROCEDURES.md` | Manifest incomplete; no down-migrations | Keep restore-from-backup guidance; list all filenames per release |
| Rollback notes | 3 | `docs/ROLLBACK_PROCEDURES.md` (277 lines), `rollback_sha` path | §4 Terraform trigger stale | Update §4 to manual dispatch |

## Detailed Review

### Item: Git history and the delta

- Evidence: `git log --oneline 9c0b88c..8d299b8d` (113 commits, PRs #94–#168); `git diff --stat`
  (99 files, +8,955/−620); `git log --format='%an' … | sort | uniq -c` → 57 Julian Butler,
  51 `Audit Remediation <audit@localhost>`, 5 dependabot.
- What it does: the delta is the second remediation wave of the 20261004 audit plus observability
  fixes; it is merge-commit based (`Merge PR #N: <description>`).
- Missing controls: no release-please/semantic-release style automation; merge subjects are not
  conventional, so naive `git log`-driven note generators would include merge noise.
- Risk: low — the individual commits are conventional and traceable to PRs.

### Item: CHANGELOG accuracy for the delta

- Evidence: `git diff 9c0b88c 8d299b8d -- CHANGELOG.md` = +112 lines inserted at line 212 (inside
  `### Fixed`, which spans lines 137–327); 18 sampled entries verified against code (table above).
- What it does: documents every functional commit in the delta; docs/audit-register syncs, tests and
  Dependabot bumps correctly have no entries.
- Missing controls: `ea427954` (handlebars CRITICAL override) has no entry; all entries are filed
  under `Fixed`, so `?limit` search paging (`CHANGELOG.md:267`), the new secret-history-scan workflow
  (`:275`) and the Dependabot image coverage (`:312`) read as bug fixes.
- Risk: medium — the changelog is the input for release notes; misclassification and one missing
  security entry degrade the release story.

### Item: Version identity and tags

- Evidence: `VERSION` = `0.1.0` (single commit `6757a478`); 0 tags; no release workflow;
  `scripts/generate-sbom.mjs:300-306,325-326,444-459` (serialNumber + `mct:commit`);
  `docs/RELEASING.md:55-61` ("no git tag requirement — the commit SHA is authoritative");
  `deploy-do.yml:334` (`NEXT_PUBLIC_APP_VERSION=<ref_name>-<run_number>`);
  `apps/web/scripts/generate-version.js:4-12` writes `version.json` from it.
- What it does: releases are SHA-tagged GHCR images with digest-bound SBOM/provenance; the SBOM
  records `<VERSION>+<commit SHA>`.
- Missing controls: `VERSION` is never bumped, so two releases share `0.1.0`; the UI badge shows
  `main-168`, not the product version; no annotated tag or GitHub Release exists to attach the
  release notes/SBOM to.
- Risk: medium — product-version identity is ambiguous across surfaces.

### Item: Breaking changes and upgrade manifest

- Evidence: `CHANGELOG.md:12-25`; `git ls-tree 8d299b8d supabase/migrations/` (134 files, up to
  `5302436`); `supabase/migrations/5302432_drop_unused_soft_delete_columns.sql:19-30`;
  `5302434_anon_privilege_least_privilege.sql`; `grep 5302432|5302434 CHANGELOG.md` → none.
- What it does: flags the RLS entitlement changes and tells operators to apply `5302420`–`5302428`
  in order, with restore-from-backup rollback.
- Missing controls: the `[Unreleased]` window includes `5302430`–`5302436`; the column drops and the
  anon-grant removal are behavior/schema-affecting and unflagged. The delta itself adds no
  migrations, which the release notes should state explicitly.
- Risk: medium — an operator reading only `Breaking Changes` gets an incomplete upgrade picture.

### Item: Release notes template and process

- Evidence: `templates/RELEASE_NOTES_TEMPLATE.md:1-53` (version/sha/date, images, Added/Changed/
  Fixed/Security, Breaking Changes, Migrations, Operator Actions, Known Issues, Verification);
  `docs/RELEASING.md:64-74`; `templates/release_scorecard.md` (1-line placeholder).
- What it does: a complete, fill-in-the-blanks GitHub Release body; the process is documented as
  manual (cut the notes, move shipped entries under a dated heading, leave `[Unreleased]` empty).
- Missing controls: never exercised (no Release exists); the scorecard template is a dead stub.
- Risk: low — process is documented; execution is pending.

### Item: Rollback notes

- Evidence: `docs/ROLLBACK_PROCEDURES.md:1-58` (Docker/`rollback_sha`), `:62-113` (Supabase
  hard-delete + reverse migration/PITR/manual undo), `:114-186` (S3 restore contract),
  `:185-232` (Terraform), `:248-258` (`prod-approval`). Stale: `:199-203` claims a push/PR triggers
  `terraform-do` and applies automatically; `.github/workflows/terraform-do.yml:3-10` is
  manual-dispatch only (weekly plan gated by `TF_DRIFT_PLAN_ENABLED`).
- Risk: medium — an operator following §4 would push a revert and expect an apply that never runs.

### Item: Committed audit outputs (binding/aggregate check)

- Evidence: `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/follow_up_register.md:3`
  binds the run to `9c0b88c`; 14 commits after publication edit those registers (e.g. `7a8eb1ce`,
  `69777d94`) and update `findings.json`'s `generated` timestamp while leaving the header commit
  unchanged; the row notes record the later reconciliation ("reconciled 2026-10-11 … (#157)").
- Assessment: this matches the pack's documented reconciliation workflow
  (`runbooks/POST_AUDIT_PIPELINE.md` step 5 + `tools/remediation_status.py`, which updates registers
  in place). **Not raised as a finding**; the only residual is that a reader cannot tell from the
  header at which commit each status was verified — the per-row note carries it.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| REL-001 | Git history | 113 delta commits, conventional subjects | Merge-based traceability | Merge subjects non-conventional; one human author | P3 | Keep conventional subjects; document merge filtering |
| REL-002 | PR templates | `.github/PULL_REQUEST_TEMPLATE.md:17` | Changelog checkbox | No artifact checkbox; no enforcement | P3 | Add release-artifact line; enforce or drop |
| REL-003 | Changelog/release notes templates | `CHANGELOG.md`, `templates/RELEASE_NOTES_TEMPLATE.md` | Complete template, refreshed changelog | All delta entries under `Fixed`; handlebars entry missing | P3 | Re-file entries; add missing entry |
| REL-004 | Version files | `VERSION` = 0.1.0; SBOM binding | `<VERSION>+sha` in SBOM | Never bumped; web badge diverges | P1/P2 | Bump per release; pass to web build |
| REL-005 | Package versions | `private: true` everywhere | No npm publishing | No package versions | P3 | Keep; rely on SHA identity |
| REL-006 | Migrations | 134 migrations; none in delta | Changelog lists migrations where relevant | Manifest stops at `5302428` | P2 | Complete the manifest |
| REL-007 | API/UI/security/bug/dependency/infra/docs changes | 18/18 sampled entries match | Comprehensive delta entries | handlebars CRITICAL override undocumented | P3 | Add the entry |
| REL-008 | Breaking changes | `CHANGELOG.md:12-25` | Section exists | `5302432` drops columns; `5302434` anon grants — unflagged | P2 | Add both + "no migrations in this delta" |
| REL-009 | Known issues | Template section; `AGENTS.md` Known Debt | Template requires them | No known-issues pointer in `[Unreleased]` | P3 | Link Known Debt in the release notes |
| REL-010 | Operator actions | Template section | Template requires them | Delta actions embedded in `Fixed` entries | P3 | Add an Operator Actions block |
| REL-011 | Migration steps | Upgrade note + `ROLLBACK_PROCEDURES.md` | Restore-from-backup documented | No down-migrations; manifest incomplete | P2 | List filenames per release |
| REL-012 | Rollback notes | `ROLLBACK_PROCEDURES.md` | Docker/DB/S3 paths | §4 Terraform trigger stale | P2 | Update to manual dispatch |

## Findings

Verification outcomes for the previous register's REL rows (same titles) plus new findings:

1. **No version identity: no tags, no product version, no commit binding in generated artifacts** —
   P1, `partially-fixed`. SBOM now binds `<VERSION>+sha`; residual: 0 tags, `VERSION` never bumped,
   web badge uses `main-<run>`.
2. **Documented production deploy path is stated as non-functional and the approval gate claim is
   false** — P1, `verified-fixed` (`docs/RELEASING.md:76-106,134-148`, `deploy-do.yml:565-571`).
3. **`CHANGELOG.md` is stale relative to HEAD for the final commits in the delta** — P2,
   `verified-fixed` (26 delta commits touch it; +112 lines; final non-merge commit included).
4. **No explicit Breaking Changes or upgrade manifest despite 34 migrations and RLS/entitlement
   behavior changes** — P2, `partially-fixed` (section exists; manifest stops at `5302428`).
5. **No release-notes or GitHub Release body template; release body must be authored ad hoc** —
   P2, `verified-fixed` (`templates/RELEASE_NOTES_TEMPLATE.md`, referenced by `docs/RELEASING.md`).
6. **Rollback documentation is stale (Terraform push flow) and repeats the false approval claim** —
   P2, `partially-fixed` (approval claim fixed; `:203` push/apply claim stale).
7. **Commit history contains non-conventional noise commits and a single author, reducing
   automated-notes quality** — P3, `partially-fixed` (conventional subjects in the delta; merge
   subjects + single human author remain).
8. **PR template lacks changelog and versioned-artifact checkboxes** — P3, `partially-fixed`
   (CHANGELOG checkbox present; versioned-artifact box absent; unenforced).
9. **CRITICAL dependency fix (handlebars override) shipped without a CHANGELOG entry** — P3, `open`.
10. **Delta changelog entries are filed under `Fixed` only, mislabelling features and operator
    changes** — P3, `open`.
11. **Release docs claim `main` is far behind `develop`; the repo state is the opposite** — P2, `open`.

Detailed rows (severity/evidence/impact/recommendation/owner/confidence/status/note) are in the
domain JSON; the full verification notes are in the table above.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Incomplete breaking-change manifest misleads an upgrade | P2 | Medium | A consumer relying on dropped columns or anon access breaks at deploy | `CHANGELOG.md:22-25` vs `5302432`/`5302434` | Complete the manifest; flag both migrations |
| Release notes under-report a security fix | P3 | Medium | Stakeholders/auditors miss the CRITICAL advisory closure | `ea427954` vs `grep handlebars CHANGELOG.md` | Add the entry; refresh the Security bullet |
| Ambiguous product version across surfaces | P2 | Medium | Wrong artifact assumed for a release; SBOM/UI mismatch | `VERSION` vs `deploy-do.yml:334` | Bump `VERSION`; pass it to the web build; tag releases |
| Operator follows a stale Terraform rollback flow | P2 | Low | Revert pushed but never applied; drift persists | `ROLLBACK_PROCEDURES.md:203` vs `terraform-do.yml:3-10` | Update §4 to manual dispatch |
| Stale "main behind develop" claim in release docs | P3 | Medium | Wrong release-gate decision | `docs/RELEASING.md:149`, `AGENTS.md:100` vs `git rev-list` | Update both docs |

## Recommendations

### Immediate / Release Blocking

- None. This delta introduces no migrations and no API-spec change; the changelog covers the
  functional commits. (Release still gated by the operator items in `docs/RELEASING.md`:
  `prod-approval`/`prod` reviewers, prod secrets, `DO_API_TOKEN`.)

### This Week

- Add the missing `handlebars >=4.7.10` entry and refresh the `### Security` "0 critical/high"
  statement with the advisory that appeared and was cleared.
- Complete the `Breaking Changes` manifest to `5302436`, explicitly flagging `5302432` (column
  drops) and `5302434` (anon grant removal); state "this delta adds no migrations".

### This Month

- Bump `VERSION` per promotion (or record the owner decision to freeze it) and pass it to the web
  build so the badge/`version.json`, the SBOM and the release-notes header agree.
- Update `docs/ROLLBACK_PROCEDURES.md` §4 to manual `terraform-do` dispatch; correct
  `docs/RELEASING.md:149` / `AGENTS.md:100` about `main` vs `develop`.
- Re-file the delta's changelog entries under Added/Changed/Security and add an Operator Actions
  block for the release.
- Cut the first GitHub Release from `templates/RELEASE_NOTES_TEMPLATE.md` (tag or SHA-pinned) and
  attach the SBOM artifact — this also exercises the template.

### Later / Platform Evolution

- Decide tag/release automation (annotated tags on promotion + Release creation) or keep the
  SHA-authoritative decision and record it where release notes are cut.
- Replace the `templates/release_scorecard.md` placeholder with a real scorecard or delete it.
- Consider a lightweight changelog lint in CI (entry present when `apps/**` changes; classification
  keywords) instead of the honour-system PR checkbox.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add the handlebars entry | Closes a security-record gap | `CHANGELOG.md` (Fixed/Security) | `grep handlebars CHANGELOG.md` hits |
| List `5302430`–`5302436` in the upgrade note | Honest upgrade path | `CHANGELOG.md:22-25` | Read-through against `ls supabase/migrations` |
| Fix the two "main behind develop" sentences | Accurate release gate | `docs/RELEASING.md:149`, `AGENTS.md:100` | `git rev-list --count <sha>..origin/develop` = 0 |
| Update the Terraform rollback paragraph | Matches the manual-dispatch workflow | `docs/ROLLBACK_PROCEDURES.md:199-203` | Compare with `terraform-do.yml:3-10` |
| Delete or fill the scorecard stub | Removes a dead template | `templates/release_scorecard.md` | `grep -rn release_scorecard` = no refs |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Version bump + web badge alignment | P2 | release owner | S | Owner decision on tagging |
| Breaking-change manifest completion + guard | P2 | release owner / DB lead | S | None |
| Changelog classification lint in CI | P3 | platform/CI owner | M | None |
| Release automation (tags + Release + SBOM attach) | P3 | release owner | M | Owner decision; GitHub token |
| First cut of release notes from the template | P3 | release owner | S | Operator prod prerequisites |

## Suggested Tests

- **CI (changelog gate)**: fail a PR touching `apps/**` without a `CHANGELOG.md` diff (or an explicit
  `N/A` label); assert entry classification keywords match the touched paths.
- **Docs guard**: extend `scripts/check-docs-counts.mjs`-style checks to assert
  `docs/RELEASING.md`/`AGENTS.md` do not claim `main` is behind `develop` when
  `git rev-list --count <sha>..origin/develop == 0`.
- **Migration manifest guard**: a script that diffs `Breaking Changes` migration ranges against
  `supabase/migrations/` and fails when a schema-breaking migration (DROP COLUMN/REVOKE) is not
  referenced.
- **Release dry-run (manual)**: cut a GitHub Release for a past SHA from the template and verify the
  SBOM artifact/digest resolves; record the outcome in `docs/RELEASING.md`.
- **Regression (notes quality)**: parse `CHANGELOG.md` with Keep-a-Changelog tooling and assert no
  `Added`-class entry sits under `Fixed`.

## Suggested Documentation Updates

- `CHANGELOG.md` — complete `Breaking Changes`, add the handlebars entry, re-file the delta entries,
  add an Operator Actions block.
- `docs/RELEASING.md` — fix the `main` vs `develop` state claim; document when `VERSION` is bumped
  and how the web badge derives from it.
- `AGENTS.md` — same state-claim fix in Known Debt.
- `docs/ROLLBACK_PROCEDURES.md` — §4 Terraform: manual dispatch only; note the weekly gated plan.
- `templates/release_scorecard.md` — replace the placeholder with the real scorecard or remove it.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `VERSION` intended to stay `0.1.0` forever (SHA-authoritative), or should it be bumped per promotion? | Two identity surfaces disagree today | Owner statement or a `RELEASING.md` line; a tag in the remote |
| Do any annotated tags / GitHub Releases exist on the remote? | Local clone has 0 tags; cannot fetch | `git ls-remote --tags origin` or the GitHub Releases page |
| Are `NTFY_ALERTS_*` / `ALERTMANAGER_WEBHOOK_*` set in the target environments? | The delta's alerting entries claim live delivery | GitHub environment secrets (operator) |
| Has `pnpm audit` been re-run after `ea427954`? | The Security section's "0 critical/high" claim | CI `dependency-audit` run at/after `ea427954` |
| Was the `5302432` column drop communicated to any external consumer? | The columns were "never written", but consumers may read them | Search of integrations/SDK docs; product decision |

## Appendix

### A. Delta summary (`9c0b88c` → `8d299b8d`)

- 113 commits / 99 files; API 46, worker 18, docs 14, CI 7, infra 4, web 3, root/compose/etc. 7.
- No new migrations; `apps/api/src/openapi/` unchanged.
- Themes: audit-register reconciliation, notification/webhook correctness, worker resilience,
  CSV-export safety, SSE tenant scoping, search paging, observability auth + ntfy alerting,
  deploy SSH host-key verification, secret-history scan, dependency hygiene.

### B. Release notes draft for the delta (`release_notes_draft.md`)

```markdown
# Release notes — 0.1.0 (8d299b8d) — 2026-10-11

**Release:** `0.1.0` (`8d299b8d`, 2026-10-11)
**Images:** `ghcr.io/mainecybertech/mainecybertech/mct-{api,worker,web}:8d299b8d`
**Environments:** dev / prod

## Summary
Second remediation wave from the 2026-10-04 audit (9c0b88c → 8d299b8d): 113 commits of
correctness, security and observability fixes across API, worker, web, CI and infra. No schema
migrations and no API-spec change in this delta. Operator-visible additions: authenticated
Prometheus scrape, ntfy alert routing, weekly full-history secret scan.

## Added
- Admin search pagination (`?limit`, default 5 / cap 25) + per-entity counts (SEARCH-P2-004).
- Weekly full-history gitleaks scan (checksum-pinned, allowlist self-test) (SECRET-P2-003).
- Dependabot coverage for digest-pinned base images (CTR-P2-001).
- Migration dry-run plan captured as a CI artifact (IR-P2-006).

## Changed
- Worker resilience: `unhandledRejection` logs-and-continues; force-exit shutdown watchdog
  (`WORKER_SHUTDOWN_TIMEOUT_MS`, default 30s); `/health` reports `draining`/503 (NOTIF-P2-003 /
  RES-P2-001 / RES-P3-001).
- Web fails fast in production without `NEXT_PUBLIC_API_URL` (SECRET-P3-002).
- Local compose e2e service profile-gated; `E2E_ADMIN_PASSWORD` required (CTR-P2-002).

## Fixed
- CSV export formula-injection guard + mandatory tenant scope (FILE-P2-006).
- Sensitive exports audit-logged (ADMIN-P2-001).
- Webhook retry accounting + delivery/DLQ metering; raw-body signature fail-closed; M365 replay
  window (WH-P2-002/003/004/001).
- SSE notification stream asserts the resolved org (MT-P2-004).
- JSM sync pagination/retry (API-P2-002); inline email bounded retry (NOTIF-P2-006);
  notification-email XSS fix (CodeQL #6); atomic scheduled notification emails (NOTIF-P2-004).
- Declared-but-unused Prometheus metrics wired (IR-P2-001).

## Security
- `/metrics` and `/health/detail` require `METRICS_TOKEN` (404 otherwise); Prometheus authenticates
  via a 0600 credentials file.
- Alertmanager critical/default receivers post to ntfy with basic auth; backup/storage/restore-test
  failures notify ntfy (Slack fallback).
- Deploy SSH verifies the droplet host key on every path (CI-P3-003).
- `handlebars >=4.7.10` override clears new CRITICAL dev-only advisories.

## Breaking Changes
- None at the schema/API level in this delta (no migrations; OpenAPI spec unchanged).
  Operator-facing:
  - `METRICS_TOKEN` must be set or `/metrics` returns 404 and the `mct-api` scrape reports down.
  - Production worker refuses `QUEUE_BACKEND=inline`.
  - A production API without SMTP logs an error at boot (emails skipped and metered) — not fatal.

## Migrations
- None applied by this delta (`supabase/migrations/` unchanged since `9c0b88c`). The environment
  must still be current with the `[Unreleased]` manifest `5302420`–`5302436`.
- Rollback: redeploy the previous SHA images; no DB rollback needed for this delta
  (restore-from-backup procedure remains for schema changes).

## Operator Actions
- [ ] Set/refresh `METRICS_TOKEN`, `NTFY_ALERTS_*`, `ALERTMANAGER_WEBHOOK_USER/PASS` before deploy.
- [ ] Configure required reviewers on `prod-approval` and `prod` (still not configured).
- [ ] Confirm the ntfy topic receives a test alert after deploy.

## Known Issues
- `prod` environment still lacks `SUPABASE_*`/`JWT_SECRET`; `DO_API_TOKEN` returns 401
  (`docs/RELEASING.md` "Before promoting to prod").
- E2E data-dependent flakiness; re-run before treating a failure as a regression.
- `docs/RELEASING.md:149` still claims `main` is behind `develop` (stale; see REL findings).

## Verification
- [ ] `deploy-do` green; containers healthy (`docker ps`)
- [ ] Smoke checks: app login, API `/health`, storefront, admin dashboard
- [ ] Post-deploy alerts quiet for 30 minutes
```

### C. Upgrade / rollback note for the delta

- **Upgrade:** none — no migrations are added by `9c0b88c` → `8d299b8d`. Ensure the database is at
  the `[Unreleased]` migration set (`5302420`–`5302436`) per `supabase-migrations.yml`.
- **Rollback:** dispatch `deploy-do` with `rollback_sha=9c0b88c` (images already exist); no DB
  rollback required for this delta. General procedure: `docs/ROLLBACK_PROCEDURES.md`.
- **Watch items after deploy:** `METRICS_TOKEN` present (else `MCTServiceDown` fires on a healthy
  API); ntfy receivers reachable; worker starts (not `QUEUE_BACKEND=inline` in prod).

### D. Evidence gaps

- No node/pnpm in the audit environment → SBOM generation, changelog tooling and `pnpm audit` were
  not executed.
- No network → remote tags/Releases and GitHub environment settings are `unverifiable`; live ntfy
  delivery is `unverified` (the changelog claims it was verified live at deploy time).
