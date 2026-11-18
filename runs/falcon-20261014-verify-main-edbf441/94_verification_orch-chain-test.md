# Post-merge verification re-audit — ORCH / CHAIN / TEST findings

- **Target repo:** `/home/user/falcon-build` @ `edbf441` (main, clean) — read-only; date 2026-10-14.
- **Previous verification:** 2026-10-12 @ `3623d2e` (pack `19e7532`); **original run:** `falcon-20261011-0416-full-f5cb7c9`.
- **Findings re-checked:** 10 (ORCH ×4, CHAIN ×3, TEST ×3); verdicts per `POST_MERGE_REAUDIT.md` (verification lens).
- **Method:** repo at edbf441 (`git show`/`diff`), audit pack at `b80aaf0`, live read-only checks
  (DO site host over SSH, lab Traefik/nftables/timers, vantage probes, textfile metrics), GitHub API.
- **CI on edbf441:** validate run `38485693681` **success** (runner `edge-builder`, 2026-10-13 23:40Z) —
  `PASS shell tests (52 suite(s))`, `PASS evidence integrity (0 captures, 1164 external skipped in CI)`,
  `PASS secret scan`, gitleaks history scan `exit 0`.

## Summary table

| ID | Sev | Audit status | Verdict | Key evidence |
|---|---|---|---|---|
| CHAIN-P2-001 | P2 | verified-fixed | **verified-fixed** | DO watcher sha `239d3a4c` == repo, cron `*/5`, posture fresh 2026-10-14 00:30:02Z; DO vantage 302 → cloudflareaccess.com; residual stale workflow text now fixed (`ee4be3f`) |
| ORCH-P2-001 | P2 | open | **open** | Committed 2026-10-05 run still `GO WITH CONDITIONS` + P0×1 (34/34 open); no note; `docs/audits/repo-deep-dive/` unchanged since 3623d2e; canonical pack run still NO-GO |
| ORCH-P2-002 | P2 | partially-fixed | **partially-fixed** | Pack `00356a6` now renders the profile in INDEX/register (NEW-2 fixed); falcon-lab manifest shape (lens IDs/targets/status, waves) still not emitted (`full_domain.py:224`); runs still base/42 prompts |
| TEST-P2-001 | P2 | verified-fixed | **verified-fixed** | Same DO-watcher fix live; `external-smoke.yml` text honest at edbf441; last run `38446409098` success prints "Access enforcement NOT asserted from this vantage" |
| CHAIN-P3-001 | P3 | open | **open** | No diff since 3623d2e: public routers still `[sec-headers, public-rate-limit]` only; live Traefik sha `3ed78f94` == repo; lab probes reach origin (iris `/dashboard`, soc `/app/login`); Shuffle socket mounts still guarded |
| CHAIN-P3-002 | P3 | open | **open** | Tunnel drift live/in-sync (2026-10-14 00:00Z, metric 0); still **no** live-vs-repo nftables drift check; live parity holds (`/etc/nftables.conf` == repo, sha `91fe36ef`) |
| ORCH-P3-001 | P3 | verified-fixed | **verified-fixed** | Regex unchanged (`audit_run_lifecycle.sh:120-124`); reproduced with a real published run + repo prefix → PASS, `check_failures=0` |
| ORCH-P3-002 | P3 | open | **open** | 20261009 artifact still report `verified-fixed` vs array/register `open`; no in-folder note (pack reconcile commits unmerged); no `check_run.sh` cross-check |
| TEST-P3-001 | P3 | open | **open** | CI `PASS evidence integrity (0 captures, 1164 external skipped in CI)`; 1164 metas all absolute lab paths, 0 in-repo; no split check |
| TEST-P3-002 | P3 | open | **open** | Reader still first 15 lines (`ci/validate.py:462`); line-26 marker is fixture content; suite PASS in the 52-suite gate; general late-marker risk unchanged |

**Counts:** verified-fixed 3 · partially-fixed 1 · open 6 · owner-accepted 0 · **regressed 0**.

---

## Per-finding detail

