<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the two unassigned repository-inventory findings in catch-all patch set `PS-U09`
(`INV-P2-003`, `INV-P3-002`) with a minimal, documentation-only change. No application code,
workflows, dependencies, schema, lockfile, or `.env*` templates are touched.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U09` — Unassigned INV findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (`develop`)
- Branch: `remediation/ps-u09-20261003-0018-develop-a72b8cc`
- Commit: `3a46f2f8c3ab723d3f07402e1559bca9094e21a1`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `INV-P2-003` | P2 | open -> partially-fixed | Hand-written audit artifacts are now explicitly marked as historical, non-authoritative snapshots (`docs/audits/README.md`), and the concrete false claim that `test-signin.json` is absent from the repo is corrected in `docs/audits/compare/audit_final_testing_20260724.md` — it **is tracked** (`git ls-files test-signin.json`), which is the security problem (`INV-P2-002`), not its absence. |
| `INV-P3-002` | P3 | open -> partially-fixed | `docs/environments/env-vars.md` is corrected to state the real source of truth (the Zod schemas) and now documents the schema keys missing from the examples, including `WEBHOOK_ENCRYPTION_KEY` — which the webhook service throws without (`apps/api/src/modules/webhooks/service.ts:22`) while none of `.env.example`, `apps/api/.env.example`, `infra/docker/.env.prod.example`, or `infra/docker/.env.devremote.example` define it. |

Statuses map to `partially-fixed` while the PR is a draft; they advance to `verified-fixed` only
after a human merges (the residual items below require files this PR deliberately does not touch).

## Changes

| File | What changed |
|---|---|
| `docs/audits/README.md` | New **Authoritativeness** section: `docs/audits/**` are historical snapshots; current status must come from the pipeline's `findings.json` + `RELEASE_GATE.md` and be commit-stamped; "ALL CLEAN" verdicts in old reports are not the current status. |
| `docs/audits/compare/audit_final_testing_20260724.md` | Added a correction callout and fixed the two `E2E-002` statements that claimed `test-signin.json` is "not in repo"; it is tracked (see `INV-P2-002`). No other finding content changed. |
| `docs/environments/env-vars.md` | Corrected the "root `.env.example` documents all variables" claim; added `WEBHOOK_ENCRYPTION_KEY`, `SHOW_STACK_TRACES`, `EMAIL_FROM` to the API table; new **Canonical schema and example consistency** section listing which templates omit which keys and calling out the webhook-encryption requirement. Rows are appended without reformatting the existing table. |

Scope: three documentation files. No code, workflow, dependency, schema, or lockfile changes.

## Verification Performed

Runner: lab `ci-runner` (172.23.128.51) via `scripts/lab-sync.ps1 -Repo chat` +
`scripts/lab-run.ps1 -Repo chat`. Raw log: `remediation/PS-U09/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | lab `ci-runner` | 0 | `verify.log` §2 — `Lockfile is up to date`; 883 packages; `Done in 2.4s` |
| `corepack pnpm exec prettier --check docs/audits/README.md docs/audits/compare/audit_final_testing_20260724.md` | lab `ci-runner` | 0 | `verify.log` §3 — `All matched files use Prettier code style!` |
| `corepack pnpm exec prettier --check docs/environments/env-vars.md` | lab `ci-runner` | 1 | `verify.log` §3 — **pre-existing only**: the unmodified base file (`git show HEAD:...`) reproduces the identical exit 1; PS-U09 appends rows without reformatting the table, so this is not a regression |
| `git ls-files test-signin.json` | lab `ci-runner` | 0 | `verify.log` §4 — lists `test-signin.json` (the audit report's "not present" claim was false) |
| `grep -c not.present.in.repo docs/audits/compare/audit_final_testing_20260724.md` | lab `ci-runner` | 0 (count 0) | `verify.log` §4 — stale phrase gone |
| `grep -l WEBHOOK_ENCRYPTION_KEY .env.example apps/api/.env.example infra/docker/.env.prod.example infra/docker/.env.devremote.example` | lab `ci-runner` | 0 (no files) | `verify.log` §4 — key absent from every template, while `service.ts:22` throws without it |
| `gitleaks detect --no-git --redact --no-banner --source <each changed file and diff.patch>` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` §5 — `no leaks found` (9,221-byte diff + 3 files) |

- Secret scan (gitleaks): **pass** — no leaks in the diff or any changed file.
- Scope check: **pass** — three docs only.
- No API test run was required (docs-only change; no runtime/config/workflow change).

## Evidence bundle

- `remediation/PS-U09/diff.patch` — bytes 9221; SHA-256 `8678127C2F01301310C8C6141D6B080D33ED94B4F2BC41C8CC7FE0595CFF0C51`
- `remediation/PS-U09/manifest.json`
- `remediation/PS-U09/verify.log`
- `remediation/PS-U09/lab-sync.log`

## Risk and rollback

- Risk: **very low**. Documentation only; no runtime, CI, dependency, or schema behavior changes.
- Rollback: `git revert 3a46f2f8c3ab723d3f07402e1559bca9094e21a1`.

## Review checklist

- [ ] Diff touches only the three cited docs (+ no unrelated reformatting)
- [ ] `INV-P2-003`: the corrected statements match `git ls-files test-signin.json`
- [ ] `INV-P3-002`: the stated required key and the omitted-template list match the schemas/compose files
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Rollback is practical

## Definition of done (for this set)

- No `docs/audits/**` artifact is presented as current status; the audit index says how status is derived.
- The stale `test-signin.json` claim is corrected where it appears in the cited report.
- The canonical env doc records the keys the examples omit and the webhook-encryption requirement.

## Open questions / deferred

1. **`.env*.example` templates were not edited.** The remediation profile lists `**/.env*` as a
   blocked path, so the example files are left untouched. The recommended fix (align/generate the
   templates from `packages/config/env-schema.ts` + `apps/api/src/config/env.ts`, and pass
   `WEBHOOK_ENCRYPTION_KEY` through `docker-compose.prod.yml`) is recorded in the canonical env doc
   as a follow-up. A reviewer may prefer to do the template edits as a separate, explicitly
   approved PR.
2. **`INV-P2-003` overlaps `EXEC-P2-002`.** `AGENTS.md`'s "0 P0/P1 / ALL CLEAN / both healthy"
   claims are the other half of this finding and are already addressed by `PS-U05`
   (`docs/operations/release-readiness-status.md`, draft PR #71). This PR deliberately does not
   touch `AGENTS.md` to avoid a conflicting edit; the two PRs should be considered together.
3. **Historical audit reports are otherwise left as-is.** Only the one cited concrete falsehood and
   the index note were changed; rewriting every stale "ALL CLEAN" verdict in the report pack is a
   larger cleanup and is out of scope for this catch-all.
4. `INV-P3-002` is P3 (below the profile's default P2 auto-patch scope) and is included only
   because the catch-all `PS-U09` groups the unassigned INV findings.
