# Archived Runs

| Run | Date | Repos | Type | Findings | Gate | Status |
|---|---|---|---|---|---|---|
| [20260930-0320-falcon-794ba31_edge-2b5bc8b](20260930-0320-falcon-794ba31_edge-2b5bc8b/) | 2026-09-30 | falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b` | lens-focused (conversion of six audits) | P0 ×6 · P1 ×22 · P2 ×35 · P3 ×27 | GO WITH CONDITIONS | complete; verification pass pending |
| [20260930-0701-falcon-8282d3f_edge-45dfed0](20260930-0701-falcon-8282d3f_edge-45dfed0/) | 2026-09-30 | falcon-build @ `8282d3f` · falcon-edge-build @ `45dfed0`→`f1c5def` | full-domain (45 prompts + 5 lenses) | P0 ×13 · P1 ×80 · P2 ×131 · P3 ×40 | GO WITH CONDITIONS | complete; validation PASS at `8282d3f`/`45dfed0`; **verification pass current at 2026-10-04 (remediation waves W1-W10 + the 2026-10-03 deploy record, bound to the run's commits): 104 verified-fixed / 115 partially-fixed / 45 open**; post-run hardening 2026-09-30 evening: offsite delta + full remote verification gate + WireGuard boot fix (see the run's verification_log.md) |
| [buddy-20261003-0018-master-99abf29](buddy-20261003-0018-master-99abf29/) | 2026-10-03 | buddy @ `99abf29` | full-domain (13 reports + finals) | P0 ×0 · P1 ×11 · P2 ×24 · P3 ×5 | GO WITH CONDITIONS | complete; toolchain PASS |
| [chat-20261003-0018-develop-a72b8cc](chat-20261003-0018-develop-a72b8cc/) | 2026-10-03 | chat @ `a72b8cc` | full-domain (13 reports + finals) | P0 ×1 · P1 ×24 · P2 ×31 · P3 ×7 | GO WITH CONDITIONS | complete; toolchain PASS |
| [falcon-20261003-0018-fix-backup-abort-markers-20b5e57](falcon-20261003-0018-fix-backup-abort-markers-20b5e57/) | 2026-10-03 | falcon @ `20b5e57` | full-domain (13 reports + finals) | P0 ×4 · P1 ×20 · P2 ×18 · P3 ×4 | NO-GO (production) | complete; toolchain PASS |
| [falcon-edge-20261003-0018-fix-trust-root-87532ec](falcon-edge-20261003-0018-fix-trust-root-87532ec/) | 2026-10-03 | falcon-edge @ `87532ec` | full-domain (13 reports + finals) | P0 ×0 · P1 ×3 · P2 ×27 · P3 ×12 | GO WITH CONDITIONS | complete; toolchain PASS |
| [mainecybertech-20261003-0018-fix-p2-batch-31-2295958d](mainecybertech-20261003-0018-fix-p2-batch-31-2295958d/) | 2026-10-03 | mainecybertech @ `2295958d` | full-domain (13 reports + finals) | P0 ×1 · P1 ×3 · P2 ×26 · P3 ×14 | NO-GO | complete; toolchain PASS |
| [repo-deep-dive-20261003-0018-main-7bac320](repo-deep-dive-20261003-0018-main-7bac320/) | 2026-10-03 | repo-deep-dive @ `7bac320` (recorded) / `6cada03` (generating worktree) | full-domain (13 reports + finals) | P0 ×0 · P1 ×9 · P2 ×20 · P3 ×12 | GO WITH CONDITIONS | complete; toolchain PASS bound to `6cada03` |
| [snowride-20261003-0018-main-59e12b9](snowride-20261003-0018-main-59e12b9/) | 2026-10-03 | snowride @ `59e12b9` | full-domain (13 reports + finals) | P0 ×0 · P1 ×6 · P2 ×25 · P3 ×15 | GO WITH CONDITIONS | complete; toolchain PASS |

## Notes

- A run is complete when `tools/check_run.sh <run-folder>` prints `PASS`.
- Each archived run is bound to the commit(s) it was generated at, recorded in its row above and in the run's `INDEX.md`/`audit_manifest.json`. Gate verdicts, findings, and register statuses are valid only at those commits; later tooling commits do **not** inherit them. Re-verification at a newer commit produces its own `verification_log.md`.
- Canonical copies live in the repositories (`docs/audits/repo-deep-dive/{run}/`); the copies here keep the pack portable.
- Machine-readable findings for a run: `findings.json` (generate with `tools/collect_findings.py <run> --write`).
- New rows are append-only; compare runs with `tools/diff_runs.py <old> <new>`.
| [buddy-20261004-0700-master-29d7928](buddy-20261004-0700-master-29d7928/) | 2026-10-04 | buddy @ `29d7928` | focused (security/supply-chain/CI) | P0 ×0 · P1 ×2 · P2 ×3 · P3 ×4 | GO | published by tools/publish_audit.py |
| [falcon-20261004-0700-main-ff868e5](falcon-20261004-0700-main-ff868e5/) | 2026-10-04 | falcon @ `ff868e5` | focused (security/supply-chain/CI) | P0 ×0 · P1 ×0 · P2 ×6 · P3 ×8 | GO | published by tools/publish_audit.py |
| [chat-20261004-0700-develop-0695894](chat-20261004-0700-develop-0695894/) | 2026-10-04 | chat @ `0695894` | focused (security/supply-chain/CI) | P0 ×0 · P1 ×2 · P2 ×10 · P3 ×10 | GO | published by tools/publish_audit.py |
| [snowride-20261004-0700-main-d79d0d7](snowride-20261004-0700-main-d79d0d7/) | 2026-10-04 | snowride @ `d79d0d7` | focused (security/supply-chain/CI) | P0 ×0 · P1 ×1 · P2 ×3 · P3 ×6 | GO | published by tools/publish_audit.py |