### CHAIN-P2-001 — Access-posture check no longer verifies Access from the lab vantage — verified-fixed

- Repo fix unchanged since 3623d2e: `automation/alerting/do_watcher/watch.sh:56-97` `check_access()`
  asserts `302` **and** `location` contains `cloudflareaccess.com` for falcon/iris/soc, alerting to the
  independent ntfy on failure; comment states the non-owner vantage rationale.
- Deployed and live: `/opt/falcon-watcher/watch.sh` sha256 `239d3a4c…` == repo (edbf441) sha; cron
  `*/5 * * * *`; `/var/lib/falcon-watcher/posture` fresh at **2026-10-14 00:30:02Z** = `ok`; log tail
  `posture ok: https://falcon|iris|soc.mainecybertech.us/ -> 302 (Cloudflare Access)`.
- Vantage contrast re-probed live: from the DO host all three 302 → `mainecybertech.cloudflareaccess.com`;
  from the lab iris → `302 /dashboard`, soc → `302 /app/login`, enroll 404 (owner-IP bypass).
- Residual fixed too: `external-smoke.yml` header/comment/job summary no longer claim the Access
  assertion (commit `ee4be3f`; lines 5-11, 29-31, 73-75) — the previous report's NEW-1 is closed.

### ORCH-P2-001 — Committed 2026-10-05 run contradicts the gate — open

- `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md:3` still
  `Verdict: **GO WITH CONDITIONS**` with P0 ×1 / P1 ×7; `findings.json` = 34 findings, **34 `open`**;
  the folder still has 12 files, no dated/appended reconciliation note (grep).
- `git log 3623d2e..edbf441 -- docs/audits/repo-deep-dive/` is empty; the newest committed record is
  still the 20261005 run (listing ends there). Pointers (`AGENTS.md:86`, `README.md:11`,
  `docs/RELEASE_GATE.md:16`, `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:40`) still name the 20261011 pack run.
- Canonical pack run for the same audit (`runs/falcon-20261005-full-main-e267ce1/RELEASE_GATE.md`)
  still says `Decision: **NO-GO**` — the contradiction stands.
- `ci/validate.py` (edbf441) has no `docs/audits` publish gate; `audit_run_lifecycle.sh` checks
  structure only (run id/JSON/artifacts), not the gate-vs-P0 rule.

### ORCH-P2-002 — profile hardcoding / falcon-lab shape — partially-fixed

- Progress since 3623d2e: pack `00356a6` made `render_index` (`tools/full_domain.py:240`) and
  `register_md` (`:421`) render the manifest profile — the contradictory `Profile: base` INDEX (NEW-2)
  is fixed.
- Still not landed: `"lenses": [d["area"] for d in domains]` (`tools/full_domain.py:224`) — 43 area
  codes, no lens IDs/targets/status and no waves; `profiles/falcon-lab.manifest.json:61` waves are
  never emitted by the driver; no manifest-shape validation against the falcon-lab example.
- Current falcon runs remain base: `runs/falcon-20261014-verify-main-edbf441/audit_manifest.json`
  = profile `base`, promptCount 42, `scope.lenses` = area codes; `--profile` exists (`:721`) and
  `check_run.sh:47-52` requires the falcon-lab lens reports only when `profile == falcon-lab`, which
  the driver does not produce.
- Residual unchanged: coverage claims for falcon still rest on the base 42-prompt set; no documented
  scope reduction.

### TEST-P2-001 — external-smoke Access claim — verified-fixed

- Identical substance and live evidence as CHAIN-P2-001 (DO watcher is the enforcement assertion).
- Workflow text at edbf441: `external-smoke.yml:5-11` NOTE (Access enforcement asserted by the DO
  watcher, not here), `:29-31` job comment availability-only, `:73-75` summary "the lab vantage cannot
  assert Access; the DO watcher does". The stale claims from the previous report are gone (`ee4be3f`).
- Last run `38446409098` (success, 18ef265 which contains `ee4be3f`): output
  `OK … (owner-IP bypass: origin reachable; Access enforcement NOT asserted from this vantage)` for
  iris/soc, enroll 404 — honest availability-only behavior.

