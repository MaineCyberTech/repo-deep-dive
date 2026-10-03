# Remediation PR

<!-- Opened as a DRAFT by the repo-deep-dive remediation runner. A human reviewer merges. -->

## Summary

Catch-all observability remediation for the unassigned `OBS` findings from the
2026-10-03 audit run. It gives the self-hosted OTLP collector a real **retained**
trace sink (rotating OTLP-JSON on a dedicated volume, with a one-shot init that
makes the volume writable for the non-root collector), commits **SLOs with error
budgets and burn-rate alerts** against the metrics the service already exports,
and documents **metric restart semantics** so dashboards do not misread a process
recycle. No application/runtime code, CI workflow, dependency or lockfile change.

- Audit run: `20261003-0018-main-59e12b9`
- Patch set: `PS-U10` — Unassigned OBS findings (catch-all)
- Repo / base: `MaineCyberTech/snowride` @ `59e12b9b2259ab21ae56113b214160dd1150c5ba`

## Findings addressed

| Finding | Severity | Status | Note |
|---|---|---|---|
| `OBS-P2-001` | P2 | open -> **partially-fixed** | The collector no longer exports traces only to `debug`. A `file/traces` exporter retains OTLP-JSON on the `otel-traces` volume with bounded rotation (64 MB / 5 backups / 7 days); a verified functional probe (`OTLP POST 200` -> `grep` match in `traces.json`) proves a known request is retrievable after the fact. The dependency `OBS-P1-001` (committed alert schedule) is untouched, so this stays partially-fixed until the draft PR merges. |
| `OBS-P2-002` | P2 | open -> **partially-fixed** | `docs/runbooks/SLO.md` declares SLIs/SLOs for availability, session/stream/ledger integrity, run-submission durability, purchase processing, latency and client frame/boot budgets, with error-budget burn-rate alerts. The alert **transport** is still host-side and owned by `OBS-P1-001`; this commits the agreed paging basis, so it is partially-fixed pending merge. |
| `OBS-P3-001` | P3 | open -> **verified-fixed** | `docs/runbooks/OBSERVABILITY.md` documents that counters are process-local, that snapshots exist only when `METRICS_SNAPSHOT_INTERVAL_MS > 0`, and how to read rate/trends reset-aware across a restart. The snapshot timer was already explicit in production compose; this closes the documentation half of the finding at the commit. |

## Changes

| File | What changed |
|---|---|
| `infra/otel/collector-config.yaml` | Added `file/traces` exporter (`/var/lib/otel/traces.json`, rotation `max_megabytes: 64`, `max_days: 7`, `max_backups: 5`) and added it to the traces pipeline alongside `debug`. |
| `infra/compose/docker-compose.yml` | New one-shot `otel-init` service (busybox pinned) that `chown`s the `otel-traces` named volume to `1001:1001`; `otel` mounts the volume and `depends_on: service_completed_successfully`; declared the top-level `otel-traces` volume. |
| `docs/runbooks/OBSERVABILITY.md` (new) | Trace topology, retention/read-back, non-root write path, and metric restart/snapshot semantics (`OBS-P2-001`, `OBS-P3-001`). |
| `docs/runbooks/SLO.md` (new) | SLI definitions from real `/metrics` series, objectives/error budgets, burn-rate alerts, ownership and open questions (`OBS-P2-002`). |
| `docs/runbooks/README.md` | Added the two new runbooks to the index (inserted near the top of the table). |

