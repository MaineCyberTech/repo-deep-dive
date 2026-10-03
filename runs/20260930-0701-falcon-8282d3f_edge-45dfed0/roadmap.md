# Remediation Roadmap — run `20260930-0701-falcon-8282d3f_edge-45dfed0`

Findings IDs are the authoritative set (256). Windows follow the shared rules: P0 same day (release blocking), P1 this week, P2 this month, P3 this quarter. Nothing closes without a verification pass at the then-current commit; `partially-fixed` items are listed at their residual scope. Patch-set mappings are in `patch_plan.md`.

## Immediate / Release Blocking (P0)

Still required before any release is described as approved or delivered. Owner blocks: `owner` for verdict/approval items, `falcon`/`both` for artifacts, `falcon/ops` for the live alert/backup items.

| ID | Action | Owner | Effort |
|---|---|---|---|
| API-P0-001 | Rotate the exposed Wazuh/VT/Shuffle credentials; redact in place and record hashes; rebuild package/delivery; close the scanner's XML-tag blind spot. | falcon | S |
| EVID-P0-001 | Re-review and rebind approval to the exact delivered commit (or rebuild an immutable package at `c312ab7`); stop publishing gate flips with the approval commit. | owner | M |
| EVID-P0-002 | Obtain a reviewer-produced signed disposition with provenance; disambiguate JPB (installer vs reviewer) or replace the reviewer; record the outcome. | owner | M |
| INV-P0-001 | Version the manifest filename; regenerate the `.sha256` sidecar atomically; update the pin; add a drift check that fails on mismatched cited digests. | both | S |
| INV-P0-002 | Make `PACKAGE_DIGEST.txt`, `FINAL_RESPONSE.json` and the verdict derive from one source; fail closed on non-APPROVED content; re-freeze. | owner | M |
| LIVE-P0-001 | Deploy relay canary on the independent instance; add watcher-age/freshness rules for every timer and exporter; shorten the host-loss threshold; write the blind-ops checklist. | falcon/ops | M |
| LIVE-P0-002 | Add offsite and new-services last-success gauges + 36 h staleness rules; commit/rebind the recovery capture; retained-union remote retention; record key custody. | falcon/ops | S/M |
| RES-P0-001 | Emit offsite last-success metric and add the offsite-stale alert; force a failure and confirm one alert per ntfy path. | falcon/ops | S |
| RES-P0-002 | Add an end-to-end canary that must arrive each cycle plus a relay freshness rule; drill by stopping the relay for 15 minutes. | falcon/ops | M |
| REV-P0-001 | Re-review over the exact delivered archive; make re-review mandatory on rebuild; CI equality check verdict ↔ digest ↔ shipped packet. | owner | M |
| XREPO-P0-001 | Regenerate the pairing pin from the current edge manifest; add `verify_edge_pin.sh` (digest/commit/SBOM/artifact names); stop hand-copying digests. | both | S |

## This Week (P1 — 74)

Ordered by the seven patch sets. Security substance first, then release records, then the operational/pipeline P1s.

### Release records and artifact consistency (9)

- `DOC-P1-001` — Falcon entry docs still contradict the ledgers on current state _(owner: falcon, effort: S)_
- `EVID-P1-001` — The delivered package ships closeout records that do not match the delivery… _(owner: falcon, effort: S)_
- `EVID-P1-002` — FINAL_RESPONSE.json contradicts PACKAGE_DIGEST.txt at HEAD _(owner: falcon, effort: S)_
- `FEAT-P1-001` — Status claims in README, AGENTS.md and edge FINAL_RESPONSE.json contradict t… _(owner: both, effort: S)_
- `FEAT-P1-002` — Published production verdict and current digest bind different artifact sets _(owner: owner, effort: M)_
- `FLEET-P1-001` — Release manifest checksum sidecar no longer matches the signed manifest _(owner: edge, effort: S)_
- `INV-P1-001` — README/AGENTS still describe the pre-closure open-gate state _(owner: falcon, effort: S)_
- `REV-P1-002` — Machine-readable verdict artifacts disagree at HEAD and are not derived from… _(owner: falcon, effort: S)_
- `XREPO-P1-001` — The signed release manifest is rewritten in place _(owner: both, effort: S)_

