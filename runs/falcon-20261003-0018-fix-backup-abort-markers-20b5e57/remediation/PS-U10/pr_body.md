# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all patch set `PS-U10` (unassigned OBS findings). After checking `origin/main`
(`430da82`), two of the three findings were already remediated on `main` *after* the audited
commit (`20b5e57`), and the third had only half of its fix: the relay per-path metrics were
added, but nothing alerted on a **single** failing path. This PR closes the remaining gap and
adds offline regression guards so the three findings cannot silently regress.

- `OBS-P1-003` (open) - **fixed here**: add the `falcon-relay-path-failures` rule
  (`increase(falcon_alert_relay_path_failures_total[15m]) > 0`). The pre-existing
  `falcon-relay-publish-failures` rule only moves when **every** path fails, so one degraded
  destination (lab or independent) stayed invisible until the weekly canary.
- `OBS-P1-001` (partially-fixed at base) - **guarded here**: the bool-comparison guard exists
  (`a29fcf3`) and runs in the gate; this PR adds an offline rule linter that sanity-checks
  every provisioned expression (non-empty, balanced delimiters) in addition to the existing
  bool check.
- `OBS-P1-002` (partially-fixed at base) - **guarded here**: no duplicate rule UIDs or
  identical expressions exist (verified: 78 unique UIDs/expressions); the linter derives the
  rule count from `bootstrap/90-alerting.sh` (source of truth) instead of relying on a
  hand-maintained count, and rejects duplicates/identical conditions.

- Audit run: `20261003-0018-fix-backup-abort-markers-20b5e57`
- Patch set: `PS-U10` - Unassigned OBS findings (catch-all)
- Repo / base: `MaineCyberTech/falcon` @ `main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Branch: `remediation/ps-u10-20261003-0018-fix-backup-abort-markers-20b5e57`
- Commit: `aef63addacb79888c0d540257a8b0470115c3102`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P1-003` | P1 | open -> partially-fixed (draft PR) | Per-path counters already exist (`85b068d`), but total-failure `falcon-relay-publish-failures` cannot see one degraded path. New `falcon-relay-path-failures` warning rule fires per `path="lab\|alt"` within one evaluation interval. No live firing proof yet (needs deploy + fault injection; see below). |
| `OBS-P1-001` | P1 | partially-fixed at base, guarded here | `automation/validation/tests/alert_expression_bool_test.sh` (`a29fcf3`) is already executed by the `ci/validate.py` shell-test gate. New `alert_rule_lint_test.sh` adds a static parse/balance check over every `write_rule` expression. Residual: a full PromQL parser is not available offline; the bool guard remains the semantic authority. |
| `OBS-P1-002` | P1 | partially-fixed at base, guarded here | No duplicate UIDs/expressions at base (verified). `readme_ledger_drift_test.sh` already asserts the README alert-rule count against the committed `ALERT_CATALOGUE.yaml`, and `f1d2d0a` surfaced the authoritative firing-proof coverage. New linter derives the count from the rule source and rejects duplicates. |

Status maps to `partially-fixed` while the PR is a draft; a finding only becomes
`verified-fixed` after a human merges with green CI and its evidence requirements are met.

## Changes

| File | What changed |
|---|---|
| `bootstrap/90-alerting.sh` | New `falcon-relay-path-failures` warning rule (5m `for`, `increase(falcon_alert_relay_path_failures_total[15m]) > 0`) beside the existing total-failure rule. 9 added lines, comment-only + one `write_rule`. |
| `automation/validation/tests/alert_rule_lint_test.sh` | New offline linter: parses every `write_rule` in `bootstrap/90-alerting.sh`, prints the derived count, and fails on empty/unbalanced expressions or duplicate UIDs/identical expressions. Runs automatically in the `ci/validate.py` shell-test gate. |
| `automation/validation/tests/remediation_guards_test.sh` | Pins the new linter file and the per-path relay rule/metric so a future edit cannot silently drop them. |

Scope: three observability files; no workflow, dependency, schema, ledger, lockfile or
machine-artifact changes.

## Verification Performed

