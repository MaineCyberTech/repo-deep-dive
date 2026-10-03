# Remediation PR — PS-08 Supply chain & inventory fidelity

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Puts the dependency tree under active management and adds runnable supply-chain
tooling. Adds `.github/dependabot.yml` (npm + GitHub Actions, weekly, grouped
minor/patch updates) and an `engines.node >= 20` field so installs are
reproducible and aged/EOL lines are surfaced as reviewable PRs
(SUPPLY-P2-001). Adds `npm run audit` (`npm audit --omit=dev`) and
`npm run sbom` (`npm sbom --sbom-format cyclonedx --omit=dev`) so
vulnerability scanning and a CycloneDX SBOM can run in CI (SUPPLY-P2-002,
partial — wiring needs PS-01's CI, and the license allowlist is a legal
decision). INV-P2-002 is the audit run's own `inventory.json`, corrected
out-of-band. API-P2-001 is deferred: there is still no server/API in the tree
to version. No dependency versions were bumped — the live advisories require a
breaking Next.js major and are handed to Dependabot/humans, not auto-fixed.

- Audit run: `20261003-0018-master-99abf29`
- Patch set: `PS-08` — Supply chain & inventory fidelity
- Repo / base: `MaineCyberTech/buddy` @ `99abf294dae0d9de8770dfde257bdef5fae9ae1b` (master)
- Commit: `f31ebd44f3e616d74013e3702cd4d50bfe43835b`
- Branch: `remediation/ps-08-20261003-0018-master-99abf29`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `SUPPLY-P2-001` | P2 | open -> partially-fixed | Dependabot (npm + GitHub Actions) + `engines.node >= 20` added. No version was force-bumped; the remaining aged/EOL lines (Next 14, ESLint 8) are now managed by Dependabot PRs. `npm audit` is non-clean and is triaged below — a Next.js major upgrade is a product/compat decision, so this is not `verified-fixed`. |
| `SUPPLY-P2-002` | P2 | open -> partially-fixed | `npm run audit` and `npm run sbom` (CycloneDX) added and verified. Wiring them into a workflow depends on PS-01 (CI), which is not merged; the license allowlist needs a legal/product decision. Both are recorded as open questions rather than guessed. |
| `INV-P2-002` | P2 | open -> partially-fixed | The run's `inventory.json` was hand-corrected: `entry_points` (`app/layout.tsx`, `app/page.tsx`), `routes` (`/` from `app/page.tsx`), `tests.files` (7 -> 5) and `tests.dirs` (populated). This is an audit-run artifact, not a buddy repo file, so it is not in the diff. The tool's Next.js App Router detection gap is an open question. |
| `API-P2-001` | P2 | open -> deferred | Still no `app/api/`, route handler or server action to bind a versioned contract to. Recorded as an open question; owned by future cloud work. |

## Changes

| File | What changed |
|---|---|
| `.github/dependabot.yml` (new) | Weekly Dependabot updates for npm and GitHub Actions; grouped production / development minor+patch updates, 5-PR limit, `dependencies` + `audit-remediation` labels, `chore(deps)`/`chore(ci)` commit prefixes. |
| `package.json` | Added `"engines": { "node": ">=20" }`; added `"audit": "npm audit --omit=dev"` and `"sbom": "npm sbom --sbom-format cyclonedx --omit=dev"`. |
| `package-lock.json` | Root `packages[""]` entry gains the matching `engines` field (`npm install --package-lock-only`); no resolution changes. |
| `lib/progression/lifecycle.test.ts` | One-line `[...new Set]` -> `Array.from(new Set)` unblock for the pre-existing `TS2802` typecheck error (same unblock used by PS-01/PS-03/PS-06/PS-07). |

