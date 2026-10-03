# Remediation PR — PS-U02 Unassigned EXEC findings (catch-all): EXEC-P1-001

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes `EXEC-P1-001` ("Unresolved P1 findings preclude an unconditional GO") with the
minimal, correct fix available at this commit: the release gate and its conditions are now
**explicitly documented** in `docs/release-readiness.md`, and a doc test enforces that the
policy states the conditional verdict and the evidence-binding rule.

The finding's own recommended fix is "close or explicitly accept the P1 patch sets PS-01
through PS-04 (at minimum) with validation artifacts; then re-audit for GO." Closing those
P1s is the work of the other patch sets in this run (PS-01 CI, PS-02 LICENSE, PS-03
state/identity, PS-04 save integrity) and requires a maintainer/release decision; it cannot
be completed by a single catch-all code change. What this set can do — and does — is make the
gate policy and the outstanding conditions explicit in the repository so the conditional
verdict is not left implicit in an audit report. The doc records that an unconditional GO
requires zero open P0/P1, each closed with a validation artifact bound to the commit, and a
re-audit.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-U02` — Unassigned EXEC findings (catch-all)
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `2f04de62b80cecf69e4ad52e06c297bd553044c0`
- Branch: `remediation/ps-u02-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `EXEC-P1-001` | P1 | open -> partially-fixed | The release gate policy, the current **GO WITH CONDITIONS** verdict, the conditions (PS-01..PS-04) required before a wider release, and the unconditional-GO evidence rule are now documented and test-enforced. The finding closes only when those P1 patch sets are merged/accepted with commit-bound validation evidence and the gate is re-confirmed; until then it remains `partially-fixed`. |

## Changes

| File | What changed |
|---|---|
| `docs/release-readiness.md` (new) | Release gate policy: current verdict is **GO WITH CONDITIONS** (not an unconditional GO) for the guest-only RC; states the unconditional-GO rule (zero open P0/P1, each with a validation artifact bound to the release commit, plus a re-audit); lists the P1 patch sets PS-01..PS-04 and required evidence; requires accepted/deferred risks to be recorded with an owner and date. Cites the audit run, commit `99abf29`, and `EXEC-P1-001`. |
| `docs/release-readiness.test.ts` (new) | Documentation test (the finding's suggested validation): asserts the doc records the conditional verdict (not an unconditional GO), the zero-open-P0/P1 + commit-bound-evidence rule and re-audit, and the PS-01..PS-04 conditions. |
| `lib/progression/lifecycle.test.ts` | `[...new Set(x)]` -> `Array.from(new Set(x))`: unblocks `npm run typecheck` on the base commit (pre-existing `TS2802`; the identical minimal unblock was already applied in PS-01, PS-03, and PS-U01). Supporting change so the required verification command runs green. |

No application/runtime logic changed. `docs/release-readiness.md` is a new, dedicated path
that does not conflict with `README.md` / `CHANGELOG.md` (PS-09) or `docs/architecture.md`
(PS-U01).

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `2f04de6`) | 0 | `remediation/PS-U02/verify.log` — lint clean; typecheck clean; 6 files / 112 tests passed incl. `docs/release-readiness.test.ts` (3) (`__VERIFY_EXIT=0`) |
| `git archive HEAD \| tar -x -C /tmp/glscan-psu02 && gitleaks detect --no-git --redact --source /tmp/glscan-psu02 -v` | lab: `ci-runner` | 0 | `remediation/PS-U02/verify.log` — `no leaks found`; scanned ~258070 bytes of tracked content at the commit |
| `npm run lint` | local (node v24.19.0) | 0 | `remediation/PS-U02/verify.log` — No ESLint warnings or errors |
| `npm run typecheck` | local (node v24.19.0) | 0 | `remediation/PS-U02/verify.log` — clean |
| `npm run test` | local (node v24.19.0) | 0 | `remediation/PS-U02/verify.log` — 6 files / 112 tests passed |

- Secret scan (gitleaks): **pass** on tracked repository content at the commit, exit 0, no leaks found.
- Scope check: **pass** — one new doc and one new doc test (both for `EXEC-P1-001`), plus the
  pre-existing `TS2802` typecheck unblock identical to PS-01/PS-03/PS-U01. No runtime logic touched.

## Evidence bundle

- `remediation/PS-U02/diff.patch` — SHA-256 `4d55e7090d98983de9d778fda57312914871ba090e07eafbedd451a5f648f928`
- `remediation/PS-U02/manifest.json`
- `remediation/PS-U02/verify.log`

## Risk and rollback

- Risk: **low**. Documentation plus a doc test; no runtime behavior changes. The added test reads
  `docs/release-readiness.md` from `process.cwd()` (the repo root) and will fail only if the doc is
  removed or its policy wording regresses.
- Rollback: `git revert 2f04de6`.

## Open questions / reviewer actions

1. **`EXEC-P1-001` cannot be fully closed by a code change.** It closes when PS-01..PS-04 are
   merged/accepted with commit-bound validation evidence and the gate is re-confirmed by a re-audit.
   Please confirm the finding stays `partially-fixed` until then.
2. **Public OSS vs private product** remains a maintainer decision; until it is made, the release
   gate is deliberately conditional. The gate rule and conditions in the new doc are the
   decision-ready inputs.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

The release gate policy, current conditional verdict, the PS-01..PS-04 conditions, and the
unconditional-GO evidence rule are documented and a doc test enforces them; lint/typecheck/test
pass in the lab.
