# Falcon Pi Edge Sensor — New-Developer Audit

- **Auditor role:** new developer joining the Falcon Pi Edge Sensor program; read-only, in-depth onboarding audit.
- **Repository:** `/home/user/falcon-edge-build` (branch `main`).
- **Audit window:** 2026-09-30 ~03:00–03:35 UTC.
- **Snapshot note:** the repository was **being actively modified by other sessions during this audit**. HEAD moved from `cfaf09d` (02:56Z) to `96c3e08` (03:33Z); a P9-G04 hard-reset endurance run and a P7-G06 recovery drill were running against the lab Pi. Every observation below is timestamped where it matters; re-check the ledgers before acting.
- **Hard boundaries observed:** no repository writes/commits, no service/container changes, no deploy/update/sign flows, no mutations on the host or the Pi, no secret values printed. All shell commands, tests, and GET requests below were read-only or wrote only to `/tmp` / temp dirs.
- **No secret values appear in this report.** Paths such as `/home/user/.env` and `/home/user/falcon-edge-secrets` were only tested for existence/behavior, never read for values.

---

## 1. Executive summary

The program is real, disciplined, and technically strong; a newcomer can become productive in a day with the code, but **not yet from the front page** — the top-level docs describe a state of the world that is one or more hardware generations stale, several closeout artifacts contradict the ledgers they are supposed to summarize, and the entry points for building/running/enrolling/verifying are scattered across phase documents, closeouts, and runbacks.

What works, verified today:

- `ci/validate.sh` → **ALL PASS** (contract lint, generated models/schemas in sync, 88-gate ledger, evidence integrity, secret scan). Re-run at `96c3e08`: ALL PASS, 298 captures, 835 files scanned, one in-progress WARN.
- Full test suite → **161 tests OK** in 93 s (`python3 -m unittest discover -s tests -p "test_*.py"`).
- Evidence manifest → **`manifest.sh check` exit 0** (593 entries).
- Signed release manifest → **31/31 artifacts verified**, Ed25519 signature **VALID** (`keyId 5ea52faf9cf6ee97`); SBOM CycloneDX 1.5, **714 components**, lab7 image digest embedded and matching (`a81b1ff4…ea2c9d`).
- Live control plane → GET-only inspection succeeded: `/healthz` 200 (v0.1.0); `/sensors` shows 9 sensors, exactly one ACTIVE (`fes_b9f5c03d58713121659f1796`) with a fresh heartbeat; the explainable lab-only residue (5 RETIRED, 3 REVOKED).
- Lab Pi → reachable on the WireGuard tunnel (`10.99.0.30`, ping 2/2, heartbeats fresh); Raspberry Pi 3B Rev 1.2; `falcon-agent`, Vector, Suricata, pmacctd, the update-apply path unit and the cert-reload path active; `throttled=0x0`; disk 12%; USB `0846:9055` (RTL8812BU) attached; **no MT7612U** (`0e8d:7612` absent).
- Evidence discipline is sincere: failures and incident windows are retained, contradictions are logged, and the newest independent review is in the tree (`closeout/REVIEW-2026-09-30.md`, CONDITIONAL_PASS).

Highest-value problems for a new developer:

1. **F-01 (HIGH):** README/REPOSITORY/AGENTS still say the Pi and RTL8812BU are not attached; both are attached, enrolled, and running right now.
2. **F-02 (MEDIUM):** the "authoritative" OpenAPI contract is missing three live endpoints (`renewals`, `release`, `ingest/vector`), so generated schemas/models and client generators are incomplete.
3. **F-03 (MEDIUM):** `FINAL_RESPONSE.json`'s `commit` is stale (it claimed to be the latest ledger change), `PROGRAM_CLOSEOUT.md` still says "120 tests"/"18 artifacts", and `docs/phase6/CLOSEOUT.md` gate counts predate P6-G05.
4. **F-04 (MEDIUM):** a reproduced latent queue bug — `purge_expired()` deletes non-expired items.
5. **F-05 (MEDIUM):** `falcon_edge_sensor_pending_directives` never decrements (dead `consume_directive`, no expiry filter), so the dashboard will show phantom pending directives forever.
6. **F-06 (MEDIUM):** the three host maintenance units (metrics timer, operator-cert renewal, secrets backup) exist only on the lab host, not in `deploy/`.

None of these invalidate the lab results. They are exactly the class of thing an onboarding pass should surface before a second developer starts changing code.

---

## 2. Reconstruction: what this program is and how it works

### 2.1 Purpose and topology

A Raspberry Pi edge sensor (`falcon-agent`) managed by a Falcon control plane on the lab host over **mTLS over a WireGuard management tunnel** (`wg0`, `10.99.0.0/24`). The sensor passively collects Ethernet telemetry (Suricata IDS metadata via EVE, pmacct flow 5-tuples/counters via Vector) and has an optional **metadata-only** wireless profile (Kismet; payload/pcap prohibited). Updates and directives are signed artifacts with rollback/recovery. Observability is a Prometheus textfile exporter feeding the existing monitoring stack, plus a Grafana dashboard and (undeployed) alert rules. Everything is governed by an evidence-first, append-only doctrine with 88 gates across phases P0–P10.

```
owner/admin ── SSH over tunnel ──> Pi (10.99.0.30)
                                     falcon-agent (systemd, non-root, 192M/50% CPU limits)
                                       ├─ heartbeat/inventory/desired-state/directives  ── mTLS ──> control plane
                                       ├─ Vector   (Suricata EVE + pmacct JSON → /api/v1/ingest/vector)
                                       ├─ Suricata (AF_PACKET on eth0, EVE metadata only)
                                       ├─ pmacctd  (flow counters → /run/pmacct/flows.json)
                                       └─ Kismet   (installed, idle; vendor helper deadlock)
lab host falcon (192.168.222.228)
  ├─ falcon_control (systemd `edge-control-plane.service`, 0.0.0.0:9443, mTLS)
  ├─ fleet_metrics.py → /srv/falcon/textfile/falcon_edge_metrics.prom (node-exporter textfile)
  └─ monitoring stack (separate program, not rewritten)
```

### 2.2 `falcon-agent` (`src/falcon_agent/`, ~1,300 lines)

