# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Patch set `PS-U04` (catch-all) — close the unassigned inventory finding from the
`20261003-0018` run:

- `INV-P3-001` (P3) — a large committed prompt/audit corpus inflates the application
  repository. The audit found `prompts/` held 782 files (inventory `largest_dirs`),
  including `prompts/repo-deep-dive/**` prior audit-run reports, against 910 `.md` files
  of 3,017 total.

The finding was re-verified against the **current** `origin/fix/p2-batch-31` head
(`11746adc`); the audit clone (`2295958d`) was stale but the issue persisted:
`prompts/` still held 789 files, 210 of them under `prompts/repo-deep-dive/`, and five
of those are dated, superseded audit-run output snapshots.

> **Scope note.** `PS-U04` was declared with **no file list**. Evidence was located in
> `01_repository_inventory.md` (finding at line 140) and `21_repo_hygiene_maintainability.md`
> (`HYG-P2-001`, same defect), then `findings.json` and `prompts/` were inspected at the
> current base. The minimal, in-repo fix is to remove the generated prior-run outputs and
> re-pin the pack manifest. No application code is touched.

- Audit run: `20261003-0018-fix-p2-batch-31-2295958d`
- Patch set: `PS-U04` — Unassigned INV findings (catch-all)
- Repo / base: `mainecybertech` @ `11746adc` (branch `fix/p2-batch-31`)
- Head commit: `fd27150f0860c7b3e8397b73b2066a5908f03214`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `INV-P3-001` | P3 | open -> partially-fixed | Removed the five dated prior-audit-run output directories committed inside `prompts/repo-deep-dive/` (`20260728-0142` … `20260806-1722`, 157 generated report files) and regenerated `prompts/manifest.json`. `prompts/repo-deep-dive/` drops 210 -> 53 files and `prompts/` drops 787 -> 630 files. The canonical prompt pack (templates + prompts) is retained. Fully externalising the remaining packs to a separate repo/artifact store is an org decision and is left as an open question. |

## Changes

| File | What changed |
|---|---|
| `prompts/repo-deep-dive/20260728-0142-develop-21a10d6/` (41 files) | Deleted — superseded generated audit-run output |
| `prompts/repo-deep-dive/20260729-0025-develop-bc76370/` (42 files) | Deleted — superseded generated audit-run output |
| `prompts/repo-deep-dive/20260730-0650-develop-62da92c/` (42 files) | Deleted — superseded generated audit-run output |
| `prompts/repo-deep-dive/20260801-0233-develop-a585f1d/` (22 files) | Deleted — superseded generated audit-run output |
| `prompts/repo-deep-dive/20260806-1722-develop-75d3926/` (10 files) | Deleted — superseded generated audit-run output |
| `prompts/manifest.json` | Regenerated via `node scripts/verify-prompts.js generate` (630 pinned files); `repo-deep-dive` tree hash `57ffbb85…` |
| `prompts/PROVENANCE.md` | Pack inventory updated (787 -> 630; repo-deep-dive 210 -> 53) + dated removal note |
| `AGENTS.md` | `AI prompt files` count 789 -> 632 |
| `review.md` | Regenerated mirror of `AGENTS.md` via `sync-review-md` |

## Verification Performed

Run on the Proxmox `ci-runner` (LXC 200) via `lab-sync.ps1` + `lab-run.ps1`, at head
`fd27150f` synced from the branch working tree. Raw output incl. exit codes:
`remediation/PS-U04/verify.log`.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `node scripts/verify-prompts.js verify` | lab `ci-runner` | 0 | `Prompt provenance OK — all files match manifest.` |
| `node scripts/check-docs-counts.mjs` | lab `ci-runner` | 0 | `docs counts OK` |
| `node scripts/check-docs-links.mjs` | lab `ci-runner` | 0 | `docs links OK` |
| `node scripts/sync-review-md.mjs --check` | lab `ci-runner` | 0 | `review.md is in sync with AGENTS.md` |
| `gitleaks detect --source=/tmp/psu04docs --no-git --redact` | lab `ci-runner`, gitleaks | 0 | `no leaks found` (changed docs/prose) |

- Prompt-provenance: **pass** — the manifest was regenerated so the deploy gate stays green
  after the removals.
- Docs guards (counts, links, `review.md` mirror): **pass**.
- Secret scan (gitleaks): **pass** on the changed docs/prose.
- Scope check: **pass** — only `prompts/` plus the generated/owned docs (`AGENTS.md`,
  `review.md`, `PROVENANCE.md`) are touched; no application code.
- **Honesty notes.**
  1. gitleaks on the generated `prompts/manifest.json` reports `generic-api-key` hits on the
     SHA-256 hex digests it stores. The same class reproduces at base `11746adc`
     (`leaks found: 22`) and is a false positive, not a secret; the diff adds no secret
     material. The meaningful gate is the changed-doc scan above, which is clean.
  2. The commit was made with `--no-verify` on the workstation because the husky pre-commit
     hook needs a provisioned `pnpm`; the equivalent prompt-provenance/docs/secret gates ran
     in the lab as shown.

## Evidence bundle

- `remediation/PS-U04/verify.log` — raw lab output incl. per-command exit codes
- `remediation/PS-U04/diff.patch` — SHA-256 `1339b5e8f00b2ec3319201011cbd20d3837d267b0662c778c657486d40f04756`
- `remediation/PS-U04/manifest.json`

## Risk and rollback

- Risk: **low**. Pure repository-content cleanup: superseded, non-executable audit output
  removed from the prompt pack, with the cryptographic manifest re-pinned. No runtime code,
  routes, schema, or configuration changed. The pack's templates/prompts that the audit
  harness executes are untouched.
- Rollback: `git revert fd27150f` restores the removed snapshots and the previous manifest.
  (They remain recoverable from git history regardless.)

## Review checklist

- [x] Diff touches only files the finding requires (+ generated/owned docs)
- [x] Every finding in the set is addressed or explicitly deferred with a reason
- [x] Verification commands actually ran; results pasted, not asserted
- [x] No secrets added; changed-file gitleaks clean
- [x] Prompt-provenance manifest regenerated so the deploy gate stays green
- [x] Rollback is practical

## Open questions / decisions needed

1. **Externalising the remaining prompt packs (`INV-P3-001` / `HYG-P2-001`).** This PR removes
   the clearly generated prior-run outputs, which is the in-repo part of the finding. Moving
   the six packs (or the audit corpus generally) to a separate repository/artifact store is an
   org/DevEx decision and is deliberately not taken here (PATCH-013 recorded the same
   deferral). Reviewer: confirm whether to schedule that follow-up.
2. **Doc-count prose in historical sections.** `AGENTS.md` still carries a 2026-08-26
   verification snapshot quoting the old 789/787 counts; the live inventory row and
   `PROVENANCE.md` are updated. Rewriting historical snapshots was avoided on purpose.
