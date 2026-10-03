# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d`
- Patch set: `PATCH-005` — (P2) Fail-closed search
- Repo / base: `mainecybertech` @ `11746adc` (`fix/p2-batch-31`)

Closes API-P2-001. `routes/search.ts` now honors the tenant scope already resolved by
`requireOrgAccess` (`req.orgScope`) instead of re-deriving it, so an explicitly requested
organization narrows the search (even for a cross-tenant super admin) and an empty resolved org
set fails closed instead of degrading to an unscoped query. The only path allowed to span every
tenant (super admin with no explicit org) is now recorded in the search audit event.

Note: the branch base already carried the earlier `SEARCH-P1-002` hardening (mandatory org
predicates + `__no_match__` sentinels). This set adds the remaining PATCH-005 requirements:
`req.orgScope`/explicit-org narrowing and the audited all-tenants flag.

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `API-P2-001` | P2 | open -> fixed | Explicit org scope honored; empty scope fails closed; all-tenants audited |

## Changes

| File | What changed |
|---|---|
| `apps/api/src/routes/search.ts` | Derive `requestedOrgId` from `req.orgScope`; `allTenants = canSeeAllTenants && !requestedOrgId`; scope every entity query with `scopedOrgIds`; add `allTenants` to the audit metadata |
| `apps/api/src/__tests__/search-tenant-scope.test.ts` | Regression tests: empty scope -> no rows; explicit org -> narrows for a super admin; no explicit org -> all-tenants + audited; super admin with empty memberships -> no rows |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` (setup) | ci-runner (LXC 200, `172.23.128.51`) | 0 | `remediation/PATCH-005/verify.log` |
| `corepack pnpm --filter api typecheck && corepack pnpm --filter api test` | ci-runner (LXC 200, `172.23.128.51`) | 0 | `remediation/PATCH-005/verify.log` — 123 suites / 1410 tests passed |

- Secret scan (gitleaks 8.30.1, `detect --no-git --redact` on both changed files): **pass**, no leaks.
- Scope check (files within patch set): **pass** — `apps/api/src/routes/search.ts` plus the added test only.
- ESLint on both files (`apps/api/eslint.config.js`, `--max-warnings=0`): pass (exit 0).

## Evidence bundle

- `remediation/PATCH-005/diff.patch` — SHA-256 `a144dc0b6832796715d16ac504f27ab70acd397306601ee2c1f2d322f8611a81`
- `remediation/PATCH-005/manifest.json`
- `remediation/PATCH-005/verify.log`

## Risk and rollback

- Risk: low. Narrowing an explicit-org request is a behavior tightening; the all-tenants path is
  unchanged for a super admin with no explicit org. No schema, config, or dependency change.
- Rollback: `git revert ab783ed7e282544d803dd26da095a8476d5ceb29`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md` PATCH-005: non-platform admin with no memberships -> no rows; status-drift
membership -> no rows; platform admin explicit org -> scoped. Validation `pnpm --filter=api test`.
