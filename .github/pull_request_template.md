<!--
repo-deep-dive default PR template. Keep changes evidence-first: draft PRs only, never
auto-merge or self-approve. See AGENTS.md and prompts/REMEDIATION_RUNNER.md.
-->

## What / why

<!-- One or two sentences. Link the finding(s) / patch set(s) / run. -->

## Lab preflight (REQUIRED before audit/remediation work)

- [ ] I ran `bash tools/lab-vpn/lab-audit-preflight.sh` and it printed `RESULT: PASS`
      (or the **Lab preflight** CI check is green for this PR).
- [ ] Any lab verification for this change ran on `ci-runner` / `edge-builder`, and the
      log/artifact is linked or committed — or it is explicitly marked `not run` with a reason.

## Evidence & rules

- [ ] Findings cite repository evidence (file/symbol/lines) or are marked `Unknown`; no secrets committed.
- [ ] A finding is `verified-fixed` only with an artifact at the current commit (no assertions).
- [ ] Draft PR only: no auto-merge, no self-approval.
- [ ] `bash tools/pack_digest.sh` regenerated and `bash tools/lint_pack.sh` prints `RESULT: PASS`.
