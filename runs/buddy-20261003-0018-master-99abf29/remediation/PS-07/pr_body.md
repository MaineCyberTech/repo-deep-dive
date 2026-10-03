# Remediation PR — PS-07 Operations, privacy, offline

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Hardens the observability, privacy and offline behaviour of the Buddy PWA. Adds a Next.js
route error boundary that reports a structured, privacy-aware error event and gives users a
recovery path (OBS-P2-001/002); injects a build marker into the runtime (OBS-P3-001);
self-hosts the two web fonts so there is no runtime Google request and the typography works
offline (API-P2-002); adds a restrictive CSP plus defensive HTTP headers on every response
(SEC-P2-002); and versions the service-worker cache per build so stale app shells are purged
(ARCH-P2-001). API-P2-001 (API contract/versioning) remains deferred — there is no server in
the tree yet and the item is carried forward by PS-08.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-07` — Operations, privacy, offline
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `de0cae1f170e567502cc99ee6509f9f6c68afed9`
- Branch: `remediation/ps-07-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P2-001` | P2 | open -> partially-fixed | `reportError` in `app/error.tsx` emits a single structured JSON line (message, Next digest, build id, timestamp) and dispatches a `buddy:error` window event so a reporter (Sentry/OTLP) can be attached later. No third-party tracker or dependency was added — that is an infra/product decision (see open questions). |
| `OBS-P2-002` | P2 | open -> fixed | New `app/error.tsx` route error boundary renders a `SYSTEM FAULT` fallback with TRY AGAIN (`reset`), RELOAD and RESET SAVE (`deleteSave`) actions instead of a blank screen. Covered by `app/error.test.tsx`. |
| `OBS-P3-001` | P3 | open -> fixed | `next.config.js` resolves a build id (env -> `GITHUB_SHA` -> `git rev-parse --short HEAD` -> `dev`), sets `generateBuildId`/`NEXT_PUBLIC_BUILD_ID`, and the error fallback displays it. |
| `API-P2-002` | P2 | open -> fixed | Fonts are self-hosted at build time with `next/font/google` (IBM Plex Sans, JetBrains Mono); the `fonts.googleapis.com` `@import` and the two `preconnect` links are removed, so there is no third-party runtime request and the fonts cache offline. |
| `SEC-P2-002` | P2 | open -> fixed | `next.config.js` `headers()` adds `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy` and `Strict-Transport-Security` to all routes, and revalidates `/sw.js`. |
| `ARCH-P2-001` | P2 | open -> fixed | `/sw.js` derives `CACHE_NAME` from the `?v=<build id>` query used at registration (`lib/offline/sw.ts`); a new build is a new script URL, so it installs, opens a fresh cache and `activate` deletes every older `buddy-cache-*`. |
| `API-P2-001` | P2 | open -> deferred (partial) | There is still no `app/api/`, route handler or server action to bind a versioned contract to. The contract/versioning discipline is owned by PS-08/future cloud work; recorded as an open question rather than guessing a shape. |

## Changes

| File | What changed |
|---|---|
| `app/error.tsx` (new) | Route error boundary + `reportError` structured event; recovery actions (retry / reload / reset save); shows the build id. |
| `app/error.test.tsx` (new) | Renders the fallback, asserts the structured report contains the message/digest, verifies TRY AGAIN calls `reset`, and RESET SAVE calls `deleteSave`. |
| `next.config.js` | Build-id resolution + `NEXT_PUBLIC_BUILD_ID`; security headers and CSP via `headers()`; `Cache-Control` revalidation for `/sw.js`. |
| `public/sw.js` | Cache name resolved from the worker URL `?v=` query instead of the hardcoded `buddy-cache-v1`; install/activate kept `skipWaiting`/`clientsClaim` and old-cache purge. |
| `lib/offline/sw.ts` | Registers `/sw.js?v=<NEXT_PUBLIC_BUILD_ID>` so the SW URL (and therefore cache) changes per build. |
| `app/layout.tsx` | `next/font` self-hosted IBM Plex Sans + JetBrains Mono with CSS variables; removed the Google `preconnect` links. |
| `app/globals.css` | Removed the Google Fonts `@import`; body/LCD/button font families now use the `next/font` CSS variables. |
| `lib/progression/lifecycle.test.ts` | One-line `[...new Set]` -> `Array.from(new Set)` unblock for the pre-existing `TS2802` typecheck error (same minimal unblock used in PS-01/PS-03/PS-06). |

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `de0cae1`) | 0 | `remediation/PS-07/verify.log` — lint clean; typecheck clean; 6 files / 112 tests passed |
| `npm run build && npm run test -- error` | lab: `ci-runner` | 0 | build compiled successfully (fonts self-hosted); `app/error.test.tsx` 3 tests passed |
| `curl -sSI http://127.0.0.1:3999/` and `/sw.js` (`next start`) | lab: `ci-runner` | 0 | CSP + `X-Content-Type-Options` + `X-Frame-Options` + `Referrer-Policy` + `Permissions-Policy` + HSTS present; `/sw.js` `Cache-Control: public, max-age=0, must-revalidate` |
| offline/privacy/cache checks (see `verify.log`) | lab: `ci-runner` | 0 | built CSS + server app output + rendered HTML contain 0 `fonts.googleapis.com` refs; build id `99abf29` -> `verify-abc123` is inlined into the client bundle that registers `/sw.js?v=<id>` |
| `git archive HEAD \| tar -x -C /tmp/glscan-ps07c && gitleaks detect --no-git --redact --source /tmp/glscan-ps07c -v` | lab: `ci-runner` | 0 | `no leaks found` (~262 KB, tracked content at the commit) |
| `npm run lint` / `npm run typecheck` / `npm run test` / `npm run build` | local (node v24.19.0) | 0 | lint clean; typecheck clean; 6 files / 112 tests; build OK |

