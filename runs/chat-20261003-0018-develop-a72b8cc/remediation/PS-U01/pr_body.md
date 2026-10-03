<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the unassigned API findings for run `20261003-0018`: stop interpolating raw user
input into PostgREST filter expressions (`API-P2-003`), and add an OpenAPI route-coverage
test so the served spec is checked against the implemented route registry (`API-P3-005`).
Changes are confined to `apps/api` source and its tests.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PS-U01` — Unassigned API findings (catch-all)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (`develop`)
- Branch: `remediation/ps-u01-20261003-0018-develop-a72b8cc`
- Commit: `43ad5e62db6ce224c696cf4c24c7887333ae41c5`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `API-P2-003` | P2 | open -> partially-fixed | Raw interpolation into `.or(...)` removed. `auth` search now uses a structured `.ilike()` with a normalised, length-capped pattern; `admin /users` quotes filter-syntax characters before embedding the term in `.or(...)`. |
| `API-P3-005` | P3 | open -> partially-fixed | Added a route-coverage test asserting the served OpenAPI spec documents every route exposed by `routeRegistry`; exported the spec generator used by the `/v1/openapi.json` route. |

Statuses map to `partially-fixed` because the PR is a draft; a human reviewer / green CI is
still required before `verified-fixed`.

## Changes

| File | What changed |
|---|---|
| `apps/api/src/lib/postgrest-filter.ts` (new) | `quotePostgrestValue` (double-quotes a value and escapes `\`/`"` for PostgREST `or()`/`and()`), `normalizeSearchTerm` (trim + 100-char cap), `containsPattern` (bounded `%term%` for structured `.ilike()`). |
| `apps/api/src/modules/auth/service.ts` | `searchUsers` uses `.ilike("display_name", containsPattern(query))` instead of `.or(\`display_name.ilike.%${query}%\`)`. |
| `apps/api/src/modules/auth/routes.ts` | `GET /v1/auth/search` validates/normalises the term with `normalizeSearchTerm` (rejects <2 or >100 chars). |
| `apps/api/src/modules/admin/routes.ts` | `GET /v1/admin/users` normalises `search` and builds the two-column OR with `quotePostgrestValue(\`%term%\`)`, so `,` `(` `)` `.` `"` are literal. |
| `apps/api/src/modules/openapi/routes.ts` | Export `generateDynamicSpec` for the coverage test (no behaviour change). |
| `apps/api/src/lib/__tests__/postgrest-filter.test.ts` (new) | Unit tests for quoting / normalisation / pattern building. |
| `apps/api/src/modules/auth/__tests__/auth.service.test.ts` | Asserts the structured `.ilike` filter and that filter syntax is passed as a literal value; length cap. |
| `apps/api/src/modules/admin/__tests__/admin.test.ts` | Asserts filter syntax is quoted in the admin user search. |
| `apps/api/src/modules/openapi/__tests__/openapi-coverage.test.ts` (new) | Route-coverage test: every method+path in `routeRegistry` must appear in the generated spec. |

Scope: `apps/api` source files cited by the findings plus the minimal tests the fixes
require. No dependency, config, or unrelated refactors.

## Verification Performed

Runner: `ci-runner` via `lab-run.ps1 -Repo chat` (ssh `root@172.23.128.51`, `/srv/work/chat`),
synced from the local branch working tree at `a72b8cc` + this change. Full raw log:
`remediation/PS-U01/verify.log` / `lab-raw.txt`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter @chat/api test` | ci-runner (node 20.x, vitest 3.2.6) | 0 | 64 test files passed, 496 tests passed; includes new `postgrest-filter` (6), `auth.service` (12), `admin` (14) and `openapi-coverage` (2) — `verify.log` §2 |
| local (pre-lab) `pnpm --filter @chat/api typecheck` | workstation (tsc) | 0 | no type errors |
| local (pre-lab) `pnpm --filter @chat/api lint` | workstation (eslint) | 0 | clean |
| `git diff origin/develop \| gitleaks stdin --redact --exit-code 1` | ci-runner (gitleaks 8.30.1) | 0 | no secrets added by the diff — `verify.log` §3 |

- Secret scan (gitleaks): **pass** on the diff (no leaks found).
- Scope check (files within patch set): **pass** — only the two finding locations, the
  shared filter helper, and their tests.

## Evidence bundle

- `remediation/PS-U01/diff.patch` — SHA-256 `205B97CC731CEB99319E4B943796B3DCD6E1CA2F820301A5DD9F23F7105E31A4`
- `remediation/PS-U01/manifest.json`
- `remediation/PS-U01/verify.log` (+ `lab-raw.txt`, `gitleaks-raw.txt`)

## Risk and rollback

- Risk: **low**.
  - `API-P2-003`: search semantics are unchanged (case-insensitive contains on the same
    columns); only the unsafe string construction changed. Admin OR terms are now quoted;
    `%` is still used as the wildcard, matching the existing `messages` search.
  - `API-P3-005`: test-only plus an export; no runtime behaviour change.
- Rollback: `git revert 43ad5e62db6ce224c696cf4c24c7887333ae41c5`.

## Review checklist

- [ ] Diff touches only `apps/api` source/tests for the two findings
- [ ] `API-P2-003` structured/quoted filters preserve search intent (`email`/`display_name` OR, `display_name` contains)
- [ ] `API-P3-005` route-coverage test is meaningful (fails if a registry route is missing from the spec)
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] No secrets added; gitleaks clean on the diff
- [ ] Tests added/updated for the fixes
- [ ] Rollback is practical

## Definition of done (for this set)

- No API code path interpolates raw user input into a PostgREST filter expression.
- The served OpenAPI spec is covered by a test that fails on registry/spec drift.

## Open questions

1. **`API-P3-005` is P3 (below the default P2 auto-patch scope).** It is included here only
   because the catch-all patch set `PS-U01` groups the unassigned API findings; a reviewer
   may prefer to split it into its own issue/PR.
2. **Static spec completeness.** The coverage test asserts the *served* (dynamically
   generated) spec covers the registry. Fully regenerating the committed
   `docs/api/openapi.json` from code is a larger change and is not attempted here.
3. **`messages/service.ts` cursor `.or(...)` (`created_at.lt...,and(...)`) and
   `status/routes.ts` `.or('expires_at.gt...')`** also use raw interpolation, but their
   inputs are not user-controlled free text and they are outside `API-P2-003`'s cited
   locations. Left untouched to keep scope minimal; worth a follow-up if these are later
   fed by request data.