### CHAIN-P3-001 — Anonymous origin exposure + Shuffle socket mounts — open

- No change since 3623d2e (`git diff 3623d2e..edbf441` empty for `config/traefik/dynamic.yml` and
  `mct/compose/docker-compose.shuffle.yml`).
- Public routers still carry only `[sec-headers, public-rate-limit]`: `falcon-grafana:94`,
  `iris-public:118`, `soc-wazuh:133`; only `/ntop` has `falcon-basic-auth` (`:101`); the dead
  `ntfy-auth` middleware was removed earlier (comment at `:26-28`).
- Live Traefik `/etc/traefik/dynamic.yml` sha256 `3ed78f94…` == repo file; lab probes reach origin
  (iris → `302 /dashboard`, soc → `302 /app/login`), so an Access bypass still leaves only the app login.
- Shuffle half remains closed: both `/var/run/docker.sock` mounts still commented out with the dated
  note (`docker-compose.shuffle.yml:48-51`, `:90-93`); live scan: **0** running containers mount
  `docker.sock`; no Shuffle containers running.

### CHAIN-P3-002 — Tunnel-ingress vs nftables drift checks — open

- Tunnel-ingress half still landed/live: `falcon-tunnel-drift.timer` enabled; last run
  **2026-10-14 00:00:00Z**, `Result=success`; `/srv/falcon/textfile/falcon_tunnel_drift.prom`
  = `falcon_tunnel_drift 0`, `checked_timestamp_seconds 1791936003`; declared == live.
- Nftables half still absent: no nft/firewall drift unit among the 26 `falcon-*` timers;
  `automation/validation/post_reboot_verify.sh:25-30` still checks only the default-deny policy +
  stale tables (manual); `automation/validation/tests/exposure_edges_test.sh` is the static repo guard;
  `bootstrap/30-firewall.sh` only applies the file. No metric like `falcon_nft*` exists (grep).
