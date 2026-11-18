# Post-merge verification re-audit — ORCH / CHAIN / TEST

- **Target repo:** `/home/user/falcon-build` @ `3623d2e` (main) — read-only.
- **Original run:** `falcon-20261011-0416-full-f5cb7c9` (pack: `/tmp/opencode/repo-deep-dive-remote` @ `19e7532`).
- **Findings re-checked:** 10 (ORCH ×4, CHAIN ×3, TEST ×3).
- **Date:** 2026-10-12.
- **Procedure:** `POST_MERGE_REAUDIT.md` §3 (verification lens; repo + live re-check, no fabrication).

Working-tree note: during verification the repo working tree was **not clean** — another session had an
uncommitted `config/grafana/dashboards/edge-fleet-overview.json` (459+/60−; 23 panels vs 7 committed).
That change is unrelated to these findings and made the local `readme_ledger_drift_test.sh` fail; the
committed `3623d2e` tree (extracted with `git archive`) passes all gates, and CI run `38299786463` at
`3623d2e` is green. All repo-state checks below use the committed tree.

## Verdict table

| ID | Sev | Verdict | Basis |
|---|---|---|---|
| CHAIN-P2-001 | P2 | **closed** | Access enforcement now asserted from a non-owner vantage by the DO watcher (repo-versioned, deployed, cron */5, live posture OK). Residual stale text in `external-smoke.yml` → new finding. |
| CHAIN-P3-001 | P3 | **still-open** | Shuffle `docker.sock` mounts removed/guarded (closed half); public routers still carry no origin auth (live config == repo; lab probes reach origin). |
| CHAIN-P3-002 | P3 | **still-open** | Tunnel-ingress drift check landed and is live/in-sync; **no** live-vs-repo check for the nftables ruleset (the wg0 narrowing) — the finding's core risk remains uncovered. |
| ORCH-P2-001 | P2 | **still-open** | Committed 2026-10-05 run still says GO WITH CONDITIONS with P0 ×1 open; no appended reconciliation note; newer runs not published there; pointers only refreshed. |
| ORCH-P2-002 | P2 | **still-open** | `--profile` added to the pack driver (partial); falcon-lab manifest shape (lens IDs/targets/status, waves) still not emitted; `INDEX.md` hardcodes `Profile: base`. |
| ORCH-P3-001 | P3 | **closed** | Consumer regex broadened to accept repo-prefixed run ids; reproduced: the current run id passes the lifecycle check. |
| ORCH-P3-002 | P3 | **still-open** | 20261009 artifact still has report `verified-fixed` vs findings-array/register `open`; no dated reconciliation note; no `check_run.sh` report-vs-array cross-check. |
| TEST-P2-001 | P2 | **closed** | Same fix as CHAIN-P2-001 (DO watcher is the external-vantage assertion); residual stale text → new finding. |
| TEST-P3-001 | P3 | **still-open** | Live CI at `3623d2e`: `PASS evidence integrity (0 captures, 1136 external skipped in CI)`; all metas still absolute lab paths; no split check. |
| TEST-P3-002 | P3 | **still-open** | Reader still reads only the first 15 lines; unchanged and harmless (the line-26 marker belongs to the skip fixture and works). |

No regressions were found in these three areas.

---

## Per-finding detail

### CHAIN-P2-001 — closed (Access enforcement now asserted externally)

Original claim: the only automated Access-posture check (`external-smoke`) accepts any 302 from the lab
vantage, so an Access outage/policy removal for iris/soc would be undetected.

Fix (cite):
- `automation/alerting/do_watcher/watch.sh:56-97` — new public-posture section; `check_access()` at
  line 67 asserts `302` **and** `location` contains `cloudflareaccess.com` for falcon/iris/soc, and
  alerts to the independent ntfy on failure (lines 82-94). Comment at lines 56-59 states the vantage
  rationale (this host is not the owner network, so the challenge is observable).
- Deployed and live-verified: `/opt/falcon-watcher/watch.sh` sha256
  `239d3a4c…` == repo `automation/alerting/do_watcher/watch.sh`; cron `*/5 * * * *` on `mct-portal-dev`
  (`root@138.197.105.82`); `/var/lib/falcon-watcher/posture` fresh at 2026-10-12 20:10:02Z; log tail:
  `posture ok: https://falcon|iris|soc.mainecybertech.us/ -> 302 (Cloudflare Access)`.
- Vantage contrast (live): from the DO host all three hostnames 302 →
  `mainecybertech.cloudflareaccess.com`; from the lab, iris → `/dashboard` and soc → `/app/login`
  (owner-IP bypass), i.e. the external assertion is exercised where the lab one cannot be.