Run artifact (not in the PR diff): `20261003-0018-master-99abf29/inventory.json` corrected for INV-P2-002.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `npm ci && npm run lint && npm run typecheck && npm run test` | lab: `ci-runner` (`172.23.128.51:/srv/work/buddy`, wiped + re-synced clean at `f31ebd4`) | 0 | `remediation/PS-08/verify.log` §1 — lint clean; typecheck clean; 5 files / 109 tests passed |
| `npm run --silent sbom > /tmp/ps08-sbom.json` | lab: `ci-runner` | 0 | `verify.log` §2 — valid CycloneDX 1.5, 22581 bytes, 17 npm components |
| `npm run --silent audit` (`npm audit --omit=dev`) | lab: `ci-runner` | 1 | `verify.log` §3 — 3 production vulnerabilities (2 high, 1 critical); triaged, not hidden |
| `git archive HEAD \| tar -x -C /tmp/glscan-ps08 && gitleaks detect --no-git --redact --source /tmp/glscan-ps08` | lab: `ci-runner` | 0 | `verify.log` §4 — `no leaks found` (~254 KB tracked content at `f31ebd4`) |
| `npm install --package-lock-only` (engines sync) | local (node v24.19.0 / npm 11.17.0) | 0 | `verify.log` §5 — 3-line lockfile diff, no resolution changes |

- Secret scan (gitleaks): **pass** — `no leaks found` at commit `f31ebd4`.
- Scope check: **pass with one documented deviation.** Repo diff touches exactly the
  patch-set files (`package.json`, `package-lock.json`, `.github/dependabot.yml`) plus
  `lib/progression/lifecycle.test.ts`, the pre-existing `TS2802` one-line test unblock
  already used by PS-01/PS-03/PS-06/PS-07 (without it `npm run typecheck` fails at master).

## Evidence bundle

- `remediation/PS-08/diff.patch` — SHA-256 `338586C16FD6EA5907BF0E9621546EACCF206BABC199A29D23AEE3C5D87D575E`
- `remediation/PS-08/verify.log` — raw transcripts in `raw-main.log`, `raw-audit.log`, `raw-ps08verify.log`, `raw-gitleaks.log`
- `remediation/PS-08/manifest.json`

## Risk and rollback

- Risk: **low**. Config/docs/scripts only; no runtime code, no dependency version
  changes, no schema or storage changes. The only behavioural change is the extra
  npm scripts and the Dependabot config (which yields reviewable PRs, not auto-merges).
- Rollback: `git revert f31ebd4` (single commit).

## Open questions / reviewer actions

1. **Non-clean production audit.** `npm audit --omit=dev` reports 3 production
   vulnerabilities: `next` (critical, 20 advisories) and its bundled `postcss` (high)
   are only fixed by the breaking `next@16.3.8`; `nanoid` (high) has a non-breaking
   fix. A Next.js 14 -> 16 major upgrade is a product/compat decision owned outside
   this patch set. Note GitHub already reports 33 vulnerabilities on the default
   branch; Dependabot alerts are active at the repo level.
2. **PS-01 dependency not merged.** The plan lists PS-01 (CI + Dependabot) as a
   dependency. This branch is based on `origin/master`, which has no `.github/`
   directory, so it adds `.github/dependabot.yml` itself; expect a trivial merge
   conflict with PR #3, resolved by keeping either copy. Wiring `npm run audit` /
   `npm run sbom` into a workflow should happen in PS-01's `ci.yml` after both land.
3. **License allowlist (SUPPLY-P2-002).** No license policy was added because the
   acceptable-license set is a legal/product decision. Confirm the allowlist (e.g.
   MIT/ISC/Apache-2.0/BSD) and whether it should be a script or a CI step.
4. **API-P2-001 remains deferred.** No server/API exists to version.
5. **Inventory generator gap (INV-P2-002).** `tools/repo_inventory.py` does not detect
   Next.js App Router entry points/routes and over-matches `test`/`spec` substrings
   (`data/species.ts`, `vitest.config.ts`). The run's `inventory.json` was hand-corrected;
   a future tool fix should be tracked by the audit-tooling owner.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests), or the deviation above is accepted
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (from `patch_plan.md`)

- `npm audit` clean/triaged; SBOM artifact; inventory matches tree.
  Status: `npm audit` **triaged** (3 production advisories recorded, non-clean);
  SBOM **generated** (CycloneDX, 17 components); inventory **corrected** for the run.