- **State machine** (`state.py`): 13 states (`UNPROVISIONED → BOOTSTRAP → ENROLLING → CONFIGURING → VALIDATING → ACTIVE`, plus `DEGRADED/RECOVERY/ROLLING_BACK/QUARANTINED/SUSPENDED/REVOKED/RETIRED`); an explicit transition map; security states force-only; atomic 0600 JSON persistence with a 200-entry history (`reason`, counter, action/result, correlation id).
- **Runner** (`runner.py`): one `cycle()` per interval does heartbeat → inventory (every 900 s) → desired-state fetch/verify/apply → directives → update manifest → optional auto-download/stage → flush queue. Response order follows enable-tänk: retry → recover → degrade → escalate → rollback (never reboot first). `sd_notify` watchdog integration (`WATCHDOG=1`, Readiness `READY=1`).
- **Client** (`client.py`): stdlib `http.client` + TLS; distinguishes `ApiUnavailable` (5xx/429/timeouts/retryable problems) from `ApiError` (definitive 4xx). mTLS once enrolled; TOFU only if explicitly allowed for lab.
- **Queue** (`queue.py`): SQLite bounded queue (2 GiB/100k events/7 days), priorities (state 0 → flow 3), checksums, eviction of lowest-priority/oldest with loss accounting, DLQ for corruption/ApiError. *(One latent defect: F-04.)*
- **Directives** (`directives.py`): Ed25519 signature + schema + expiry + revision/sequence monotonicity for desired state, update manifests, recovery directives.
- **Identity** (`identity.py`): device-generated Ed25519 key + CSR; private key never leaves the device; key/cert written `0640` (group `falcon-agent`) so Vector (same group) can read them; renewal generates a fresh key pair and commits only on success.
- **Collectors** (`collectors.py`): every source optional/degrading; MACs HMAC-hashed with a site salt; no payloads; adapter detection via USB IDs.
- **Auto-renewal:** at ≤10 days remaining the heartbeat triggers rotation via `POST /sensors/{id}/renewals` (6 h cooldown), with renewal-due events as fallback.
- **Tests:** `tests/phase3/` covers the exhaustive 13×13 transition matrix, queue bounds/corruption, directive tamper/expiry/replay, runner rollback.

### 2.3 Control plane (`src/falcon_control/`, ~1,400 lines)

- **Transport** (`http_server.py`): `ThreadingHTTPServer` + TLS (min TLS 1.2, `CERT_OPTIONAL` so bootstrap enrollment can connect without a client cert; per-route auth then applies). Client identity = SHA-256 cert fingerprint → sensor, or `CN=operator` → operator.
- **Service** (`service.py`): 19 routes. Enrollment with single-use bearer bootstrap token + CSR → CA-signed 30-day device cert; heartbeats with clock-skew (±300 s), sequence replay/conflict and idempotency handling; inventory; signed desired state with strong ETag/304; state reports; events; Vector NDJSON ingest spool; update-manifest issuance (signed, TTL) and retrieval; signed recovery directives with server-side `after` cursor; quarantine/release/revoke; certificate renewal. RFC 9457 `application/problem+json` everywhere.
- **Store** (`store.py`): SQLite (single connection, lock-guarded) with tables for sensors, tokens, desired state, idempotency, heartbeat sample, inventory, state reports, events, manifests, directives, audit log.
- **PKI** (`pki.py`): openssl-CLI lab CA (Ed25519); server cert (SANs `falcon.lab`, `localhost`, `127.0.0.1`, later `10.99.0.1`), operator cert `CN=operator`, sensor certs 30 days.
- **Signing** (`falcon_common/signing.py` + `ed25519.py`): canonical JSON (signature removed) + base64 Ed25519. **Pure-Python Ed25519 is explicitly "lab grade only", not constant-time** in the module header and closeouts.
- **Tests:** `tests/phase2/` spins up a real mTLS server on an ephemeral port with a temp PKI and exercises the contract end to end.

### 2.4 API contract (`api/`)

Authoritative OpenAPI 3.1 (`falcon-edge-v1.yaml`, currently 16 paths/30 schemas) with generated JSON Schemas (30 files) and generated Python models/validators (`src/falcon_common/models_generated.py`). `ci/validate.sh` checks schema/model drift, but **not** service-route parity (F-02).

### 2.5 Image and onboarding pipeline

- **Two distinct pipelines** (an easy early confusion):
  1. **Release bundle** (`image/build-image.sh` + `image/verify-image.sh`): signed tarball of `overlay/` + `src/` + manifest; guarded media writer `image/prepare-media.sh`. The `bin/falcon deploy edge build-image|verify-image|prepare-media` commands delegate to this.
  2. **Real flashable Pi image** (`automation/validation/bake_lab_test_image.sh` → `image/build-pi-image.sh`): loop-mounted customization of a pinned Raspberry Pi OS Lite (Trixie) base, plus `image/verify-pi-image.sh --image …` (45/45 structural checks claimed; verifier code is in-tree).
- First boot: `falcon-bootstrap.service` (root, oneshot) installs the admin SSH key, consumes `/boot/firmware/falcon-claim.json` (URL + single-use 7-day token + CA), waits for route/NTP/CP health over the tunnel, enrolls once, shreds the token, then `OnSuccess=` starts `falcon-agent.service`.
- Lab-side onboarding: `automation/validation/onboard_lab_side.sh --peer-key-file …` adds the Pi WG peer (with `wg0.conf` backup + rollback note), ensures the server cert has the tunnel SAN, installs/enables/starts the CP service, health-checks it.
- Claim refresh: `automation/validation/mint_claim_file.sh` (for expired pre-baked tokens).
- Delivery directory (`/home/user/falcon-edge-delivery`, outside the repo): lab5/lab6/lab7 images + sha256 + credentials (0600) + SSH keys + WG pubkeys + SBOMs + signed manifest + review packages + backups.

### 2.6 Profiles (`profiles/`)

- **Sensor:** Suricata (`falcon-pi.yaml`: AF_PACKET on eth0, EVE alert/dns/flow/tls/stats, payload/packet off, no pcap, 30 s stats); Vector (`edge.toml`: 2 GiB disk buffer, VRL strips `payload`/`packet`, mTLS with the device cert to the ingest endpoint); pmacct (`pmacctd.conf`: JSON 5-tuple + AS mapping, 022 umask so Vector can read); Kismet (`kismet_site.conf`: JSON only, `pcap_logging=false`; capture blocked by a vendor helper deadlock).
- **Pi hardening** (`profiles/pi/hardening/*.sh`): headless baseline, ZRAM 452M + bounded tmpfs, 30 s hardware watchdog, default-deny nftables (management/WG/DHCP/DNS/NTP allowlist), journald caps; applied on the live Pi and cold-boot validated.
- **AB strategy** (`profiles/pi/AB_STRATEGY.md`): documented, but `tryboot` is unavailable on the Pi 3B, so real A/B boot remains BLOCKED (P7-G05).
- **Adapter plans** (`profiles/adapter/ADAPTER_PLANS.md`): RTL8812BU proved on in-tree `rtw88_8822bu`; MT7612U certification pending hardware + reviewer.

