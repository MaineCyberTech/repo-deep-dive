# Falcon Lab — Release Notes (audit cycle 2026-09-30)

**Audit run:** `20260930-0701-falcon-8282d3f_edge-45dfed0` · **Central:** `falcon-build` @ `8282d3f` · **Edge:** `falcon-edge-build` @ `45dfed0`
**Prior run:** `20260930-0320-falcon-794ba31_edge-2b5bc8b` (90 findings)
**Status of this document:** DRAFT from the audit — not a published release. Do not publish as "verified" until the P0 release-binding items below are repaired.

These notes summarize what changed in the repositories and on the shared lab since the prior audit, what remediation landed, and what remains known-open. They are written from the audit's evidence (commits, captures, ledgers), not from any shipped release artifact.

## Audit outcome at a glance

- **264 findings** registered this run: **13 × P0**, **80 × P1**, **131 × P2**, **40 × P3**.
- Prior run (90 findings) re-verified at the current commits: **1 verified-fixed** (digest derivation), **31 partially-fixed**, **53 still-open**, **2 regressed**, **3 not re-assessed**.
- **No P0 was verified-closed.** The 11 P0s are release-binding, credential, monitoring/backup-detection, and approval-independence issues; see "Known issues".

## Verified fixes and partial fixes since the prior run

- **Ledger-derived package digest** — `PACKAGE_DIGEST.txt` now derives verdict/readiness/open-gates from the ledgers (`publish_digests.sh:30-35`, commit `93ea9c6`); the publication chain verifies with 0 failures. Prior ND-P1-001 → **verified-fixed**.
- **Backup/offsite runner repaired** — the `.env` quoting bug that broke every `set -e` run is fixed; the offsite run completed **exit 0 at 2026-09-30 07:43Z**, and new-services uploads are encrypted with round-trip verification (`1f76aca`). Prior LIVE-P0-001/002 → **partially-fixed** (detectors still missing).
- **WireGuard peer preservation** — `95-wireguard.sh` merges/preserves runtime peers and a regression check (`wg_peer_preservation_check.sh`) exists; the edge peer `10.99.0.30` is live and reachable. Prior INTG-P0-002 → **partially-fixed** (template/docs stale).
- **Log growth and disk guards** — EVE/stats rotation and disk-guard pruning landed (`c5755f5`, `f1db6d8`); the data LV stabilised (~45–47 GB free). Prior LIVE-P0-003 → **partially-fixed** (no warning band; reclaim never exercised).
- **Alert-noise tuning** — TLS-silence window widened 30 m → 6 h (`d83f421`), labels and actionable links added; the alert catalogue is regenerated from live rules **31 = 31** (`a614af8`). Prior LIVE-P0-004 → **partially-fixed**, prior INTG-P2-004 catalogue part → **verified-fixed**.
- **CI hardening** — falcon gained `.github/workflows/validate.yml` + `ci/validate.py` (`6f33a06`) with follow-up fixes (`1dbb86c`, `80d8e8b`); edge gained ruff + independent gitleaks gates (`824f701`), zizmor + Python 3.13 matrix + release SHA256SUMS (`f0996b8`), and weekly drift + scheduled validate (`45dfed0`). Prior ND-P3-006/ND-P3-011 → **partially-fixed**.
- **Edge review/response consistency** — phase-10 consistency test is green and the gate-ledger CSV was repaired (`4332503`, `d6147ef`); prior REV-P1-006 → **partially-fixed** (commit lag and sidecar drift remain).
- **Edge fleet drill** — P9-G04 hard-reset endurance PASS (`96c3e08`, 10/10 to ACTIVE, 0 fs errors); approval of the reset approximation remains an open owner decision (D2).

## New findings that matter for operators

- **P0 — release binding:** approval/digest still bind a superseded package; the reviewed archive carries a denying digest (`EVID-P0-001`, `INV-P0-002`, `REV-P0-001`); the edge manifest sidecar no longer matches the signed manifest (`INV-P0-001`/`FLEET-P1-001`), and the pairing pin does not verify against the edge manifest (`XREPO-P0-001`).
- **P0 — independence:** the reviewer disposition is a transcription and the named reviewer is recorded as the system installer (`EVID-P0-002`).
- **P0 — detection:** the monitoring stack cannot announce its own death (relay-blind delivery, up to ~26 h on total loss, stale monitors read healthy — `LIVE-P0-001`, `RES-P0-002`); offsite backup outcomes are still invisible to alerting (`RES-P0-001`); a green backup can hide a stale offsite tier (`LIVE-P0-002`).
- **P1 — identity:** a single-use device token becomes fleet-wide operator authority (`ADV-P1-001`, `SEC-P1-001`/`ACM-P1-001`); the privileged update-apply path still trusts an agent-writable request (`SEC-P1-002`/`CTR-P1-002`).
- **P1 — capacity/availability:** root LV ~83 % with ~-3.8 GB/day and no reclaim path (`PERF-P1-001`); data-LV only guarded by an unexercised 10 GiB guard (`PERF-P1-002`).
- **P1 — edge:** the fleet is visible but not alertable (`LIVE-P1-003`/`OBS-P1-004`); edge PKI/DB backup remains local-only (`DR-P1-005`).