All commands ran on the lab `ci-runner` (172.23.128.51) against a clean LF worktree synced
with `scripts/lab-sync.ps1 -Repo falcon` and driven by the job API (`tools/lab_runner.py`).
Raw log: `remediation/PS-U10/verify.log` (commit `aef63ad`).

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| `HOME=/root FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` | lab `ci-runner` | 0 | `verify.log` - `validation_failures=0`; 31/31 shell suites incl. `alert_rule_lint_test.sh`; shell syntax 601 scripts; shellcheck 173 scripts; secret scan; edge-pin skipped |
| `bash automation/validation/tests/alert_rule_lint_test.sh` | lab `ci-runner` | 0 | `verify.log` - `PASS alert_rule_lint (derived_rule_count=78; unique_uids=78; unique_expressions=78)` |
| `bash automation/validation/tests/remediation_guards_test.sh` | lab `ci-runner` | 0 | `verify.log` - `PASS remediation_guards` |
| Negative control: append a rule re-using UID `falcon-relay-path-failures`, then run the linter | lab `ci-runner` | 1 (expected) | `verify.log` - `FAIL alert_rule_lint / duplicate rule uid(s): falcon-relay-path-failures` |
| Negative control: remove the `falcon-relay-path-failures` rule, then run the guards | lab `ci-runner` | 1 (expected) | `verify.log` - `FAIL: bootstrap/90-alerting.sh does not match /falcon-relay-path-failures/` |
| `git diff origin/main HEAD \| gitleaks stdin --redact --exit-code 1` | lab `ci-runner` (gitleaks) | 0 | `verify.log` - `no leaks found` (5,994 bytes scanned) |

Negative controls were run on the lab checkout and restored with `git checkout`/backup copy
before the gate run; `verify.log` records `restore_clean_exit=0`. The committed diff is
unaffected.

- Secret scan (gitleaks): **pass** - no leaks on the diff.
- Scope check: **pass** - only the three files above.
- Prometheus rule-file check: **not applicable** - there is no `config/prometheus/rules/`
  directory; the alert rules are Grafana-provisioned from `bootstrap/90-alerting.sh` via the
  API, so `promtool` has no artifact to check (recorded, not fabricated).
- Note: the lab worktree carries pre-existing CRLF-only differences in four
  `docs/phase8/reviews/*.md` files (finding `HYG-P2-002`); they are not in this diff.

## Evidence bundle

- `remediation/PS-U10/diff.patch` - SHA-256 `1523144ffc56278a1c54b5bf848c1f06095081db8a87d4b90f1ee4a00fcae565`
- `remediation/PS-U10/verify.log`
- `remediation/PS-U10/manifest.json`
- `remediation/PS-U10/pr_body.md`

## Risk and rollback

- Risk: **low**. One new Grafana alert rule (warning severity, 5m `for`) plus two offline
  test files that run in the existing gate. The rule can only fire on real per-path relay
  failures; it overlaps the existing critical total-failure rule only when both paths fail,
  which is intentional (different severity, same incident).
- Rollback: `git revert aef63addacb79888c0d540257a8b0470115c3102`.

## Review checklist

- [ ] Diff touches only the patch-set files (one rule + two test files; no runtime/data/service edits)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted (`verify.log`)
- [ ] Negative controls prove the new guards fail closed
- [ ] No secrets added; gitleaks clean on the diff
- [ ] The per-path warning rule is acceptable for page volume (warning, 5m `for`)
- [ ] Rollback is practical

## Open questions / deferred

1. **`OBS-P1-003` live firing proof - deploy + one-path fault injection.** The new rule is
   provisioned by `bootstrap/90-alerting.sh` and has no live firing proof at this commit
   (the audit's suggested validation). It requires a deploy and injecting a failure on one
   relay path (`ntfy_relay.py` per-path counter). Owner/ops action; recorded as
   `partially-fixed` until then. No proof was fabricated.
2. **Alt path disabled -> false warning.** `ntfy_relay.py` records an `alt` failure even when
   `MON_RELAY_ALT_URL` is unset (`publish_alt` returns False). The shipped unit sets the alt
   URL, so the lab is fine; if the owner later disables the independent path, the new warning
   would fire on every alert. A follow-up could record path outcomes only for configured
   paths. This is a relay behaviour change and is left as an owner decision, not guessed.
3. **Committed catalogue lags the rule source.** After deploy the live rule count becomes 78,
   while the committed `docs/phase9/ALERT_CATALOGUE.yaml` and the README count still record
   76 (they are generated from the live Grafana API and need a live regen). Ops action after
   deploy; the offline linter derives the true count from `bootstrap/90-alerting.sh` in the
   meantime.

## Not run

| Command | Reason |
|---|---|
| Live per-path fault injection | needs the provisioned rule deployed to Grafana and a deliberate relay-path failure; out of scope for a static repo-local PR, not fabricated. |
| `promtool check rules` | no Prometheus rule files in the repo; Grafana-provisioned rules only. |
