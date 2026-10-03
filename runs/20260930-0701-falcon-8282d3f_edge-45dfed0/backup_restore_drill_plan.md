# Backup & Restore Drill Plan (Companion to 32_backup_restore_drill.md)

- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` · Central `8282d3f` · Edge `f1c5def` (manifest `45dfed0`)
- Generated: 2026-09-30 · Owner: falcon maintainer; restore/credential decisions require owner authorization
- Rule: no drill may overwrite live indices; scratch-only (`restored-*`, `restore-test-*`) unless the owner authorizes otherwise with a fresh snapshot first.
- Doctrine: every step captured with `automation/evidence/capture.sh`; secrets never in argv; failures recorded, not rewritten.

## 1. Backup Inventory (what exists today)

| # | Dataset | Mechanism | Location(s) | Cadence | Retention | Encryption | Verified how | Status |
|---|---|---|---|---|---|---|---|---|
| B1 | `falcon-*` indices (telemetry) | OpenSearch fs snapshot (`snap-*`) | local `/srv/falcon/backups/opensearch`; Spaces `monitoring/opensearch` | daily (duplicated) | local newest 3; offsite 7 inventories | local: volume perms; offsite: bucket/private (no client-side) | `_verify` + 3-file SHA read-back | OK/fragile (DR-P1-002/003) |
| B2 | Repo config (config, compose, bootstrap, automation, ci, docs, ledgers, pins) | tar.gz + AES-256-CBC/PBKDF2 | local `/srv/falcon/backups/config-<date>.tar.gz[.enc]`; Spaces `monitoring/backups/config/` | daily (duplicated) | local newest 3 (disk guard) | AES-256 (key host-side) | offsite SHA round-trip | OK; no digest (DR-P1-002) |
| B3 | New-services state (WireGuard keys, `mct.env`, `iris-web.env`, enrollment, `/opt/iris-web`, Wazuh registry/configs, IRIS dump) | root tar.gz (0600) | local `/srv/falcon/backups/falcon-new-services-*.tar.gz`; Spaces `monitoring/backups/new-services/*.enc` | daily | local newest 7 | local plaintext 0600; offsite AES-256 | item check (unevidenced) | Partial (DR-P1-002) |
| B4 | Edge PKI/DB (CA key+cert, signing seed, sensor certs, control-plane SQLite) | `backup_edge_secrets.py` tar.gz (0600) + sha256 | `/home/user/falcon-edge-delivery` (host-local) | daily 01:13Z | keep 7 | none (0600 archive) | sha256 sidecar only | Gap (DR-P1-005 / INTG-P1-003) |
| B5 | R2 searchable cold tier (`falcon-eve-2026.09.21`) | `remote_snapshot` mount from R2 | R2 bucket `falcon` (manual registration) | one-off | manual | provider-side; keys in owner `.env` | P9-G08 query proof | Manual (SEARCH-P2-004) |
| B6 | Wazuh indexer (`.security`, `wazuh-alerts-*`, dashboard state) | mount `/opt/wazuh-backups/elasticsearch` → `/snapshots`; no scheduled job | VM-local dir (stale 2026-09-21) | none | n/a | n/a | none | **No backup** (DATA-P1-002) |
| B7 | Grafana SQLite, Prometheus TSDB, ntfy DB, Redis | none | volume-only | none | n/a | n/a | none | Accept/rebuild decision (DR-P2-001) |
| D1 | Delivery artifacts (edge images, SBOM, manifests, agent bundle) | files in `/home/user/falcon-edge-delivery` (host-local) | same host | per release | manual | some 0600 | manifest hashes | Host-local |
| D2 | Backup encryption key, CA, cloud keys | owner custody (claimed) | **unknown** | n/a | n/a | n/a | not evidenced | Critical gap (DR-P1-004) |

## 2. Restore Dependency Inventory (order matters)

| Step | Dependency | Source | Notes |
|---|---|---|---|
| 1 | Host baseline (Ubuntu 24.04, packages, Docker) | `bootstrap/10-host-baseline.sh` | clean host; rollback `docs/phase1/ROLLBACK.md` |
| 2 | Storage LV `/srv/falcon` | `bootstrap/20-storage.sh` | snapshot path `path.repo` set by `60` |
| 3 | Firewall / SSH | `bootstrap/30`, `40` | keep isolated until security validation |
| 4 | Secrets custody (OpenSearch admin, Grafana, CA, **backup_enc.key**) | owner offline archive; `FINGERPRINTS.txt` | never regenerated without owner sign-off (CA rotation invalidates certs) |
| 5 | Repo at recorded commit | git clone @ published commit; `ci/validate.sh` | config archive is fallback (B2) |
| 6 | Config + render | `bootstrap/50`, `60`, `70` | `60` rebuilds security users/config; `70` probe render |
| 7 | Repo registration + snapshot restore | `POST /_snapshot/falcon-backup/<snap>/_restore` with `rename_*` | `include_global_state:false`; `.security` is rebuilt, dashboard saved objects rebuilt from repo |
| 8 | New-services unpack | B3 archive → `/etc/wireguard`, `/srv/falcon/secrets`, `/opt/*`, docker volumes | extract with `--absolute-names` (create used it); restart affected units |
| 9 | Edge PKI/DB unpack | B4 archive → `/home/user/falcon-edge-secrets`; restart `edge-control-plane.service` | **not offsite today** |
| 10 | Access/identity recovery | owner custody; rotate every credential used | RESTORE.md §4.8 |
| 11 | External paths | Cloudflare tunnels, WireGuard peers, notification paths | verify with `NOTIFICATION_SEPARATION_RUNBOOK` |
| 12 | Edge fleet | sensors re-enroll if PKI lost | avoid by restoring B4 from offsite |

## 3. Drill Plans

### D1 — Config + snapshot scratch restore (weekly; ~10 min; non-destructive)
- Preconditions: root wrapper; target cluster live; scratch-only.
- Steps: run `automation/validation/restore_rehearsal.sh`; confirm nonzero exit on any `FAILED`; record download/decrypt/restore seconds and doc counts.
- Pass: offsite config archive SHA matches local; `gzip -t` OK; newest snapshot restores `restore-test-*` with count > 0; cleanup done; exit 0.
- Evidence: `--gate P6-G09` capture; update `test_execution.csv`.
- Fix-first: add fail-fast + offsite restore leg (DR-P1-003).

### D2 — Offsite retention integrity (after every retention run, and monthly)
- Steps: list retained inventories; for the newest snapshot, download its `snap-*.dat` + a random 10 files from each retained inventory; compare SHA-256; then on a scratch node register the offsite repo copy (or a downloaded full copy) and restore one index.
- Pass: every sampled file hash-matches and the index restores. Fail: freeze retention, re-upload from local, file DR-P1-002.
- Evidence: capture with sampled names/hashes; note the offsite repo is list-free (paths from inventories).

### D3 — Snapshot-only restore regression (monthly)
- Steps: `phase6_backup_restore.sh` on a maintenance window; verify scratch `restored-*` counts; delete scratch.
- Pass: repository `_verify` 200; snapshot SUCCESS; restored docs > 0; no live index touched.
- Note: script also rebuilds the probe — run only with the owner-approved window.

### D4 — Clean-host full reconstruction (quarterly; ~2–4 h)
- Steps: per `docs/phase9/CLEAN_HOST_REBUILD_RUNBOOK.md`; extend to unpack B3 (new-services) and B4 (edge PKI/DB) and re-enroll a test sensor; verify services, firewall, TLS, VPN, feeds, dashboards, alerting, backup timer, post-restore ingestion.
- Pass: no dependency on the original host; RPO/RTO targets met; sensor enrolls with restored CA; record measured RPO/RTO.
- Evidence: new gate capture + ledger entry.

### D5 — Bad-migration drill (quarterly; fixture indices only)
- Steps: create fixture `falcon-mig-drill-*`; run a rename/reindex variant from `index_rename_migration.sh` against it; kill the reindex mid-flight; assert: source intact, destination partial, counts differ, no deletion of source; then clean up; also test wrong-mapping path (reject) and task-cancel path.
- Pass: no data loss; documented abort procedure works; script guard (`:40`) honored.
- Evidence: capture PASS/FAIL; add regression note.

### D6 — Secrets/key custody drill (semiannual)
- Steps: offline owner copy only → decrypt newest Spaces config archive, download one snapshot file, open edge PKI/DB archive; verify fingerprints.
- Pass: all readable with custody material alone; record where custody copies live (path + type only).
- Fail: restore key escrow before production.

### D7 — Total-loss rehearsal (annual; tabletop + partial live)
- Steps: assume host destroyed; walk D4 using only offsite + custody; time each phase; reconcile with owner RPO/RTO; document gaps (Wazuh, Grafana/Prometheus/ntfy/Redis).
- Pass: decision log entry + updated coverage matrix.

## 4. Tenant / Site Integrity Validation After Restore

Single owner/tenant lab, but the site boundary matters (`falcon_reader` vs `other-site-index`, `site_id`). After any restore:
1. `_count` per restored index vs snapshot metadata doc counts (tolerance 0; record).
2. Assert per-site isolation: query by `site_id` returns only expected sites; `other-site-index` denies for `falcon_reader` (reuse `phase4_data_checks.sh` boundary test).
3. Confirm newest restored event timestamp vs snapshot time (RPO actual).
4. Confirm aliases/templates/ISM attachments are re-applied (`falcon-eve-policy`), and the reader role still resolves.
5. Record counts before/after and cleanup of scratch names.

## 5. Verification Checklist (per drill)

- [ ] Owner authorization recorded; window/scope stated.
- [ ] Scratch-only names used (`restored-*`, `restore-test-*`, `falcon-mig-drill-*`).
- [ ] Evidence captured (start/end UTC, command, exit code, SHA-256, commit).
- [ ] Archive/repo identity verified before use (hash/`_verify`).
- [ ] Restore measured (seconds, docs, shards OK) and compared to RPO/RTO.
- [ ] Site/tenant integrity checks (above) executed.
- [ ] Credentials used rotated; scratch removed.
- [ ] `test_execution.csv` + relevant ledger updated append-only.
- [ ] Post-drill data flows confirmed (event age, DLQ, feeds).

## 6. RPO/RTO Reference (owner-approved, P6-G09)

| Metric | Target | Last measured (2026-09-23) | Note |
|---|---|---|---|
| RPO | ≤ 24 h (daily snapshot) | snapshot cadence daily; offsite copy depends on run | Offsite silent staleness is the real RPO risk |
| RTO config | ≤ 1 h | ~2–3 min (lab) | Restore-runbook steps |
| RTO data | ≤ 4 h | 7 s for 720,474 docs; 52 s / 4.79 M docs clean host | Lab-scale; re-measure at production size |

## 7. Cadence Summary

- Daily: job runs; check freshness metric + (new) offsite metric.
- Weekly: D1 + offsite retention sample (D2 after retention).
- Monthly: D3 + coverage-matrix review; verify edge backup schedule single-run.
- Quarterly: D4, D5; semiannual D6; annual D7.
- Any failed drill freezes retention changes until resolved.

## 8. Roles & Guardrails

- Owner: authorizes restores, credential actions, and any live-index overwrite; holds offline custody.
- Maintainer: runs drills, captures evidence, proposes fixes; never self-closes owner gates.
- Read-only auditors: may run non-mutating checks; destructive scripts (`phase6_backup_restore.sh` touches probe; `central_recovery_test.sh` restarts Docker) require the sanctioned window and capture.
- Forbidden in drills without explicit authorization: overwriting live indices, deleting `restored-*` outside cleanup, rotating the CA, deleting source indices during reindex, purging offsite files.

## 9. Evidence Templates

- Capture: `automation/evidence/capture.sh --sudo --gate <P6-G09|REVIEW-FIX> --name <drill>`.
- Record per drill: date/actor/commit, backup artifact IDs+hashes, restore target, measured RPO/RTO, integrity checks, deviations, follow-ups (`follow_up_register.md`).
- After any fix: re-run the affected drill and mark the finding `verified-fixed` only with an artifact at the current commit.
