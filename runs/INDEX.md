# Archived Runs

| Run | Date | Repos | Type | Findings | Gate | Status |
|---|---|---|---|---|---|---|
| [20260930-0320-falcon-794ba31_edge-2b5bc8b](20260930-0320-falcon-794ba31_edge-2b5bc8b/) | 2026-09-30 | falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b` | lens-focused (conversion of six audits) | P0 ×6 · P1 ×22 · P2 ×35 · P3 ×27 | GO WITH CONDITIONS | complete; verification pass pending |
| [20260930-0701-falcon-8282d3f_edge-45dfed0](20260930-0701-falcon-8282d3f_edge-45dfed0/) | 2026-09-30 | falcon-build @ `8282d3f` · falcon-edge-build @ `45dfed0`→`f1c5def` | full-domain (45 prompts + 5 lenses) | P0 ×13 · P1 ×80 · P2 ×131 · P3 ×40 | GO WITH CONDITIONS | complete; validation PASS; **verification pass 2026-09-30 (updated 2026-10-01): 50 verified-fixed / 38 partially-fixed / 176 open**; post-run hardening 2026-09-30 evening: offsite delta + full remote verification gate + WireGuard boot fix (see the run's verification_log.md) |
| [buddy-20261003-0018-master-99abf29](buddy-20261003-0018-master-99abf29/) | 2026-10-03 | buddy @ `99abf29` | full-domain (13 reports + finals) | P0 ×0 · P1 ×11 · P2 ×24 · P3 ×5 | GO WITH CONDITIONS | complete; toolchain PASS |
| [chat-20261003-0018-develop-a72b8cc](chat-20261003-0018-develop-a72b8cc/) | 2026-10-03 | chat @ `a72b8cc` | full-domain (13 reports + finals) | P0 ×1 · P1 ×24 · P2 ×31 · P3 ×7 | GO WITH CONDITIONS | complete; toolchain PASS |
| [falcon-20261003-0018-fix-backup-abort-markers-20b5e57](falcon-20261003-0018-fix-backup-abort-markers-20b5e57/) | 2026-10-03 | falcon @ `20b5e57` | full-domain (13 reports + finals) | P0 ×4 · P1 ×20 · P2 ×18 · P3 ×4 | NO-GO (production) | complete; toolchain PASS |
| [falcon-edge-20261003-0018-fix-trust-root-87532ec](falcon-edge-20261003-0018-fix-trust-root-87532ec/) | 2026-10-03 | falcon-edge @ `87532ec` | full-domain (13 reports + finals) | P0 ×0 · P1 ×3 · P2 ×27 · P3 ×12 | GO WITH CONDITIONS | complete; toolchain PASS |
| [mainecybertech-20261003-0018-fix-p2-batch-31-2295958d](mainecybertech-20261003-0018-fix-p2-batch-31-2295958d/) | 2026-10-03 | mainecybertech @ `2295958d` | full-domain (13 reports + finals) | P0 ×1 · P1 ×3 · P2 ×26 · P3 ×14 | NO-GO | complete; toolchain PASS |
| [repo-deep-dive-20261003-0018-main-7bac320](repo-deep-dive-20261003-0018-main-7bac320/) | 2026-10-03 | repo-deep-dive @ `7bac320` | full-domain (13 reports + finals) | P0 ×0 · P1 ×9 · P2 ×20 · P3 ×12 | GO WITH CONDITIONS | complete; toolchain PASS |
| [snowride-20261003-0018-main-59e12b9](snowride-20261003-0018-main-59e12b9/) | 2026-10-03 | snowride @ `59e12b9` | full-domain (13 reports + finals) | P0 ×0 · P1 ×6 · P2 ×25 · P3 ×15 | GO WITH CONDITIONS | complete; toolchain PASS |

## Notes

- A run is complete when `tools/check_run.sh <run-folder>` prints `PASS`.
- Canonical copies live in the repositories (`docs/audits/repo-deep-dive/{run}/`); the copies here keep the pack portable.
- Machine-readable findings for a run: `findings.json` (generate with `tools/collect_findings.py <run> --write`).
- New rows are append-only; compare runs with `tools/diff_runs.py <old> <new>`.