### Security and isolation (18)

- `ACM-P1-001` — Operator authority is derived from an enrollable certificate subject string… _(owner: edge, effort: M)_
- `ACM-P1-002` — Lifecycle state is not enforced everywhere: revoked ingest, inert destroyKey… _(owner: edge, effort: S/M)_
- `ADV-P1-001` — A single-use device token becomes fleet-wide operator authority (reproduced) _(owner: edge, effort: M)_
- `ADV-P1-002` — One readable directory (or one lost device) exposes CA, operator and update… _(owner: edge, effort: M)_
- `API-P1-001` — Enrollment signs an unconstrained CSR subject _(owner: edge, effort: S)_
- `ARCH-P1-003` — Trust-boundary matrix does not match live port binds _(owner: falcon/ops, effort: S/M)_
- `CTR-P1-001` — Root systemd services execute code from user-writable repository trees _(owner: both, effort: M)_
- `CTR-P1-002` — Privileged update-apply path trusts an agent-writable request (REV-P1-005) _(owner: edge, effort: M)_
- `EVID-P1-004` — Secret literals ship in repo/package/delivery _(owner: falcon, effort: S/M)_
- `PRIV-P1-001` — "Synthetic traffic" privacy claim is contradicted by live real owner-device… _(owner: owner, effort: M)_
- `PRIV-P1-002` — Evidence-capture wrappers export the whole credential file into captured com… _(owner: both, effort: S)_
- `SC-P1-001` — Secret-scan controls have systemic false-negative blind spots _(owner: both, effort: M)_
- `SEC-P1-001` — Enrollment signs attacker-supplied CSR subjects _(owner: edge, effort: M)_
- `SEC-P1-002` — Root update-apply trusts an agent-writable request file (REV-P1-005 still-op… _(owner: edge, effort: M)_
- `SECRET-P1-001` — Host and Wi-Fi credentials are baked into sensor images and shared across en… _(owner: edge, effort: M)_
- `SECRET-P1-002` — /home/user/.env is a single cleartext multi-class credential store driving r… _(owner: falcon/ops, effort: M)_
- `SECRET-P1-003` — Edge secret backups are unencrypted in the delivery surface and hashed in th… _(owner: edge, effort: M)_
- `XREPO-P1-003` — Secret material in the shared delivery directory and delivery archives _(owner: both, effort: M)_

### CI and supply chain (6)

- `ARCH-P1-002` — Live services execute code from dirty working trees, and "what is deployed"… _(owner: both, effort: M)_
- `BP-P1-001` — Neither main is protected _(owner: owner, effort: S)_
- `INTG-P1-002` — The pair has no joint release gate, upgrade order, or atomic rollback _(owner: both, effort: M)_
- `INV-P1-002` — Live images and vendored stacks sit outside the pin check _(owner: falcon, effort: S)_
- `SBOM-P1-001` — No license data or license gate exists _(owner: both, effort: M)_
- `XREPO-P1-004` — No automated pin verification or skew detection _(owner: both, effort: S)_

### Data, retention and backups (16)

- `DATA-P1-001` — Schema and retention controls exist only in validation scripts, not in deplo… _(owner: falcon, effort: M)_
- `DATA-P1-002` — Wazuh indexer data has no scheduled backup _(owner: falcon, effort: M)_
- `DATA-P1-003` — purge_expired() deletes non-expired queue items (latent data loss) _(owner: edge, effort: S)_
- `DQ-P1-001` — DLQ counts only pre-sink validation errors _(owner: falcon, effort: M)_
- `DR-P1-001` — Offsite outcome still has no metric/alert, and its recovery evidence is unco… _(owner: falcon, effort: S)_
- `DR-P1-002` — Backup verification weaknesses: offsite retention deletes blobs by stale inv… _(owner: falcon, effort: M)_
- `DR-P1-003` — Backup structure: duplicate snapshots/config per run, undocumented window, r… _(owner: falcon, effort: M)_
- `DR-P1-004` — Secrets and backup-key custody unverified _(owner: owner, effort: S/M)_
- `DR-P1-005` — Edge PKI/DB backup remains local-only (prior INTG-P1-003) _(owner: both, effort: S/M)_
- `LIVE-P1-001` — Disk pressure leaves the operator a late signal, a mislabelled alert and an… _(owner: falcon, effort: M)_
- `OBS-P1-002` — Offsite and new-services backup outcomes are unmonitored _(owner: falcon, effort: S)_
- `PERF-P1-001` — Root LV is ~3 GB from its warning threshold with no reclaim path _(owner: falcon, effort: M)_
- `PERF-P1-002` — Data LV's only signal is an unexercised 10 GiB disk guard _(owner: falcon, effort: M)_
- `RES-P1-004` — Backup quality: new-services verification unproven, duplicate snapshots, und… _(owner: falcon, effort: S)_
- `RES-P1-005` — Capacity: root LV unguarded _(owner: falcon, effort: M)_
- `RES-P1-006` — Peers that never handshake are invisible (6 configured, 4 exported) _(owner: falcon, effort: S)_

### Operator experience and docs (6)

- `AI-P1-001` — Agent instruction files direct work at closed gates and stale environment fa… _(owner: both, effort: S)_
- `DOC-P1-002` — Edge entry docs state the hardware is absent _(owner: edge, effort: S)_
- `DOC-P1-003` — Falcon README quick start cannot deploy, and its first step fails in-tree _(owner: falcon, effort: S/M)_
- `INFRA-P1-001` — Incident runbooks contradict the live architecture (no VPN, no SPAN, no back… _(owner: falcon, effort: S)_
- `LIVE-P1-002` — The paged operator cannot execute the incident runbooks as written, and they… _(owner: falcon, effort: M)_
- `ND-P1-001` — No orientation layer tells a newcomer which status document is current _(owner: both, effort: S)_

### Observability and resilience (16)

- `ARCH-P1-001` — Single-host topology is a shared point of failure under live memory/disk pre… _(owner: falcon/ops, effort: M/L)_
- `FLEET-P1-002` — Update apply is not power-loss safe and the OS/rootfs rollback path does not… _(owner: edge, effort: M)_
- `INTG-P1-001` — The prepared edge alert-rule deployment targets a plane the central alert pa… _(owner: both, effort: M)_
- `IR-P1-001` — No tabletop scenario for total loss of the monitoring and alerting path _(owner: owner, effort: M)_
- `IR-P1-002` — Exercise coverage and artefacts fall short of the required catalogue _(owner: falcon, effort: M)_
- `LIVE-P1-003` — The edge fleet is visible but not alertable _(owner: edge, effort: M)_
- `NOTIF-P1-001` — Total-host failure still has no real-time external notification _(owner: falcon, effort: M)_
- `NOTIF-P1-002` — Relay acknowledges Grafana before delivery and keeps nothing on failure _(owner: falcon, effort: M)_
- `OBS-P1-001` — Total-host failure has no real-time external notification _(owner: falcon, effort: M)_
- `OBS-P1-003` — Monitoring-of-the-monitoring freshness, resources and alert-evaluation healt… _(owner: falcon, effort: M)_
- `OBS-P1-004` — Edge fleet has live metrics and dashboards but zero alerts _(owner: both, effort: M)_
- `OBS-P1-005` — Peers that never handshaked are invisible to the WireGuard stale rule _(owner: falcon, effort: S)_
- `RES-P1-001` — Total-host loss has up to ~26 h detection _(owner: falcon, effort: M)_
- `RES-P1-002` — Monitor freshness is not monitored _(owner: falcon, effort: M)_
- `RES-P1-003` — Edge path: no deployed alert and local-only PKI/DB backup _(owner: both, effort: M)_
- `XREPO-P1-002` — No central alerting for the edge path _(owner: both, effort: S)_

### Records, verdict and evidence (3)

- `AI-P1-002` — Edge review gates closed by a same-automation subagent review while R-002 st… _(owner: edge, effort: S)_
- `EVID-P1-003` — Doctrine docs and progress ledger describe the pre-closure state _(owner: falcon, effort: S)_
- `REV-P1-001` — The independence claim is self-referential _(owner: owner, effort: M)_

## This Month (P2 — 131)

Grouped by patch set; each line is one theme with its finding IDs and the concrete outcome. P2 work is where the systemic detectors live (staleness, drift, contract parity, mapping, retention observability).

### Release records and artifact consistency (4)

- **AI:** `AI-P2-003` · **DOC:** `DOC-P2-004` · **HYGIENE:** `HYGIENE-P2-003` · **SBOM:** `SBOM-P2-001`

### Security and isolation (26)

- **ACM:** `ACM-P2-001`, `ACM-P2-002`, `ACM-P2-003`, `ACM-P2-004` · **ADV:** `ADV-P2-001`, `ADV-P2-002`, `ADV-P2-003` · **AI:** `AI-P2-004` · **API:** `API-P2-005` · **ARCH:** `ARCH-P2-001`, `ARCH-P2-002` · **CTR:** `CTR-P2-004` · **FLEET:** `FLEET-P2-005`, `FLEET-P2-006` · **NOTIF:** `NOTIF-P2-001` · **PRIV:** `PRIV-P2-001` · **SC:** `SC-P2-001` · **SEC:** `SEC-P2-001`, `SEC-P2-002`, `SEC-P2-003`, `SEC-P2-004`, `SEC-P2-005` · **SECRET:** `SECRET-P2-004`, `SECRET-P2-005`, `SECRET-P2-006`, `SECRET-P2-007`

### CI and supply chain (25)

- **AI:** `AI-P2-005`, `AI-P2-006` · **API:** `API-P2-001`, `API-P2-002`, `API-P2-003`, `API-P2-004` · **BP:** `BP-P2-001`, `BP-P2-002`, `BP-P2-003` · **CI:** `CI-P2-001`, `CI-P2-002`, `CI-P2-004` · **CTR:** `CTR-P2-003`, `CTR-P2-005` · **EVOL:** `EVOL-P2-004` · **FLEET:** `FLEET-P2-003` · **HYGIENE:** `HYGIENE-P2-001` · **SBOM:** `SBOM-P2-002`, `SBOM-P2-003`, `SBOM-P2-004` · **SC:** `SC-P2-004` · **TEST:** `TEST-P2-001`, `TEST-P2-002`, `TEST-P2-004` · **XREPO:** `XREPO-P2-003`

### Data, retention and backups (27)

- **DATA:** `DATA-P2-004`, `DATA-P2-005`, `DATA-P2-006` · **DQ:** `DQ-P2-002`, `DQ-P2-003`, `DQ-P2-004`, `DQ-P2-005`, `DQ-P2-006`, `DQ-P2-007`, `DQ-P2-008` · **DR:** `DR-P2-001`, `DR-P2-002` · **EVOL:** `EVOL-P2-003` · **FEAT:** `FEAT-P2-001` · **FLEET:** `FLEET-P2-007` · **INFRA:** `INFRA-P2-003` · **INTG:** `INTG-P2-002` · **PERF:** `PERF-P2-001`, `PERF-P2-002`, `PERF-P2-004` · **PRIV:** `PRIV-P2-002` · **RES:** `RES-P2-002` · **SEARCH:** `SEARCH-P2-001`, `SEARCH-P2-002`, `SEARCH-P2-003`, `SEARCH-P2-004` · **TEST:** `TEST-P2-003`

### Operator experience and docs (19)

- **DOC:** `DOC-P2-001`, `DOC-P2-002`, `DOC-P2-003` · **EVOL:** `EVOL-P2-001` · **FEAT:** `FEAT-P2-002` · **FLEET:** `FLEET-P2-004` · **INFRA:** `INFRA-P2-001`, `INFRA-P2-002` · **INTG:** `INTG-P2-003` · **IR:** `IR-P2-001` · **LIVE:** `LIVE-P2-001`, `LIVE-P2-002`, `LIVE-P2-004` · **ND:** `ND-P2-001`, `ND-P2-002`, `ND-P2-003`, `ND-P2-004`, `ND-P2-005` · **RES:** `RES-P2-003`

### Observability and resilience (17)

- **EVOL:** `EVOL-P2-002` · **INTG:** `INTG-P2-001` · **IR:** `IR-P2-002`, `IR-P2-003`, `IR-P2-004`, `IR-P2-005` · **LIVE:** `LIVE-P2-003` · **NOTIF:** `NOTIF-P2-002`, `NOTIF-P2-003` · **OBS:** `OBS-P2-001`, `OBS-P2-002`, `OBS-P2-003` · **PERF:** `PERF-P2-003` · **RES:** `RES-P2-001` · **XREPO:** `XREPO-P2-001`, `XREPO-P2-002`, `XREPO-P2-004`

### Records, verdict and evidence (13)

- **EVID:** `EVID-P2-001`, `EVID-P2-002`, `EVID-P2-003` · **HYGIENE:** `HYGIENE-P2-002`, `HYGIENE-P2-004` · **INV:** `INV-P2-001` · **PRIV:** `PRIV-P2-003` · **REV:** `REV-P2-001`, `REV-P2-002`, `REV-P2-003` · **SC:** `SC-P2-002`, `SC-P2-003` · **TEST:** `TEST-P2-005`

## This Quarter (P3 — 40)

Cleanup, consistency and small hardening; batch by patch set so each item rides a themed PR.

- **Security and isolation:** `ACM-P3-001`, `ACM-P3-002`, `ADV-P3-001`, `SECRET-P3-008`, `SECRET-P3-010`, `XREPO-P3-001`
- **CI and supply chain:** `API-P3-001`, `API-P3-002`, `BP-P3-001`, `BP-P3-002`, `CI-P3-001`, `CI-P3-002`, `CTR-P3-006`, `CTR-P3-007`, `SBOM-P3-001`, `SC-P3-001`, `SEC-P3-001`
- **Data, retention and backups:** `DATA-P3-007`, `DQ-P3-009`, `SEARCH-P3-005`, `SEARCH-P3-006`
- **Operator experience and docs:** `FEAT-P3-001`, `FLEET-P3-008`, `HYGIENE-P3-002`, `INFRA-P3-001`, `INFRA-P3-002`, `ND-P3-001`, `NOTIF-P3-002`, `RES-P3-001`
- **Observability and resilience:** `EVOL-P3-001`, `EVOL-P3-002`, `IR-P3-001`, `NOTIF-P3-001`, `PERF-P3-001`, `PERF-P3-002`, `TEST-P3-001`
- **Records, verdict and evidence:** `EVID-P3-001`, `HYGIENE-P3-001`, `PRIV-P3-001`, `PRIV-P3-002`

## Later / Platform Evolution

- Rebuild the pin/verdict lineage end-to-end and re-run synthesis (22/23/40) after the P0/P1 waves; then a verification-only pass closes findings one by one.
- Second-node / hosting decision for the single-host SPOF (`ARCH-P1-001`, EX-22) and the lab data-LV/offsite capacity curve (`PERF-P1-002`, `LIVE-P1-001`).
- Cross-repo joint release gate and upgrade/rollback choreography beyond the automated pin check (`INTG-P1-002`, `XREPO-P2-003`, patch set 3).
- Edge control-plane packaging (versioned artifact instead of the mutable worktree) and schema migrations (`XREPO-P2-004`, `EVOL-P2-003`, `ARCH-P1-002`).
- DQ scorecard ownership/scheduling, per-feed rate bands and event-time fidelity (`DQ-P2-004`, `DQ-P2-005`, `DQ-P3-009`).
- License gate and SBOM/vulnerability enforcement with an exception register (`SBOM-P1-001`, `SBOM-P2-003`, `EX-11/EX-12`).
- Owner decisions still outstanding: total-loss detection target, escalation contacts, break-glass custody, Wazuh indexer snapshot ownership (see Open Questions).

## Deferred / Accepted Risks (owner decisions)

These are not closable by engineering alone; each needs an explicit owner-acceptance row plus contradiction/exception register entries, and is re-reviewed before the exception expiry (2026-12-31 class) or on the next change to the affected path.

| Risk / finding | Current position | Required decision |
|---|---|---|
| EX-01 SSH password auth remains enabled | Owner-accepted; fail2ban active; addressed in `access_control_matrix.md` | Keep with evidence, or move to keys-only |
| EX-22 single-host lab / no independent infra | Owner-accepted as-is; drives `ARCH-P1-001` | Accept residual SPOF or fund a second node |
| Edge PKI/DB backup local-only (`DR-P1-005`, `RES-P1-003`) | Open; option to document an owner-accepted gap | Encrypt + offsite, or accept and record |
| Wazuh indexer snapshot coverage (`DATA-P1-002`) | Open; no lab-side schedule known | Schedule snapshots or record accepted gap |
| License-free amendment + OD-11 (`SBOM-P1-001`) | Accepted in prose (`OWNER_ACCEPTANCE.md`, `CLOSEOUT.md`) | Encode as a license policy + exception rows |
| OD-17 vulnerability threshold (`CTR-P3-006`) | Accepted 2026-09-22; disposition records stale | Refresh disposition against current pins |
| EX-23 no cutover / no-change promotion | Accepted; rollback path unexercised | Re-accept or exercise a rollback drill |
| Secrets backups in the delivery surface (`SECRET-P1-003`, `XREPO-P1-003`) | Open; P0 credential literals must go first | Encrypt/move out of the release surface |
| Third-party outside-in scan never performed | Prior-run limitation, still true | Schedule or formally accept |
| Not-applicable prompts (04/05/17/25–29/37/39) | Excluded from counts; `audit_manifest.json` records N/A | Re-scope only if the product changes |

## Milestones

- **M1 (day 0):** P0 set 1 closed or explicitly owner-accepted with evidence; no new releases shipped in the interim.
- **M2 (week 1):** P1 identity/ladder fixes merged (`SEC-P1-001/002`, `API-P1-001`, `CTR-P1-002`); branch protection live (`BP-P1-001`); release records re-bound.
- **M3 (week 1–2):** alert-path and backup detectors live and drilled (`RES-P0-002`, `RES-P0-001`, `LIVE-P0-001/002`, `OBS-P1-001–005`); runbooks executable non-root.
- **M4 (month 1):** all P2 sets merged with tests; first SLO-style review of the new detectors (false-positive/noise review).
- **M5 (quarter):** P3 cleanup + CI drift guards; verification-only pass over every fixed finding; synthesis re-run.

## Dependency Notes

- `EVID-P0-001`/`REV-P0-001`/`INV-P0-002` share the re-review dependency (owner + release engineer); resolve together in patch set 1.
- `API-P0-001` rotation must precede package rebuild/publication (`EVID-P1-001`, `EVID-P1-004`).
- `LIVE-P0-001`/`RES-P0-002` canary depends on DO watcher access; `LIVE-P0-002`/`RES-P0-001` gauges depend on the offsite job change.
- P2 detector work (staleness, mapping, retention) depends on the P1 deploy-path fixes (`DATA-P1-001`, `INV-P1-002`) or it will drift again.
- Edge fleet P1 fixes (`FLEET-P1-002`, `SEC-P1-002`) are prerequisites for the joint release gate (`INTG-P1-002`).

