# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Adds the missing canonical, in-repository **release-gate record**. Until now the
release gate's conditional status lived only in the audit run and in the
self-asserted launch-attestation values; this PR makes the gate rubric, the
current `GO WITH CONDITIONS` verdict and the blocking conditions an explicit,
version-controlled artifact, so a release cannot be represented as *attested*
while those conditions are open.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U05` — Unassigned EXEC findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `EXEC-P2-001` | P2 | open -> partially-fixed | The executive/release-gate gap is closed by recording the rubric, the conditional verdict and the blocking conditions in-repo. The finding itself is a rollup that becomes `verified-fixed` only when its dependency P1 conditions close and a fresh attestation is captured (sibling patch sets P1-1..P1-4); that is recorded as an open question below. |

## Changes

| File | What changed |
|---|---|
| `docs/RELEASE_GATE.md` | New: release-gate rubric, the current status (`GO WITH CONDITIONS`; not an attested release), the four blocking conditions for an attested release mapped to findings (`SEC-P1-001`, `DATA-P1-001`, `FINAL-P1-001`, `CI-P1-001`, `SUPPLY-P1-001`, `OBS-P1-001`), strongly-recommended items, and the procedure for closing a condition with captured evidence. |
| `README.md` | Linked the new page from the documentation map. |

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab (`/srv/work/snowride-ps-u05`) at commit `3e9e56c`. Docs-only change, so the snowride profile gate plus a relative-link check and gitleaks were run.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| relative-link existence check for `docs/RELEASE_GATE.md`, `README.md` | ci-runner | 0 | `linkcheck_broken=0` (`remediation/PS-U05/verify.log`) |
| `npm ci` | ci-runner | 0 | 628 packages installed (`verify.log`) |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` (`verify.log`) |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed (`verify.log`) |
| `git status --short` after gates | ci-runner | 0 | clean (generated files not committed) |
| `gitleaks detect --no-git --redact --source README.md` | ci-runner | 0 | no leaks |
| `gitleaks detect --no-git --redact --source docs/RELEASE_GATE.md` | ci-runner | 0 | no leaks (`remediation/PS-U05/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing audited fixture hits under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff (`gitleaks.log`) |

- Secret scan (gitleaks): **pass** — both changed files clean; the 19 full-tree hits are the same audited, pre-existing fixtures recorded by the sibling PS-U03/PS-U04 runs.
- Scope check (files within patch set): **pass** — `PS-U05` declared no file list; the diff is limited to the new release-gate page and its README link.

## Evidence bundle

- `remediation/PS-U05/diff.patch` — SHA-256 `a6cb18f0bdeb797df80275b8c3477c64d4660a393ebdd0b65aeb1581ca6b1c40`
- `remediation/PS-U05/verify.log` — SHA-256 `66d0648248c4070ba1c092b44e639a7e1639208c62feda014d7d2852e47cc1cb`
- `remediation/PS-U05/gitleaks.log` — SHA-256 `d7acc89f900c08c1ad1f192a04f6660d9d9acd957113df27ad49b1ff8d791d7c`
- `remediation/PS-U05/manifest.json`

## Risk and rollback

- Risk: **very low**. Documentation only; no runtime code, CI workflow, dependency or lockfile change. The new page states the current conditional gate status and does not grant or change any runtime gate.
- Rollback: `git revert 3e9e56c273160ef9a3d63259d7052e57635e8caf`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **Final closure of `EXEC-P2-001` is dependency-gated.** The finding's own recommended fix is to close the six P1 items and capture a fresh attestation at the released commit/migration head. This catch-all PR makes the gate explicit but cannot close the P1 conditions; those live in the sibling patch sets (P1-1 release identity, P1-2 branch protection, P1-3 SBOM, P1-4 alerting). `EXEC-P2-001` should move to `verified-fixed` only after those merge and a verification run at the new attestation confirms all six P1s.
2. **Attestation values are still stale in `main`.** This PR does not touch `infra/compose/docker-compose.yml`; the stale `LAUNCH_ATTESTED_COMMIT`/`LAUNCH_MIGRATION_HEAD` and the committed approval string are handled by P1-1. The new page points at that condition rather than duplicating the fix.

## Definition of done (for this set)

- `docs/RELEASE_GATE.md` records the rubric, the current `GO WITH CONDITIONS` status, and the blocking conditions for an attested release with finding mappings.
- The README documentation map links the page.
- The snowride profile gate remains green (`npm ci`, `npm run lint`, `npm test`) and the changed docs scan clean under gitleaks.
