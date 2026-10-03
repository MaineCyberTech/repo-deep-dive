# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Makes the `/install` page SSR/prerender-safe so the web build no longer fails. Next.js
prerenders the `InstallPage` client component at build time in a Node environment where
`navigator` is undefined. The page called `getPlatform()` / `getInstallInstructions()`
during render, and `getPlatform()` read `navigator.userAgent` unguarded, throwing
`ReferenceError: navigator is not defined` and aborting `next build` at the `/install`
prerender step. This patch adds a `typeof navigator === "undefined"` guard (defaulting to
`"unknown"` + generic instructions) and derives the platform client-side with a stable
`"unknown"` initial value so the prerendered HTML and the first client render match and
the page hydrates without a mismatch. Client behavior is otherwise unchanged.

- Audit run: `20261003-0018-develop-a72b8cc`
- Patch set: `PATCH-16` — Fix /install SSR prerender (navigator is not defined)
- Repo / base: `MaineCyberTech/chat` @ `a72b8cc43590848b052bd5e8954dbbc726b3d7fd` (develop)

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `BLD-P1-001` | P1 | open -> partially-fixed | `navigator` guarded in a pure `detectPlatform()`; `/install` now prerenders (`○ /install`) and the web build exits 0. Status advances to `verified-fixed` on merge. |

## Changes

| File | What changed |
|---|---|
| `apps/web/lib/pwa/install-state.ts` | Extracted SSR-safe `detectPlatform()` (`typeof navigator === "undefined"` -> `"unknown"`); `getPlatform()` delegates to it. `getInstallInstructions()` now accepts an optional `platform` override so callers can render a safe default server-side. |
| `apps/web/app/install/page.tsx` | `platform` is now React state initialized to `"unknown"` and upgraded in `useEffect` from `getPlatform()`; `instructions` is derived from `platform`. No `navigator` access during render/prerender. |
| `apps/web/components/pwa/__tests__/install-state.test.ts` | New unit tests: `detectPlatform()` returns `"unknown"` with no `navigator`, and detects `windows`/`android` from `userAgent`. |

Scope: 2 in-scope product files + 1 test. No dependency, config, or unrelated changes.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile && corepack pnpm --filter web build` | lab `ci-runner` (172.23.128.51) | 0 | `remediation/PATCH-16/verify.log` — `✓ Generating static pages (9/9)`; `/install` = `○` (prerendered) |
| `corepack pnpm exec vitest run --config vitest.config.ts apps/web/components/pwa/__tests__/install-state.test.ts apps/web/components/pwa/__tests__/install-prompt.test.tsx` | lab `ci-runner` | 0 | `verify.log` — 2 files, 10 tests passed |
| `corepack pnpm --filter web typecheck` | lab `ci-runner` | 0 | `verify.log` — `tsc --noEmit` clean |
| `gitleaks dir /tmp/p16scan --redact` (changed files) | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` — `no leaks found` (11.50 KB) |
| `git diff --cached --unified=0 ... \| gitleaks stdin --redact` | lab `ci-runner` (gitleaks 8.30.1) | 0 | `verify.log` — `no leaks found` (2.77 KB) |

- Secret scan (gitleaks): **pass** — gitleaks 8.30.1, no leaks on the changed files or the staged diff.
- Scope check (files within patch set): **pass** — only `apps/web/lib/pwa/install-state.ts`, `apps/web/app/install/page.tsx`, plus the in-scope test.

## Evidence bundle

- `remediation/PATCH-16/diff.patch` — SHA-256 `FBEFE2A19DE89185ED9CF8A03D3813964C26DA789CDCDE2F5C916EE10A9D02D6`
- `remediation/PATCH-16/manifest.json`
- `remediation/PATCH-16/verify.log`

## Risk and rollback

- Risk: **low**. The change only affects how/when platform detection runs. Server renders
  the generic "Install App" instructions and `unknown`; after hydration the effect swaps in
  the real platform. No API, data, or dependency changes.
- Rollback: `git revert c01525def487107299ef04148e20854c90f013a3`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- `corepack pnpm --filter web build` succeeds.
- `/install` prerenders (verified: `○ /install` in the route table) rather than throwing
  `ReferenceError: navigator is not defined`.

## Follow-ups (not in this patch set)

- Audit other render-scope PWA helpers for unguarded `navigator`/`window` access (the lens
  open question). `useInstallPrompt`'s `useEffect` body still assumes a browser, which is
  safe because effects do not run during prerender.
