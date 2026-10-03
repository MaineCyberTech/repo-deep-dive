# Archived audit runs — sensitive content

Everything under `runs/` is an **archive of audit output** for a target
repository. Per the shared audit rules (`prompts/00_SHARED_AUDIT_RULES.md`),
repository exports, logs, `.env`-adjacent files, test artifacts, and generated
outputs are **sensitive** and may contain host topology, service/socket
inventory, paths, and findings that aid reconnaissance.

## Handling

- Treat this directory as internal. Review it before sharing the repository
  outside the organization.
- Do **not** commit a live-host snapshot (`live_snapshot.txt`) that names
  hosts, users, or sensitive paths. Redact host-identifying fields first, or
  store the snapshot outside the repository and commit only a redacted summary.
- Keep the raw capture and any secret-like values out of PR bodies and evidence;
  reference path and secret type only.

## Generated artifacts and retention

- A completed run commits its generated `dashboard.md`, `dashboard.html`, and
  `pr_comment.md` alongside the reports so reviewers can see the score and
  severity mix in-repo.
- Run-over-run diffs are **ephemeral**: regenerate on demand with
  `tools/diff_runs.py <previous-run> <current-run>` rather than committing a
  delta file, because the delta is only meaningful relative to another run.

## Known state

The `runs/20260930-*` runs predate this policy; `runs/20260930-0701-falcon-8282d3f_edge-45dfed0/live_snapshot.txt`
is retained in place under this documented policy. Redacting or relocating
existing snapshots is tracked as a follow-up under finding HYG-P3-003 in audit
run `20261003-0018-main-7bac320`.
