# Observability contract for the pack

The audit pipeline is only trustworthy if a failed or stale run is observable.
This page defines the machine-readable outputs, exit codes, and freshness signal
for the **repo-deep-dive** tools. Findings referenced here are from audit run
`20261003-0018-main-7bac320`.

## Exit-code taxonomy

| Command | `0` | non-zero |
|---|---|---|
| `tools/lint_pack.sh` | every pack check passed | one or more checks failed (fail closed) |
| `tools/self_test.sh` | every tool check passed | one or more failed |
| `tools/check_run.sh <run>` | prints `PASS` | prints `FAIL` and exits non-zero |
| `tools/deterministic_checks.py <repo>` | checks ran; findings written | `2` = bad repo path |
| `tools/collect_findings.py <run>` | findings aggregated | non-zero on unreadable input |
| `tools/risk_score.py <run>` | score printed | non-zero on unreadable input |
| `tools/render_dashboard.py <run>` | summary printed | non-zero on unreadable input |

Note: `deterministic_checks.py` exits `0` even when it finds issues — findings
are **data**, not a process failure. Gate on the produced JSON, not the exit
code, when you want to fail on a finding class.

## Structured output

- `tools/deterministic_checks.py <repo> -o <outdir>` writes
  `deterministic-findings.json` (`run`, `generated` UTC timestamp, `counts`,
  `findings[]`) plus `lens_deterministic.md`. Parse the JSON instead of scraping
  stdout.
- Each run's `audit_manifest.json` records `run` and `scaffolded_at`
  (ISO-8601 UTC), the binding used for freshness.
- `tools/render_dashboard.py <run> --write` emits `dashboard.md`,
  `dashboard.html`, and `pr_comment.md` into the run folder.

## Freshness signal

The scheduled/archived runs must not silently go stale. Compute the age of the
newest archived run from its manifest:

```bash
python3 - <<'PY'
import glob, json, datetime
manifests = [json.load(open(p, encoding="utf-8-sig")) for p in glob.glob("runs/*/audit_manifest.json")]
newest = max(manifests, key=lambda r: r.get("scaffolded_at", ""))
ts = datetime.datetime.fromisoformat(newest["scaffolded_at"])
age = (datetime.datetime.now(datetime.timezone.utc) - ts).days
print("newest run: %s age_days: %d" % (newest.get("run"), age))
raise SystemExit(0 if age <= 7 else 1)
PY
```

A non-zero exit means no run has completed within the freshness window and
should raise an external alert. (This complements, and does not replace, the
fail-closed workflow change for finding **OBS-P2-002** in patch set PS-003.)

## Dashboard and delta retention

- A completed run commits its dashboard and PR-comment snippet with the reports
  (see `runs/README.md`).
- Run-over-run diffs are ephemeral: regenerate with
  `tools/diff_runs.py <previous-run> <current-run>`; do not commit the delta.

This closes finding **OBS-P3-003** by making the retention rule explicit; the
two `runs/20260930-*` runs predate the policy and are noted in `runs/README.md`.
