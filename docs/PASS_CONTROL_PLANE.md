# Pass control plane (`tools/pass.py`)

State machine for an **org-wide audit pass** across many repos. It closes the
Orchestration gap in [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) by making the standard
[`runbooks/POST_AUDIT_PIPELINE.md`](../runbooks/POST_AUDIT_PIPELINE.md) sequence explicit
and resumable.

```
sweep -> deepdive -> publish -> remediate -> merge -> reconcile
```

Each repo in the pass walks the same six stages, with status
`pending | in_progress | done | blocked` and evidence (`run_url`, `pr_numbers`,
`commit_shas`, `note`).

## State

| Path | What |
|---|---|
| `docs/audits/_org/<id>/manifest.json` | Machine state (schema: [`schemas/org_pass.schema.json`](../schemas/org_pass.schema.json)) |
| `docs/audits/_org/<id>/INDEX.md` | Human status matrix + next phase |
| `docs/audits/_org/<id>/commands.log` | Append-only log of every command run by `advance --execute` |

`_org` is deliberately outside `runs/` so `tools/check_run.sh` (which validates every
folder under `runs/`) is unaffected.

## Usage

```bash
# scaffold a pass for two repos
python3 tools/pass.py new --org MaineCyberTech --repos chat,buddy \
    --lenses security,supply-chain,ci

# inspect
python3 tools/pass.py status --id 20261004-mainecybertech [--json]
python3 tools/pass.py next   --id 20261004-mainecybertech [--json]

# print the exact commands for the next phase (does not run them)
python3 tools/pass.py plan   --id 20261004-mainecybertech [--repo chat] [--json]

# record state only (safe)
python3 tools/pass.py advance --id <id> --stage sweep --status done \
    --run-url https://github.com/MaineCyberTech/repo-deep-dive/actions/runs/12345

# execute the documented commands for a stage (logs every command; fail-closed)
python3 tools/pass.py advance --id <id> --stage publish --execute \
    --repo chat --branch develop --sha <full-sha> --source-dir <dir>
```

## Stage commands

`plan` (and `advance --execute`) emit the standard tools, never ad-hoc steps:

| Stage | Command(s) |
|---|---|
| `sweep` | `gh workflow run deep-dive-deterministic.yml -R <org>/repo-deep-dive -f org=… -f repos=… -f deep=true` |
| `deepdive` | `tools/new_run.py` + the audit agent (`prompts/MASTER_RUNNER_FULL_HARDENING.md`) |
| `publish` | `tools/publish_audit.py` (dry-run first), then `tools/pack_digest.sh` + `tools/lint_pack.sh` |
| `remediate` | `tools/remediation_plan.py` + draft PRs per `prompts/REMEDIATION_RUNNER.md` |
| `merge` | `gh pr ready` + `gh pr merge --merge` (audit PR first) |
| `reconcile` | `tools/remediation_status.py` |

## Safety

- **Plan/status only by default.** `new`, `status`, `next`, `plan`, and `advance` without
  `--execute` change no remote state.
- `advance --execute` runs only commands that are complete (no `<placeholder>`), not
  comments, and not the manual `deepdive` stage; every command is appended to
  `commands.log`. If a command fails, the stage is marked `blocked` and the command exits
  non-zero (fail closed).
- **Merge is gated:** the `merge` stage is never executed unless `--confirm-merge` is
  passed in addition to `--execute` — matching "draft PRs only; no auto-merge without
  explicit authorization."

## Intentionally stubbed

- The `deepdive` stage is agent-driven, so it has no shell command to execute; `plan`
  documents the runner and `--execute` records it as `in_progress` rather than `done`.
- `publish`/`reconcile` need real inputs (`--source-dir`/`--sha`/`--patch-set`); without
  them the command is a placeholder and is skipped on execution.
- No dedup/resume across passes, no work queue, no PR conflict automation yet — those
  remain on the roadmap (`docs/DEEP_DIVE_ROADMAP.md`).