## User-facing notes

- No user-facing application changed. The lab's public surfaces (Wazuh 1516/1517, client-VPN enrollment) are unchanged and remain under audit remediation (`SEC-P2-005`, `API-P2-005`).
- The "synthetic traffic" privacy claim is contradicted by live real owner-device telemetry; privacy authority is pending an owner decision (`PRIV-P1-001`). Do not repeat the synthetic-traffic claim in any external note until that decision is recorded.

## Administrator / operator notes

- **Backups:** the offsite run succeeded on 09-30, but its recovery evidence is uncommitted and there is still **no alert on offsite/new-services outcomes**. Treat backup "green" as unverified for the offsite tier until `RES-P0-001`/`DR-P1-001` land. The new-services check completeness is unproven (`DR-P1-002`).
- **Alerts:** a genuinely dead Wazuh/TLS path now pages up to 6 h late; a relay-only failure is invisible to the dead-man (`RES-P0-002`); the 09-28 outage produced no external notification (`RES-P1-001`). Do not rely on the current dead-man as a total-loss guarantee.
- **Disk:** root LV has no guard/reclaim and the warning band is late; the disk-guard reclaim has never fired (`RES-P1-005`).
- **Edge:** no central alert covers the edge path even though prepared rules exist (deployment blocked, owner decision D3). Edge update apply is not power-loss safe and no OS/rootfs rollback exists (`FLEET-P1-002`).
- **Operator actions:** several owner decisions are recorded in the follow-up register (D1–D8). The incident runbooks still describe a no-VPN/no-SPAN/no-backup lab and cannot be executed as written (`INFRA-P1-001`, `LIVE-P1-002`).

## Security notes

- A committed Wazuh credential set shipped through the secret scanner; the scanner is blind to the XML-tag credential form (`API-P0-001`, `EVID-P1-004`, `SC-P1-001`). **Rotate/remove and rescan before any release.**
- Unencrypted edge PKI/secret backups and private keys remain in the shared delivery directory, hash-listed in the signed manifest (`SECRET-P1-003`, `SECRET-P2-001`, `XREPO-P1-003`).
- The owner credential file remains a cleartext multi-class store sourced into capture environments (`SECRET-P1-002`, `PRIV-P1-002`).
- Sensor images bake host/Wi-Fi credentials shared across environments (`SECRET-P1-001`).
- No credential values were printed in this audit; references are path/type only.

## Upgrade / rollback notes

- **Central delivery:** do not treat the current package/verdict as a releasable binding — the approval binds a superseded package and the verdict contradicts itself (`EVID-P0-001`, `EVID-P1-002`). If a package must ship, record a fresh rebind and a decision-log entry.
- **Edge:** the live unit runs lab5 plus in-place agent updates; no released image/SBOM reproduces it (`FLEET-P2-003`). Upgrades are apply-then-verify with rejection of broken bundles proven (`0b83acc`), but there is **no crash-consistent rollback** on the Pi 3B (`FLEET-P1-002`).
- **Rollback:** keep the previous review package and manifest digest before any upgrade; verify `sha256sum -c` on the shipped set (currently FAILs on the sidecar — rebuild first).

## Migration steps

- None for this cycle: no central schema migrations exist; OpenSearch retention is ISM-only. There is no migration mechanism for the edge SQLite store (`EVOL-P2-003`); no index-rename/rollback drill exists (`DR-P2-002`). If you change index mappings, do it behind the mapping guardrail template and capture the revert plan first.

## Known issues (blocking a truthful release)

1. Approval/digest/verdict bind a superseded package (`EVID-P0-001`, `INV-P0-002`, `REV-P0-001`).
2. Reviewer independence is unverifiable; installer named as reviewer (`EVID-P0-002`, `REV-P1-001`).
3. Edge manifest sidecar fails verification; manifest rewritten in place (`FLEET-P1-001`, `XREPO-P1-001`).
4. Credentials in repo/package/delivery; scanner blind spots (`API-P0-001`, `EVID-P1-004`, `SC-P1-001`).
5. Monitoring/alerting cannot report its own death; offsite unalerted (`LIVE-P0-001/002`, `RES-P0-001/002`).
6. No license gate; no public release key (`SBOM-P1-001`, `SBOM-P2-004`).
7. Owner decisions D1–D8 open (register).

## Verification performed for these notes

- Prior-run statuses reconciled across domain/lens reports at `8282d3f`/`45dfed0` (90/90 accounted).
- Commit-cited fixes cross-checked against the reports that reproduced them.
- Release filenames verified versioned; manifest sidecar verification reproduced FAIL; digest binding read directly from `PACKAGE_DIGEST.txt` (binds `3ac6cd4`).
- No secret values printed; redaction/paths only.

## What's next

1. Rebind the release (manifest + sidecar + digest + verdict, atomically) and rotate the exposed credentials.
2. Close the detection gaps (offsite metrics/alerts, relay-independent dead-man, edge rules deployment).
3. Add `CHANGELOG.md` + `VERSION` + tags, and adopt the `changelog_draft.md` categories for every future release.
