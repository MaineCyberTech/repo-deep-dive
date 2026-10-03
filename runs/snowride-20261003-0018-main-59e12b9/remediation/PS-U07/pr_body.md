# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Adds the missing **version-controlled record of operational reliability
controls** and a per-release drill procedure, and defines the **RPO/RTO** the
audit found undocumented. Until now the recovery targets, control cadence and
the expectation to exercise recovery/alerting per release lived only in the
audit run and on the host; this PR makes them reviewable in-repo and makes a
per-release drill an explicit, evidence-backed gate.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U07` — Unassigned FINAL findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `FINAL-P2-001` | P2 | open -> partially-fixed | RPO/RTO are now defined, the reliability controls and their cadence are inventoried against in-repo sources, and per-release backup/restore + alert-path + rollback drills with required evidence are documented. The finding's remaining halves are runtime/operator actions: a committed crontab/timer file (`OBS-P1-001`, dependency) and **captured drill evidence at the released commit**. Neither can be produced by a documentation PR; recorded as open questions below. |

## Changes

| File | What changed |
|---|---|
| `docs/runbooks/RELIABILITY_DRILLS.md` | New: RPO (`≤24h`) / RTO (`≤4h`) targets with their basis, a table of the versioned reliability controls mapped to in-repo sources, the three per-release drills (backup/restore, alert-path, rollback) and the append-only evidence each must capture. |
| `docs/runbooks/README.md` | Linked the new runbook from the runbook index. |
| `docs/runbooks/BACKUP_RESTORE.md` | Replaced "There is no documented RPO/RTO yet" with a pointer to the now-defined targets (retaining the ≤24h conservative default until a drill ratifies them). |

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab (`/srv/work/snowride-ps-u07`)
at commit `6fa5596`. Docs-only change, so the snowride profile gate plus a
relative-link check and gitleaks were run.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| relative-link existence check for the 3 changed docs | ci-runner | 0 | `linkcheck_broken=0` (`remediation/PS-U07/verify.log`) |
| `npm ci` | ci-runner | 0 | 628 packages installed (`verify.log`) |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` (`verify.log`) |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed (`verify.log`) |
| `git status --short` after gates | ci-runner | 0 | clean (generated files not committed) |
| `gitleaks detect --no-git --redact --source <changed file>` ×3 | ci-runner | 0 | no leaks (`remediation/PS-U07/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing audited fixture hits under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff (`gitleaks.log`) |

- Secret scan (gitleaks): **pass** — all three changed files clean; the 19
  full-tree hits are the same audited, pre-existing fixtures recorded by the
  sibling PS-U03/PS-U04/PS-U05 runs.
- Scope check (files within patch set): **pass** — `PS-U07` declared no file
  list; the diff is limited to the new reliability-drills runbook and its two
  runbook-doc references.

## Evidence bundle

- `remediation/PS-U07/diff.patch` — SHA-256 `85b84026a92ef1c0c6b256b62281396c15c902f8ead0ab6defab71002f38d376`
- `remediation/PS-U07/verify.log` — SHA-256 `3873ecb82648f0adb4e7b3d44ae26c1796dc3ec286c9c46bbac3ee3fe5826d57`
- `remediation/PS-U07/gitleaks.log` — SHA-256 `9b172dc3992775bbb9c61c61c726e6e118a2e23f46fe2d82840db0c14ce5f9b7`
- `remediation/PS-U07/manifest.json`

## Risk and rollback

- Risk: **very low**. Documentation only; no runtime code, CI workflow,
  dependency or lockfile change. The new page defines targets and records
  existing machinery; it changes no runtime gate or schedule.
- Rollback: `git revert 6fa559685cd1e9a20508f3cce4f3b345a24a0088`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Open questions

1. **Final closure of `FINAL-P2-001` is evidence-gated.** Its own recommendation
   is to *execute* backup/restore + alert drills per release and capture
   evidence. This catch-all PR documents the procedure and targets but cannot
   run a real production restore/drill from the audit role. `FINAL-P2-001`
   should move to `verified-fixed` only after a drill transcript (restore
   counts + observed RPO/RTO; `exit 90` alert delivery; rollback output) is
   captured under `evidence/` at the released commit.
2. **Committed schedule remains `OBS-P1-001`.** The crontab/timer and ntfy
   config still live only on the host (documented as a known gap in
   `INCIDENT.md`, patch set P1-4). This PR inventories the schedule and
   thresholds in-repo but deliberately does not duplicate or pre-empt the P1
   fix.
3. **RPO/RTO targets need owner ratification.** The `≤24h`/`≤4h` targets follow
   the existing daily dump cadence and restore procedure; a real drill should
   confirm or revise them.
4. **Non-conflict with PS-U05.** `docs/RELEASE_GATE.md` (patch set PS-U05) is
   not on this base, so this PR does not edit it. It is additive by design; if
   both merge, the release-gate page's `FINAL-P2-001` line can link here.

## Definition of done (for this set)

- RPO/RTO defined and committed (`docs/runbooks/RELIABILITY_DRILLS.md`).
- Reliability controls inventoried against in-repo sources; crontab gap
  attributed to `OBS-P1-001`.
- Per-release backup/restore, alert-path and rollback drills documented with
  required evidence.
- Runbook index and `BACKUP_RESTORE.md` reference the new page.
- The snowride profile gate remains green (`npm ci`, `npm run lint`,
  `npm test`) and the changed docs scan clean under gitleaks.
