# Executive Summary — repo-deep-dive

- **Repo:** repo-deep-dive (audit pack), branch `main`
- **Audited commit:** worktree `6cada03` (run recorded `7bac320`; see INV-P1-001)
- **Run:** 20261003-0018-main-7bac320
- **Findings:** 41 total — **P0 0 · P1 9 · P2 20 · P3 12**
- **Advisory score:** 0/100 (`risk_score.py`; P3 unpenalized, P1×10 + P2×3 = 150)
- **Release gate:** **GO WITH CONDITIONS**

## What this is

The target is the **repo-deep-dive audit pack itself**: a prompt-driven, evidence-first repository audit framework with stdlib-only Python tools, shell gates, templates, profiles, lenses, and archived runs. Auditing it means auditing the machinery that audits other repos.

## Strengths

- No committed secret values; no language dependencies; portable forward-slash, ASCII-safe tools.
- Rich, consistent prompt/template structure; thorough `lint_pack.sh`; a smoke harness (`self_test.sh`).
- Clear severity model, finding vocabulary, and an advisory-only score that never overrides the gate.

## Top risks

1. **CI supply-chain RCE (P1).** The org workflow pipes remote scripts/tarballs to `bash`/`sudo tar` with no pin or checksum, and masks failures (SEC-P1-001, SUPPLY-P1-001, CI-P2-003).
2. **PAT exposure (P1).** The org token is embedded in the git clone URL, where it can surface in CI logs (SEC-P1-002).
3. **Broken data contract (P1).** `collect_findings.py` emits `sourceReports` as an array while the schema requires an integer; the self-test doesn't check types (DATA-P1-001, TEST-P2-003).
4. **Scaffold fails its own gate (P1).** The base example manifest lacks `profile`/`scope`/`findings`, so `new_run.py --profile base` is rejected by `check_run.sh` (DATA-P1-002).
5. **CI that never runs (P1).** `ci/audit.yml` sits outside `.github/workflows/` and assumes a vendored `PACK_DIR` that doesn't match this repo (CI-P1-001/002, TEST-P1-001).
6. **Unpinned actions/tools (P1).** GitHub Actions use mutable major tags (SUPPLY-P1-001).
7. **Gate bypass on Windows (P2).** `run_toolchain.py` skips `check_run.sh` without bash and still prints PASS (ARCH-P2-002).
8. **Duplicated orchestration truth (P2).** Execution order is copied across runner/manifests with no drift check (ARCH-P2-001).
9. **Deterministic findings detached and area-colliding (P2).** New machine checks reuse `SEC`/`CI` area codes and never feed the run findings flow (API-P2-001/002).
10. **Hygiene/sensitivity gaps (P2/P3).** No LICENSE/`.gitignore`/`.gitattributes`; a committed `live_snapshot.txt` host capture (HYG-P2-001, HYG-P3-003).

## Conditions to move from GO WITH CONDITIONS to GO

1. Fix the data contract (PS-002): schema/scaffold alignment + type-checked schema test.
2. Harden the org workflow (PS-003): pin+checksum tools, remove root remote exec, mask token / use header auth, gate secret scan.
3. Wire the audit CI (PS-004): move to `.github/workflows/audit.yml`, `PACK_DIR: .`, PR trigger, required checks + CODEOWNERS.
4. Make `run_toolchain.py` strict by default and lint execution-order equality (PS-006).

## Reconciliation

The archived falcon-lab runs carry existing **GO WITH CONDITIONS** verdicts. This audit neither grants nor revokes them; it adds a pack-level opinion at the audited commit.
