# Edge Fleet, Image, and Hardware Audit

## Audit Metadata

- Audit name: repo-deep-dive (Falcon Lab profile)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: `/home/user/falcon-edge-build` (edge) · `/home/user/falcon-build` (falcon) · `/home/user/falcon-edge-delivery` (delivery)
- Branch/commits: main; edge `f1c5defe6b66887ae49bc44c2cd79b37ad249663` (clean) · falcon `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c` (only audit artifacts dirty)
- Generated at: 2026-09-30T16:35Z (live sensor inspected read-only 16:15–16:16Z)
- Auditor: audit subagent (read-only, prompt 43) · Area code: FLEET
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/43_edge_fleet_hardware_audit.md`
- Scope limitations: no bake/reflash/update/power-cut/destructive checks; MT7612U absent; independent review (ED-18/19) unassigned; root-only files only via captured evidence.

## Scope

Reviewed: image build/reproducibility, release artifacts and binding, install/enrollment/rebind, update/rollback atomicity and power-loss outcomes, hardware claims vs live reality, per-unit identity/lifecycle, fleet inventory/state, failure modes (storage/thermal/power/connectivity/clock), field diagnostics, decommissioning. Live Pi `10.99.0.30` inspected read-only over SSH with the delivered lab5 key. Not reviewed: central data plane (prompt 44), falcon↔edge pin mechanics (XREPO), OS package vulnerability state (prompts 11/35).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `delivery/falcon-edge-release-manifest-20260930.json` + `.sha256` | release | Manifest/SBOM/digest/binding | Signature ed25519 `5ea52faf9cf6ee97` **VALID**; 44 artifacts hash-match; sidecar **FAILS** |
| `delivery/falcon-edge-sensor-2026.09.29-lab5…/lab6/lab7/lab8` | images+SBOM | Release lineage vs live state | Live card = **lab5**; lab8 built in GitHub Actions (636 pkgs) |
| `image/build-pi-image.sh`, `automation/validation/bake_lab_test_image.sh` | build | Reproducibility, pinned inputs | Base = external `/tmp/opencode/pi-image/2026-09-15-raspios-trixie…`; digest checked, not committed |
| `deploy/falcon-update-apply.*`, `image/overlay/usr/local/sbin/falcon-apply-update.sh` | update | Atomicity/power-loss | Rename+move swap; revert only inside script |
| `src/falcon_agent/runner.py` (`apply_update`, `_write_slot_marker`), `tests/phase7/test_update_apply.py` | agent/tests | Update staging, slot switch | SWITCH_SLOT `mode: lab-simulated`; no interruption test |
| `profiles/pi/AB_STRATEGY.md`, `ledgers/gate_ledger.csv` | design/gate | A/B rollback claim | P7-G05 **BLOCKED**; fallback selector design-only |
| Live SSH: model, `lsusb`, `lsmod`, `lsblk`, `vcgencmd`, `wdctl`, `timedatectl` | live | Hardware matrix vs reality | Pi 3B Rev 1.2; `0846:9055`; no `0e8d:7612`; 2 partitions; watchdog armed |
| `docs/phase9/COMPATIBILITY_MATRIX.md`, `profiles/adapter/ADAPTER_PLANS.md`, evidence P9-G02/G04/G05 | claims/evidence | Hardware/thermal/power | RTL8812BU lab column proven; SD endurance not evidenced |
| `control-plane.db` (mode=ro), `automation/observability/fleet_metrics.py`, `falcon_edge_metrics.prom` | fleet | Inventory/identity/lifecycle | 9 sensors: 1 ACTIVE, 5 RETIRED, 3 REVOKED; 61 live series |
| `docs/runbooks/{update-rollback,retirement-key-destruction,clean-reimage}.md` | runbooks | Field/decommission | Some steps unimplemented (real slot switch) |

## Verification Performed

| Check | Command / read | Result | Notes |
|---|---|---|---|
| HEAD/dirty state | `git rev-parse HEAD; git status` | edge `f1c5def` clean; falcon `8282d3f` | Edge HEAD moved 45dfed0→f1c5def mid-run |
| Manifest signature | `falcon_common.signing.verify` (seed pubkey) | **VALID**, keyId matches | Independent re-hash of 44 artifacts: 0 mismatches |
| Manifest sidecar | `sha256sum -c …json.sha256` | **FAILED** | Sidecar `1868175…` vs actual `3fa4a49…`; manifest regenerated 06:25 after 04:44 sidecar |
| Hardware vs matrix | SSH `lsusb`/`lsmod`/model | Pi 3B; RTL8812BU `rtw88_8822bu`; MT7612U absent | Matrix RTL8812BU column supported |
| Live image/version | SSH `cat /etc/falcon-edge-image.json` | `2026.09.29-lab5`, built 19:58:19Z; agent `0.1.1-lab` | Matches no released image/SBOM |
| Update state | SSH units + DB `update_manifests`/`state_reports` | apply path active; 0.1.1 applied, 0.1.2-broken rejected | Revision-2 reports flipped APPLIED→FAILED (05:19Z, 13:05Z); unexplained |
| Fleet reality | DB read + live metrics | 9 rows, 1 ACTIVE, heartbeat 57 s | Adapters `chipset: unknown`; `site_id`/`human_name` NULL everywhere |

## Executive Summary

Hardware reality is well-evidenced: Pi 3B Rev 1.2, NetGear A6150 (RTL8812BU) on in-tree `rtw88_8822bu`, monitor-mode 10/10, 10/10 forced resets to ACTIVE with clean fsck, thermal/power inside the lab envelope, and MT7612U genuinely absent (BLOCKED). Strengths: valid signed manifest with matching artifact digests, four verified image digests, working agent-package update (including rejection of a broken bundle), and applied watchdog/ZRAM/journal hardening. Fleet-level risks dominate: the manifest checksum sidecar no longer matches its artifact; the only live unit runs lab5 plus in-place agent updates (no released image/SBOM reproduces it); OS/rootfs updates and true A/B rollback do not exist on the Pi 3B and the agent swap has no crash-consistent recovery; fleet inventory cannot verify adapter/driver or site identity; SD endurance (half of P9-G04) has no evidence. Prior-run status (20260930-0320): ND-P1-005 **partially-fixed** (matrix/ADAPTER_PLANS updated; `AGENTS.md` still says adapter not attached); ND-P2-012 **still-open** (OpenAPI lacks `renewals`/`release`/`ingest/vector`); ND-P2-016 **still-open** (host-only edge-metrics timer); ND-P2-017 **partially-fixed** (bundle in manifest; new sidecar drift); REV-P2-004 **partially-fixed** (package includes `image/`, `docs/phase9/`); REV-P2-005 **partially-fixed** (owner-flash citations added); REV-P2-006 **still-open** (P9-G04 PASS on unapproved reset approximation).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Release manifest | `build_release_manifest.py` | Sign delivery inventory | Valid signature; stale sidecar | High | FLEET-P1-001 |
| Update apply | `falcon-apply-update.sh` + `.path`/`.service` | Root package swap | Exercised live | High | FLEET-P1-002 |
| A/B strategy | `profiles/pi/AB_STRATEGY.md` | OS rollback | Design only | High | P7-G05 BLOCKED; p1/p2 only live |
| Fleet DB | `store.py` (`sensors`, `inventory`) | Unit registry | 9 rows; 1 ACTIVE | Medium | No site/human_name |
| Fleet exporter | `fleet_metrics.py` | Prometheus metrics | Live; 61 series | Medium | Alerts undeployed (OBS-P1-004) |
| Decommission | runbooks + `retire_stale_sensors.py` | Retire/revoke | DB states applied | Medium | FLEET-P2-005 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Image build/reproducibility | 2 | digest-checked base; lab5–8 digests OK | Base/toolchain not repo-reproducible | Record base URL+digest |
| Release artifacts | 2 | signed manifest; SBOMs lab6–8 | Sidecar mismatch; lab5 no SBOM | Atomic re-publish + binding test |
| Install/enrollment/rebind | 3 | bootstrap + claim bundle; EDGE-ONBOARD | Rebind not rehearsed on lab7/lab8 | Clean-reimage rehearsal |
| Update/rollback safety | 1 | apply + reject + config rollback proven | No crash-safe swap; no OS path | FLEET-P1-002 |
| Hardware matrix | 3 | live USB/driver; P9-G02/G05 | Live-image row wrong; inventory "unknown" | Fix row + inventory mapping |
| Identity/lifecycle | 2 | PKI, 30-day renewal live | No CRL; destruction unverified | TLS revocation + destruction check |
| Fleet inventory/state | 2 | DB + exporter + dashboard | No hardware/site/version in fleet view | Extend inventory/metrics |
| Failure modes | 3 | soak/reset/watchdog/zram | SD wear unmeasured; no skew alert | Wear telemetry / descope |
| Diagnostics | 2 | boot logs; UPLOAD_DIAGNOSTICS | No redaction test; no archive | Scan bundle; archive |
| Decommissioning | 2 | runbooks; RETIRED/REVOKED | destroy-keys intent-only | Verify destruction |

## Detailed Review (condensed)

- **Build**: the bake script verifies the base `.xz` sidecar when present and records the decompressed digest (`49fafba6…`) in `/etc/falcon-edge-image.json`; reproducibility depends on external files and root tooling.
- **Update**: staging is digest+size checked (agent), re-checked plus compile-checked by the privileged unit; swap = rename old→`.previous`, move new, restart, revert if not ACTIVE in 90 s. The live drill matches P7-G01 evidence (0.1.1-lab applied; 0.1.2-broken rejected "compile check failed").
- **Rollback**: `update-rollback.md` step 2 assumes a real boot-slot switch; on the Pi 3B the agent only writes `slot-state.json` (`mode: lab-simulated`). Config rollback is genuinely atomic (`os.replace` + previous copy).
- **Fleet**: 5 QEMU test sensors retired 2026-09-30T01:11Z; 3 REVOKED remain with cert files; 15 directives remain unconsumed/expired (cross-ref ND-P2-015).
- **Cross-references (not duplicated)**: SECRET-P1-001, CTR-P1-001/002, REV-P1-004/005/007, REV-P3-010, OBS-P1-004, XREPO pin.

## Hardware Compatibility Matrix

| Component | Claimed support | Evidence | Actual state | Gap | Notes |
|---|---|---|---|---|---|
| Pi model | Pi 3B Rev 1.2 (a22082) | docs; live `/proc/device-tree/model` | Confirmed | Serial hash not in fleet DB | none |
| OS image | "Debian 13 live card; clean lab6 digest" | live metadata | Card is **lab5**; lab6 digest is another artifact | Stale row | FLEET-P2-003 |
| Kernel | 6.18.50+rpt-rpi-v8 aarch64 | live `uname` | Matches | none | none |
| RTL8812BU | Attached/proven; in-tree `rtw88_8822bu` | live `0846:9055` + `lsmod`; P9-G05 x10, 0 errors | Attached/bound/monitor-proven | Inventory says chipset "unknown" | FLEET-P2-004 |
| MT7612U | `0e8d:7612`, in-kernel mt76, pending | live `lsusb` | Absent; BLOCKED as documented | Adapter + reviewer pending | Owner action |
| SD storage | SN32G 32 GB High-Speed (~20 MB/s) | live CID; P9-G01 | Present; 13% used | Endurance/wear **unsupported** | FLEET-P2-007 |
| Power/thermal | `throttled=0x0`; ≤80 °C | P9-G03 soak 73.6 °C; live 48.3 °C | In envelope | 72 h soak unapproved | P9-G06 BLOCKED |
| Packet loss | 100% at 10k pps/2 min, 0 drops | P9-G02 | 2-min lab run only | 15-min certification not run | Limitation retained |
| A/B rollback | Strategy + fallback selector | `AB_STRATEGY.md`; P7-G05 BLOCKED | **Not implemented** | No OS rollback | FLEET-P1-002 |
| Watchdog/ZRAM | Hardening scripts | live `wdctl` 30 s; zram swap | Applied/armed | Boot-loop only design-reviewed | none |

## Update / Rollback Power-Loss Matrix

| Path | Mechanism | Power-loss outcome (explicit) |
|---|---|---|
| Agent package swap | rename→move→restart→timed revert | **Unsafe**: loss between rename and move leaves `falcon_agent` absent; no boot restore; path unit may not re-fire; agent down until manual recovery |
| OS/rootfs update | none (P7-G05 BLOCKED; single p2) | Not applicable — cannot be attempted; corrupt rootfs requires card recovery/reflash |
| Desired-state config | stage, `os.replace`, previous copy | Old or new file intact; ROLLED_BACK reported |
| SWITCH_SLOT directive | write `slot-state.json` (simulated) | No device effect; nothing lost |
| Watchdog | RuntimeWatchdogSec=30 | Reset to healthy image; fsck clean 10/10 |
| Enrollment/rebind | one-time token removed on success | Loss mid-enroll leaves token unredeemed; rerun consumes it once |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| FLEET-001 | Image build/reproducibility | build/bake scripts | Base digest verified | Inputs external | P2 | Commit base record |
| FLEET-002 | Release artifacts | manifest+sidecar+SBOM | Signature; digests verified | Sidecar stale; lab5 no SBOM | P1 | Re-publish; binding test |
| FLEET-003 | Install/enrollment/rebind | bootstrap; EDGE-ONBOARD | Token+CA; no TOFU | Rebind untested at lab7/8 | P2 | Rehearse reimage |
| FLEET-004 | Update/rollback safety | apply script; P7-G01 | Digest+compile checks; revert | Not crash-safe; no OS path | P1 | Crash-safe apply + test |
| FLEET-005 | Hardware matrix vs reality | live SSH; P9-* | Mostly supported | Live-image row; SD wear | P2 | Fix row; measure/descope |
| FLEET-006 | Identity/lifecycle | pki; DB; runbooks | 30-day certs; renewal live | No CRL; destruction unverified | P2 | TLS revocation; destruction check |
| FLEET-007 | Fleet inventory/state | DB; exporter | 9 sensors; states accurate | No hardware/site/version | P2 | Extend inventory |
| FLEET-008 | Failure modes | soak/resets/watchdog | Power/thermal covered | SD wear; clock after loss | P2 | Wear telemetry; skew alert |
| FLEET-009 | Diagnostics | boot logs; directive | Logs on FAT; state snapshot | No redaction test/archive | P2 | Scan + archive |
| FLEET-010 | Decommissioning | runbooks; retire script | RETIRED/REVOKED states | Asset record + destruction unverified | P3 | Asset record; destruction check |

## Findings

### Finding ID: FLEET-P1-001 - Release manifest checksum sidecar no longer matches the signed manifest

- Severity: P1 · Confidence: High · Area: FLEET / release binding
- Evidence: `delivery/falcon-edge-release-manifest-20260930.json.sha256` records `1868175…`; `sha256sum -c` fails (actual `3fa4a49…`); manifest `generatedAt 06:25:23Z`, commit `155f244` (HEAD is `f1c5def`); `.sha256` mtime 04:44; builder `build_release_manifest.py` (skips unreadable root-owned `…secrets-backup-20260930T011356Z.tar.gz`); P10-G05 capture `20260930T044359Z_final-delivery-rebuild.out` produced the `1868175…` value.
- What is happening: the manifest was regenerated after its sidecar and bound to a commit older than HEAD; the sidecar was not refreshed; one delivery artifact is outside the manifest.
- Why it matters: the instructed verification path fails, and the delivery does not bind to a single commit/artifact set.
- User / business impact: false verification failure or manual interpretation; provenance ambiguity for the reviewed images.
- Security / privacy / reliability impact: stale sidecar cannot distinguish tampering/replacement; unlisted secret-bearing archive.
- Recommended fix: regenerate manifest and sidecar atomically at the intended publication commit; make root-owned files either hashed via a privileged pass or explicitly declared excluded.
- Suggested validation: CI/release test asserting `sha256sum -c` passes, manifest commit == tagged commit, and artifact-set equality minus declared exclusions.
- Owner suggestion: edge maintainer + owner · Effort: S · Dependencies: none · Status: open

### Finding ID: FLEET-P1-002 - Update apply is not power-loss safe and the OS/rootfs rollback path does not exist

- Severity: P1 · Confidence: High · Area: FLEET / update and rollback
- Evidence: `falcon-apply-update.sh` (rename old→`.previous`, `shutil.move` new, restart, revert only in-process); `deploy/falcon-update-apply.path` (`PathChanged=`, no boot recovery); `profiles/pi/AB_STRATEGY.md` (fallback design only); live `lsblk` shows only p1/p2; `gate_ledger.csv` P7-G05 **BLOCKED**; `test_update_apply.py` has no interruption case.
- What is happening: the swap is two non-atomic filesystem operations. Explicit outcome: power loss between rename and move leaves `falcon_agent` missing, the unit fails to start, the path unit may not re-trigger, and nothing restores `.previous` automatically. No OS/rootfs update exists; the documented cmdline selector is unimplemented.
- Why it matters: the most likely update failure (power cut, explicitly treated in P9-G04) bricks the agent; OS recovery requires physical reflash.
- User / business impact: silent sensor loss after an update; field intervention.
- Security / privacy / reliability impact: no proven rollback for the privileged update path.
- Recommended fix: crash-consistent swap (versioned dir + symlink, or in-progress journal restored at boot) and a boot-time recovery unit; implement or explicitly descope the cmdline-selector fallback with a documented reflash outcome.
- Suggested validation: kill the apply at each step in QEMU and assert boot recovery; negative test for interrupted swap.
- Owner suggestion: edge maintainer (owner for descope) · Effort: M · Dependencies: P7-G05 decision · Status: open

### Finding ID: FLEET-P2-003 - The live unit runs an image/SBOM combination that no release artifact reproduces

- Severity: P2 · Confidence: High · Area: FLEET / release–fleet binding
- Evidence: live `/etc/falcon-edge-image.json` = `2026.09.29-lab5` (built 19:58:19Z), agent `0.1.1-lab`; delivery ships lab5 (no SBOM), lab6, lab7 (714 pkgs, "current clean reflash artifact"), lab8 (636 pkgs, CI); `docs/edge/EDGE_RELEASE_PIN.md` pins manifest `dffcbbb7…`, commit `35f0793c…`, SBOM lab6, image lab5.
- What is happening: the fielded card reached current code via in-place agent updates on lab5 while the released artifacts (lab7/lab8) are unflashed; the falcon-side pin describes a third combination.
- Why it matters: "what is running and can it be rebuilt?" is unanswerable; replacement needs rebind.
- User / business impact: recovery/replacement guesswork; pin contract stale (XREPO).
- Security / privacy / reliability impact: running system cannot be attested against a reviewed SBOM.
- Recommended fix: reflash to lab7/lab8 under clean-reimage, re-issue manifest, refresh the pin; expose image version in inventory/metrics.
- Suggested validation: post-reflash capture (ACTIVE + digest) and a pin-vs-delivery digest test.
- Owner suggestion: edge maintainer + owner · Effort: M · Dependencies: token freshness; XREPO · Status: open

### Finding ID: FLEET-P2-004 - Fleet inventory cannot verify the hardware matrix or site identity

- Severity: P2 · Confidence: High · Area: FLEET / inventory
- Evidence: DB inventory for the ACTIVE sensor: `adapters[].chipset "unknown"`, `driver "usb"`, `usbId "0846:9055"`; `hardware.model` has a trailing `\u0000`; `sensors.site_id`/`human_name` NULL for all 9 rows; `fleet_metrics.py` exports no hardware/image/site fields; live SSH confirms RTL8812BU on `rtw88_8822bu`.
- What is happening: the fleet view cannot confirm the compatibility matrix per unit, identify sites, or detect hardware/driver drift.
- Why it matters: matrix rows and inventory-state claims are not auditable per unit; a swapped adapter or kernel change would be invisible.
- User / business impact: slower hardware triage; wrong-matrix operation risk.
- Security / privacy / reliability impact: unidentified radio is a monitoring blind spot.
- Recommended fix: USB-ID→chipset/driver mapping, NUL strip, site/human-name at enrollment, image version + hardware in exporter.
- Suggested validation: unit tests for mapping/NUL; live compare of inventory vs `lsusb`/`lsmod`.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: none · Status: open

### Finding ID: FLEET-P2-005 - Revocation and decommissioning are database states, not enforced key lifecycle

- Severity: P2 · Confidence: High · Area: FLEET / identity lifecycle
- Evidence: `service.py` (`h_revoke` sets `REVOKED`; routes then 403), `pki.py` (no CRL), `retirement-key-destruction.md` (`destroyKeys` recorded as intent; physical wipe unverified), DB (3 REVOKED + 5 RETIRED; certs still on disk), `identity.py` (key 0600, cert 0640 group-readable for Vector).
- What is happening: revoked credentials keep working at the TLS layer until expiry (30 days) and only fail at route checks; key destruction is attestation-only.
- Why it matters: a lost sensor cannot be provably neutralized; fleet lifecycle record diverges from cryptographic reality.
- User / business impact: decommission audits rely on unverifiable statements.
- Security / privacy / reliability impact: compromise window equals certificate lifetime.
- Recommended fix: CRL or short-lived certs with handshake-time rejection; recorded destruction evidence; retain revoked fingerprints in fleet records.
- Suggested validation: revoked cert fails TLS; wiped unit fails enrollment with old material (captured).
- Owner suggestion: edge maintainer + security reviewer · Effort: M · Dependencies: REV-P1-004/007 · Status: open

### Finding ID: FLEET-P2-006 - Support bundles are written to an unauthenticated partition with no redaction verification

- Severity: P2 · Confidence: Medium · Area: FLEET / diagnostics
- Evidence: `falcon-early-log.sh` dumps `dmesg` (tail 400) + `journalctl -b -n 400`; `falcon-log-export.sh` adds `nmcli dev wifi list`, `nmcli con show`, `wg show`, image metadata; output on FAT `/boot/firmware/falcon-logs`; README claims "No private keys or tokens" with no test.
- What is happening: free-text logs and network state are exported to a card-readable partition; the no-secrets claim is asserted, not checked.
- Why it matters: lost/loaned cards can leak operational detail (SSIDs/MACs, endpoints, log snippets).
- User / business impact: privacy/support-flow exposure; claim may not hold.
- Security / privacy / reliability impact: physical-access data exposure.
- Recommended fix: secret-pattern scan of generated bundles in CI/periodic checks; narrow early-log journal scope; gate WiFi scan; add bundle digest metadata.
- Suggested validation: synthetic token/PSK patterns are redacted/excluded; bundle scan in CI.
- Owner suggestion: edge maintainer · Effort: S–M · Dependencies: SECRET-P1-001 · Status: open

### Finding ID: FLEET-P2-007 - SD endurance half of P9-G04 has no evidence and no wear monitoring

- Severity: P2 · Confidence: High · Area: FLEET / storage failure mode
- Evidence: `gate_ledger.csv` P9-G04 "power interruption and SD endurance" cites only 10/10 forced resets + fsck; `OPERATING_ENVELOPE.md` endurance test item has no capture (`evidence/raw/P9-G01` = space/bus mode only); live card SN32G OEM 04/2022, 13% used; P9-G03 notes Vector buffer peak 35 MiB.
- What is happening: the gate combines two scenarios but only power was exercised; no write-amplification/wear indicator or daily-write metric exists.
- Why it matters: SD wear-out is near-irrecoverable in the field; disk-percentage alone cannot show consumption rate.
- User / business impact: premature unit loss/replacement.
- Security / privacy / reliability impact: silent storage failure degrades queue/capture durability.
- Recommended fix: bounded endurance measurement + write-rate metric, or explicitly descope the endurance claim in gate/scorecard.
- Suggested validation: 7-day write-volume + extcsd health capture; threshold proposal.
- Owner suggestion: edge maintainer + owner · Effort: M · Dependencies: gate-scope correction · Status: open

### Finding ID: FLEET-P3-008 - Documentation contradictions remain between AGENTS.md and the proven hardware matrix

- Severity: P3 · Confidence: High · Area: FLEET / documentation
- Evidence: `falcon-edge-build/AGENTS.md` says the adapter hardware "is NOT attached, so adapter gates stay BLOCKED"; `ADAPTER_PLANS.md` says "ATTACHED AND PROVEN (2026-09-30)" with in-tree driver and 10/10 monitor mode; `COMPATIBILITY_MATRIX.md` preamble still says "Empty until the hardware is attached"; live SSH confirms attachment.
- What is happening: agent-facing environment facts are stale from before the hardware arrived.
- Why it matters: future agents may block or skip adapter work (prior ND-P1-005).
- User / business impact: wasted cycles and contradictory status.
- Security / privacy / reliability impact: low.
- Recommended fix: update `AGENTS.md` and the matrix preamble; add a docs-consistency check against ADAPTER_PLANS.
- Suggested validation: `ci/validate.sh` textual check.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Delivery verified against stale checksum/pre-audit commit | High | Medium | Provenance failure | FLEET-P1-001 | Atomic re-publish + test |
| Power loss during update leaves agent dead | High | Medium | Silent fleet loss | FLEET-P1-002 | Crash-safe apply + boot recovery |
| Live unit runs unreproducible image/SBOM mix | Medium | High | Recovery uncertainty | FLEET-P2-003 | Reflash; re-pin |
| Revoked credentials stay valid | Medium | Medium | Lost-unit misuse | FLEET-P2-005 | CRL/handshake rejection |
| Diagnostic bundles leak detail | Medium | Low-Med | Physical exposure | FLEET-P2-006 | Bundle scan |
| SD wear-out unnoticed | Medium | Medium | Unit loss | FLEET-P2-007 | Wear telemetry/descope |

## Recommendations

### Immediate / Release Blocking
1. Re-generate manifest + sidecar atomically at the publication commit (FLEET-P1-001).
2. Add boot-time package recovery / crash-safe swap before further updates (FLEET-P1-002).

### This Week
3. Reflash the live unit to lab7/lab8 and refresh the pin/manifest binding (FLEET-P2-003).
4. Fix `AGENTS.md`, matrix preamble, and the live-image row (FLEET-P3-008).
5. Add falcon-logs redaction/scan to CI (FLEET-P2-006).

### This Month
6. Inventory hardware mapping + site/human-name + image version (FLEET-P2-004).
7. CRL/short-lived certs + destruction verification (FLEET-P2-005).
8. SD endurance measurement or explicit descope (FLEET-P2-007).

### Later / Platform Evolution
9. Implement cmdline-selector A/B fallback (or read-only-rootfs model) and close P7-G05 with device evidence.
10. Fleet desired-version tracking and update-drift alerting (cross-ref OBS-P1-004).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix AGENTS.md/matrix preamble | Removes last stale hardware status | `AGENTS.md`, `COMPATIBILITY_MATRIX.md` | docs test |
| Scan falcon-logs patterns | Verifies no-secrets claim | log scripts, `ci/` | synthetic-pattern test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Crash-safe apply + boot recovery | P1 | edge maintainer | M | P7-G05 decision |
| Manifest/sidecar binding test | P1 | edge maintainer | S | publish flow |
| Reflash + re-pin | P2 | edge + owner | M | token freshness |
| Inventory hardware/site/version | P2 | edge maintainer | M | none |
| TLS-level revocation | P2 | edge maintainer | M | REV-P1-004/007 |
| SD endurance metric/descope | P2 | edge + owner | M | gate scope |
| Host-unit mirror for edge exporter | P3 | falcon maintainer | S | ND-P2-016 |

## Suggested Tests

- Unit: NUL strip; USB-ID→chipset map; inventory schema.
- Integration (QEMU): kill apply at rename/move/restart and assert boot recovery; request reconciliation.
- E2E: clean-reimage lab7/lab8 → enroll → ACTIVE → fleet version metric matches.
- CI: sidecar check, commit binding, artifact-set equality, docs-consistency for hardware claims.
- Security/regression: revoked cert fails TLS; bundle scan; SWITCH_SLOT stays simulation-only until implemented.

## Suggested Documentation Updates

- `falcon-edge-build/AGENTS.md` — hardware facts, live image version, update power-loss outcome.
- `docs/phase9/COMPATIBILITY_MATRIX.md` — separate live-card row from released digests; SD endurance status.
- `docs/runbooks/update-rollback.md`/`recovery-boot.md` — slot switch is simulated on Pi 3B; manual reflash outcome.
- `docs/runbooks/retirement-key-destruction.md` — required destruction evidence artifact.
- `docs/GITHUB_CI.md` — external base URL+digest; atomic publication order.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why did revision-2 state reports flip APPLIED→FAILED after the fact? | Possible live apply bug or test residue | Agent/CP logs/context |
| Is the 2-hour soak accepted for P9-G06? | Certification closure | Owner approval |
| Are physical power cuts required for P9-G04? | Whether the reset approximation suffices | Owner decision |

## Appendix

- Live checks were read-only over SSH; nothing restarted or reconfigured. `timedatectl`: NTP active, UTC authoritative, local Europe/London; `throttled=0x0`; 13% root usage; watchdog timeleft 8 s.
- `falcon_edge_metrics.prom` 15:13Z: 9 sensors, ACTIVE heartbeat 57 s, `edge_capture_kernel_packets_total 1,161,512` (0 drops, 0 errors), `edge_ids_events_window_total{alert}=1`.
- Secrets: no values printed; references are path/type only (Wi-Fi PSK/WG keys in images — SECRET-P1-001; signing seed; relay tokens).
