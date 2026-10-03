# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all supply-chain remediation for the unassigned `SUPPLY` findings from the
2026-10-03 audit run. It makes the **license allow-list merge-gating**, wires the
**production vulnerability and registry-provenance checks into PR CI**, and
documents the **install-script (`allowScripts`) policy** and the
**Dependabot security-update grouping**. All changes are additive: the workflow
is a **new file** (`.github/workflows/supply-chain.yml`) and the SBOM work from
`P1-3`/`SUPPLY-P1-001` in `ci-foundation.yml` is untouched.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U12` — Unassigned SUPPLY findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SUPPLY-P2-001` | P2 | open -> **partially-fixed** | The **license allow-list** now runs as a **blocking** PR gate (`node scripts/license-assurance.mjs`); the negative probe below proves a planted disallowed license fails it. The **production audit** (`npm audit --omit=dev --audit-level=high`) now runs per-PR but is **advisory** because the base already carries one high advisory in the transitive runtime dep `@grpc/grpc-js` (blocking would red every PR). OSV is not added; `npm audit` is the pinned equivalent the daily host lane uses. |
| `SUPPLY-P2-002` | P2 | open -> **partially-fixed** | `docs/SUPPLY_CHAIN.md` documents every `allowScripts` entry, why its install script is required, the provenance-first rule, and the per-release review cadence. `npm audit signatures` is wired into the PR workflow but is **advisory** because the registry currently returns no public key for `@playwright/test@1.63.0`'s attestation (`EMISSINGSIGNATUREKEY`). |
| `SUPPLY-P3-001` | P3 | open -> **partially-fixed** | `.github/dependabot.yml` now defines `security` groups (`applies-to: security-updates`) for **both** the npm and github-actions ecosystems, so security updates no longer share a queue with routine version updates. `yq` validates the structure; the "prioritized PR" behaviour is only observable at the next security advisory. |

## Changes

| File | What changed |
|---|---|
| `.github/workflows/supply-chain.yml` (new) | New `supply-chain` workflow triggered on PRs/pushes touching `package.json`, `package-lock.json`, or the license script. Steps: `npm ci`; **license allow-list (blocking)**; production `npm audit` (advisory, documented); `npm audit signatures` (advisory, documented). Actions pinned to the same SHAs as the `CI-P2-002` work. |
| `docs/SUPPLY_CHAIN.md` (new) | Merge-gating checks table; install-script allowlist with per-package rationale; provenance and review rules; manual verification commands. |
| `.github/dependabot.yml` | `security` group (`applies-to: security-updates`, `patterns: ["*"]`) added to the npm and github-actions ecosystems. |

Coordination: `P1-3` (`SUPPLY-P1-001`, draft #9) and `PS-U03`/`CI-P2-002` both edit
`.github/workflows/ci-foundation.yml`. This PR deliberately does **not** touch
that file — every change is in a new workflow, a new doc, or `dependabot.yml` —
so it cannot conflict with the SBOM step or the action pins.

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab
(`/srv/work/snowride-ps-u12`, `core.autocrlf` unset, HEAD `b1c0f21`), Node
v20.20.2 / npm 10.8.2 / gitleaks 8.30.1 / actionlint 1.7.12 / yq 4.54.1. Raw
output with exit codes is in `remediation/PS-U12/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `actionlint .github/workflows/supply-chain.yml` | ci-runner | 0 | no findings |
| `yq parse .github/dependabot.yml` | ci-runner | 0 | groups: npm = production/development/security; github-actions = security |
| `npm ci` | ci-runner | 0 | 628 packages installed |
| `node scripts/license-assurance.mjs` | ci-runner | 0 | 173 production deps checked, 173 allowed, 0 violations |
| license gate **negative probe** (planted `GPL-3.0-only` prod dep) | ci-runner | 1 (blocked) | `violations [('ps-u12-planted','GPL-3.0-only')]`; tree restored afterwards |
| `npm audit --omit=dev --audit-level=high` | ci-runner | 1 (advisory) | 1 high: `@grpc/grpc-js` GHSA-m9gg-hp2v-232j / GHSA-f596-whhp-79r4 |
| `npm audit signatures` | ci-runner | 1 (advisory) | `EMISSINGSIGNATUREKEY @playwright/test@1.63.0` |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` (profile gate) | ci-runner | 0 | 131 test files, 873 tests passed |
| `git status --short` after the gates | ci-runner | 0 | clean |
| `gitleaks detect --no-git --redact` on each changed file | ci-runner | 0 | 3/3 files clean |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing `generic-api-key` fixtures under `evidence/**`; **none** in this diff |

- Secret scan (gitleaks): **pass** for this diff — all three changed files clean;
  the 19 full-tree hits are the audited fixtures also recorded by
  PS-U03/U04/U10/U11.
- Scope check (files within patch set): **pass** — `PS-U12` declared no file
  list; the diff is limited to the SUPPLY fixes (one new workflow, one new doc,
  the Dependabot config).

## Evidence bundle

- `remediation/PS-U12/diff.patch` — SHA-256 `fe8e8f0f7bc30a0353fde13ae137a18c8abb94a0728ed4e8c3400e1f2c1848e3`
- `remediation/PS-U12/verify.log` — SHA-256 `c45ebb5a2e14919760f71cd59a15d39d359bd22226ad70914f9d6bea506b0de0`
- `remediation/PS-U12/gitleaks.log` — SHA-256 `d8f8ab77f3f96e75564d69bee8595a4b8bdb4f98a0b1a3362bffdb2920c5bdfb`
- `remediation/PS-U12/manifest.json`

## Risk and rollback

- Risk: **low**. No application code, dependency, or lockfile change. The new
  workflow only runs on dependency-graph PRs; its license step is the only
  blocking gate and was validated against the current lockfile (pass) and a
  planted violation (block). No secrets are added.
- Rollback: `git revert b1c0f21781607084626789ba95d587444de83b64`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Rollback is practical

## Definition of done (for this set)

- A disallowed **license** in a production dependency fails PR CI (`SUPPLY-P2-001`).
- The install-script allowlist has a documented rationale and provenance rule (`SUPPLY-P2-002`).
- Dependabot security updates are grouped/prioritized (`SUPPLY-P3-001`).

## Open questions

1. **`SUPPLY-P2-001` — promote the production audit to blocking.** The base lockfile
   carries one high advisory in `@grpc/grpc-js` (GHSA-m9gg-hp2v-232j /
   GHSA-f596-whhp-79r4), so the audit step is `continue-on-error: true`. Once
   that dependency is bumped (a lockfile change outside this patch set), remove
   `continue-on-error` to make high/critical production advisories merge-gating.
   Should we also add an OSV scan step, or is `npm audit` sufficient?
2. **`SUPPLY-P2-002` — promote signature verification to blocking.** `npm audit
   signatures` reports `EMISSINGSIGNATUREKEY` for `@playwright/test@1.63.0`
   (attestation present, registry public key not found). This may be an
   npm-version or registry-key issue; it should be re-checked under Node 24 /
   npm 11 (the CI runtime) and then made blocking, or the package's provenance
   handled explicitly.
3. **`SUPPLY-P3-001` — security-update grouping requires repo settings.**
   Grouping with `applies-to: security-updates` only takes effect when
   Dependabot security updates are enabled for the repository. Confirm that
   setting; the recommended auto-merge for low-risk security PRs is a separate
   policy decision and is not included here.
