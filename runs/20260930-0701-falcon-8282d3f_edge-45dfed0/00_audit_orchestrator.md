# Audit Orchestrator

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab v1.0.0 (pack v1.2.1)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (full-domain)
- Repository scope: `falcon-build` @ `8282d3f` (clean) · `falcon-edge-build` @ `45dfed0` (dirty — in-flight CI work, recorded)
- Generated at: 2026-09-30T07:01Z
- Auditor: repo-deep-dive full run (orchestrator + subagent fan-out)
- Area code: ORCH
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/00_audit_orchestrator.md`
- Scope limitations: read-only audit account (no root/docker/wg); live checks limited to systemd, listeners, filesystem, HTTP, read-only metrics/DB; edge repo dirty at start

## Scope

This is the **first full-domain run** of the falcon lab under the repo-deep-dive pack. It covers all applicable prompts (27 RUN + 8 ADAPTED), the 10 N/A prompts as short evidenced reports, all five lenses, and the synthesis finals. It also verifies the status of the 90 findings from the prior lens-focused run (`20260930-0320-falcon-794ba31_edge-2b5bc8b`) at the current commits.

Not reviewed: deep-dive changes landed after the run's recorded commits; anything requiring root/docker/wg on the live host.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git rev-parse`/`status` for both repos | repo state | Run binding | falcon `8282d3f` clean; edge `45dfed0` dirty (recorded in manifest) |
| `live_snapshot.txt` (07:01:55Z) | live state | Read-only host snapshot | 167 lines: uptime, memory, disk, units, sockets, probes, journal tail |
| Prior run archive + `findings.json` | records | Prior findings to verify | 90 findings (P0×6, P1×22, P2×35, P3×27) |
| Pack: `profiles/falcon-lab.md`, `prompts/`, `lenses/` | procedure | Run rules and prompts | Pack lint PASS before the run |

## Verification Performed

| Check | Command / read | Result | Notes |
|---|---|---|---|
| Repo states | `git rev-parse --short HEAD`, `git status --porcelain` | recorded | falcon clean; edge dirty (in-flight CI) |
| Live snapshot | `tools/live_snapshot.sh` | captured | `live_snapshot.txt` |
| Pack health | `tools/lint_pack.sh` | PASS | Pack consistent before the run |

## Executive Summary

Full run initialized. Waves: (0) recon — this report; (1) domain fan-out — subagents per prompt group, dependency order; (2) lenses — ND/REV/INTG/LIVE/ADV; (3) synthesis — 22/23/40 + finals; (4) doctrine wiring — proposed decision-log entry, follow-up register, verification plan. Prior-run findings are checked at the current commits by each domain agent and marked fixed/still-open/regressed with evidence.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Run folder (canonical) | `falcon-build/docs/audits/repo-deep-dive/{run}/` | All reports + finals | created | — | This report, INDEX, manifest, snapshot |
| Edge mirror | `falcon-edge-build/docs/audits/repo-deep-dive/{run}/` | Edge-scoped artifacts + pointer | created | — | Populated in wave 4 |
| Prompt set | `repo-deep-dive/prompts/` (45) | Audit procedure | ready | — | 35 deep, 10 N/A |
| Lens set | `repo-deep-dive/lenses/` (5) | Cross-cutting overlays | ready | — | — |

## Findings

No orchestrator-level findings at setup. Domain findings follow in waves 1–3.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Edge repo dirty during run | P3 | actual | Some edge observations bind to an uncommitted tree | `git status` | Recorded in manifest; edge findings cite the working tree |
| Read-only account limits live verification | P3 | actual | Some claims marked `unverified` | audit account | Stated per report |

## Recommendations

1. Run domain fan-out in dependency order; each agent writes only its reports.
2. Verify prior findings at current commits inside the relevant domains.
3. Keep every report evidence-cited; mark unknowns `Unknown`.
4. After synthesis: `tools/check_run.sh` + `tools/collect_findings.py --write --update-manifest`.

## Quick Wins

None at this stage.

## Hardening Backlog

None at this stage.

## Suggested Tests

Run validation at the end: `tools/check_run.sh <run>` must PASS; `tools/collect_findings.py --write --update-manifest` must match register counts.

## Suggested Documentation Updates

None at this stage.

## Open Questions

None at this stage.

## Appendix

- Prompt statuses: 27 RUN · 8 ADAPTED · 10 N/A (see `audit_manifest.json`).
- Output map: canonical run folder + edge mirror (see `INDEX.md`).
