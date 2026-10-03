# Changelog

All notable changes to the falcon lab (central `falcon-build` + edge `falcon-edge-build`) are recorded here.

Format: [Keep a Changelog](https://keepachangelog.com/)-style categories — Added / Changed / Fixed / Security / Removed / Deprecated. This is the first changelog; entries below cover the audit cycle `20260930-0701` (`8282d3f` / `45dfed0`) and the verified fixes since the prior audit run `20260930-0320` (`794ba31` / `2b5bc8b`). Commit SHAs are the evidence anchors; findings are referenced by registered ID.

## [Unreleased] — audit cycle 2026-09-30

### Added

- **Audit run artifacts** — the full-domain run `20260930-0701-falcon-8282d3f_edge-45dfed0` was added under `docs/audits/repo-deep-dive/` in both repos (central + edge mirror): 45+ reports, 5 lenses, `findings.json` (264 findings), `risk_register`/`roadmap`/`patch_plan` synthesis outputs, `follow_up_register.md` (this cycle), plus `release_notes_draft.md` and `changelog_draft.md`.
- **Falcon CI** — `.github/workflows/validate.yml` + `ci/validate.py` (actionlint, shellcheck, ruff, gitleaks, zizmor; YAML/JSON, pinning, gate-ledger, evidence and secret-scan checks) (`6f33a06`, followed by `1dbb86c`, `80d8e8b`). Prior ND-P3-006 → partially-fixed.
- **Wazuh stack reproducibility** — lab multi-node stack files committed (compose overlays, cloudflare sidecar, certs, custom rules, `ossec.conf`, decoder/CDB/relay configs; credential fields redacted) (`1c79d02`…`27095b4`).
- **Monitoring** — per-agent Wazuh state metric and critical-agent-down rule (catalogue now 31 rules) (`6beaeec`); disconnected-count fix + phase-9 catalogue entry (`8281808`); alert catalogue regenerated from live rules (`a614af8`).
- **Evidence tooling** — verifier guard for the immutable signed 2026-09-29 archives (`789846b`); evidence index/manifest refresh workflow documented in `AGENTS.md`.
- **Edge CI** — ruff (Python) + independent gitleaks gates (`824f701`); zizmor security audit, Python 3.13 test matrix, release `SHA256SUMS`, date-revision image naming (`f0996b8`); manual image-bake workflow + `docs/GITHUB_CI.md` (`09aae7e`); weekly drift check + scheduled validate (`45dfed0`); `ci_status.sh` (`bfc1e22`); dependabot + pinned action SHAs (`3ad4a85`); auto-merge-on-green sweep (`.github/workflows/dependabot-merge.yml`, `45dfed0`).
- **Edge release tooling** — portable shipped tooling (path-portability regression test) (`968cb9e`, `ff54deb`); runner-temp bake fix (`598bd3b`); CI artifact fetch tool (`cc49107`).
- **Edge evidence** — lab8 CI bake verification captures and refreshed evidence index (`ddf9869`).

### Changed

- **Digest derivation (central)** — `PACKAGE_DIGEST.txt` now derives `program_verdict`, `production_readiness` and open-gate counts from the ledgers instead of hardcoding them (`93ea9c6`); publication chain verifies with 0 failures. Prior ND-P1-001 → verified-fixed.
- **Disk hygiene** — rotate `stats.log` daily and prune rotated stats in the disk guard (`c5755f5`, `f1db6d8`); edge EVE rotation manual + clean Suricata restart.
- **Alerting** — TLS-silence window 30 m → 6 h; richer ntfy alerts with labels and actionable links (`d83f421`). Prior LIVE-P0-004 → partially-fixed.
- **WireGuard** — bootstrap preserves runtime peers on re-run (`95-wireguard.sh` peer merge) with `wg_peer_preservation_check.sh` regression check. Prior INTG-P0-002 → partially-fixed.
- **Endpoint kit** — single VPN fail-loud policy, embedded sysmon, repeatable sync (`c5ae6e1`); current rollout status doc updated (`4278198`).
- **Edge review flow** — gate-ledger CSV repair + semantic/round-trip CI checker (`4332503`); phase-10 consistency test green at `f1c5def`; review gates closed with dispositions (`d6147ef`). Prior REV-P1-006 → partially-fixed.
- **Edge update drill** — apply path exercised: `0.1.1-lab` applied in 30 s, broken bundle rejected (`0b83acc`); CLI idempotency keys body-hashed (`9acd660`); fresh desired-state revision on release (`a8a4a9c`).

### Fixed

- **Backup/offsite runner** — `.env` quoting bug that broke every `set -e` backup/offsite run; offsite completed exit 0 on 2026-09-30 07:43Z; encrypted new-services upload with round-trip verify (`1f76aca`). Prior LIVE-P0-001/002 → partially-fixed (outcome still unalerted).
- **`program_verdict` derivation** (`1f76aca`), superseding the earlier hardcoded value.
- **Secret scanner false positives on CI pins** — GitHub Actions pin SHAs treated as integrity pins, not secrets (`80d8e8b`); gitleaks binary kept out of the repo tree (`1dbb86c`).
- **Edge bake workflow** — checksum filename, wireguard-tools, decompressed SBOM source, disk-space step (`35fea1c`); SBOM/upload permissions (`dd1efe0`); actionlint/shellcheck findings (`c0c9831`, `3ad4a85`).
- **Edge relay import lint** (`b8542bf`, `12aa2fd`); Wazuh redacted password field marker cleared (`6c2b4db`).

### Security

- **Credential round (audit action required)** — the audit found integration credentials committed into the published Wazuh config, invisible to the scanner's XML-tag blind spot (`API-P0-001`, `EVID-P1-004`). Rotation/removal + scanner fix is **open**; do not re-publish the current package until done.
- **Secret material in the shared delivery directory** — private keys, credentials and unencrypted secrets backups remain where owners can read/copy them (`SECRET-P1-003`, `SECRET-P2-001`, `XREPO-P1-003`). Encryption or explicit owner acceptance pending (owner decision D5).
- **Sensor image credentials** — host/Wi-Fi credentials baked into images and shared across environments (`SECRET-P1-001`); rotation path open.
- **History scan drift** — falcon history scan exits 1 / `REVIEW_REQUIRED` while the gate ledger records a clean history scan (`SC-P2-003`, `TEST-P2-002`). Re-record after scanner fix.

### Removed

- Nothing removed in this cycle (append-only doctrine).

### Deprecated

- Nothing deprecated in this cycle.

## Breaking changes

- **None declared.** The edge API contract remains at 16 documented paths while 19 routes are implemented (`API-P2-001`, `CI-P2-004`); consumers should treat undocumented routes as unstable. No schema migrations or data-format changes shipped.

## Projected next-cycle entries (candidates — do not publish yet)

These are the highest-value fixes the audit expects; each maps to an open finding and is a candidate for the next changelog cut:

- `Fixed` — atomic release rebind (manifest + sidecar + digest + verdict) — EVID-P0-001, FLEET-P1-001, XREPO-P0-001.
- `Fixed` — offsite/new-services outcome metrics and alerts — RES-P0-001, DR-P1-001, OBS-P1-002.
- `Fixed` — relay-independent dead-man / external notification — RES-P0-002, NOTIF-P1-001.
- `Security` — rotate exposed credentials; scanner XML-tag rule; redaction ledger entry — API-P0-001, EVID-P1-004, SC-P1-001.
- `Changed` — edge fleet alert rules deployed centrally — INTG-P1-001, XREPO-P1-002, OBS-P1-004.
- `Fixed` — `purge_expired()` boundary bug + directives decrement — DATA-P1-003, RES-P2-002.
- `Added` — `VERSION`/tag conventions, license gate, public release key — SBOM-P1-001, SBOM-P2-004.

## Upgrade and rollback notes

- **Central:** the current package/verdict binding is not releasable as-is (superseded package approval, self-contradicting verdict). If a package must ship, record a fresh rebind + a decision-log entry first; keep the previous `review-package/` archive and digest for rollback.
- **Edge:** the live unit is lab5 with in-place agent updates; no released image/SBOM reproduces it (`FLEET-P2-003`). Keep the previous image (`falcon-edge-sensor-2026.09.29-lab5-arm64.img.xz`) and the prior manifest digest before any upgrade.
- **Verification step for any upgrade:** `sha256sum -c` over the shipped image and SBOM, plus the manifest sidecar once rebuilt (currently FAILs — see Fixed/Security above).
- **Rollback:** apply-path rollback is drill-proven (`0b83acc`) but there is no crash-consistent or OS/rootfs rollback on the Pi 3B (`FLEET-P1-002`); replace the unit image if an OS-level regression occurs.
- **No migrations:** no schema migrations or data-format changes ship in this cycle; do not change index mappings without the mapping guardrail and a revert plan (`DR-P2-002`).

## Evidence and verification

- Commits cited were taken from `git log 794ba31..8282d3f` (central) and `2b5bc8b..45dfed0` (edge).
- Fixes marked "partially-fixed" were re-checked by the owning domain/lens agent at the current commits; none is `verified-fixed` except the digest derivation (ND-P1-001).
- Release artifacts referenced by filename only; no credential values are recorded in this changelog.