- Secret scan (gitleaks): **pass** — no leaks at commit `de0cae1`.
- Scope check: **pass with two documented deviations.** Runtime files are the patch-set files
  (`app/error.tsx`, `next.config.js`, `public/sw.js`, `app/globals.css`, `app/layout.tsx`). The
  two extra files are required/unblocking: `lib/offline/sw.ts` is the one-line registration that
  actually versions the worker URL (without it the SW cache cannot change per build), and
  `lib/progression/lifecycle.test.ts` is the pre-existing `TS2802` one-line unblock already used
  by PS-01/PS-03/PS-06. `app/error.test.tsx` is the required test.

## Evidence bundle

- `remediation/PS-07/diff.patch` — SHA-256 `5ad4d8f8e40d4ae7ad5aa4709cae8b9482fd571453afe20215abdaaff7f7e73f`
- `remediation/PS-07/verify.log` — SHA-256 `a7da03635d9a620c792701d12ed2f69417cb7d1a45475dba68e2024add5c747d`
- `remediation/PS-07/manifest.json`

## Risk and rollback

- Risk: **low–moderate**. The headers/CSP are the main behavioural change; the policy stays
  same-origin and keeps `'unsafe-inline'` for scripts/styles because Next.js inlines its runtime
  bootstrap (no `'unsafe-eval'` in production). Self-hosting fonts adds a build-time download from
  Google (the lab build retried one `fonts.gstatic.com` fetch once, then succeeded) but removes the
  runtime request. Behaviour of the game itself is unchanged.
- Rollback: `git revert de0cae1` (single commit; no schema, storage or dependency changes).

## Open questions / reviewer actions

1. **API-P2-001 is deferred.** No server/API exists to version. Confirm it stays with PS-08 /
   future cloud work rather than being force-fitted here.
2. **Error-reporting backend.** `buddy:error` and the JSON line are the integration point; choose
   Sentry/OTLP (or nothing) in a follow-up. This is why OBS-P2-001 is `partially-fixed`, not fixed.
3. **CSP strength.** `script-src`/`style-src` allow `'unsafe-inline'` for Next.js. Moving to
   nonces/hashes would need middleware and is out of this patch set.
4. **PS-03 dependency not merged.** The plan lists PS-03 as a dependency; this branch is based on
   `origin/master` and touches none of PS-03's files, so it can land independently.
5. **Two files outside the plan list** (`lib/offline/sw.ts`, `lib/progression/lifecycle.test.ts`)
   are documented under the scope check above.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests), or the deviations above are accepted
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (from `patch_plan.md`)

- error-boundary test; header assertions; offline font load; cache name changes on build.