### 2.7 Update / rollback / recovery design

- **Offer:** operator `POST /sensors/{id}/update-manifests` (signed, TTL, canary-targeted at explicit sensor ids); agent verifies signature/expiry and records the offer; expired manifests stop being served (device drill E-P7-G01-243/E-P7-G07-244).
- **Apply:** agent `apply_update()` downloads over HTTPS (bundle CA), verifies SHA-256 and size, stages under the state dir, writes `updates/apply-request.json`; `falcon-update-apply.path` triggers the root `falcon-update-apply.service`: re-verify digest, reject unsafe archive members, `compileall`, swap `falcon_agent` with a `falcon_agent.previous` backup, restart, wait for ACTIVE, auto-restore on failure; result reported by the agent as `update.applied`/`update.rolled_back`. Deployed on the live card; **lab7 image predates it**.
- **Layered rollbacks:** candidate config rollback (previous.json), `RESET_CONFIG`, `ENTER_RECOVERY` hold, `SWITCH_SLOT` (lab-simulated on the 3B), real boot-slot switch blocked; `EXIT_QUARANTINE`/`release`; diagnostics bundles.
- **Directive semantics quirk:** the server never marks directives consumed; the agent keeps a local cursor and the server serves by `after=` (`store.consume_directive` is dead code → F-05).

### 2.8 Observability

- `automation/observability/fleet_metrics.py` reads the CP DB + ingest spool and writes `falcon_edge_*` / `edge_capture_*` / `edge_*` Prometheus textfile metrics. Deployed additively via `falcon-edge-metrics.timer` (every 5 min) into the monitoring stack's node-exporter textfile collector (61 series initially; 73 lines in the current `.prom`), plus a Grafana dashboard provisioned as `falcon-edge-fleet`.
- `config/prometheus/edge-alerts.yaml` (silence, queue backlog/loss, cert expiry, quarantine/revoked, temperature, capture drops, queue age) is **prepared but not deployed** (needs a Prometheus rule-file mount in the other program, an owner decision).
- Capture-quality contract in `docs/phase8/CAPTURE_QUALITY.md`; Suricata stats → Vector → CP spool → exporter is live.

### 2.9 Security model

- Bootstrap is the only bearer-token flow (single-use, scoped, expiring; only hashes stored; atomic redemption).
- All operational APIs require mTLS; sensor certs are device-generated (CSR), 30 days, auto-rotated; old certs are unmapped at rotation (live drill: old cert → 403).
- Signed desired state / manifests / directives with expiry and replay/downgrade rejection; idempotency keys on most state-changing routes; clock-skew rejection; quarantine on identity/path mismatch.
- Least-privilege systemd units (`NoNewPrivileges`, empty capability set, ProtectSystem, memory/CPU caps); firewall default-deny; secrets outside the repo (`/home/user/falcon-edge-secrets` 0700; `/home/user/.env` owner-only); capture wrapper redacts known key/topic patterns and feeds sudo via stdin.
- Stated lab limitations: pure-Python Ed25519 (not constant-time), lab CA/HTTP service not internet-hardened, `allow_insecure_enrollment` exists but the image disables it (baked trust bundle).

### 2.10 Program governance: gates, evidence, release

