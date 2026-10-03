# Remediation PR — PS-U01 Unassigned ARCH findings (catch-all): ARCH-P1-001

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes `ARCH-P1-001` ("Entire game is client-authoritative with no server trust boundary") with the
minimal, correct fix available at this commit: the guest-only trust model is now **explicitly
documented** in `docs/architecture.md`. The finding's own recommended fix is "Explicitly document
guest-only trust model... before account/cloud features, add an API/edge layer"; no backend exists
and adding one is a product decision (effort `L`) that the audit and patch plan both defer to the
platform roadmap, so this set documents the boundary rather than inventing one. A doc test asserts
the trust model is stated, which is the finding's suggested validation until a server validator
exists.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-U01` — Unassigned ARCH findings (catch-all)
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `4c2cc7caee7437fe9a179c7d5b87c6c35a1e0b88`
- Branch: `remediation/ps-u01-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P1-001` | P1 | open -> partially-fixed | The trust model is now documented and test-enforced. The server trust boundary itself is **not** implemented: the audit classifies it as future platform work (effort `L`, requires a product decision) and `patch_plan.md` explicitly excludes it from the release patch plan. The audit's "recommended fix" step for today (document guest-only trust) is complete; the server step is deferred and tracked. |

## Changes

| File | What changed |
|---|---|
| `docs/architecture.md` (new) | Records the current topology (pure client-side, local-first SPA; no backend/API/DB/queue/auth) and states the **guest-only, client-authoritative trust model**: IndexedDB saves are user-editable, rewards are client-computed, and there is no server validation, rate limiting, or replay rejection. States the server/edge trust boundary required before account/cloud/competitive features, quoting `specs/security-economy-authority.md`. Includes a context diagram and the open deployment-shape question (`output: "standalone"` with no server entry). |
| `docs/architecture.test.ts` (new) | Documentation test (the finding's suggested validation): asserts the doc exists and states the client-authoritative/guest-only/no-backend/user-editable model plus the required server trust boundary and spec reference. |
| `lib/progression/lifecycle.test.ts` | `[...new Set(x)]` -> `Array.from(new Set(x))`: unblocks `npm run typecheck` on the base commit (pre-existing `TS2802`; the identical minimal unblock was already applied in PS-01 and PS-03). Supporting change so the required verification command runs green. |

No application/runtime logic changed. `docs/architecture.md` is a new, dedicated path that does
not conflict with `README.md` (PS-09), `docs/README.md` (PS-02), or the vendored prompt pack.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `4c2cc7c`) | 0 | `remediation/PS-U01/verify.log` — lint clean; typecheck clean; 6 files / 111 tests passed incl. `docs/architecture.test.ts` (2) (`__VERIFY_EXIT=0`) |
| `git archive HEAD \| tar -x -C /tmp/glscan-psu01 && gitleaks detect --no-git --redact --source /tmp/glscan-psu01 -v` | lab: `ci-runner` | 0 | `remediation/PS-U01/verify.log` — `no leaks found`; scanned ~258695 bytes of tracked content at the commit |
| `npm run lint` | local (node v24.19.0) | 0 | `remediation/PS-U01/verify.log` — No ESLint warnings or errors |
| `npm run typecheck` | local (node v24.19.0) | 0 | `remediation/PS-U01/verify.log` — clean |
| `npm run test` | local (node v24.19.0) | 0 | `remediation/PS-U01/verify.log` — 6 files / 111 tests passed |

- Secret scan (gitleaks): **pass** on tracked repository content at the commit, exit 0, no leaks found.
- Scope check: **pass** — one new doc, one new doc test (both for ARCH-P1-001), and the pre-existing
  `TS2802` typecheck unblock identical to PS-01/PS-03. No runtime logic touched.

## Evidence bundle

- `remediation/PS-U01/diff.patch` — SHA-256 `999fbe29ff16c3b9b8ceb861ae67e36ba6109786e57769b751e6972c5c3c4a37`
- `remediation/PS-U01/manifest.json`
- `remediation/PS-U01/verify.log`

## Risk and rollback

- Risk: **low**. Documentation plus a doc test; no runtime behavior changes. The added test reads
  `docs/architecture.md` from `process.cwd()` (the repo root) and will fail only if the doc is
  removed.
- Rollback: `git revert 4c2cc7c`.

## Open questions / reviewer actions

1. **Server trust boundary is deferred, not built.** `ARCH-P1-001` cannot be fully closed by a code
   change in this repo at this commit without a product decision (account/cloud roadmap) and new
   infrastructure. `patch_plan.md` lists it as future platform work. This PR intentionally closes
   only the "document the trust model now" half. Please confirm the finding stays
   `partially-fixed` until a server validator exists.
2. **`output: "standalone"` vs static export.** `next.config.js` sets `output: "standalone"` but no
   server entry exists. The doc records this as an open question; the deployment shape should be
   decided when the server work is scheduled.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

The guest-only trust model is explicitly documented and a doc test enforces that the model and the
required server trust boundary are stated; lint/typecheck/test pass in the lab.
