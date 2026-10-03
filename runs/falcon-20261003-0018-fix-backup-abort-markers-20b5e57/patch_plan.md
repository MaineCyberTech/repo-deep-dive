# Patch Plan

Run `20261003-0018-fix-backup-abort-markers-20b5e57` — `falcon` @ `20b5e57`.
Implementation-ready patches for the highest-value findings. Each patch lists files, the change, and validation. Do not bundle unrelated changes.

## Patch 1 — Abort-marker contract (ARCH-P1-002)

**Files:** `bootstrap/85-backup-job.sh`, `bootstrap/lib.sh`, `automation/validation/tests/abort_marker_test.sh`

**Change:**
1. In `85-backup-job.sh`, do **not** call `clear_abort_marker` in the startup warning block; instead, if a marker is present, run (or force) the re-verification and only then return to normal flow, or fail closed. Remove the early clear.
2. Wrap the job so the marker is written on any non-clean exit: install a `trap` on `EXIT` that writes the marker unless a `BACKUP_OK=1` flag was set at the very end (after the final `clear_abort_marker`).
3. Keep the existing TERM/INT trap behavior (exit 130 + marker).
4. Ensure `clear_abort_marker "falcon-backup"` remains the last successful action.

**Validation:** extend `abort_marker_test.sh`:
- simulate a snapshot failure (`exit 1`) and assert `falcon-backup.aborted` exists afterwards;
- simulate a pre-existing marker and assert the re-verification path runs;
- simulate a clean completion and assert no marker remains.

## Patch 2 — Extend the abort trap to all long-running jobs (ARCH-P2-005)

**Files:** `bootstrap/80-offsite-backup.sh`, `automation/validation/r2_cold_copy.sh`, `automation/validation/wazuh_indexer_backup.sh`, `automation/validation/restore_rehearsal.sh`

**Change:** `source bootstrap/lib.sh` (where not already) and call `install_abort_trap "<job>"` early; call `clear_abort_marker "<job>"` only on clean completion.

**Validation:** a grep test asserting each long-running script calls `install_abort_trap`; extend `abort_marker_test.sh` to cover one additional job.

## Patch 3 — Offsite retry/backoff + dead-letter (FEAT-P2-002)

**Files:** `bootstrap/85-backup-job.sh`, `bootstrap/80-offsite-backup.sh`, `automation/validation/export_monitor_metrics.sh`

**Change:** retry the offsite copy N times with exponential backoff; on exhaustion, append a record to a dead-letter file and emit a `falcon_backup_offsite_dlq` metric; add a Grafana rule firing on a non-zero/dead-letter age.

**Validation:** fault-injection test with a stubbed object store returning 5xx; assert retries then DLQ + metric.

## Patch 4 — Monitoring-death independence (OBS-P0-001)

**Files:** `config/prometheus/prometheus.yml`, `bootstrap/90-alerting.sh`, `automation/validation/heartbeat.sh`

**Change:** add scrape targets that do not depend on the textfile exporter where endpoints exist; add a `falcon_*_last_run` staleness rule per critical exporter and an `up == 0` rule; ensure the dead-man/heartbeat path is independent of the textfile file.

**Validation:** stop the exporter timer; assert a staleness rule fires within the configured window.

## Patch 5 — Supply-chain gate scope + vuln gate (SUPPLY-P1-001, SUPPLY-P1-002)

**Files:** `ci/validate.py`, `automation/validation/check_compose_digests.py`, `.github/workflows/validate.yml`

**Change:**
1. Invoke `check_compose_digests.py` for each of `compose/`, `mct/compose/`, `automation/wazuh/` (or extend `--compose-dir` to accept multiple roots).
2. Pass `--max-lock-age-days 30`.
3. Run `sbom_coverage_check.sh --require-vuln` (scheduled if scanner availability is a concern).

**Validation:** mutate an `automation/wazuh` image ref and assert CI fails; stale lock fails; planted CVE fixture fails `--require-vuln`.

## Patch 6 — Release rebind + CI equality test (FINAL-P0-001, HYG-P0-001/002)

**Files:** `closeout/FINAL_RESPONSE.json`, `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `ci/validate.py` (or a new test under `automation/validation/tests/`)

**Change:**
1. Freeze a commit; rebuild the review package from that tree; regenerate `FINAL_RESPONSE.json`, `PACKAGE_DIGEST.txt` and the manifest from the same commit in the documented order.
2. Add a CI test that asserts: `repository_commit == CLOSEOUT_SOURCE_COMMIT == DELIVERED_PACKAGE_COMMIT == HEAD`, that the manifest hash matches a fresh build, and that `verify_publication_chain.sh` exits 0.

**Validation:** `bash automation/validation/verify_publication_chain.sh` returns 0 in a full clone; the new CI test passes and fails on a mutated digest.

## Patch 7 — Data retention (DATA-P1-001)

**Files:** `bootstrap/61-search-policies.sh`, `automation/validation/ism_retention_metrics.sh`

**Change:** add ISM policies for `wazuh-*` and an IRIS data lifecycle aligned to the owner's retention decision; add growth/projection rules.

**Validation:** `ism_retention_metrics.sh` reports coverage for every index pattern; a test asserts an ISM policy exists for each pattern.

## Patch 8 — Exposure edges (SEC-P1-001/002/003)

**Files:** `config/nftables/falcon.nft`, `compose/mct/docker-compose.opencanary.yml`, `bootstrap/32-inbound-mode.sh`, `docs/architecture/PORT_PROTOCOL_MATRIX.md`

**Change:** replace the blanket `iifname "wg0" accept` with per-destination/port rules; bind OpenCanary ports to a management interface; make the inbound state file authoritative and record each toggle in a ledger row; reconcile the architecture doc.

**Validation:** `nft` negative tests from a non-allowlisted source; `ss -ltn` shows decoys fenced; `32-inbound-mode.sh status` captured to evidence.

## Suggested validation commands

```bash
python3 ci/validate.py
bash automation/validation/verify_publication_chain.sh
bash automation/validation/tests/abort_marker_test.sh
bash automation/validation/sbom_coverage_check.sh --require-vuln
```

## Ordering

C0 (Patch 6) is independent. Within resilience: Patch 1 → Patch 2 → Patch 3. Patch 5 can proceed in parallel with Patch 4.