- **88 gates**, 8 per phase P0–P10, in `ledgers/gate_ledger.csv`. Statuses `NOT_RUN/IN_PROGRESS/PASS/FAIL/BLOCKED/INSUFFICIENT_EVIDENCE/NOT_APPLICABLE`; a PASS needs evidence refs; closeouts and review gates need an independent disposition (ED-19 still unassigned).
- Ledgers: gate ledger, test execution (derived), evidence index (derived), risk register, exception register, contradiction ledger, decision log, progress ledger.
- Every execution runs through `automation/evidence/capture.sh` (UTC start/end, target, actor, command, exit code, raw artifact + SHA-256, redaction statement); `index.sh` rebuilds the index; `manifest.sh create|check` maintains `evidence/MANIFEST.sha256`.
- Release controls: `automation/validation/build_sbom.py` (CycloneDX 1.5 from the live device's dpkg list + image digest), `build_release_manifest.py` (SHA-256 + size of delivery artifacts + SBOM digest + repo commit, Ed25519-signed), `build_review_package.sh`/`verify_review_package.sh` (secret-scan-gated, reproducible review tarball).

---

## 3. What I actually ran / observed (verification log)

| # | Command / action | Result (observed) |
|---|---|---|
| 1 | `bash ci/validate.sh` at HEAD `cfaf09d` (~03:04Z) | **ALL PASS** — 296 captures, secret scan 831 files clean |
| 2 | same at HEAD `96c3e08` (~03:33Z) | **ALL PASS** — 298 captures, 835 files clean; 1 WARN: in-progress capture `P7-G06/…recovery-quarantine-drill.out` (a sibling session's drill) |
| 3 | `python3 -m unittest discover -s tests -p "test_*.py"` | **Ran 161 tests … OK** (93 s; one ResourceWarning in `tests/phase9/test_soak_harness.py`) |
| 4 | `bash automation/evidence/manifest.sh check` | exit 0, 593 entries |
| 5 | Manifest verification script + independent Python re-hash | 31/31 artifacts exist and match SHA-256; signature **VALID** `keyId 5ea52faf9cf6ee97`; SBOM 714 components; lab7 image digest `a81b1ff4…ea2c9d` matches sidecar and SBOM |
| 6 | 5 spot-checked evidence index entries (`E-P9-G02-288`, `E-P4-G01-282`, `E-P10-G05-280/281`, `E-P8-G04-266`) re-hashed | all match the index |
| 7 | Spot-read raw evidence (`P9-G02` drop budget, `P10-G05` lab7 manifest rebuild, `P4-G01` lab7 verify, `P8-G04` renewal drill) | contents support the gate notes (offered 1,201,233 pkts / 0 engine drops; 31 artifacts signature VALID; old cert 403) |
| 8 | `image/verify-image.sh --bundle image/out/0.1.0` | signature PASS, checksums OK, manifest digests match → VERIFY OK |
| 9 | `verify_review_package.sh` on newest delivery package (`…3101bf0`) | manifest 756 entries verified, no caches/build outputs, secret scan 736 files clean → OK (package content is from commit `35f0793`, i.e. pre-remediation) |
| 10 | Live control plane GETs (`/healthz`, `/sensors`, `/sensors/{id}`) with the operator cert | 200/ok v0.1.0; 9 sensors, 1 ACTIVE with fresh heartbeat; inspect: profile PASSIVE_EDGE, configRevision 1, cert notAfter 2026-10-30 |
| 11 | `systemctl show edge-control-plane.service` | exactly one instance, MainPID 440203, since 00:51:05Z |
| 12 | Live CP DB **read-only** (`sqlite3 mode=ro`) | 9 sensors (1 ACTIVE/5 RETIRED/3 REVOKED); ingest audit entries flowing every few seconds; 10 unredeemed bootstrap tokens (3 expired, 7 valid to Oct 6–7); live sensor has 2 unconsumed expired directives |
| 13 | Pi over SSH (read-only) | Raspberry Pi 3 Model B Rev 1.2; image metadata `2026.09.29-lab5`; eth0 10.11.12.158; wlan0 192.168.111.170; wlan1 DOWN; wg0 10.99.0.30; `falcon-agent`, `falcon-bootstrap`, Vector, Suricata, pmacctd, `falcon-update-apply.path`, `vector-cert-reload.path` active; Kismet inactive; disk 12%; 593 MiB available; `throttled=0x0`; agent modules include auto-renewal (live-patched beyond lab5) |
| 14 | `ping -c2 10.99.0.30` + heartbeat freshness | tunnel up; sensor heartbeat within ~30 s of checks |
| 15 | Pi USB enumeration | `0846:9055` (NetGear A6150 / **RTL8812BU**) present; no `0e8d:7612` (**MT7612U absent**) |
| 16 | `bin/falcon deploy edge --help` | 18 subcommands present |
| 17 | `bin/falcon --json deploy edge preflight/list/inspect` | all pass (secrets 0700, CA/operator cert present, CP HTTP 200) |
| 18 | Contract↔service comparison script | service `ROUTES` = 19; contract paths = 16 (missing `renewals`, `release`, `ingest/vector`) |
| 19 | `purge_expired()` reproduction in `/tmp` | mixed queue (1 fresh + 1 stale): reports `1` purged but depth 2 → 0 — **fresh item deleted** (F-04) |
| 20 | `systemctl cat` on maintenance timers | units exist on host with hardcoded repo paths; **not versioned in `deploy/`** (F-06) |
| 21 | `git remote -v`, `git log` | remote `github.com/MaineCyberTech/falcon-edge`; local `main` ahead of `origin/main` (origin at `0348fa1`); 84+ commits; `git status` clean at each check |

Gate ledger at my last read: **62 PASS / 0 FAIL / 10 BLOCKED / 16 INSUFFICIENT_EVIDENCE** (88). During the audit a sibling session closed P9-G04 (commit `96c3e08`), so the live count is 63/0/9/16 — expect it to keep moving while drills run.

---

## 4. Findings

Severity is from a *new-developer/operability* perspective (not a security severity rating). Each finding was observed directly; nothing below is inferred from another document alone.

### F-01 HIGH — Status documentation says the hardware is absent; the hardware is attached and running

- **Evidence:** `README.md:23` ("Hardware (Pi 3B, RTL8812BU, MT7612U) — Not attached to the lab host"); `REPOSITORY.md:22` ("HARDWARE … not present"); `AGENTS.md:44-45` ("The planned adapter hardware (RTL8812BU/MT7612U) is NOT attached"). Live: tunnel ping 2/2; SSH device model `Raspberry Pi 3 Model B Rev 1.2`; USB `0846:9055` present; control plane reports `fes_b9f5c03d58713121659f1796` ACTIVE with a fresh heartbeat; gate ledger P0-G02 and P6-G05 PASS.
- **Impact:** the first document a newcomer reads tells them they cannot exercise the device, while a live, enrolled sensor is one `ssh` away; the task brief itself (supplied externally) repeats the stale claim. It also undermines trust in the status table generally.
- **Recommendation:** update the three status lines to "Pi 3B attached/enrolled (`fes_b9f5…`, tunnel `10.99.0.30`); RTL8812BU attached (in-tree rtw88); MT7612U not attached; device phases P5/P6/P9 mostly executed — see `ledgers/gate_ledger.csv` and `closeout/OWNER_ACTIONS.md`". Keep historical text only inside closeout amendments.

### F-02 MEDIUM — "Authoritative" OpenAPI contract is missing three live endpoints

- **Evidence:** `api/openapi/falcon-edge-v1.yaml` = 16 paths; `src/falcon_control/service.py` `ROUTES` = 19, including `POST /sensors/{sensor}/renewals`, `POST /sensors/{sensor}/release`, `POST /ingest/vector`. The renewal endpoint was exercised live in P8-G04; the ingest endpoint is used every few seconds by the live Vector (audit log shows `ingest_vector` entries). The contract text also says "State-changing requests require an Idempotency-Key", but `h_quarantine`/`h_revoke` don't accept one.
- **Impact:** generated schemas/models (30 files) and any client generator omit three production-used routes; reviewers and future SDKs will treat the contract as incomplete; "authoritative" is currently aspirational.
- **Recommendation:** add the three paths (+ request/response schemas) to `falcon-edge-v1.yaml`, regenerate models/schemas, extend `ci/lint_openapi.py` or add a CI parity test that enumerates `ROUTES` versus contract paths, and reconcile the idempotency wording.

### F-03 MEDIUM — Summary artifacts contradict the ledgers they summarize (several known, still open)

- **Evidence:**
  - `closeout/FINAL_RESPONSE.json` `commit = 6cad6ec…` while `commit_note` claims it is "the latest ledger/evidence change" — it was 7+ commits behind at the start of the audit, and HEAD has moved further.
  - `closeout/PROGRAM_CLOSEOUT.md:14` "(120 tests)" and the 2026-09-30 update section "18 artifacts" while the suite is 161 and the current manifest has 31.
  - `ledgers/gate_ledger.csv` P10-G05 says "lab6 image digest embedded" while the current SBOM is lab7 (E-P10-G05-280/281).
  - `docs/phase6/CLOSEOUT.md:42-43` says "4 PASS / 3 BLOCKED / 1 IE" while the ledger is 5/2/1 (P6-G05 later PASS) and the same document's later "Adapter identification" section contradicts it.
  - Contradiction ledger C-101…C-105 remain OPEN pending reviewer re-verification (correct per doctrine, but confusing on first read since C-106 says "remediated").
- **Impact:** a newcomer can quote a wrong program status; the review-gate re-verification cannot rely on the top-level documents; "what is actually true now" requires reading 4–5 files.
- **Recommendation:** run `closeout/generate_final_response.py` after the in-flight drills, correct `commit_note`, append phase-6 count corrections, refresh the P10-G05 note to lab7, and add a one-line "superseded by amendment dated X" marker in stale sections (append-only).

### F-04 MEDIUM — Latent queue data-loss bug: `purge_expired()` deletes non-expired items

- **Evidence:** `src/falcon_agent/queue.py:126-138` computes the age cutoff for the *count* but uses `cutoff = iso_now()` in the `DELETE`. Reproduction (`/tmp`, public API plus a mixed queue): depth 2 → `purge_expired()` returns 1 → depth 0 (both the stale **and the fresh** item deleted). `tests/phase3/test_queue.py:76-86` only tests an all-expired queue, so the suite is green. The function is currently not called anywhere in `src/` (only the test calls it); `_evict()` handles age on enqueue.
- **Impact:** no production impact today, but any future wiring (e.g., a maintenance pass) silently loses fresh queued telemetry — the opposite of the loss-accounting doctrine.
- **Recommendation:** share one cutoff (`now - max_age_seconds`) between the count and the delete, add a mixed-queue regression test, and either wire it into `cycle()` or mark it explicitly "not used".

### F-05 MEDIUM — `falcon_edge_sensor_pending_directives` never decrements; directives are never marked consumed

- **Evidence:** `store.consume_directive()` (`store.py:323`) is dead code (no callers in `src/`); `automation/observability/fleet_metrics.py:61-64` counts `WHERE consumed_at IS NULL` with **no expiry filter**; the live DB shows the ACTIVE sensor with `pending = 2` directives from 2026-09-29 that expired 2026-09-30T00:14 (the agent handled them; its cursor is local). The Grafana panel "Pending directives / update versions" uses this gauge.
- **Impact:** the fleet dashboard permanently shows phantom pending directives after any directive is issued; any future alert on the metric would misfire. Operators cannot distinguish "issued" from "acknowledged".
- **Recommendation:** filter `expires_at > now` (and optionally `sequence > last known agent cursor`) in the exporter, or add an agent acknowledgement that calls `consume_directive`; document the chosen semantics in `CAPTURE_QUALITY.md`.

### F-06 MEDIUM — Host maintenance automation is not reproducible from the repository

- **Evidence:** `systemctl cat` shows `/etc/systemd/system/falcon-edge-metrics.{service,timer}`, `falcon-edge-operator-cert.{service,timer}`, `falcon-edge-secrets-backup.{service,timer}` with hardcoded `/home/user/falcon-edge-build/...` paths. The repo contains the Python scripts (`automation/observability/fleet_metrics.py`, `automation/validation/{renew_operator_cert,backup_edge_secrets}.py`) and prose (D-007 rollback note, phase-8 closeout) but **no unit files**; `deploy/` ships only agent/bootstrap/control-plane/log-export/update-apply units.
- **Impact:** a rebuilt host or a new developer cannot reproduce the deployed maintenance automation from the repo; the review package does not include it either.
- **Recommendation:** move the six unit files into `deploy/maintenance/` (lab-only), add a short install/rollback script, and reference them from D-007 and the phase-8 closeout.

### F-07 MEDIUM — Release/delivery artifact set is not coherent with the current repository (known as F11/P10-G01/P10-G03)

- **Evidence:** the signed manifest was built at commit `14e7c70` (01:19Z) with 31 artifacts; `falcon-agent-0.1.1-lab.tar.gz` (01:50Z) is **not** in it; the newest review package in delivery (`…3101bf0.tar.gz`, 00:34Z) verifies cleanly but was staged from commit `35f0793`, pre-remediation and pre-lab7. The live card runs modules (auto-renewal, update-apply) that **lab7 does not contain** (owner actions §8, phase-7 closeout), so reflashing lab7 would lose update-apply.
- **Impact:** "the signed release" covers a superseded snapshot; a new developer could deliver or flash the wrong artifact; a reviewer re-verifying P10-G03 is looking at stale material.
- **Recommendation:** after the in-flight drills, freeze a commit, rebuild the agent bundle + SBOM + manifest (re-sign), rebuild and verify the review package from that commit, update the P10 rows, and record the exclusion rules (root-owned backups) explicitly.

### F-08 LOW/MEDIUM — Shipping Vector profile hardcodes the single lab sensor identity and tunnel URL

- **Evidence:** `profiles/sensor/vector/edge.toml:33` `.sensor_id = "fes_b9f5c03d58713121659f1796"`; `:42` `uri = "https://10.99.0.1:9443/api/v1/ingest/vector"`.
- **Impact:** onboarding a second sensor requires editing the profile by hand and risks mis-tagging telemetry; the same applies to any future CP address change.
- **Recommendation:** template the identity/URL at deploy time (generate from the enrolled identity) or add explicit placeholder markers plus a validation rule; note it in the profiles README.

### F-09 LOW — Dead/duplicate first-boot script and overlay README drift

- **Evidence:** `image/overlay/usr/local/sbin/falcon-firstboot.sh` exists but is referenced by nothing (the baker installs and the unit runs `falcon-bootstrap.sh`); only `image/overlay/etc/falcon-agent/README` mentions `falcon-firstboot.sh` and claims the token is stored 0600, while the baker/bootstrap uses `0640 root:falcon-agent`.
- **Impact:** a newcomer editing image behavior may patch the wrong script; the permission claim misleads a security review.
- **Recommendation:** delete the obsolete script (or mark it deprecated in a header), fix the README text.

### F-10 LOW — Small documentation/repo-hygiene inaccuracies

- **Evidence:** `docs/phase4/CLOSEOUT.md:38` "CLI with 16 commands" vs 18 subcommands (`bin/falcon deploy edge --help`); `README.md` layout lists `bootstrap/` "(later)" but the directory does not exist; `docs/phase10/` is empty (phase-10 documents live in `closeout/`); `tests/phase10/test_release_artifacts.py:15` defines `SCHEMA = …/templates/agent_final_response.schema.json` for a `templates/` directory that does not exist (constant unused — the field tests are hand-written); `docs/phase5/CLOSEOUT.md` still shows the device-absent header counts alongside its amendment (append-only, but easy to quote wrongly).
- **Impact:** minor time loss; reinforces the "which document is current?" problem.
- **Recommendation:** batch refresh with explicit "historical" markers; add a `docs/README.md` "current state" pointer.

### F-11 LOW — Secrets-directory hygiene and operator visibility

- **Evidence:** `/home/user/falcon-edge-secrets/control.db` is a **0-byte root-owned stray** (created 2026-09-29 22:39) next to the live 561 KiB `control-plane.db`; there is no pruning/reporting for bootstrap tokens (10 unredeemed; 3 expired since 2026-09-29, 7 valid to Oct 6–7); the README/AGENTS do not document that the edge program's secrets live in `/home/user/falcon-edge-secrets` (distinct from `/srv/falcon/secrets` and `.env`).
- **Impact:** a newcomer may open the wrong database, and expired-token residue accumulates silently.
- **Recommendation:** remove the stray file (owner/root action), add a token-expiry/prune helper (e.g., extend `retire_stale_sensors.py` or a small `prune_tokens.py`), document the secrets layout in `AGENTS.md`/README.

### F-12 LOW — CI validates the contract but not the service-vs-contract surface; "validate ALL PASS" ≠ "tests pass"

- **Evidence:** `ci/validate.sh` runs json/yaml parse, contract lint, model/schema drift, decision register, gate ledger, evidence integrity, secret scan — but not the unit/integration suite (which is a separate 93 s unittest run). No route-parity check exists.
- **Impact:** a newcomer may commit after `validate.sh` alone; new endpoints can drift from the contract (as F-02 shows).
- **Recommendation:** add the route-parity test (cheap), and put both commands in the README quick start and `AGENTS.md` standard flow.

---

## 5. First-week friction (onboarding experience)

**What is clear and good**

- The doctrine (`README.md` §Doctrine, `AGENTS.md` hard rules, `REPOSITORY.md` conventions) is unambiguous and unusually well written; a newcomer knows immediately that evidence is raw-first, append-only, and that secrets never enter the repo.
- `closeout/OWNER_ACTIONS.md` is the single best "what needs a human" document; `ledgers/gate_ledger.csv` is the best "what is true" document; `closeout/REVIEW-2026-09-30.md` is honest and hugely informative.
- The code is small, stdlib-only, readable (~4.4k lines src vs 3.5k tests), and the tests exercise real mTLS, real SQLite, and real signing.
- Runbooks exist for 15 failure scenarios with an index, and the operational state of the live device can be inspected safely (`bin/falcon … preflight/list/inspect`, `ssh … systemctl is-active …`).
- `ci/validate.sh` is safe, fast, and passes out of the box; the test suite runs with one command.

**What is confusing / implicit (friction in rough order of encountered pain)**

1. **Wrong front-page status (F-01).** Before discovering the gate ledger, I believed there was no Pi and no adapter. The device is up and enrolled. A newcomer may spend their first hours re-deriving reality from `ps`, `wg`, and the ledgers.
2. **No end-to-end quick start.** The README quick start covers only `ci/validate.sh`, `capture.sh`, and index/manifest. To do the actual loop you must assemble knowledge from `docs/phase4/PI_IMAGE_AND_ONBOARDING.md`, `docs/runbooks/enrollment-failure.md`, `deploy/*.json`, `bin/falcon --help`, and this program's environment facts. The commands themselves are straightforward once found.
3. **Hidden environment prerequisites:** `PYTHONPATH=$REPO/src` (or `bin/falcon`), PyYAML for validate, `openssl`, root for image work, Docker for NM profile validation, `/home/user/.env` keys `wifi_ssid`/`wifi_key` for the baker, and the pinned base image under `/tmp/opencode/pi-image` (still present). None of these are in the README.
4. **Three secret locations, only two documented.** `AGENTS.md` says `/srv/falcon/secrets` + `/home/user/.env`; the edge program actually uses `/home/user/falcon-edge-secrets` (CA, signing seed, DB, ingest spool). New secrets work starts in the wrong place until you read `deploy/edge-control-plane.lab.json`.
5. **"build-image" naming collision.** `falcon deploy edge build-image` builds the signed *release bundle*, not the flashable Pi image (`bake_lab_test_image.sh` → `image/build-pi-image.sh`). The real image pipeline is not exposed through the CLI. I lost time on this.
6. **Append-only history makes "now" hard to find.** Multiple closeouts keep their original verdicts and amend later; the FINAL_RESPONSE and PROGRAM_CLOSEOUT are internally inconsistent (F-03). The reliable path is gate ledger → phase closeout amendment → newest evidence; that path is not signposted.
7. **Hardcoded absolute paths** in `automation/validation/*` and the installed systemd units (`REPO="/home/user/falcon-edge-build"`) mean a second checkout or a moved repo breaks scripts and host services — surprising for a repo that preaches reproducibility.
8. **Evidence workflow overhead.** `capture.sh` is easy, but a newcomer must remember index.sh + manifest.sh afterwards; the in-flight capture warning in `validate.sh` (WARN, not FAIL) is easy to misread as a failure. Also `capture.sh` does not redact unknown argv (documented in AGENTS, but easy to forget).
9. **A live shared lab with concurrent sessions.** During my 35-minute audit, HEAD advanced 4 commits and two device drills ran (P9-G04 hard resets, P7-G06 recovery drill); the Pi was rebooting underneath my SSH checks. There is no obvious "who owns the device right now" signal. A newcomer could easily collide with a running test.
10. **The control-plane database is noisy by design.** `list` shows 8 non-ACTIVE sensors and 10 unredeemed tokens; without reading OWNER_ACTIONS, a newcomer may "clean up" residue that is intentionally retained (RETIRED/RETIRED history) or, worse, reactivate a revoked one.
11. **Update/rollback mental model.** The A/B story is documented, but the Pi 3B cannot do it (no tryboot); the live update path is a privileged in-place package swap with a single rollback copy. The "real" A/B design remains aspirational until different hardware appears. `P7-G05` blocked is correct but the reasons are spread across phase-5/7 docs.
12. **Testing expectations.** The suite is 161 tests/93 s, but the README never says how to run it (only `docs/phase1/TEST_PLAN.md` and the review do), and there is no lint/test CI in the conventional sense — `ci/validate.sh` is static only.

**The missing/implicit steps, condensed as a would-be quick start**

```bash
# 0. Environment
export PYTHONPATH=/home/user/falcon-edge-build/src      # or use bin/falcon
# secrets: /home/user/falcon-edge-secrets (created by the control plane on first run)

# 1. Static validation + tests (no root)
cd /home/user/falcon-edge-build
ci/validate.sh
python3 -m unittest discover -s tests -p "test_*.py"

# 2. Run the control plane (lab host; already installed as a service here)
python3 -m falcon_control --config deploy/edge-control-plane.lab.json
# or: systemctl status edge-control-plane.service

# 3. Operate
bin/falcon --json deploy edge list
bin/falcon --json deploy edge inspect --sensor-id <id>
bin/falcon --json deploy edge create-token --profile PASSIVE_EDGE --ttl 600 --out /tmp/token

# 4. Enroll a device-local agent (same code path as first boot)
bin/falcon --json deploy edge enroll --state-dir /tmp/agent --token-file /tmp/token

# 5. Rebuild the flashable Pi image (root; needs .env wifi creds + base image)
automation/validation/bake_lab_test_image.sh
image/verify-pi-image.sh --image /home/user/falcon-edge-delivery/falcon-edge-sensor-<v>-arm64.img.xz

# 6. Evidence per change
automation/evidence/capture.sh --gate <GATE|REVIEW-FIX> --name <short> -- <command>
automation/evidence/index.sh && automation/evidence/manifest.sh create
```

---

## 6. Documentation inaccuracies found (exact locations)

| # | Location | Says | Actual (verified) |
|---|---|---|---|
| 1 | `README.md:23` | Hardware "Not attached to the lab host — hardware gates stay blocked" | Pi attached/enrolled; RTL8812BU attached; MT7612U absent; device gates mostly PASS |
| 2 | `REPOSITORY.md:22` | `HARDWARE` "not present" | same as above |
| 3 | `AGENTS.md:44-45` | "planned adapter hardware (RTL8812BU/MT7612U) is NOT attached" | RTL8812BU (`0846:9055`) attached and proven (P6-G05 PASS) |
| 4 | `closeout/FINAL_RESPONSE.json` | `commit=6cad6ec`, "the commit above is the latest ledger/evidence change" | 7+ commits behind at observation (HEAD `cfaf09d`, later `96c3e08`) |
| 5 | `closeout/PROGRAM_CLOSEOUT.md:14` | "full suite is green (120 tests)" | 161 tests |
| 6 | `closeout/PROGRAM_CLOSEOUT.md` update § | "18 artifacts with SHA-256 and sizes" | 31 artifacts in the current signed manifest |
| 7 | `ledgers/gate_ledger.csv` P10-G05 note | "lab6 image digest embedded" | current SBOM/manifest cover lab7 |
| 8 | `docs/phase6/CLOSEOUT.md:42-43` | "4 PASS / 3 BLOCKED / 1 IE" | 5 PASS / 2 BLOCKED / 1 IE (P6-G05 later PASS) |
| 9 | `docs/phase4/CLOSEOUT.md:38` | "CLI with 16 commands" | 18 subcommands |
| 10 | `README.md` layout table | `bootstrap/` "(later) lab host provisioning steps" | directory does not exist |
| 11 | `docs/README.md` | phase dirs "1..10" hold plans/closeouts | `docs/phase10/` is empty; phase-10 docs live in `closeout/` |
| 12 | `image/overlay/etc/falcon-agent/README` | `falcon-firstboot.sh` installs token 0600 | obsolete script; deployed bootstrap uses `falcon-bootstrap.sh` and 0640 root:falcon-agent |
| 13 | `tests/phase10/test_release_artifacts.py:15` | references `templates/agent_final_response.schema.json` | `templates/` does not exist (unused constant) |
| 14 | `ledgers/progress_ledger.md` X-043 | heartbeats "monotonic ACTIVE" | envelope analysis records 3 DELIBERATE `DEGRADED` samples (reviewer F7; being corrected in a sibling commit) |
| 15 | External brief supplied with this audit | "the planned adapter hardware (RTL8812BU/MT7612U) is NOT attached" | the RTL8812BU is attached (MT7612U is not) |

Notes: items 4–8 are partially tracked in `ledgers/contradiction_ledger.md` C-101…C-105 (OPEN, awaiting reviewer re-verification) and `closeout/OWNER_ACTIONS.md`; items 1–3 are **not** tracked anywhere and are the most damaging for onboarding.

---

## 7. Quick wins (ordered by value/effort)

1. **Fix the hardware/status lines** in `README.md`, `REPOSITORY.md`, `AGENTS.md` and add a "current state (updated …)" line pointing to `ledgers/gate_ledger.csv` + `closeout/OWNER_ACTIONS.md`. (~15 min, huge onboarding payoff.)
2. **Regenerate `FINAL_RESPONSE.json`** after the in-flight drills (`closeout/generate_final_response.py`), fix `commit_note`, and append phase-6 count corrections; mark the PROGRAM_CLOSEOUT "120 tests/18 artifacts" text as superseded. (~1 h.)
3. **Sync the OpenAPI contract** with the three missing routes and add the CI route-parity check. (~2–3 h; prevents a whole class of future drift.)
4. **Fix `purge_expired()`** to use the age cutoff and add the mixed-queue test; decide whether to call it from `cycle()`. (~30 min.)
5. **Filter expired directives** in `fleet_metrics.py` (or implement agent acknowledgement) so the dashboard gauge is honest. (~30 min.)
6. **Commit the six maintenance unit files** under `deploy/maintenance/` with an install/rollback note; reference them in D-007 and phase-8 closeout. (~1 h.)
7. **Remove or deprecate `falcon-firstboot.sh`** and fix the overlay README (obsolete script is an image-work trap). (~15 min.)
8. **Add a `QUICKSTART.md`** (or extend README) containing the §5 command block: start CP, token/claim/enroll, tests, image bake/verify, evidence flow, and the PYTHONPATH/secrets/env prerequisites.
9. **Add token pruning/reporting** and remove the stray root-owned `control.db` (owner action); document the secrets layout in `AGENTS.md`.
10. **Template the Vector profile identity/URL** or document the single-sensor assumption prominently in `profiles/README`.
11. **Refresh the delivery set** (agent bundle + manifest + SBOM + review package) from the freeze commit once the update-apply drill finishes; this is the P10-G01/G03/F11 closure path.

---

## 8. Open questions — what I would ask a human

1. **Source of truth:** when README/closeouts/ledgers disagree, is the gate ledger + latest closeout amendment always authoritative? Should I update the stale front-page docs, or is the stale text considered "historical record" that must not be touched?
2. **Worktree workflow:** the repo is live and shared; HEAD moved 4 commits during my audit. Is there a procedure for "I want to run something on the Pi" — a lock/claim, a channel in chat, or just check `ps`? (I observed a hard-reset endurance run rebooting the Pi while I read it.)
3. **Remote policy:** local `main` is ahead of `origin/main` (`github.com/MaineCyberTech/falcon-edge`). Is pushing part of the release ritual, or is the remote a mirror only? (No force-push is clear; push timing is not.)
4. **The three maintenance units on the host** (`falcon-edge-metrics`, `-operator-cert`, `-secrets-backup`): intentionally host-local, or should they move into `deploy/` and the review package? The D-007 rollback note mentions only metrics.
5. **ED-19:** who is the independent reviewer / acceptance authority? The review package and every phase closeout are waiting on this; it is repeatedly called "the biggest unlock".
6. **Owner decision batch** (P0-G03/G05/G06; ED-05…ED-18): has the owner confirmed OS/storage, monitoring scope details, and adapter certification strategy? Several gates remain INSUFFICIENT_EVIDENCE solely on this.
7. **Pi 3B and A/B:** tryboot is impossible on this board, so the A/B/rollback design (ED-14) cannot be fully proven here. What is the target hardware for a real slot test, and is the in-place package swap (current live update path) the accepted lab substitute?
8. **Image roadmap:** lab7 predates the update-apply feature that the live card runs, and the auto-renewal feature is also live-patched. Is a lab8 rebuild planned to make the clean artifact match the live card? Should the agent bundle be part of the signed manifest from then on?
9. **Soak approval (P9-G06) / hard-reset approximation (P9-G04):** P9-G04 was just closed by a sibling session using forced resets; is the 2-hour lab soak accepted as the alternative to 72 h? These are owner decisions per `OWNER_ACTIONS.md`.
10. **Alert rules deployment:** the monitoring program's Prometheus has no `rule_files` mount; is changing that owned by this program or the monitoring program? (Dashboard is live; rules are not.)
11. **Production crypto/SBOM:** pure-Python Ed25519 and package-level CycloneDX are explicitly lab-grade. Is selecting the production library/tooling in scope now, or only when a production deployment is planned?
12. **Residue policy:** the live CP DB intentionally keeps 5 RETIRED / 3 REVOKED sensors and 10 unredeemed tokens. Should a new developer ever prune these, and with which tool/approval?
13. **`purge_expired`:** is it intended to run periodically (then it needs the fix and wiring), or is it dead code to remove?
14. **Two first-boot scripts:** is `falcon-firstboot.sh` retained for any reason, or can it be deleted?

---

## 9. Appendix A — Repository map for a newcomer

| Path | What it is | Start here |
|---|---|---|
| `README.md`, `AGENTS.md`, `REPOSITORY.md` | entry docs (partly stale; see F-01/F-10) | read, then re-check status docs below |
| `ledgers/gate_ledger.csv` | **authoritative** gate status + evidence refs | always |
| `closeout/OWNER_ACTIONS.md` | what needs the owner, current state | always |
| `closeout/REVIEW-2026-09-30.md` | independent review, findings F1–F11 | review context |
| `closeout/PROGRAM_CLOSEOUT.md`, `FINAL_RESPONSE.json` | summary artifacts (stale; F-03) | cross-check only |
| `docs/phase0…phase9/`, `docs/runbooks/` | discovery, designs, test plans, closeouts, 15 runbooks | as needed |
| `api/openapi`, `api/schemas`, `api/generate_*.py` | contract + generated schemas/models | contract work |
| `src/falcon_agent`, `src/falcon_control`, `src/falcon_common`, `src/falcon_cli` | agent, control plane, crypto/models, CLI | code |
| `deploy/` | systemd units + lab/example configs (missing maintenance units; F-06) | deploy |
| `image/` | bundle builder + real Pi image builder/verifier + overlay | image work |
| `profiles/` | sensor profiles, Pi hardening, adapter plans | device work |
| `automation/evidence`, `automation/validation`, `automation/observability`, `automation/ledger` | evidence tooling, drills/builders, metrics, ledger generation | operations |
| `tests/phase0…phase10` | unittest suites + walkthroughs | testing |
| `evidence/raw`, `ledgers/` | append-only evidence + derived ledgers | audit |
| `config/` | Grafana dashboard + Prometheus alert rules (rules undeployed) | observability |
| `/home/user/falcon-edge-delivery` | images, keys, credentials (0600), SBOMs, signed manifest, review packages | release |
| `/home/user/falcon-edge-secrets` | live CA, signing seed, DB, ingest spool (0700) | **never commit/print** |

## 10. Appendix B — Verified health snapshot (2026-09-30 ~03:25Z)

- Control plane: systemd `edge-control-plane.service` active, v0.1.0, `0.0.0.0:9443`, one process (MainPID 440203, up since 00:51Z).
- Sensor `fes_b9f5c03d58713121659f1796`: ACTIVE, PASSIVE_EDGE, configRevision 1, cert expires 2026-10-30, heartbeat ≤30 s old; Vector ingest arriving every few seconds.
- Fleet: 9 sensors (1 ACTIVE, 5 RETIRED, 3 REVOKED); 459 idempotency records; 2,286 audit entries; exporter textfile fresh (03:23Z, 73 metric lines).
- Pi: RPi 3B Rev 1.2; Debian 13, kernel 6.18.50; lab5 image + live-patched agent modules; eth0 10.11.12.158 / wlan0 192.168.111.170 / wg0 10.99.0.30; disk 12%, 593 MiB available, `throttled=0x0`; agent/Suricata/Vector/pmacctd/update-apply path/cert-reload path active; Kismet idle (P6-G04 blocked).
- Adapters: RTL8812BU (NetGear A6150) attached; MT7612U absent.
- Repo: `ci/validate.sh` ALL PASS; 161 tests OK; evidence manifest 593/593; release manifest 31/31 + valid signature; SBOM 714 components.

*End of report.*
