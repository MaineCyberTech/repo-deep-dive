# Post-merge verification re-audit

After the remediation PRs for a repo are reviewed and merged, run a **verification-mode
re-audit** to (a) confirm the remediated findings are actually closed at the merged commit and
(b) catch any regression introduced by the fixes. This is the LLM re-run of the pack against the
**merged** state; it complements the machine checks (`tools/deterministic_checks.py --deep`).

The queue (repos + PRs) is in `REAUDIT_QUEUE.md` (generate with `tools/reaudit_queue.py`).

## 0. Preconditions

- The stack is valid: `bash tools/lint_pack.sh` and `bash tools/self_test.sh` both `PASS`.
- The repo's default branch is at the merged state.

## 1. Reconcile merged PRs -> verified-fixed

A finding becomes `verified-fixed` only with a **merge commit as evidence**:

```bash
python3 tools/remediation_status.py <run> --patch-set <PS> --state merged \
    --commit <merge-sha> [--pr <pr-url>]
python3 tools/normalize_register.py <run>
bash tools/check_run.sh <run>
```

## 2. Machine re-audit (fast, LLM-free)

```bash
python3 tools/deterministic_checks.py <repo-root> -o /tmp/det --run <repo> --deep
```

Compare against the archived deterministic baseline. Expected: findings tied to merged fixes
disappear; **any new P0/P1 is a regression** and blocks close-out. The org sweep is also available
as the `Deep-dive deterministic checks` workflow (dispatch with `deep: true`).

> Note: cloning private repos over git-over-HTTPS requires **Basic** auth
> (`Authorization: Basic base64(x-access-token:<pat>)`); a Bearer header is rejected by the git
> endpoint (it is only valid for the REST API). This is handled in the workflow.

## 3. Verification-mode LLM re-audit

1. Create the run: `python3 tools/new_run.py --profile base --name <repo>-verify-<date>`.
2. Execute the master runner via the agent harness with a **verification lens**: for each original
   finding ID record `closed | still-open | regressed` with evidence at the new commit. Use
   `lenses/independent_reviewer.md` for the cross-check.
3. Emit the standard reports + `findings.json` + registers in the new run folder.
4. Diff new vs original: **closed** (cite the merge commit), **still-open** (reopen/follow-up),
   **regressed/new** (highest priority).
5. Record the diff in the new run's `verification_log.md` and reconcile the original run
   (`tools/remediation_status.py --state regressed` for regressions).

## 4. Close-out

```bash
bash tools/pack_digest.sh && bash tools/lint_pack.sh && bash tools/self_test.sh
```

Update `runs/INDEX.md`, the review board (`tools/remediation_report.py`) and this queue. A repo is
close-out-complete only with **zero open/regressed P0/P1** at the merged commit and every merged
patch set `verified-fixed`.

## Notes

- Never self-approve: the re-audit reports state; a human owns the final gate.
- Keep the original run immutable; append status only through `tools/remediation_status.py`.
- For edge/polyglot repos, run the machine re-audit in the lab (`tools/lab_runner.py`).
