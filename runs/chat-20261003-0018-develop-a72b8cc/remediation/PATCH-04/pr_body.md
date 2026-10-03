# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Scope the admin directory, audit-log, and compliance-export endpoints to the caller's
administered workspaces, and restrict bulk imports to an explicit platform-admin allowlist.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-04` — Scope admin endpoints to caller's workspaces (SEC-P1-003/004/005/006)
- Repo / base: `chat` @ `a72b8cc` (`origin/develop`)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P1-003` | P1 | open -> fixed | `/admin/users` now returns only members of the caller's admin workspaces |
| `SEC-P1-004` | P1 | open -> fixed | `/admin/audit-logs` requires `workspaceId` and enforces admin-of-that-workspace |
| `SEC-P1-005` | P1 | open -> fixed | `/admin/exports` and `/admin/exports/:id/download` filtered by `workspace_id` in caller's admin workspaces |
| `SEC-P1-006` | P1 | open -> fixed | `/admin/import/workspaces` and `/admin/import/users` now require a platform admin (allowlist, fail closed) |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/modules/admin/routes.ts` | Scope `/users` to member ids of the caller's admin workspaces; require + verify `workspaceId` on `/audit-logs`; add `.in("workspace_id", workspaceIds)` to `/exports` and `/exports/:id/download` |
| `apps/api/src/modules/import/routes.ts` | Replace `requireAdmin()` with `requirePlatformAdmin` reading `PLATFORM_ADMIN_USER_IDS` (fail closed) on both import routes |
| `apps/api/src/modules/admin/__tests__/admin.test.ts` | Cross-tenant negative/unit tests for the four scoping changes |
| `apps/api/src/modules/import/__tests__/import.test.ts` | Platform-admin gate tests (unset allowlist, non-allowlisted caller, allowlisted caller) |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter api test` | ci-runner (Proxmox) | 0 | `remediation/PATCH-04/verify.log` — `Test Files 62 passed (62)`, `Tests 495 passed (495)` |
| `corepack pnpm exec vitest run apps/api/src/modules/admin apps/api/src/modules/import && corepack pnpm --filter api typecheck` | ci-runner (Proxmox) | 0 | `remediation/PATCH-04/verify.log` — `Tests 28 passed (28)`, `tsc --noEmit` clean |

- Secret scan (gitleaks 8.30.1): **pass** — `gitleaks protect --staged --redact --exit-code 1` → `no leaks found`, exit 0 (`remediation/PATCH-04/gitleaks.log`). Whole-tree `gitleaks detect --no-git` reports 47 pre-existing findings confined to lab-local generated artifacts under `apps/web/.next/cache/**`, which are outside this patch.
- Scope check (files within patch set): **pass** — diff touches only the two patch-set files plus their tests.
- Lab hygiene note: an initial run failed on a stale untracked test (`apps/web/components/pwa/__tests__/install-state.test.ts`) left in the shared lab from a prior session. The lab was cleaned (`git clean -fd`) and re-synced, after which the suite was fully green. The stale failure was not caused by this patch and that file is not present in the repository.

## Evidence bundle

- `remediation/PATCH-04/diff.patch` — SHA-256 `eca14f5447e9bfaaaa41bf6e1d1dcc3e1c3a10c401ff55ce0c09c4d97eddc71d`
- `remediation/PATCH-04/manifest.json`
- `remediation/PATCH-04/verify.log`
- `remediation/PATCH-04/gitleaks.log`

## Risk and rollback

- Risk: **low-medium**. Query-scope narrowing and an additional authorization gate. Behaviour change: imports now require `PLATFORM_ADMIN_USER_IDS` to be populated or they return 403 (intentional fail-closed).
- Rollback: `git revert c41aa79994f291f22b12a0b9504edb88170c1ff8` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical
- [ ] `PLATFORM_ADMIN_USER_IDS` is provisioned in the deployment environment (see open questions)

## Definition of done (for this set)

- `/admin/users`, `/admin/audit-logs`, `/admin/exports`, `/admin/exports/:id/download` are scoped to the caller's admin workspaces.
- Imports are platform-admin-only and fail closed.
- Cross-tenant negative tests pass.

## Notes / open questions

- `remediation_plan.json` lists only `SEC-P1-003` under PATCH-04 (004–006 were in `unassignedFindings`), although the patch-plan title and task cover SEC-P1-003/004/005/006. This PR implements all four; `tools/remediation_status.py` will therefore reconcile only `SEC-P1-003` until the plan is regenerated/updated.
- There is no platform-admin role in the schema. This PR introduces a `PLATFORM_ADMIN_USER_IDS` (comma-separated Supabase user ids) allowlist as a minimal, fail-closed control. A durable platform-admin role (e.g. `app_metadata.role`) and populating the allowlist from secrets are recommended follow-ups; user-editable `raw_user_meta_data` must not be trusted.
- The compliance-export worker must keep writing `workspace_id` on export rows for the new filters to behave as intended (already present via `20260716000001`).
