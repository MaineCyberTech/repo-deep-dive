# Archived Runs

| Run | Date | Repos | Type | Findings | Gate | Status |
|---|---|---|---|---|---|---|
| [20260930-0320-falcon-794ba31_edge-2b5bc8b](20260930-0320-falcon-794ba31_edge-2b5bc8b/) | 2026-09-30 | falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b` | lens-focused (conversion of six audits) | P0 ×6 · P1 ×22 · P2 ×35 · P3 ×27 | GO WITH CONDITIONS | complete; verification pass pending |
| [20260930-0701-falcon-8282d3f_edge-45dfed0](20260930-0701-falcon-8282d3f_edge-45dfed0/) | 2026-09-30 | falcon-build @ `8282d3f` · falcon-edge-build @ `45dfed0`→`f1c5def` | full-domain (45 prompts + 5 lenses) | P0 ×13 · P1 ×80 · P2 ×131 · P3 ×40 | GO WITH CONDITIONS | complete; validation PASS; **verification pass 2026-09-30 (updated 2026-10-01): 50 verified-fixed / 38 partially-fixed / 176 open**; post-run hardening 2026-09-30 evening: offsite delta + full remote verification gate + WireGuard boot fix (see the run's verification_log.md) |

## Notes

- A run is complete when `tools/check_run.sh <run-folder>` prints `PASS`.
- Canonical copies live in the repositories (`docs/audits/repo-deep-dive/{run}/`); the copies here keep the pack portable.
- Machine-readable findings for a run: `findings.json` (generate with `tools/collect_findings.py <run> --write`).
- New rows are append-only; compare runs with `tools/diff_runs.py <old> <new>`.
