# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PS-U02` (catch-all) — add the missing in-repo **release-readiness gate** for the
repo-deep-dive audit run, covering the three consolidated FINAL findings:

- `FINAL-P1-001` (P1) — P0 data-loss path / incomplete verification blocking a clean release
- `FINAL-P2-001` (P2) — governance + observability gaps (prod not provisioned, alerts unrouted, backups unverified, single-host SPOF)
- `FINAL-P2-002` (P2) — residual fail-open authorization/secret defaults

These are consolidation findings in `22_final_risk_register_roadmap.md`. Their underlying
domain findings are owned by the per-domain patch sets (`DATA-P0-001`/`TEST-P2-001` →
`PATCH-001`; `SEC-P1-001` → `PATCH-002`; `SEC-P2-002` → `PATCH-003`; `CI-P1-001` → `PATCH-004`;
`API-P2-001` → `PATCH-005`; etc.). What was missing was a single, durable, in-repo artifact that
turns the run's NO-GO release gate into explicit **exit criteria, fail-closed decisions and
operator actions owned by a person**. This PR adds exactly that, without duplicating or
conflicting with any code patch set.

> **Scope note.** PS-U02 was declared with **no file list**, so each FINAL finding's evidence was
> located in the run (`22_final_risk_register_roadmap.md`, `23_executive_summary_release_gate.md`,
> `findings.json`) and its referenced domain reports. The findings are release-gate /
> release-readiness gaps; the minimal, non-conflicting fix is the release-gate document plus its
> discoverability links. No application code is touched.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d`
- Patch set: `PS-U02` — Unassigned FINAL findings (catch-all)
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)
- Head commit: `c11f40ad`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FINAL-P1-001` | P1 | open -> partially-fixed | `docs/RELEASE_GATE.md` records the `DATA-P0-001` + `TEST-P2-001` exit condition (folder-aware cleanup + regression test at the deployed commit) and maps it to the owning patch set. The code fix itself is `PATCH-001`; this set supplies the gate requirement and no longer leaves the "clean release" claim unverifiable. |
| `FINAL-P2-001` | P2 | open -> partially-fixed | `docs/RELEASE_GATE.md` adds the pre-go-live operator checklist (prod secrets/vars + required reviewers, dry `main` deploy, alert routing + synthetic alert, `db-restore-test` with row assertions, SPOF/backup plan) with owners and required evidence. These are GitHub/operator actions that cannot live in a PR; the gate is now explicit and traceable. |
| `FINAL-P2-002` | P2 | open -> partially-fixed | `docs/RELEASE_GATE.md` adds a fail-closed decisions register for PII encryption, CAPTCHA/Turnstile, search scoping, API keys and demo data: default today, required decision, enforcement point, owner. Each is either fail-closed by its owning patch set or explicitly owner-accepted. |

## Changes

| File | What changed |
|---|---|
| `docs/RELEASE_GATE.md` (new) | Consolidated release gate: FINAL→underlying finding map, blocking exit criteria, fail-closed decisions register (`FINAL-P2-002`), pre-go-live operator checklist (`FINAL-P2-001`), status vocabulary and references. |
| `docs/INDEX.md` | Register the new gate in the Deployment & Operations index. |
| `docs/RELEASING.md` | Link the gate from "Before promoting to prod". |

## Verification Performed

Run on the Proxmox `ci-runner` (LXC 200) via `lab-sync.ps1` + `lab-run.ps1`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `corepack pnpm --filter api typecheck` | lab `ci-runner`, tsc 5.7 | 0 | `remediation/PS-U02/verify.log` |
| `corepack pnpm --filter api test` | lab `ci-runner`, jest 29 | 0 | `remediation/PS-U02/verify.log` — 122 suites passed, 1406 tests passed |
| `node scripts/check-docs-links.mjs` | lab `ci-runner`, node 20.20.2 | 0 | `docs links OK` |
| `node scripts/check-docs-counts.mjs` | lab `ci-runner` | 0 | `docs counts OK` |
| `gitleaks detect --source=/tmp/psu02scan --no-git --redact -v` | lab `ci-runner`, gitleaks | 0 | `no leaks found` (scanned the 3 changed files) |

- Secret scan (gitleaks): **pass** — `no leaks found`, exit 0.
- Scope check: **pass** — only the 3 docs files above were touched.
- **Honesty note.** The first lab run reported 5 failures in `apps/api/src/__tests__/env.test.ts`
  (`assertProductionSecrets is not a function`). That file is **not tracked on the base branch**
  (`git cat-file -e HEAD:apps/api/src/__tests__/env.test.ts` → does not exist); it was a stale
  untracked file left in `/srv/work/mainecybertech` by an earlier branch sync (the lab sync uses
  `tar` extract, which does not delete files removed from the source tree). It was removed and the
  suite was re-run clean (122/122). The raw failing run and the clean re-run are both worth noting
  for reviewers; the fix is infra/test-isolation, not a code change in this set.

## Evidence bundle

- `remediation/PS-U02/verify.log` — raw lab output incl. exit codes
- `remediation/PS-U02/diff.patch` — SHA-256 `686a267cb1be7a0f153a968c5bfc96d99250044de51c450e6bfbb6ad381a18fd`
- `remediation/PS-U02/manifest.json`

## Risk and rollback

- Risk: **very low** — documentation only; no runtime, schema, or workflow change.
- Rollback: `git revert c11f40ad` (or drop the branch).

## Review checklist

- [x] Diff touches only files the findings require (+ index/links)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran; results pasted, not asserted
- [x] No secrets added; gitleaks clean
- [x] Rollback is practical

## Open questions / decisions needed

1. **Owner sign-off for the fail-closed register** — the decisions register records the *required*
   decisions; a named owner must still accept or implement each.
2. **Where the gate lives long-term** — this is a point-in-time gate for the `20261003-0018` run.
   If the team wants it maintained, it should become a living checklist (or be folded into
   `RELEASING.md`) with an owner. Reviewers should decide.
