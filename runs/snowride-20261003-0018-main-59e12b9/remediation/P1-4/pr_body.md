# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set **P1-4 (Alerting as code)** addresses `OBS-P1-001`: the repository's
alerting/scheduled-detection topology was only described on the host, so on-call
had no in-repo, reviewable description of the signals, thresholds, delivery path
or escalation. This change makes `docs/runbooks/INCIDENT.md` the on-call
entry point: it documents the assurance lanes and their thresholds/exit codes,
where alerts are delivered, how to escalate, how to prove the alert path with a
drill, and the rollback switches. It is **docs-only** (one file, no code,
config or dependency change).

Honesty note: `OBS-P1-001` also asks for the crontab/systemd schedule and alert
rules to be **committed**. That is not done here because this patch set's scope
is `docs/runbooks/INCIDENT.md`; the finding therefore lands at
`partially-fixed`, and the remaining in-repo schedule/rule versioning is called
out explicitly in the runbook's "Known gaps" section and as operator follow-up.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `P1-4` — Alerting as code
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P1-001` | P1 | open -> partially-fixed | Runbook now documents the real host alert path (assurance lanes, thresholds, exit codes, ntfy delivery, escalation, drill) so on-call can act. The committed crontab/alert-rule artifact is still missing (out of this patch set's scope) and is listed as a known gap + operator follow-up. |

## Changes

| File | What changed |
|---|---|
| `docs/runbooks/INCIDENT.md` | Added an on-call intro/cross-links; a **"Alerting and detection (on-call signals)"** table mapping each assurance signal to its threshold/rule and exit code (containers 2, cert 3, disk 12, daily tests 4, backup freshness 5, exception drift 6, a11y/OSV/offsite/license 7–11, capacity 13, perf 14, drill 90); an **"Escalation"** procedure; an **"Alert-path drill"** (`ASSURANCE_DRILL=1`); a disk-low common case; and a **"Known gaps"** section recording `OBS-P1-001` (schedule lives only on the host). |

All thresholds and exit codes are grounded in `scripts/assurance/assurance.sh`
at the base commit and are checked mechanically in the verification below.

## Verification Performed

Run on the lab `ci-runner` (`172.23.128.51`) in a **clean LF git clone** from a
git bundle at the exact commit `030d225` (dirty count 0), node `v20.20.2`,
npm `10.8.2`. The git blob is LF (`i/lf w/lf`); the clean clone matches a normal
CI checkout and avoids the known Windows CRLF tar issue.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `git clone -b <branch> /srv/work/p1-4.bundle` (clean LF worktree) | ci-runner | 0 | `remediation/P1-4/verify.log` — dirty count 0, `i/lf w/lf` |
| docs-consistency: relative links in `INCIDENT.md` resolve | ci-runner | 0 | `verify.log` — `relative links checked=6 missing=0` |
| docs-consistency: cited thresholds/exit codes match `assurance.sh` | ci-runner | 0 | `verify.log` — all claims ok; cited codes 2–14,90 present |
| docs-consistency: referenced repo paths exist | ci-runner | 0 | `verify.log` — `paths checked=10 missing=0` |
| `npm ci` | ci-runner | 0 | `verify.log` |
| `npm run lint` | ci-runner | 0 | `verify.log` — 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` | ci-runner | 0 | `verify.log` — 131 test files, 873 tests passed |
| `gitleaks detect --no-git --redact --source <diff.patch>` | ci-runner | 0 | `remediation/P1-4/gitleaks.log` — no leaks found |
| `gitleaks detect --no-git --redact --source docs/runbooks/INCIDENT.md` | ci-runner | 0 | `gitleaks.log` — no leaks found |

- Secret scan (gitleaks): **pass** — no leaks in the diff or the changed file.
- Scope check (files within patch set): **pass** — only `docs/runbooks/INCIDENT.md` changed.
- No repo docs-consistency gate exists; the equivalent checks above were run and recorded.
- `OBS-P1-001`'s validate criterion ("forced failure produces an ntfy alert after
  a clean rebuild") cannot be executed in this runner (it needs the host crontab +
  `NTFY_TOPIC`); the runbook documents the `ASSURANCE_DRILL=1` procedure and the
  first real firing remains the operator's post-merge evidence.

## Evidence bundle

- `remediation/P1-4/diff.patch` — SHA-256 `d07144b57ae27e18764dc7103c27a0751b58008597198f49a363b41166a5bf26`
- `remediation/P1-4/verify.log` — SHA-256 `fa1f3625d6de27bd5551e9fa03bf34e4ed3a607a9339305c654eb877ff202c3f`
- `remediation/P1-4/gitleaks.log` — SHA-256 `05916ed8ffa3bd2a8855a20afa28b9948d473a7a9d3200e5e6faedee613ef9ab`
- `remediation/P1-4/manifest.json`

## Risk and rollback

- Risk: **very low** — documentation only; no runtime, CI, config or dependency change.
- Rollback: `git revert 030d225` (or close the PR).

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

<!-- from patch_plan.md: version the schedule and thresholds; add ASSURANCE_DRILL=1 output to release evidence -->

- [x] Alert thresholds and the alert path are documented in-repo
  (`docs/runbooks/INCIDENT.md`), matching `scripts/assurance/assurance.sh`.
- [x] `ASSURANCE_DRILL=1` procedure (forced failure -> ntfy) is documented.
- [ ] Committed schedule (cron/systemd timer) + alert-rule files — **deferred**
  (outside this docs-only patch set; tracked as the remaining part of `OBS-P1-001`).

## Operator follow-up (required to reach `verified-fixed`)

1. Merge this PR (human review; this runner never merges or self-approves).
2. On the host, run `ASSURANCE_DRILL=1 bash scripts/assurance/assurance.sh quick`
   and confirm the ntfy alert + ledger/delivery evidence.
3. Commit the crontab/systemd schedule and alert rules to close the remainder of
   `OBS-P1-001`, then reconcile the register to `verified-fixed` with that evidence.
