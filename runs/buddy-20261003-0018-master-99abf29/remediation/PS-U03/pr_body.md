# Remediation PR — PS-U03 Unassigned FINAL findings (catch-all): FINAL-P1-001

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes `FINAL-P1-001` ("No release/versioning process binds artifacts to a commit") by adding
the release process the finding recommends: a tag-driven release workflow that builds and tests
at the tagged commit, records the **build id** (the full commit SHA), generates an **SBOM** and a
**changelog**, packages the build, attests its **provenance**, and publishes it as a GitHub
Release. A `docs/release-process.md` records the process and how to verify an artifact's commit,
and a doc test enforces that the process and workflow are present.

The audit found releases were manual tags with no automated build/test, no SBOM, no changelog,
and no runtime build id, so a shipped artifact could not be traced to its commit. The new
workflow is triggered only by `v*` tags, so the tag identifies the exact immutable commit under
release and every artifact (notes, SBOM, changelog, tarball) carries the same build id.

This set is additive and does **not** touch `docs/release-readiness.md` (PS-U02) or
`.github/workflows/ci.yml` (PS-01); no merge conflict with those branches.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-U03` — Unassigned FINAL findings (catch-all)
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `50c65a028dcc35a168524e3f69859af999bafef4`
- Branch: `remediation/ps-u03-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FINAL-P1-001` | P1 | open -> partially-fixed | A tag-driven release workflow (build + test + SBOM + changelog + build id + provenance attestation) and its documented process now bind release artifacts to the commit the tag points at. The finding closes when a real tagged release produces the bound artifact; until then it remains `partially-fixed`. |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/release.yml` (new) | Tag-driven (`on: push: tags: ["v*"]`) release workflow: `npm ci`, lint, typecheck, test, build; records the build id (`git rev-parse HEAD`) and tag; generates a CycloneDX SBOM (`npm sbom`) and `CHANGELOG-RELEASE.md`; packages `buddy-<tag>.tar.gz`; attests build provenance (`actions/attest-build-provenance`); publishes the GitHub Release with artifact + SBOM via `softprops/action-gh-release`. |
| `docs/release-process.md` (new) | The release/versioning process: how a release is cut from a `v*` tag, what the workflow produces, the build-id-to-commit binding, how to verify an artifact's commit, and rollback. Cites audit finding `FINAL-P1-001`. |
| `docs/release-process.test.ts` (new) | Documentation/workflow test (the finding's suggested validation): asserts the doc records the tag-driven process, build id = commit SHA, SBOM, changelog, and provenance step, and that the release workflow exists with the tag trigger and key steps. |
| `lib/progression/lifecycle.test.ts` | `[...new Set(x)]` -> `Array.from(new Set(x))`: unblocks `npm run typecheck` on the base commit (pre-existing `TS2802`; the identical minimal unblock was applied in PS-01, PS-03, PS-U01, and PS-U02). Supporting change so the required verification command runs green. |

No application/runtime logic changed. The workflow is not executed by this PR; it is validated
syntactically with `actionlint` in the lab (exit 0).

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `50c65a0`) | 0 | `remediation/PS-U03/verify.log` — lint clean; typecheck clean; 6 files / 112 tests passed incl. `docs/release-process.test.ts` (3) (`__VERIFY_EXIT=0`) |
| `actionlint .github/workflows/release.yml` | lab: `ci-runner` | 0 | `remediation/PS-U03/verify.log` — `__ACTIONLINT_EXIT=0` |
| `git archive HEAD \| tar -x -C /tmp/glscan-psu03 && gitleaks detect --no-git --redact --source /tmp/glscan-psu03 -v` | lab: `ci-runner` | 0 | `remediation/PS-U03/verify.log` — `no leaks found`; scanned ~261514 bytes of tracked content at the commit |
| `npm run lint` | local (node v24.19.0) | 0 | `remediation/PS-U03/verify.log` — No ESLint warnings or errors |
| `npm run typecheck` | local (node v24.19.0) | 0 | `remediation/PS-U03/verify.log` — clean |
| `npm run test` | local (node v24.19.0) | 0 | `remediation/PS-U03/verify.log` — 6 files / 112 tests passed |

- Secret scan (gitleaks): **pass** on tracked repository content at the commit, exit 0, no leaks found.
- Scope check: **pass** — one new workflow, one new doc, one new doc test (all for `FINAL-P1-001`),
  plus the pre-existing `TS2802` typecheck unblock identical to the sibling patch sets. No runtime
  logic touched; no declared-file list exists for this catch-all set.

## Evidence bundle

- `remediation/PS-U03/diff.patch` — SHA-256 `4ed9aa8ed45dcdb66c8587ec5d0a126892eafd696475c5adc35494552548e296`
- `remediation/PS-U03/manifest.json`
- `remediation/PS-U03/verify.log`

## Risk and rollback

- Risk: **low**. A new workflow and documentation plus a doc test; no runtime behavior changes. The
  release workflow runs only on `v*` tag pushes, so it is inert until a tag is cut. The doc test
  reads `docs/release-process.md` and `.github/workflows/release.yml` from the repo root and fails
  only if they are removed or their wording/keys regress.
- Rollback: `git revert 50c65a0`.

## Open questions / reviewer actions

1. **`action-gh-release` / `attest-build-provenance` versions** are pinned to major tags (`v2` /
   `v1`); the repo does not yet have a pinned-SHA policy (tracked separately by the supply-chain
   patch set). Confirm the chosen actions are acceptable.
2. **`npm sbom`** requires npm >= 9.8; the workflow pins Node 20 (npm 10), so this is satisfied.
3. **`FINAL-P1-001` cannot be fully closed by an untagged PR.** It closes when a real `v*` tag is
   pushed and the workflow publishes the bound artifact. Please confirm the finding stays
   `partially-fixed` until then.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

A tag-driven release workflow that binds artifacts (build id, SBOM, changelog, provenance) to the
tagged commit, plus a documented process and a doc test enforcing it; lint/typecheck/test and
actionlint pass in the lab; gitleaks clean.
