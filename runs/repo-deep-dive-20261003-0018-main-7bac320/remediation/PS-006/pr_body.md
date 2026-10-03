# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Closes the two architecture findings from the `20261003-0018-main-7bac320` audit run
(patch set **PS-006**): duplicated execution-order truth is now guarded by a lint check
(ARCH-P2-001), and the primary run gate (`check_run.sh`) is strict by default instead of
being silently skipped when `bash` is unavailable (ARCH-P2-002).

- Audit run: `20261003-0018-main-7bac320`
- Patch set: `PS-006` — Architecture: single source + strict gate
- Repo / base: `MaineCyberTech/repo-deep-dive` @ `b3d038250f5437490df21e1d25a1ea1297530559` (`main`)
- Branch: `remediation/ps-006-20261003-0018-main-7bac320`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `ARCH-P2-001` | P2 | open -> partially-fixed | `tools/lint_pack.sh` §5b now asserts execution-order / prompt-status coverage equals the `prompts/` set (base vs falcon-lab). |
| `ARCH-P2-002` | P2 | open -> partially-fixed | `tools/run_toolchain.py` fails (exit 2) when `bash` is missing unless `--no-check` is passed explicitly. |

Both remain `partially-fixed` until a human merges (per the remediation profile: merged -> verified-fixed).

## Changes

| File | What changed |
|---|---|
| `tools/lint_pack.sh` | New §5b: parses `examples/audit_manifest.example.json`, `examples/audit_manifest.falcon-lab.example.json`, `profiles/falcon-lab.manifest.json` and asserts every `prompts/[0-9][0-9]_*.md` is covered by exactly the right manifest (base `executionOrder`; falcon `executionOrder` + `naReports`; profile `promptStatus` + `waves`). Unknown/duplicate/missing numbers fail the lint. |
| `tools/run_toolchain.py` | The `check_run.sh` step is now mandatory: with no `bash` on `PATH` it prints `FAILED` and exits `2` unless `--no-check` is passed. `--strict` is retained as a deprecated no-op; docstring updated. |
| `PACK_DIGEST.txt` | Regenerated over the changed tree (last step). |

No changes to the example/profile manifests were required — the lint implements the
"lint for set-equality" option in the finding's recommended fix, so the duplicated lists
stay where they are but can no longer drift silently.

## Verification Performed

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `bash tools/self_test.sh` | local WSL Ubuntu 24.04 / Python 3.12.3 | 0 | `remediation/PS-006/verify.log` §1 (RESULT: PASS) |
| `bash tools/lint_pack.sh` | local WSL Ubuntu 24.04 / Python 3.12.3 | 0 | `remediation/PS-006/verify.log` §2 (RESULT: PASS; "46 prompts covered by order/status/waves") |
| `env PATH=/nonexistent python3 tools/run_toolchain.py <run>` | local WSL Ubuntu 24.04 | 2 | `remediation/PS-006/verify.log` §3 (FAILED, expected) |
| `env PATH=/nonexistent python3 tools/run_toolchain.py <run> --no-check` | local WSL Ubuntu 24.04 | 0 | `remediation/PS-006/verify.log` §4 (TOOLCHAIN: PASS, explicit opt-out) |
| `python3 tools/run_toolchain.py <run>` | local WSL Ubuntu 24.04 | 0 | `remediation/PS-006/verify.log` §5 (check + TOOLCHAIN: PASS) |
| Negative test: perturbed `executionOrder` in a throwaway copy | local WSL Ubuntu 24.04 | 1 | `remediation/PS-006/verify.log` §6 (FAIL "execution order/status drift", `missing=['21']`) |
| `gitleaks detect --no-git --redact` | - | not run | `gitleaks` binary not installed on the remediation host; manual regex scan of the staged diff (`AKIA…`, private-key, password/secret/token assignments) found no matches. Diff is code + digest only. |

- Secret scan (gitleaks): **not run** (binary absent) — manual diff scan clean.
- Scope check (files within patch set): **pass** — only `tools/lint_pack.sh`, `tools/run_toolchain.py`, `PACK_DIGEST.txt`.

## Evidence bundle

- `remediation/PS-006/diff.patch`
- `remediation/PS-006/manifest.json`
- `remediation/PS-006/verify.log`
- `remediation/PS-006/verify_ps006.sh` (reproducible harness)

## Risk and rollback

- Risk: **low**. A lint check added and a default made stricter; no runtime/service impact.
  Callers that relied on the soft-skip must pass `--no-check` (the intended opt-out).
- Rollback: `git revert 20f7a3d47f6f1dc4ecf8e2f9d5dae1d35cffec8c`.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean (manual scan here — gitleaks binary unavailable on host)
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

From `patch_plan.md` PS-006: *execution-order set equals prompt-number set; run without
bash fails unless `--no-check`.* Both hold (verify.log §2 and §3/§4).
