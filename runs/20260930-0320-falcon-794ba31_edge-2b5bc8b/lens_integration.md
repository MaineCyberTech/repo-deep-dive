# Lens — Integration

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab
- Run: `20260930-0320-falcon-794ba31_edge-2b5bc8b`
- Prompt: lens `integration` (`lenses/integration.md`, area `INTG`)
- Repos: falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b` (moved during audit)
- Generated: 2026-09-30 (converted from source audit)
- Area code: `INTG`
- Source report: `source_reports/05-integration-two-repos.md`
- Scope limitations: no root/docker/wg; live checks via filesystem, systemd, HTTP, read-only DB; edge repo HEAD moved during the audit

## Doctrine and Safety Compliance

- Audit-only observed: yes — read-only; no mutations performed (observed others' mutations and recorded them)
- Secret values redacted: yes
- Artifacts written only under the run folder: yes
- Repo HEAD re-checked before writing: yes — recorded in the manifest

## Executive Summary

The two programs are functionally integrated and the sensor path works (tunnel up, sensor ACTIVE, heartbeats fresh, ingest flowing), but the **pairing contract is not trustworthy as written**: the pin records a manifest digest that no longer exists anywhere (overwritten in place), one pin claim about WireGuard peer persistence is wrong in both directions, and a bootstrap re-run would silently drop the edge tunnel (the R-30 failure class). The joint system has **no alert coverage for the edge path**, executes live code directly from the edge working tree, keeps edge PKI/DB backups local-only (outside falcon's offsite job), and suffers version skew across four moving references (pin commit, manifest commit, live image lab5 vs recommended lab7, control plane 0.1.0 vs bundle 0.1.1-lab). The additive rule is mostly respected, with one boundary breach (edge-written dashboard in falcon's tree) and ownership ambiguity that followed.

Findings: 2 × P0, 4 × P1, 5 × P2, 4 × P3 (15 total).

## Scope

- Pin/release contract between the repos; manifest integrity; coupling map (services, ports, units, data paths); additive rule; failure modes of the joint system; runbook/ownership coverage
- Not reviewed: deep domain quality inside each repo (full run)

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| `docs/edge/EDGE_RELEASE_PIN.md` (falcon `0aa7e7c`) | pin | The pairing contract |
| Edge release manifest + SBOM + signing (delivery dir) | artifacts | Pin verification |
| `config/wireguard/wg0.conf.tpl`, live `/etc/wireguard/wg0.conf`, `bootstrap/95-wireguard.sh` | config | Peer persistence claim |
| Live host: units, ports, exporters, Grafana rules, DB | observation | Coupling reality |
| Both repos' git refs + origin refs | records | Publication state |
| Edge `AGENTS.md` rule 6 / `REPOSITORY.md` change classes | doctrine | Additive rule basis |

---

## Findings

### Finding ID: INTG-P0-001 - Pin ↔ delivery digest mismatch; unversioned overwritten manifest

- Severity: P0 (source: Critical) · Confidence: High
- Area: INTG · Scope: falcon pin ↔ edge delivery
- Evidence: pin records manifest `dffcbbb7…` / commit `35f0793c…` / lab6 SBOM; the delivery manifest was regenerated 7 minutes later (`9c1021e9…`, commit `14e7c70d…`, lab7 SBOM) and the old file was **overwritten in place under the same name** — the pinned digest exists nowhere on disk; edge HEAD is 32 commits past the pin's release commit. Source: 05 §INT-C1.
- What is happening: the pin names an artifact that no longer exists; the manifest is unversioned in name and was silently replaced.
- Why it matters: any consumer trusting the pin verifies the wrong artifact; release traceability is broken.
- Impact: review/verification of the edge release is not reproducible; P10 gate evidence cites a state no file matches.
- Recommended fix: version manifest filenames (never overwrite); re-pin to a stable release (digest + commit + SBOM + signature); add a cross-repo drift check that fails when the pinned digest is absent.
- Suggested validation: pinned digest resolves to a present file whose contents match; drift check fails on mismatch.
- Owner suggestion: both maintainers · Effort: M · Dependencies: edge release freeze (in-flight drills)
- Status: open at audit time (rebind work landed post-audit — see `follow_up_register.md`)

### Finding ID: INTG-P0-002 - Edge peer persistence claim is wrong; template-vs-live drift means a bootstrap re-run drops the tunnel

- Severity: P0 (source: Critical) · Confidence: High
- Area: INTG · Scope: falcon config ↔ live WireGuard
- Evidence: `git log --all -- config/wireguard/wg0.conf.tpl` shows the edge peer was **never** added to the template; `git show 36ca988` changed only evidence/ledgers; live `/etc/wireguard/wg0.conf` was last written by the **edge onboarding script** (2026-09-29 20:02:38Z; `.bak-edge-*` chain; lab5 key `sXdIz`); `bootstrap/95-wireguard.sh` renders the template over the live file. Source: 05 §INT-C2.
- What is happening: the pin's persistence claim is false in both directions; the live tunnel exists only as drift from the repo.
- Why it matters: a host rebuild or any re-run of `95-wireguard.sh` silently removes the edge peer — the exact R-30 failure class the lab documents.
- Impact: sensor offline until manual onboarding re-runs; detection only via 24 h stale-peer alert or dashboard.
- Recommended fix: make peer persistence real (template/config-managed edge peer or a dedicated non-destructive onboarding step), keep runtime peers through re-renders, correct the pin claim; regression check for peer preservation.
- Suggested validation: re-run the WireGuard bootstrap with a peer present; the peer survives (`wg syncconf`); regression check passes.
- Owner suggestion: falcon maintainer · Effort: S/M · Dependencies: none
- Status: open at audit time (peer-preservation fix + regression check landed post-audit — see `follow_up_register.md`)

### Finding ID: INTG-P1-001 - No alert covers the edge path

- Severity: P1 (source: High) · Confidence: High
- Area: INTG · Scope: live monitoring
- Evidence: live Grafana has 30 rules, none `falcon-edge`; the per-peer WG rule fires only after 24 h without handshake; the edge's own silence/queue/cert rules are prepared but undeployed; falcon's service probe does not check `9443` or exporter freshness. Source: 05 §INT-H1.
- What is happening: a sensor that stops heartbeating or an exporter that stops writing is visible only on a human dashboard.
- Why it matters: the edge fleet's health depends on manual looking.
- Impact: silent edge outages; MTTD measured in hours-to-days.
- Recommended fix: deploy the edge alert rules (additively) and/or add falcon-side probes for `9443` + `falcon_edge_*` freshness; wire to ntfy dual-path.
- Suggested validation: simulate heartbeat stop / exporter stop; alert fires within target window.
- Owner suggestion: both maintainers · Effort: M · Dependencies: doctrine on rules deployment (owner decision pending)
- Status: open at audit time

### Finding ID: INTG-P1-002 - Live code is the edge working tree

- Severity: P1 (source: High) · Confidence: High
- Area: INTG · Scope: deployment
- Evidence: `edge-control-plane.service` ExecStart runs `-m falcon_control` from `/home/user/falcon-edge-build/deploy/…`; the exporter runs `automation/observability/fleet_metrics.py` from the same tree; both enabled while HEAD moved 23 commits during the audit and docs/evidence were edited in place. Source: 05 §INT-H2.
- What is happening: production behavior changes with any checkout/branch/edit, with no deploy review.
- Why it matters: no reproducible deployment; unreviewed code is live.
- Impact: behavior drift; debugging ambiguity; review claims bound to a moving tree.
- Recommended fix: run from a pinned copy/version (release artifact or exported tree), record the deployed digest, and deploy via a scripted step.
- Suggested validation: deployed digest recorded and matches the pinned release; behavior change requires a new deploy.
- Owner suggestion: edge maintainer · Effort: M · Dependencies: INTG-P0-001
- Status: open at audit time

### Finding ID: INTG-P1-003 - Edge PKI/DB backup is local-only and outside falcon's offsite job

- Severity: P1 (source: High) · Confidence: High
- Area: INTG · Scope: backup/DR
- Evidence: edge daily backup → `/home/user/falcon-edge-delivery` (keep 7, host-local); falcon offsite uploads OpenSearch snapshots + encrypted falcon config archive only (`bootstrap/80-offsite-backup.sh`). Source: 05 §INT-H3.
- What is happening: the edge CA, signing seed, and control-plane DB exist only on the shared host.
- Why it matters: host loss = fleet trust anchor loss; every enrolled sensor's trust disappears.
- Impact: fleet-wide re-enrollment/trust reset after a host loss.
- Recommended fix: include the edge secrets backup in the offsite flow (encrypted), or document and owner-accept the risk explicitly.
- Suggested validation: restore rehearsal from offsite on a clean host reproduces the edge PKI/DB.
- Owner suggestion: both maintainers · Effort: S/M · Dependencies: secret-handling doctrine
- Status: open at audit time

### Finding ID: INTG-P1-004 - Version skew across four moving references

- Severity: P1 (source: High) · Confidence: High
- Area: INTG · Scope: release/state coherence
- Evidence: pin commit `35f0793` (32 behind edge HEAD), manifest commit `14e7c70` (21 behind), live image lab5 vs recommended lab7, control plane 0.1.0 vs bundle 0.1.1-lab (not in manifest); both repos ahead of origin refs (6/23 commits). Source: 05 §INT-H4.
- What is happening: "released", "pinned", "live", and "remote" all differ.
- Why it matters: reviewers and operators cannot answer "what is deployed?" from any single record.
- Impact: verification binds to the wrong tree; upgrade/rollback planning is ambiguous.
- Recommended fix: freeze a release commit; rebuild artifacts (bundle/SBOM/manifest) over it; re-pin; push both repos; record the deployed digest live.
- Suggested validation: pin digest == delivery manifest == deployed digest == remote commit.
- Owner suggestion: both maintainers · Effort: M · Dependencies: edge release freeze; push
- Status: open at audit time

### P2 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| INTG-P2-001 | P2 | Boundary breach on the dashboard + ambiguous ownership (edge wrote into falcon tree; falcon adopted; rollback note stale) | 05 §INT-M1 | Declare the file falcon-owned; correct the edge rollback note; record the event |
| INTG-P2-002 | P2 | WG peer administration inverted (edge script writes lab config; falcon runbook omits `.30`; decision log misdescribes) | 05 §INT-M2 | Document the joint procedure; single owner for peer changes; runbook table update |
| INTG-P2-003 | P2 | Secrets backup inside the release surface (digest-listed; root-owned newer backup silently skipped) | 05 §INT-M3 | Move secrets backups out of the release dir; explicit exclusion rules |
| INTG-P2-004 | P2 | Falcon-side record/alert drift (live `falcon-wg-peer-stale` missing from catalogue 29 vs 30; pin claim repeated; VPN runbook omits edge peer) | 05 §INT-M4 | Update catalogue + runbook + records |
| INTG-P2-005 | P2 | Shared-host resource risk unowned (root LV 82%; edge spool no retention; overlapping endurance tooling) | 05 §INT-M5 | Joint resource ownership + quotas; see LIVE-P0-003/LIVE-P1-001 |

### P3 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| INTG-P3-001 | P3 | Pin misidentifies the 15140/15141 coupling (Wazuh client proxies; sensor has no Wazuh agent) | 05 §INT-L1 | Correct the dependency model in the pin |
| INTG-P3-002 | P3 | `falcon-` prefix on edge-provided units invites ownership confusion | 05 §INT-L2 | Rename or document ownership |
| INTG-P3-003 | P3 | Cosmetic drift (stacked wg0.conf comment blocks; 0-byte `control.db`; unredeemed bootstrap tokens) | 05 §INT-L3 | Cleanup + token prune (see ND-P3-010) |
| INTG-P3-004 | P3 | Control plane binds `0.0.0.0:9443`; every VPN peer can reach it (mTLS only gate) | 05 §INT-L4 | Bind to wg0 or restrict by nft; note trust model |

## Failure Modes of the Joint System (from source §7)

| # | Trigger | Effect | Detection today |
|---|---|---|---|
| F1 | `95-wireguard.sh` re-run / host rebuild | Edge peer dropped; tunnel down | 24 h stale-peer alert / dashboard |
| F2 | Edge repo checkout/edit | Live behavior changes unreviewed | None |
| F3 | Edge control plane stops | Heartbeats/renewals stop; stale values shown | None (rules undeployed) |
| F4 | Falcon Prometheus/textfile change | `falcon_edge_*` series vanish silently | None |
| F5 | Lab host loss | Edge CA/seed/DB lost (local-only backups) | n/a (backup gap) |
| F6 | Root LV exhaustion | Both programs' writers can wedge | Disk rules (root only) |
| F7 | Sensor re-image (new WG key) | Key rewrite needed in lab config | 24 h alert / dashboard |
| F8 | Manifest/pin drift | Reviewers verify wrong digests | None |
| F9 | Rules deployment outside doctrine | Can interrupt monitored stack | Script dry-run by default |
| F10 | Edge cert/secret rotation | Trust bundle custody unoffshored | Renewal timer; no CA-backup alert |

## Cross-References

| This report ID | Related lens | Related ID | Relationship |
|---|---|---|---|
| INTG-P0-001 | REV-P2-001/002 | delivery binding | Reviewer hit the same drift |
| INTG-P0-002 | (post-audit fix) | R-30 class | Peer preservation regression check added post-audit |
| INTG-P1-001 | LIVE-P1-003, LIVE-P1-002 | monitoring gaps | Edge + falcon alert coverage |
| INTG-P1-003 | LIVE-P0-001/002 | backup gaps | Offsite coverage |
| INTG-P2-005 | LIVE-P0-003, LIVE-P1-001 | disk | Shared host resource risk |

**Domain routing for the next full run:** `42` (XREPO — this lens's domain equivalent), `12` (infra drift), `13`/`32` (resilience/DR), `14` (observability), `40` (release), `36` (container/runtime security).

## Open Questions (from source)

1. Which manifest/commit pair is the canonical pinned release? (05)
2. Who owns WG peer administration — lab or edge onboarding? (05 §INT-M2)
3. Is the dashboard file falcon-owned going forward? (05 §INT-M1)
4. Is rules deployment for the edge path authorized (owner decision pending)? (05 §F9)

## Appendix

- Full narrative, coupling map, and evidence index: `source_reports/05-integration-two-repos.md`
- Finding counts: INTG-P0 ×2, INTG-P1 ×4, INTG-P2 ×5, INTG-P3 ×4
