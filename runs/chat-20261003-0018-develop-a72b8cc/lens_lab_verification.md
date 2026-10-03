# Lab Verification Lens — chat

## Audit Metadata

- Audit name: chat
- Run: 20261003-0018-develop-a72b8cc
- Repository: `C:\temp\chat` — `develop` @ `a72b8cc`
- Generated at: 2026-10-03 (lab run on the Proxmox ci-runner LXC 200)
- Area code: BLD
- Source: real build/test execution in the lab (node 20.20.2, pnpm 10.34.3)

## Scope

Build and test execution for the web/api packages in the lab, to confirm the audit's
testing/CI findings. Not a re-audit; it records fresh evidence.

## Evidence Reviewed

- `apps/web/app/install/page.tsx` — calls `getPlatform()` / `getInstallInstructions()` in the render body.
- `apps/web/lib/pwa/install-state.ts` — `getPlatform()` reads `navigator.userAgent` with no guard.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm install --frozen-lockfile` | ci-runner | 0 | install ok |
| `corepack pnpm typecheck` | ci-runner | 0 | 11 tasks pass |
| `corepack pnpm test` | ci-runner | 1 | `@chat/api` 485 pass; `@chat/web` build fails at prerender `/install` |

Observed error:

```
Error occurred prerendering page "/install"
ReferenceError: navigator is not defined
    at <unknown> (.next/server/chunks/742.js:5:32566)
```

## Findings

### Finding ID: BLD-P1-001 - Web build fails prerendering /install (navigator is not defined)

- Severity: P1
- Confidence: High
- Area: BLD
- Evidence:
  - `apps/web/app/install/page.tsx` — `const platform = getPlatform(); const instructions = getInstallInstructions();` run during render (and therefore during `next build` prerender).
  - `apps/web/lib/pwa/install-state.ts` — `getPlatform()` uses `navigator.userAgent` with no `typeof navigator` guard.
  - Lab command `corepack pnpm test` → `@chat/web` build exits 1 at prerender `/install`.
- What is happening: `InstallPage` is a client component, but Next.js still prerenders it at build time. `getPlatform()`/`getInstallInstructions()` execute in the Node build environment where `navigator` is undefined, so the prerender of `/install` aborts the whole web build.
- Why it matters: the production web build fails, so a release cannot be produced; CI/web build is red.
- User / business impact: no web deploy from this commit.
- Security / privacy / reliability impact: release-availability blocker.
- Recommended fix: make `getPlatform()`/`getInstallInstructions()` SSR-safe — guard `typeof navigator === "undefined"` (default to `"unknown"` / generic instructions), and/or compute platform + instructions in a `useEffect` (client-only) with a safe default during prerender.
- Suggested validation: `corepack pnpm --filter web build` succeeds and `/install` prerenders (or is dynamic).
- Owner suggestion: web
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Web build cannot ship | P1 | High | High | lab build failure | BLD-P1-001 fix |

## Recommendations

### Immediate / Release Blocking
- Guard `navigator` in `lib/pwa/install-state.ts` (and any render-path PWA helpers).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `typeof navigator` guard | unblocks the whole web build | `lib/pwa/install-state.ts` | `pnpm --filter web build` |

## Suggested Tests

- Add a prerender/SSR smoke test for `/install`, or assert `getPlatform()` returns `"unknown"` without `navigator`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are other render-path helpers navigator-dependent? | same class of build break | grep for module/render-scope `navigator` |