- `external-smoke.yml:3-9` header now documents the job as availability-only and points at the watcher.

Residual (filed as NEW-1): `external-smoke.yml:26-28` (comment still claims the job "asserts the public
Cloudflare Access posture … stays on hosted") and `:71` (job summary still says "iris/soc: must be 302
to cloudflareaccess.com") were not updated and contradict the new header.

### TEST-P2-001 — closed (same fix; residual NEW-1)

Identical substance and evidence as CHAIN-P2-001. The workflow no longer claims the assertion in its
header, and the enforcement assertion now exists (DO watcher, live). Residual stale comment/summary in
`external-smoke.yml` → NEW-1.

### ORCH-P2-001 — still-open

- Committed record unchanged: `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md:3`
  `Verdict: **GO WITH CONDITIONS**`; `findings.json` = P0 ×1, P1 ×7, all 34 findings `open`; manifest
  profile `focused-security-supply-chain-ci`, promptCount 4.
- Canonical pack run for the same audit (`runs/falcon-20261005-full-main-e267ce1/RELEASE_GATE.md`) says
  `Decision: **NO-GO**` — the contradiction stands.
- No reconciliation note: the run folder contains only the original 12 files; no dated/appended file and
  no "superseded/reconciled" text (grep over the folder).
- Newer canonical runs are still not published under `docs/audits/repo-deep-dive/` (only up to
  `20261005-0354-…`), so the newest durable in-repo record remains the P0-bearing run.
- Mitigation only: run pointers refreshed to the pack runs — `AGENTS.md:86`, `README.md:11`,
  `docs/RELEASE_GATE.md:16`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:40` (commit `362b342`).
- No publish-time gate in the falcon repo (`ci/validate.py` has no check of `docs/audits` run gates).

What remains: append the dated reconciliation note (append-only) to the committed run and/or publish
the newer runs to supersede it; add the publish-time check that a P0-bearing run cannot emit
GO/GO WITH CONDITIONS while unresolved.

### ORCH-P2-002 — still-open (partially addressed)

- Landed: pack commit `7b20626` added `--profile` (`tools/full_domain.py:717-720` current) and
  `manifest_for(..., profile=…)` records it (`:200-203`, `:219`); `tools/check_run.sh:47-52` requires the
  falcon-lab lens reports when `profile == falcon-lab`; the stale "run ids must start YYYYMMDD" comment
  was corrected (`:185-191`).
- Not landed: the falcon-lab manifest shape. `"lenses": [d["area"] for d in domains]` is unchanged
  (`full_domain.py:224`) — area codes, not lens IDs/targets/status; no waves; the domain set is still the
  base 42-prompt master runner (explicit comment at the `--profile` argument). `render_index` hardcodes
  `- Profile: base` (`:240`, `:421`), so a non-base run's INDEX contradicts its manifest (NEW-2).
- Current falcon run: `runs/falcon-20261011-0416-full-f5cb7c9/audit_manifest.json` profile `base`,
  promptCount 42, while `profiles/falcon-lab.manifest.json:29-34` documents 46 prompts + 5 lens overlays
  with targets. No manifest-shape validation against the falcon-lab example.

### ORCH-P3-001 — closed

- `automation/validation/audit_run_lifecycle.sh:120-124`: the run-id check now accepts an optional repo
  prefix: `^([a-z0-9][a-z0-9-]*-)?[0-9]{8}-[0-9]{4}-` (comment cites ORCH-P3-001).
- Reproduced against the current consumer: a scratch root containing the run folder
  `falcon-20261011-0416-full-f5cb7c9` → `PASS falcon-20261011-0416-full-f5cb7c9 (external)`,
  `check_failures=0`. The regex also accepts the existing published ids.
- Pack side: `full_domain.py:185-191` comment now documents the accepted prefix (commit `7b20626`).
- Note: no publish-time regex assertion was added; closure is consumer-side acceptance (which was one of
  the finding's two allowed fixes).

### ORCH-P3-002 — still-open

- `runs/falcon-20261009-2117-full-08e20d1/_domains/02_architecture_runtime_topology.json` still
  contradicts itself: report text `### ARCH-P2-001 … (verified fixed)` with `- Status: verified-fixed`,
  while the same file's findings array has `"id": "ARCH-P2-001"` … `"status": "open"` (line 35).
- Registers still carry `open`: `runs/falcon-20261009-2117-full-08e20d1/follow_up_register.md:34` and
  `runs/falcon-20261011-0400-verify-main-584e1a3/follow_up_register.md:34`.
- No dated reconciliation note in either run (pack git history for the 20261009 folder = creation only).
- `tools/check_run.sh` (current) has no domain-report-vs-findings-array status cross-check — only
  required files, ID consistency/duplicates, and status-vocabulary checks (`:54-133`).

### CHAIN-P3-001 — still-open (Shuffle half fixed; origin-exposure half remains)

- Fixed half: `mct/compose/docker-compose.shuffle.yml:48-51` and `:90-93` — the two
  `/var/run/docker.sock` mounts are commented out with a dated note (removed while Shuffle is staged;
  re-add only behind a scoped socket proxy + recorded exception). Live: `0` running containers mount
  `docker.sock`; no Shuffle containers exist.
- Remaining half (anonymous origin exposure): `config/traefik/dynamic.yml` — `falcon-grafana` (`:89-95`),
  `iris-public` (`:114-119`) and `soc-wazuh` (`:129-134`) still carry only
  `[sec-headers, public-rate-limit]`, no origin auth; `ntfy-auth` was removed as dead config (`:26-28`).
  Live Traefik mounts the repo file byte-identically (`sha256 3ed78f94…`, checked inside
  `falcon-central-traefik-1`). Lab probes reach origin: iris → `302 /dashboard`, soc → `302 /app/login`.
  So an Access bypass still leaves only the application login on iris/soc.

### CHAIN-P3-002 — still-open (tunnel-ingress half landed; nftables half absent)

- Landed and live: `automation/validation/tunnel_drift_check.sh` (reads the live Cloudflare tunnel
  config via API and compares to `config/cloudflare/ingress.json`); `config/systemd/falcon-tunnel-drift.
  {service,timer}` enabled; last run 2026-10-12 00:00:01–03Z → `RESULT: in sync` (declared == live:
  enroll/falcon/iris), metric `/srv/falcon/textfile/falcon_tunnel_drift.prom` = `0`
  (`falcon_tunnel_drift_checked_timestamp_seconds 1791763203`); alert rule "Tunnel ingress drift"
  (`bootstrap/90-alerting.sh:675`). Commit `3b0b976` (PR #55).
- Still absent: any automated comparison of the live **nftables** ruleset with
  `config/nftables/falcon.nft`. The only live firewall checks are `post_reboot_verify.sh:25-30`
  (default-deny policy only; manual) and the static repo guard
  `automation/validation/tests/exposure_edges_test.sh`; `bootstrap/30-firewall.sh` only applies the file.
  No `falcon-*` timer performs a ruleset drift check (29 unit files enumerated; none match).
- Live parity holds today but can regress silently (the finding's stated risk): `/etc/nftables.conf`
  is byte-identical to the repo file (`sha256 91fe36ef…`, `diff` IDENTICAL), including the
  per-peer wg0 narrowing rules.

### TEST-P3-001 — still-open

- `ci/validate.py:195-215` `check_evidence_integrity()` skips any meta whose `raw_artifact` is outside
  the checkout when `FALCON_EVIDENCE_OPTIONAL=1` (`:63`); `validate.yml:117` sets it for CI.
- Live CI proof (run `38299786463`, `3623d2e`, success): `PASS evidence integrity (0 captures, 1136
  external skipped in CI)`.
- Re-scan of the committed tree: 1136 metas, **all absolute lab paths** — 872 under
  `/home/user/falcon-build/evidence`, 264 under `/home/user/monitoring-build`; 0 in-repo/relative. In CI
  (different checkout path) all are skipped, so the meta-hash check verifies nothing; the committed tree
  is still bound by the generated-drift (`evidence/MANIFEST.sha256`) and evidence-index cross-checks,
  which do run.
- The skip message (`:214`) and the `validate.yml:5-6` comment predate the finding (blame `6f33a062`,
  2026-09-30); no split check was added (e.g. CI verifying the committed manifest separately from the
  lab-side meta hashes).

### TEST-P3-002 — still-open (unchanged, harmless; re-confirmed)

- `ci/validate.py:434` still reads only the first 15 lines of each suite; the marker regex is at `:438`.
- `automation/validation/tests/validate_gate_test.sh:26` is not a suite-level marker: it is inside the
  generated skip fixture (fixture content lines 25-28; marker at fixture line 2), which is what exercises
  the skip mechanism. The suite itself runs as uid 1000 and passes (`12/12` locally; CI log
  `PASS shell tests: …/validate_gate_test.sh (0.4s)`, `PASS shell tests (50 suite(s))`), so the
  "dead marker" is harmless as noted.
- General risk remains: a genuinely root/docker-requiring suite whose marker sits below line 15 would
  run instead of being skipped. No code change was made.

---

## New findings

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
