# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all security remediation for the unassigned `SEC` findings from the
2026-10-03 audit run. It enforces an **Origin allowlist on the anonymous
browser-facing HTTP ingest endpoints** (`SEC-P2-001`) and adds the **local
pre-commit half of repository secret scanning** (`SEC-P2-002`). It touches no
application behaviour outside those routes and no dependency or lockfile. The
two P3 findings in the set (`SEC-P3-001`, `SEC-P3-002`) are recorded as open
questions below rather than guessed at, per the runner's fail-closed rule.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U11` — Unassigned SEC findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SEC-P2-001` | P2 | open -> **verified-fixed** | `POST /perf` and `POST /client-error` now reject a cross-origin `Origin` that is neither same-origin with the request `Host` nor listed in `ALLOWED_ORIGINS`, with `403 {"ok":false,"error":"origin_forbidden"}` before any body is read. An admissible `Origin` is echoed (`Access-Control-Allow-Origin` + `Vary: Origin`). Non-browser callers (no `Origin`) and same-origin callers are unaffected. Proven by `apps/realtime/src/__tests__/httpOrigin.test.ts` at the commit. |
| `SEC-P2-002` | P2 | open -> **partially-fixed** | `.githooks/pre-commit` runs `gitleaks protect --staged` (redacted) over the staged index; `SECURITY.md` documents `git config core.hooksPath .githooks`. The hook probe blocks a staged secret and passes a clean index. The **CI tree scan** half is delivered by the sibling CI catch-all `PS-U03` (draft #13), so the finding closes fully only when that merges; if PS-U03 does not merge, CI scanning must be re-homed. |
| `SEC-P3-001` | P3 | open -> **still-open (deferred)** | The suggested `current_user = 'service_role'` check does not hold for `SECURITY DEFINER` functions: inside them `current_user` is the function owner (`postgres`), not the caller, so the literal fix would deny the trusted psql path. See Open question 1 for the correct invoker signal and the needed negative-SQL proof (not covered by the npm gate). |
| `SEC-P3-002` | P3 | open -> **still-open (deferred)** | Moving `RM_SUPABASE_SERVICE_ROLE_KEY` from an env var to a Docker/Compose secret changes the runtime secret path and needs a boot read-order change plus an operator deploy rehearsal. See Open question 2. |

## Changes

| File | What changed |
|---|---|
| `apps/realtime/src/server.ts` | `rejectDisallowedOrigin()` / `originAllowed()` helpers; wired into the `POST /perf` and `POST /client-error` routes only. An allowed origin is echoed with `Vary: Origin`; a disallowed one gets `403 origin_forbidden`. |
| `apps/realtime/src/__tests__/httpOrigin.test.ts` (new) | Four tests: disallowed Origin -> 403 on both endpoints; allowlisted Origin -> 202 + `Access-Control-Allow-Origin`; same-origin (Origin host == Host) -> 202; no Origin -> 202. |
| `.githooks/pre-commit` (new, mode 100755) | `gitleaks protect --staged --redact` over the staged index; no-op (with a notice) when gitleaks is absent; skips when nothing is staged. |
| `SECURITY.md` | New "Secret scanning" section: CI + pre-commit gates and how to enable the hook. |

Coordination: `PS-U02` and `PS-U06` also edit `apps/realtime/src/server.ts`
(readiness/throughput and launch-readiness regions respectively); this PR's
hunks are confined to the `handleHttp` route table (~L1032/L1086) and new
helper methods after `handleHttp`, so the hunks do not overlap. `PS-U03`
adds `.github/workflows/ci-foundation.yml`, `.gitleaks.toml` and
`scripts/repo-secret-scan.sh`; this PR adds a distinct `.githooks/pre-commit`
and does not touch those files.

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab
(`/srv/work/snowride-ps-u11`, `core.autocrlf` unset, HEAD `559170d`), Node
v20.20.2 / npm 10.8.2 / gitleaks 8.30.1. Raw output with exit codes is in
`remediation/PS-U11/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci` | ci-runner | 0 | 628 packages installed (`verify.log`) |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npx vitest run apps/realtime/src/__tests__/httpOrigin.test.ts` | ci-runner | 0 | 1 file, 4 tests passed |
| `npm test` (profile gate) | ci-runner | 0 | 132 test files, 877 tests passed (baseline 131/873 + the new 4) |
| pre-commit hook probe: stage a synthetic token, run hook | ci-runner | 1 (blocked) | `leaks found`; clean index reruns exit 0 |
| `git status --short` after the gates | ci-runner | 0 | clean (no generated files committed) |
| `gitleaks detect --no-git --redact` on each changed file | ci-runner | 0 | 4/4 files clean |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing `generic-api-key` fixtures under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff |

- Secret scan (gitleaks): **pass** for this diff - all four changed files
  clean; the 19 full-tree hits are the audited fixtures also recorded by
  PS-U03/PS-U04/PS-U10.
- Scope check (files within patch set): **pass** - `PS-U11` declared no file
  list; the diff is limited to the two SEC P2 fixes (realtime HTTP server +
  its test, the pre-commit hook and the security doc).

## Evidence bundle

- `remediation/PS-U11/diff.patch` — SHA-256 `732f5b4ae776101823c865346de088629a5420e4f07e679d2d5148cb621c175d`
- `remediation/PS-U11/verify.log`
- `remediation/PS-U11/gitleaks.log`
- `remediation/PS-U11/manifest.json`

## Risk and rollback

- Risk: **low**. Origin enforcement only affects requests that carry a
  cross-origin `Origin`; same-origin browser traffic (the production layout)
  and non-browser callers are unchanged. On a misconfigured deployment where
  the public origin is neither forwarded as `Host` nor listed in
  `ALLOWED_ORIGINS`, anonymous RUM ingest (`/perf`, `/client-error`) would be
  rejected; set `ALLOWED_ORIGINS` to the public origin. The pre-commit hook is
  inert until `core.hooksPath` is enabled, and is a no-op without gitleaks.
- Rollback: `git revert 559170d011b0f11a6be3566760c320043e7f53e9`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- Cross-origin pages cannot drive `/perf` or `/client-error` (`SEC-P2-001`).
- A secret staged for commit is blocked locally (`SEC-P2-002`), with the CI
  tree scan provided by `PS-U03`.

## Open questions

1. **`SEC-P3-001` correct invoker signal under `SECURITY DEFINER`.** The
   finding recommends `current_user = 'service_role'` in the claim-less branch,
   but both `social_guard_self` and `social_guard_moderator` are `SECURITY
   DEFINER`, so `current_user` inside the body is the owner (`postgres`), not
   the caller; the literal change would deny the trusted psql/negative-suite
   path. The fix needs the right signal (`session_user`, `current_setting(
   'role')`, or `pg_has_role(...)` - to be established empirically) plus a
   negative SQL suite for an `anon` call, which the `npm ci && lint && test`
   gate does not exercise. Recommend a dedicated SQL/DB remediation with a
   fresh Postgres fixture before changing the guard.
2. **`SEC-P3-002` service-role key as a file secret.** Compose currently
   interpolates `RM_SUPABASE_SERVICE_ROLE_KEY` from the environment (and
   `env_file`); moving it to a Compose secret requires the realtime boot path
   to read the mounted file, plus a deploy rehearsal and a key-rotation
   decision. This is an operator/release change, not a code-only fix, so it is
   deferred rather than guessed.
3. **Cross-origin preflight.** This PR rejects/echoes `Origin` but does not add
   an `OPTIONS` preflight handler for the two ingest routes. Same-origin and
   `sendBeacon` traffic are unaffected; if a genuinely cross-origin browser
   client is ever allowed, add preflight handling in the same helper.