- Live parity holds today but can regress silently (the finding's core risk): `/etc/nftables.conf`
  byte-identical to `config/nftables/falcon.nft`, sha256 `91fe36ef…`.

### ORCH-P3-001 — Run-id prefix vs consumer lifecycle check — verified-fixed

- `automation/validation/audit_run_lifecycle.sh:120-124` unchanged since 3623d2e: accepts an optional
  repo prefix (`^([a-z0-9][a-z0-9-]*-)?[0-9]{8}-[0-9]{4}-`), comment cites ORCH-P3-001.
- Reproduced at edbf441 with a real published run copied and repo-prefixed:
  `falcon-20261005-0354-full-main-e267ce1` → `PASS … (external)`, `check_failures=0`.
- (Residual noted before and unchanged: closure is consumer-side acceptance; no publish-time regex
  assertion was added — one of the finding's two allowed fixes was taken.)

### ORCH-P3-002 — Report-vs-register status contradiction in the 20261009 artifact — open

- `runs/falcon-20261009-2117-full-08e20d1/_domains/02_architecture_runtime_topology.json`: report text
  `### ARCH-P2-001 - … (verified fixed)` with `Status: verified-fixed.` while the same file's findings
  array has `"id": "ARCH-P2-001"` … `"status": "open"`; top-level `findings.json` also `open`.
- Registers still carry `open`: `runs/falcon-20261009-2117-full-08e20d1/follow_up_register.md:34` and
  `risk_register.md:34`; the 20261011 verification run's register also `open`. No dated reconciliation
  note in the folder; the pack's run-status reconcile commits (`e110416`, `65cf8b7`, …) are only on the
  **unmerged** `origin/audit/falcon-20261009-full` branch and leave ARCH-P2-001 `open` anyway.
- `tools/check_run.sh` (b80aaf0) still has no domain-report-vs-findings-array status cross-check —
  sections are: required files, manifest keys, falcon-lab extras, ID consistency/duplicates, status
  vocabulary, informational source reports.
- Live at edbf441 supports fixed (`falcon_container_drift{kind="security"}=0`, all kinds 0; last run
  2026-10-14 00:40Z success), so the register is stale while the report claims closure.

### TEST-P3-001 — CI evidence-integrity check verifies zero captures — open

- `ci/validate.py:223-244` unchanged (`FALCON_EVIDENCE_OPTIONAL=1` skip for off-repo artifacts);
  `validate.yml:121` still sets it. No split check added (CI manifest vs lab meta hashes).
- CI run `38485693681` (edbf441): `PASS evidence integrity (0 captures, 1164 external skipped in CI)`.
- Re-scan of the committed tree: **1164** metas, all absolute lab paths — 900 under
  `/home/user/falcon-build`, 264 under `/home/user/monitoring-build`, 0 in-repo/relative. In CI all are
  skipped, so the meta-hash check verifies nothing; generated-drift + evidence-index checks still run.

### TEST-P3-002 — `test-requires` marker window — open (unchanged, harmless)

- `ci/validate.py:462` still reads only the first 15 lines (`readlines()[:15]`; regex at `:466`).
- `automation/validation/tests/validate_gate_test.sh:26` is fixture content (the generated skip
  fixture's line 2), not a suite-level declaration; the suite itself runs as uid 1000.
- CI run `38485693681`: `PASS shell tests: …/validate_gate_test.sh (0.4s)` inside
  `PASS shell tests (52 suite(s))` (52 suites = +`ci_run_watchdog_test.sh`, +`dlq_replay_test.sh`
  since 3623d2e); gitleaks/secret-scan suites present and passing (`gitleaks_curl_allowlist_test.sh`
  1.8s, `secret_scan_test.sh`).
- General risk unchanged: a genuinely root/docker-requiring suite whose marker sits below line 15 would
  run instead of skipping. No code change made.

---

## New findings

**NEW-A (P3, CI/TEST) — the dedicated SEC-001 gitleaks curl-allowlist step is a guaranteed no-op (SKIP).**
`.github/workflows/validate.yml:107-110` sets `GITLEAKS_BIN: ${{ runner.temp }}/gitleaks`, but the
pinned gitleaks binary is downloaded/extracted to `$HOME/.cache/falcon-ci-tools/gitleaks`
(`validate.yml:93-102`, same path used by the history scan at `:104-105`). The test skips when
`GITLEAKS_BIN` is set but not executable, so the dedicated step asserted nothing:
CI run `38485693681` log: `gitleaks_curl_allowlist_test: SKIP (gitleaks binary not available; set
GITLEAKS_BIN)`. Mitigation: the same suite also runs inside the shell-suite gate, where it passed in
1.8s (`PASS shell tests: …/gitleaks_curl_allowlist_test.sh (1.8s)` — a real run, not the ~0.0s skip
path), so coverage is not entirely lost; the dedicated step itself provides no signal and its skip
could mask a missing binary. Fix: point `GITLEAKS_BIN` at `$HOME/.cache/falcon-ci-tools/gitleaks`
(as the history step does). Pre-existing since `ff03297` (2026-10-04), not a regression.

No other new issues; no regressions found.

### Cross-checks run (read-only)

- DO site host (SSH): watcher sha/cron/posture/log; non-owner vantage probes for falcon/iris/soc/enroll.
- Lab: Traefik container config sha vs repo; `docker ps` mount scan for `docker.sock`; nftables
  `/etc/nftables.conf` vs repo file; tunnel-drift timer/metric; container-drift metric; lab vantage probes.
- Pack `b80aaf0`: `full_domain.py`/`check_run.sh` inspection; 20261009 artifact contradiction;
  current run manifest (`falcon-20261014-verify-main-edbf441`).
- GitHub API: validate run `38485693681` @ edbf441 (success; 52 suites; 0 captures/1164 skipped),
  external-smoke last run `38446409098` (success, honest output), run history. (Observed but not a
  finding: validate run `38464152917` @ 26e662c failed on evidence-index/generated-drift — a
  publication-timing transient, green again on later heads including edbf441.)
