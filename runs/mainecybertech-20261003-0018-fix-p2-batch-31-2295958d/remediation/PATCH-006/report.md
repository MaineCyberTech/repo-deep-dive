# PATCH-006 (OBS-P2-001) — no change required: already implemented at the PR base

## Outcome

No commit, branch, or PR was created for this patch set.

`OBS-P2-001` ("Prometheus alert rules are not routed anywhere") is **already fully
fixed on the remediation base branch `fix/p2-batch-31`** (`11746adc`). The fix came
from the prior incident-readiness remediation **IR-P0-003**, whose commits are
ancestors of the base:

| Commit | Subject | Date |
|---|---|---|
| `e59d875d53a7f97adb2dbad550405b5b02e2e0df` | `fix(alerting): deploy Alertmanager with an off-box dead-man's switch` | 2026-10-02 |
| `5e97b660cd4eec329544014fd726cbb0f3040f44` | `fix(alerting): actually deploy and configure the dead-man's switch (IR-P0-003)` | 2026-10-02 |
| `e84c8ee98033adcd101aeb6dd9aa9f7ada2dafa` | `fix(alerting): make the Alertmanager config actually loadable and proven running` | 2026-10-02 |

`e84c8ee9` is confirmed an ancestor of `origin/fix/p2-batch-31` (`11746adc`).

## Why the audit still reported it

The audit ran against a **stale local clone**: `C:\temp\mainecybertech` was at
`2295958d`, a divergent line that does not contain the IR-P0-003 merge. At
`2295958d` the audit's evidence is correct (no `alerting:` block, no Alertmanager
service). The remediation target (`origin/fix/p2-batch-31`) is 47 commits ahead of
the merge base and already carries the fix, so PATCH-006 has nothing left to add.

## What the base already contains (satisfies every part of the finding's fix)

- `infra/digitalocean/prometheus.yml` — `alerting:` block forwarding to
  `alertmanager:9093`.
- `infra/digitalocean/docker-compose.yml` — digest-pinned `alertmanager:v0.28.1`
  service, internal-only, health-checked, with `alertmanager-data` volume, and
  `prometheus.depends_on.alertmanager: service_healthy`.
- `infra/digitalocean/alertmanager.tmpl.yml` — routing tree with `critical` and
  `watchdog` receivers; Watchdog routed to an **external** dead-man's-switch URL
  (`ALERTMANAGER_WATCHDOG_WEBHOOK_URL`), values supplied via env only (no secrets
  in the repo).
- `infra/digitalocean/prometheus.rules.yml` — `Watchdog` (`expr: vector(1)`)
  liveness rule plus service/error-rate/RLS rules.
- `.github/workflows/deploy-do.yml` — writes the `ALERTMANAGER_*` values into the
  droplet `.env`, copies `alertmanager.tmpl.yml`, and fails production deploys when
  the watchdog URL is empty.

## Verification (real output in `verify.log`)

Run in the lab (`ci-runner`, LXC 200, `172.23.128.51`) against the synced PR base
`11746adc`:

| Command | Exit | Result |
|---|---|---|
| `docker compose -f docker-compose.yml config` (with dummy env) | 0 | valid; `alertmanager` service rendered |
| `promtool check rules prometheus.rules.yml` (prom/prometheus:v3.5.1) | 0 | `SUCCESS: 6 rules found` |
| `promtool test rules prometheus.rules.test.yml` | 0 | `SUCCESS` |
| render `alertmanager.tmpl.yml` + `amtool check-config` (prom/alertmanager:v0.28.1) | 0 | `SUCCESS`, 3 receivers, 1 inhibit rule |

## Guardrails

- No fabricated diff, no duplicate PR, no secrets committed (`gitleaks` not run
  because there is no diff; nothing was pushed).
- Original audit findings were not modified; status reconciled via
  `tools/remediation_status.py`.
