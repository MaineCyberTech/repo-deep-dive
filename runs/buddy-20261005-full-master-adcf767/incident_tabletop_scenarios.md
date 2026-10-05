# Incident Tabletop Scenarios

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Related findings: `IR-P3-001`, `BP-P1-001`, `BP-P1-002`, `CI-P1-001`, `SC-P2-002`

No incident-response runbook or tabletop record existed in the tree prior to this run. Because
the app is guest-only with no backend, the realistic incident classes are maintainer/release
and supply-chain incidents, not runtime data breaches.

## Scenario 1 — Compromised maintainer token

- **Trigger:** A write token for a maintainer is stolen.
- **Exposure:** With `master` unprotected (`BP-P1-001`), the token can push directly and bypass
  review and CI. With no `release` environment protection (`BP-P1-002`), a `v*` tag can publish
  a release without reviewer approval.
- **Response:** Rotate the token; audit recent pushes/tags; withdraw any bad release and tag
  (`docs/release-process.md:63-67`); restore `master` from the last reviewed commit.
- **Prevention:** Enable the master ruleset and the `release` environment (see
  `branch_protection_recommendation.md`).

## Scenario 2 — Malicious dependency / action update

- **Trigger:** An upstream package or a moving Action tag introduces malicious code.
- **Exposure:** Actions are SHA-pinned (good). Dependabot security updates and secret scanning
  are disabled (`SC-P2-002`), and the PR dependency-review gate is skipped (`CI-P2-001`).
- **Response:** Freeze merges, run `npm ci` on a clean host, diff the lockfile, `npm audit`,
  and rebuild from a known-good lockfile.
- **Prevention:** Enable Dependabot security updates and the dependency-review job.

## Scenario 3 — Bad release shipped

- **Trigger:** A green-looking tag publishes a broken build.
- **Response:** Delete the GitHub Release and tag, cut a patched tag from the corrected commit
  (`docs/release-process.md:63-67`); because artifacts carry the build id, identify affected
  installs.
- **Prevention:** Fix the currently-red security job (`CI-P1-001`) so a green CI is meaningful.

## Exercise log

_Not yet run._ Record date, participants, and outcomes here once performed.