Coordination: `PS-U07` (draft #17) appends a `RELIABILITY_DRILLS.md` row at the
**end** of the same runbook table; this PR inserts near the **top**, so the
`README.md` hunks are disjoint. `P1-4` (#10) rewrites `docs/runbooks/INCIDENT.md`;
this PR does **not** touch `INCIDENT.md`. `OBS-P2-001` links to `OBS-P1-001`'s
scope but changes no host schedule or alert config.

## Verification Performed

Run in a clean LF **bundle clone** on the ci-runner lab
(`/srv/work/snowride-ps-u10`, `core.autocrlf` unset) at commit `7c61d27`.
The lab has the pinned images available and Docker 26.1.5 / Compose 2.26.1.

| Command | Runner | Exit | Evidence |
|---|---|---|---|
| relative-link existence check for changed docs | ci-runner | 0 | `linkcheck_broken=0` (`remediation/PS-U10/verify.log`) |
| `otelcol validate` on the collector config (pinned image) | ci-runner | 0 | no output; config accepted |
| `docker compose -f infra/compose/docker-compose.yml config --quiet` | ci-runner | 0 | compose valid |
| functional retention probe: `compose up otel-init otel`; `POST /v1/traces`; read volume | ci-runner | 0 | `otel_init_state=exited exit=0`, `otlp_post_http_code=200`, `grep -c ps-u10-retention-probe traces.json = 1` |
| `npm ci` | ci-runner | 0 | packages installed |
| `npm run lint` | ci-runner | 0 | 0 errors, 1 pre-existing warning in `apps/web/components/game/Home.tsx` |
| `npm test` | ci-runner | 0 | 131 test files, 873 tests passed |
| `git status --short` after gates | ci-runner | 0 | clean |
| `gitleaks detect --no-git --redact --no-banner --source <changed file>` x5 | ci-runner | 0 | no leaks (`remediation/PS-U10/gitleaks.log`) |
| `gitleaks detect --no-git --redact --source .` | ci-runner | 1 | 19 pre-existing `generic-api-key` fixture hits under `evidence/**` + `scripts/bundle-secret-gate.mjs`; **none** in this diff |

- Secret scan (gitleaks): **pass** — all five changed files clean; the 19
  full-tree hits are the pre-existing audited fixtures also recorded by the
  sibling PS-U03/PS-U04/PS-U05/PS-U07/PS-U08/PS-U09 runs.
- Scope check (files within patch set): **pass** — `PS-U10` declared no file
  list; the diff is limited to `OBS` observability config and runbook docs.

## Evidence bundle

- `remediation/PS-U10/diff.patch` — SHA-256 `9b55cbfeb7f6c48c2dd7317745fab3060f3de0225a23fed9068125383e92e985`
- `remediation/PS-U10/verify.log` — SHA-256 `41411a94f1df97eed8486fe6d4e5991f5b0d170d7465fa2853abf09075ee266d`
- `remediation/PS-U10/gitleaks.log` — SHA-256 `7fefc4f3cba53c69b6ce3e73c7047854fdecc93fecc56eb16487831716cc8fba`
- `remediation/PS-U10/manifest.json`

## Risk and rollback

- Risk: **low**. Config + docs only; the collector change is additive (the
  existing `debug` exporter stays) and the trace sink is disk-bounded. The
  `otel-init` sidecar adds one pinned image but no new network surface
  (internal-only) and runs with `cap_drop: ALL` + only `CAP_CHOWN`.
- Rollback: `git revert 7c61d27cea59c1b5e5004fb1f14172d1e76e8e32`. Dropping the
  named volume reclaims the retained traces.

## Review checklist

- [ ] Diff touches only the patch-set files (+ tests/docs)
- [ ] Every finding in the set is addressed or explicitly deferred with a reason
- [ ] Verification commands actually ran; results pasted, not asserted
- [ ] No secrets added; gitleaks clean
- [ ] Tests added/updated for the fix where applicable
- [ ] Rollback is practical

## Definition of done (for this set)

- Traces are retained and queryable after the fact, not debug-only (`OBS-P2-001`).
- SLOs/error budgets/burn alerts are committed against real metrics (`OBS-P2-002`).
- Metric restart semantics are documented for dashboards (`OBS-P3-001`).

## Open questions

1. **`OBS-P2-001` real backend.** A rotating file sink is the minimal retained
   option and is verifiable here. A hosted trace backend (Tempo/Jaeger/SaaS) with
   its own retention and query UI is still the better long-term fix and remains a
   product/operator decision; the file sink is the committed interim.
2. **`OBS-P1-001` alert transport.** `SLO.md` defines the burn-rate rules, but
   they only page once the alert schedule/transport is committed in-repo (that is
   `OBS-P1-001`'s scope, separate PR). Do not assume automatic paging until then.
3. **`SLO.md` S9 boot target** (`median <= 2500 ms`) is an initial proposal, not a
   ratified product number; confirm against the device matrix and RUM baseline.
