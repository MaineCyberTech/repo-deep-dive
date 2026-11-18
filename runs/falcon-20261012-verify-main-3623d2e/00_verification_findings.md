# Verification findings - post-merge re-audit

- Repo: `MaineCyberTech/falcon` @ `3623d2e` (main)
- Original run: `falcon-20261011-0416-full-f5cb7c9`
- Procedure: `runbooks/POST_MERGE_REAUDIT.md`
- All 126 original findings re-checked at the current main (per-finding evidence in `verification_log.md`; the per-group reports under `verification/`).

## New findings (this pass)

### from arch-feat-ctr-infra-res.md
### N-1 (live regression, P3) — `falcon_live_image_drift` regressed 0 → 1 (forwarder reference form)
- The audit note for ARCH-P2-002 recorded live drift 0; now `falcon_live_image_drift 1` in `/srv/falcon/textfile/falcon_services.prom` (fresh 20:04Z) and `automation/validation/live_image_pin_check.sh` prints:
  `DRIFT falcon-wazuh-forwarder sha256:4c47124a… [not in pins/images.lock]` (27 containers, drift=1; all others OK).
- Cause: the forwarder was recreated 2026-10-12T19:28:58Z (hardening round) with `Config.Image = sha256:4c47124a…` — a bare digest reference — so the read-only check cannot resolve it to the lock entry even though the digest **is** the locked `python:3.12-alpine` digest (`pins/images.lock`). The image bytes are correct; the reference form is what trips the check.
- Impact: the drift metric is wrong-positive and, more importantly, **no alert rule consumes `falcon_live_image_drift`** (metric-only residual documented in TB-8 / decision log 2026-10-01), so this is silent.
- Fix: recreate the forwarder via `automation/wazuh/forwarder-install.sh` (uses `python:3.12-alpine@sha256:4c47124a…`, the proper reference), or teach the checker to resolve bare-digest refs via the image ID; consider adding a rule on the metric.

### N-2 (live secret hygiene, P2) — live Wazuh compose hardcodes the current indexer password (world-readable)
- `/opt/wazuh-docker/multi-node/docker-compose.yml:66` contains the **current** Wazuh indexer password as a literal (verified by hash equality with the live `/opt/…/.env` and the running worker's env — values not reproduced). File mode `0644 user:user` on a `755` directory, so any local user/process can read the credential.
- The committed repo file is clean (`${INDEXER_PASSWORD}` at both lines, unchanged since `1c79d02`); commit `4c423d8` ("security: redact the hardcoded indexer passwords in the committed compose…") is **empty** — `git diff-tree -r 4c423d8` shows no tree change, so the claimed redaction never landed anywhere.
- Functional state today is consistent (running master/worker use the `.env` value; the incident "stale worker value broke alert shipping" is not recurring), but the live file exposes the credential and a future edit/recreate from it can reintroduce the stale-value failure.
- Fix: replace line 66 with `${INDEXER_PASSWORD}` (and ensure the `.env` interpolation is used by the compose chain), keep the file `0600` or the value only in the root-only `.env`, and re-verify the running worker after the next recreate.

### N-3 (doc, P3) — VPN runbook does not document the actual RES-P2-002 fix
- `docs/runbooks/VPN.md:193` still says the sockets are "enabled in multi-user.target (NOT sockets.target …; fixed 2026-09-30)" and does not mention `FreeBind=yes` / the 2026-10-11 ordering removal, which is what actually fixed the boot race. Update the row so operators don't rely on the superseded mechanism.

### N-4 (doc/ops note, P3) — decision-log healthcheck coverage claim overstates the live state
- `ledgers/decision_log.md:275` says the adopted stacks carry nnp + healthchecks "27/27 where applicable"; live healthchecks are on 19/27 (8 adopted containers have none — see CTR-P2-001). Suggest correcting the record and either adding the missing healthchecks or stating the explicit "no healthcheck" exception list (ntopng-style).

### from ci-bp-sc-sbom-det.md
### NEW-1 (P2, BP/CI) — `gh` CLI missing on the self-hosted runners; the Dependabot merge sweep silently no-ops
- **What**: `.github/workflows/dependabot-merge.yml:37` uses `mapfile -t PRS < <(gh pr list …)`. On the runners `gh` is not installed; the process-substitution failure does not fail `mapfile`/the step, so the array is empty, the script prints `no open dependabot PRs`, exits 0, and the run is reported **success**. The label gate (BP-P3-001) and the head-commit pin (CI-P2-001) can therefore never act, and nothing signals it.
- **Live evidence** (job logs, read via API; same pair of lines in every run):
  - 2026-10-12T13:13:42.359Z job 114827948932 (ci-runner, run 38254211113): `line 1: gh: command not found` → `no open dependabot PRs`
  - 2026-10-11T11:26:26.830Z job 114458579876 (lab-runner-2, run 38135559364): same
  - 2026-10-10T11:12:54.111Z job 114200200490 (edge-builder, run 38047609916): same
  - 2026-10-09T18:43:36.238Z job 113810472549 (lab-runner-2, run 37926819556): same
  - 2026-10-05T12:19:39.671Z job 111758692294 (lab-runner-2, run 37308749667): same
  - 2026-10-04T11:08Z job 111422936464 (ci-runner, run 37197723327): **no error** (gh worked then) — the breakage window starts ~2026-10-05.
- **Impact**: the compensating control that replaces plan-gated required review is non-functional and invisible; `BRANCH_PROTECTION.md:95` still asserts the gate is live. Combined with BP-P3-001 (never exercised), the failure mode is now observed in production.
- **Suggested fix**: fail closed if `command -v gh` is missing; install `gh` on the lab runners (or replace with API `curl` calls); capture a skip/merge exercise once a Dependabot PR exists.

### NEW-2 (P3, audit tooling) — deterministic re-run double-counts unpinned images from the untracked `review-package/`
- `tools/deterministic_checks.py` walks the working tree without honoring `.gitignore`; the generated, gitignored `review-package/` tree exists on the lab, so the SUPPLY check counted each `mct/compose` file twice: re-run title `[SUPPLY] 58 container image(s) without a digest pin` (evidence includes `review-package/mct/compose/*`) vs the **tracked** count of **29** (unchanged from the baseline).
- No repo regression here (the 29 tracked are the same set), but the machine re-audit baseline comparison must exclude `review-package/` (or the tool should skip generated/gitignored trees) to avoid false P3s in future runs.

### NEW-3 (P3, SBOM doc/code drift) — stale "unsigned" wording after the signing fix
- `automation/validation/sbom_hashes.sh:13-14,68,84` still says the manifest is NOT signed / "manifest unsigned" although `sbom/SBOM_MANIFEST.sha256.sig` now exists and CI verifies it; `verify_publication_chain.sh:112` still labels the 2026-09-29 archives "signed" while checking only SHA-256 bytes. Cosmetic but contradicts the new control (overlaps SBOM-P2-001 residual). Fix: refresh the comments/labels to distinguish integrity vs ed25519 authorship.

### from data-search-api-wh-dr.md
**NEW-1 (P2) — The encrypted offsite copy is not the copy the nightly job maintains.**
The 2026-10-12 crypt migration was executed manually (`OFFSITE_CRYPT=1`, 14:43→18:46:35Z, stamp updated) but the scheduled job still uses the plaintext remote. Evidence: `systemctl show falcon-backup.service -p Environment -p EnvironmentFiles` → empty; `ExecStart=/home/user/falcon-build/bootstrap/85-backup-job.sh`; `85-backup-job.sh` calls `80-offsite-backup.sh` without `OFFSITE_CRYPT`; `80-offsite-backup.sh:72,501` default to `spaces:${bucket}`; no `Environment=`/drop-in anywhere. Consequence: the next nightly run (2026-10-13 03:30Z) uploads the snapshot delta to the plaintext remote and refreshes `.offsite-last-success` on success, while the encrypted copy silently ages (and the plaintext copy keeps growing, contradicting DR-P2-002's remediation). Fix: set `OFFSITE_CRYPT=1` for the nightly job (unit `Environment=` or export in `85`), run one verified nightly on the crypt path, then retire the plaintext objects per `OFFSITE_ENCRYPTION_MIGRATION.md` step 4.

Note: the working tree is dirty (`config/grafana/dashboards/edge-fleet-overview.json`, `config/prometheus/edge-alerts.yaml` modified; two `.bak-edge-rules` untracked files) — presumed in-progress user work; not assessed and not touched.

### from hygiene-inv-ai-doc.md
### N-1 (P2) — Live working-tree mutation makes the mandated gate fail in place

- At verification start the tree was clean (`git status --short` empty, ~19:56Z). At **19:59:39Z** `config/grafana/dashboards/edge-fleet-overview.json` was rewritten in place (7 → 23 panels; pretty-printed; new edge sensor-health panels). It is uncommitted (`git status --short` → ` M config/grafana/dashboards/edge-fleet-overview.json`, still dirty at 20:14Z).
- Consequence: `python3 ci/validate.py` at the current working tree → `validation_failures=1`:
  `automation/validation/tests/readme_ledger_drift_test.sh: FAIL: README: panel count (expected '89', got '73')`.
- At the committed state the gate is green for this check: `git archive HEAD` extracted to /tmp and the same test run → `readme_ledger_drift_test_checks=28 readme_ledger_drift_test_failures=0` (HEAD panels = 73 = README).
- Interpretation: a concurrent live/cross-repo process (or another session) writes the adopted edge dashboard into the tracked tree; while in flight, the repo's working tree is not self-consistent and `ci/validate.py` is red. This is not a committed regression of the assigned findings, but it is an operational hazard (the "repo is clean at the audited commit" invariant can be silently broken between publications). Recommend: treat the in-flight write as a normal change (commit + rebind) or gate the live exporter to write only outside the tracked tree / through the documented adoption flow.

### N-2 (P3) — DOC-P2-001 fix left two docs describing the wiring as open

- `docs/security/RELEASE_PACK_VERIFICATION.md:81` still: "Recommendation 3 above (wire `pack_fidelity.py` into `verify_delivery.sh`) is still open" — contradicted by `verify_delivery.sh:41-52`.
- `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` still: "`pack_fidelity.py` … still local-only | **partial**" (accurate for CI, stale for the delivery build).

### N-3 (P3, minor) — Residual doctrine/skip-path edges from HYGIENE-P2-003 / INV-P3-005

- `docs/architecture/EVOLUTION_GUIDE.md:89` (step 7) still says the review package is "gitignored — do not commit, HYG-P1-001" without the declared-manifest exception that AGENTS/REPOSITORY/.gitignore now carry.
- `automation/validation/check_publication_equality.py:187-191` keeps a fail-open skip ("post-publication ancestry restriction skipped") for the case where `review-package/MANIFEST.sha256` is absent; the tracked manifest makes this path unreachable in practice, but no test pins it closed (the suite `publication_equality_test.sh` has no absent-manifest case).

### from orch-chain-test.md
**NEW-1 (P3, CI/CHAIN/TEST) — `external-smoke.yml` still carries stale Access claims.**
`external-smoke.yml:26-28` ("this gate asserts the public Cloudflare Access posture (302 ->
cloudflareaccess.com) … so it stays on hosted") and `:71` ("iris/soc: must be 302 to
cloudflareaccess.com (Access still enforcing)") contradict the updated header (`:3-9`) and the actual
behavior (runs on `[self-hosted, lab]`, accepts any 302). Fix: delete/refresh both lines to match the
availability-only scope and point at the DO watcher. Evidence: file at `3623d2e`; `git blame` shows both
blocks unchanged since `6a682f2c`/`45d9c3e8`.

**NEW-2 (P3, ORCH) — `--profile` fix leaves a contradictory INDEX.**
With the new `--profile` option, `tools/full_domain.py` records the profile in the manifest but
`render_index` still hardcodes `- Profile: base` (`:240`, `:421`), so a `--profile falcon-lab` run would
emit an INDEX contradicting its own manifest; `check_run.sh` would then require falcon-lab lens reports
(`:47-52`) that the driver does not produce. Fix: render the manifest profile and/or emit the
falcon-lab shape (this is the residual of ORCH-P2-002).

**Observation (not a repo defect) — live working tree diverges from `3623d2e`.**
`config/grafana/dashboards/edge-fleet-overview.json` is modified in the working tree (23 panels vs 7
committed), which fails `readme_ledger_drift_test.sh` locally; the committed tree and CI at `3623d2e`
are clean/green. Treat as another session's in-flight work.

---

### Cross-checks run (read-only)

- `git archive 3623d2e | tar -x` → `/tmp/opencode/falcon-verify-3623d2e`; `FALCON_EVIDENCE_OPTIONAL=1
  python3 ci/validate.py` → `validation_failures=0` (note: on the lab host the absolute evidence paths
  resolve; CI's own log shows `0 captures, 1136 external skipped`).
- GitHub API (token from `/home/user/.env`, never printed): validate run `38299786463` at `3623d2e`
  success; external-smoke last run `38156466921` success (2026-10-11).
- DO host over SSH: watcher sha == repo, cron `*/5`, posture state/log; non-owner probes.
- Live lab: `nft` ruleset vs repo file (`diff` identical), tunnel timer/service/metric, Traefik container
  sha vs repo, `docker inspect` docker.sock scan.

### from perf-obs-notif.md
| # | Sev | Finding | Evidence |
|---|---|---|---|
| NF-1 | P3 | `docs/runbooks/CAPACITY_AND_TELEMETRY.md` was not updated by the 24/30 GiB threshold change (commit e094473 landed after the 362b342 docs pass): it still says the guard triggers below **10 GiB** on `/srv/falcon` (:39-40), calls it a **15 GiB warning band** (:21) and `falcon-data-lv-low` warns below **15 GiB** (:50), says "the disk guard watches `/srv/falcon` only" (:260) and "10 GiB / 20 GiB" (:273-274), and "keeps the newest 3" in the remediation section (:275-277). Live/repo are 24 GiB guard / 30 GiB rule / both LVs / keep-2. | `CAPACITY_AND_TELEMETRY.md:21,39-40,50,260,273-277` vs `disk_guard.sh:22-25`, `90-alerting.sh:540-542`, live journal `threshold=25165824KB` |
| NF-2 | P3 | The 120 s metrics cadence is not reflected in docs/units: `config/systemd/falcon-metrics.timer:1` description still "every minute"; `docs/runbooks/RUNTIME_AND_SCHEDULE.md:12` table cadence "1 min", `:81`/`:97` mention the 1-minute cadence, `:178` "Keep the 1-minute metrics cadence". | `config/systemd/falcon-metrics.timer:1-6`; `RUNTIME_AND_SCHEDULE.md:12,81,97,178`; live timer delta 121 s |
| NF-3 | P3 | `automation/wazuh/migration/README.md:17-19` still documents the bundle as living at `/var/tmp/wz-migration/wazuh-stack.tar` (and PVE copies) although it was relocated 2026-10-11 to `/srv/falcon/archive/wz-migration/` (review by 2027-01-31). | `automation/wazuh/migration/README.md:17-19` vs `/srv/falcon/archive/wz-migration/README.md` (live) |
| NF-4 | P3 | The Wazuh/IRIS memory-cap + hardening overlays exist only in the live `/opt` trees (`docker-compose.hardening.yml`, applied via `docker update`); the repo's vendored `automation/wazuh/multi-node/` compose has no `mem_limit`, so a repo-driven recreate would lose the caps added for PERF-P2-001. Two containers also remain uncapped (`wazuh-cloudflared`, `falcon-wazuh-forwarder`). Cross-ref CTR-P2-001 / ARCH-P2-002. | `grep mem_limit automation/wazuh/` = none; live `/opt/wazuh-docker/multi-node/docker-compose.hardening.yml`, `/opt/iris-web/docker-compose.hardening.yml`; `docker inspect` HostConfig.Memory=0 for the two containers |
| NF-5 | P3 | The removed `ntfy-auth` middleware is still described/rotated by runbooks and its users file is still mounted/generated: `docs/phase7/runbooks/CERTIFICATE_AND_SECRET_ROTATION.md:47` ("middleware `ntfy-auth`"), `docs/runbooks/ACCESS_AND_ACCOUNTS.md:48,105` ("currently unused"), `compose/central/docker-compose.yml:35` (ro mount), `bootstrap/50-secrets.sh:87-97` (generation). | paths as listed; live Traefik dynamic.yml has no such middleware |
| NF-6 | P3 | No automated check compares the provisioned rule set to `docs/phase9/ALERT_CATALOGUE.yaml` at id level: `alert_rule_lint_test.sh` is script-only (derived count, dup uids, expression balance) and `readme_ledger_drift_test.sh` compares README **counts** to the catalogue. A same-count rule substitution in `bootstrap/90-alerting.sh` would leave the catalogue stale and pass both tests (the catalogue header's "cannot drift" claim stays unenforced). | `automation/validation/tests/alert_rule_lint_test.sh:1-24,60-75`; `automation/validation/tests/readme_ledger_drift_test.sh:64-77` |
| NF-7 | P3 (observation) | `export_monitor_metrics.sh` `site_get()` emits `printf: write error: Broken pipe` when the DO site's metrics payload is large (awk exits at first match). Cosmetic only (script is `set -u`, no pipefail) but it litters the backup journal (6 lines in the 2026-10-12 run). | `automation/validation/export_monitor_metrics.sh:439`; `journalctl -u falcon-backup.service` 2026-10-12T04:22:43Z |

*No regressions were found in PERF/OBS/NOTIF:* the remediations that landed since the audit
(root-LV margin, threshold raise, rule additions, exporter exclusion, cadence change, CI caching,
middleware removal) are all present and functioning at `3623d2e`; the still-open items are the
audit's own residual clauses, not new breakage. One caveat on evidence windows: the lab journal
was vacuumed on 2026-10-12T04:30Z, so relay-noise comparisons are limited to entries after
2026-10-11T00:08Z.

### Method / commands (read-only)
- Repo: `git log/diff f5cb7c9..3623d2e`, file inspection (paths above), CI run inspection via the
  GitHub API.
- Live: `df -h`, `vgs`, `systemctl status/list-timers --failed`, `journalctl -u falcon-disk-guard|
  falcon-alert-relay|falcon-backup|falcon-metrics`, `docker inspect/ps/logs`, `fuser`,
  `/srv/falcon/textfile/*.prom`, Grafana provisioning/alert APIs (`--cacert` + `--resolve`),
  OpenSearch `_cluster/settings` GET.

### from priv-ir-rel-evol.md
**NF-1 [P3][REL/INV] Live tree not clean at verification time (concurrent in-flight changes).**
At 20:08Z `git status --porcelain` showed 1 modified file; at 20:18Z it showed 4: `config/grafana/dashboards/edge-fleet-overview.json` (mtime 19:59:39Z; 24 panels vs 7 committed; semantically equal to the live Grafana dashboard `falcon-edge-fleet`, updated 2026-10-12T20:00:01Z), `.github/workflows/external-smoke.yml`, `automation/validation/sbom_hashes.sh`, `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md` (mtimes 20:17–20:18Z). All post-date the last commit (19:45:43Z) and match a concurrent active session (in-flight files in `/tmp/opencode`). This breaks REL-P2-001's "live tree == remote main" property while uncommitted; whichever agent owns the changes must commit them (and rebind) or revert. Evidence: `git status --porcelain`; `stat`; Grafana API diff.

**NF-2 [P3][IR/EVID] No evidence captures for the 2026-10-11 post-reboot verification / PR #55 batch.**
`ledgers/decision_log.md:268` records "post_reboot_verify.sh 59/0" with no capture ID; `evidence/raw/` has no 2026-10-11 captures before 21:20Z (`find evidence -newermt '2026-10-11 05:00' ! -newermt '2026-10-11 06:30'` → none); `ledgers/evidence_index.csv` and `evidence/MANIFEST.sha256` list only the two 21:20Z credential-rotation captures for that date. The doctrine (`AGENTS.md` standard flow; `INCIDENT_RESPONSE.md` §10) expects captured commands/results. Recommendation: capture (or re-run and capture) the read-only boot checks and attach them to the record.

**NF-3 [P3][PRIV/DATA] Wazuh indexer retention is live-only (not reproducible from the repo).**
`wazuh-retention` (90 d) and `wazuh-monitoring-retention` (30 d) exist only on the live cluster (applied via API/console 2026-10-11, description "owner default 2026-10-11"); no repo script/config declares them (grep for `wazuh-retention`/`wazuh-monitoring-retention` → only `RETENTION_MATRIX.md` and the decision log; the central `config/opensearch/*.json` declarations have no Wazuh-indexer equivalent). The vendored `mct/runbooks/index-retention-policy.md:7-9` documents the upstream 30 d alerts policy — stale vs live 90 d. A rebuild/re-import would lose the owner-decided retention. Recommendation: add an idempotent provisioning script (or declared policy JSON + bootstrap step) for the Wazuh indexer ISM policies.

**NF-4 [P3][PRIV/DOC] Stale "owner decision pending" for IRIS retention.**
`docs/privacy/DATA_GOVERNANCE.md:63` says the live IRIS retention entry is "(owner decision pending)", but the owner decided 365 d on 2026-10-11 (`RETENTION_MATRIX.md:47`; `decision_log.md:271`). One-line correction needed.

