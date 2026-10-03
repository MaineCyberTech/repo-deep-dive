# Lens — New Developer

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab
- Run: `20260930-0320-falcon-794ba31_edge-2b5bc8b`
- Prompt: lens `new_developer` (`lenses/new_developer.md`, area `ND`)
- Repos: falcon-build @ `794ba31` · falcon-edge-build @ `2b5bc8b`
- Generated: 2026-09-30 (converted from source audits)
- Area code: `ND`
- Source reports: `source_reports/01-falcon-build-new-developer.md`, `source_reports/03-falcon-edge-new-developer.md`
- Scope limitations: read-only audit account (no root/docker/wg); live checks limited to systemd, listeners, filesystem, HTTP, read-only metrics/DB

## Doctrine and Safety Compliance

- Audit-only observed: yes — read-only inspection and temporary reproductions under `/tmp` only
- Secret values redacted: yes — paths and types only
- Artifacts written only under the run folder: yes
- Repo HEAD re-checked before writing: yes — edge HEAD moved during the audit and is recorded in the manifest

## Executive Summary

Both programs are real and mechanically disciplined (validators, manifests, evidence discipline), but **the first hour for a newcomer is misleading**: the front-page documents describe states of the world that are one or more generations stale, and several "authoritative" machine artifacts contradict the ledgers they summarize. In falcon-build the newcomer would conclude production is NOT_SUPPORTED (the digest and `AGENTS.md` say so) while the ledgers and verdict say APPROVED; the README quick start cannot deploy the stack; and operationally dangerous scripts are linked as health checks. In falcon-edge the first document read says the hardware is absent while an enrolled sensor is live one `ssh` away. Mechanical integrity is strong; **onboarding relies on tribal knowledge** about which document is current and which scripts are safe.

Findings: 5 × P1, 18 × P2, 11 × P3 (34 total; 22 falcon-build, 12 falcon-edge).

## Scope

- falcon-build newcomer experience: entry docs, doctrine, quick starts, runbooks, gate/delivery records, dangerous tooling, live-state reconstruction
- falcon-edge-build newcomer experience: status docs, contract, closeout artifacts, queue/observability code, maintenance units, profiles, secrets layout, CI
- Not reviewed: deep domain quality (that is the job of the domain prompts in a full run)

## Evidence Reviewed

| Evidence | Type | Why relevant |
|---|---|---|
| `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json`, `AGENTS.md`, `README.md`, `REPOSITORY.md` | status artifacts | First documents a newcomer trusts |
| `ledgers/*` (gate, phase9, contradiction, exception), `docs/phase9/review/*` | records | Ground truth the artifacts should match |
| `bootstrap/*`, `automation/*` | scripts | Onboarding/operability path; dangerous tooling |
| `docs/architecture/PORT_PROTOCOL_MATRIX.md`, runbooks | docs | Accuracy for diagnostics/incident response |
| Live host (read-only) | observation | What actually runs vs what docs claim |
| Edge: `README.md`, `REPOSITORY.md`, `AGENTS.md`, `api/`, `src/falcon_agent|control/`, `deploy/`, `profiles/`, `closeout/` | code + docs | Edge newcomer path |
| Edge live: control plane `/healthz`, `/sensors`, tunnel, Pi SSH (read-only) | observation | Hardware/state reality |

---

## Findings — falcon-build

### Finding ID: ND-P1-001 - The "authoritative" digest contradicts the ledgers and the production verdict

- Severity: P1 (source: High) · Confidence: High
- Area: ND (new developer) · Repo: falcon-build
- Evidence: `PACKAGE_DIGEST.txt` lines 10-15 (`program_verdict=INSUFFICIENT_EVIDENCE`, `production_readiness=NOT_SUPPORTED`, open gates listed) vs `ledgers/` + `docs/phase9/review/PRODUCTION_VERDICT.md` (APPROVED, 13 PASS); values hardcoded in `automation/validation/publish_digests.sh` lines 30-35; `verify_publication_chain.sh` does not check them. Source: 01 §F-01.
- What is happening: the digest (the artifact the project calls authoritative) is generated from hard-coded stale values and can never self-correct.
- Why it matters: a newcomer, reviewer, or automation reading it gets the opposite of the recorded gate state.
- Impact: false status propagation through every rebuild; publication chain reports success while the contradiction stands.
- Recommended fix: derive `program_verdict`, `production_readiness`, `open_gates`, and the phase-9 aggregate from the ledgers + verdict pointer; extend the chain verifier with a cross-check.
- Suggested validation: regenerate digest; assert field equality against ledgers; verifier fails on mismatch.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open at audit time (see `follow_up_register.md` for post-audit notes)

### Finding ID: ND-P1-002 - Agent onboarding doc (`AGENTS.md`) directs work at already-closed gates

- Severity: P1 (source: High) · Confidence: High
- Area: ND · Repo: falcon-build
- Evidence: `AGENTS.md` lines 71-74 lists P8-G10 / P9-G02/G10/G11/G12/G14 as open/blocked — all PASS in the ledgers; same drift in `README.md` lines 8-13 and `REPOSITORY.md`. Source: 01 §F-02.
- What is happening: static "current state" lists in agent/human entry docs were never updated after closure.
- Why it matters: an AI agent or new engineer will try to close done gates, miss real work, and may regenerate stale artifacts.
- Impact: wasted effort; risk of contradicting the published verdict.
- Recommended fix: replace static lists with a generated current-state block (or pointer to ledgers + a new `docs/CURRENT_STATE.md`); update it in the publication flow.
- Suggested validation: doc-drift check comparing the block to the ledgers in CI.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: ND-P1-001 (shared generator)
- Status: open at audit time

### Finding ID: ND-P1-003 - Operationally dangerous scripts are linked without warnings

- Severity: P1 (source: High) · Confidence: High
- Area: ND · Repo: falcon-build
- Evidence: `automation/vpn/test_closed_mode.sh` line 9 traps EXIT and restores **open** inbound mode; `docs/phase9/VPN_ONBOARDING_CHECKLIST.md` step 5 instructs running it. `automation/validation/probe_pipeline_test.sh` line 57 stops the central aggregator while `docs/runbooks/OPERATOR_START_HERE.md` lists it under "Quick health checks". Source: 01 §F-03 (see also F-09).
- What is happening: runbooks point newcomers at scripts that mutate live security/ingestion state, without warnings.
- Why it matters: a first-week operator can open the firewall or take ingestion down thinking they are "checking health".
- Impact: security exposure (inbound open) or data-path outage; violates the closed-inbound requirement.
- Recommended fix: warning blocks on both scripts; checklist points at the safe read-only battery (`phase9_vpn_do_tests.sh`); move the mutating test to a "mutating tests" section.
- Suggested validation: runbook grep shows no dangerous script under "health checks"; script headers carry WARNING.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open at audit time (remediation priority: P0 round — see register)

### Finding ID: ND-P1-004 - README quick start cannot deploy the stack

- Severity: P1 (source: High) · Confidence: High
- Area: ND · Repo: falcon-build
- Evidence: `README.md` line 37 says `sudo bootstrap/run-all.sh` is the deploy; `run-all.sh` runs only stages 10/20/30/40 — secrets (50), central (60), probe (70), alerting (90), dashboards (91) never run; compose requires `/srv/falcon/secrets/central.env`; `docs/phase7/runbooks/RESTORE.md` line 87 states the limitation correctly. Source: 01 §F-04.
- What is happening: the documented quick start is host preparation only, not a deploy.
- Why it matters: a newcomer on a clean host concludes the repo is broken.
- Impact: onboarding failure; support load; erosion of trust in the docs.
- Recommended fix: make `run-all.sh` complete (with explicit `--full`), or rewrite the README to list the real ordered steps (50→60→70→90→91→95-99).
- Suggested validation: follow the README on a clean host (or a staged rehearsal) end-to-end.
- Owner suggestion: falcon maintainer · Effort: S/M · Dependencies: none
- Status: open at audit time

### Finding ID: ND-P1-005 - Edge status docs say the hardware is absent; the hardware is attached and running

- Severity: P1 (source: High) · Confidence: High
- Area: ND · Repo: falcon-edge-build
- Evidence: `README.md:23`, `REPOSITORY.md:22`, `AGENTS.md:44-45` say Pi/RTL8812BU/MT7612U not attached; live: tunnel `10.99.0.30` ping 2/2, Pi 3B Rev 1.2, USB `0846:9055` (RTL8812BU) present, sensor `fes_b9f5c03d58713121659f1796` ACTIVE, no MT7612U. Source: 03 §F-01.
- What is happening: the first document read contradicts the live enrolled device.
- Why it matters: newcomers cannot trust the status table generally; they may skip device work that is actually executable.
- Impact: onboarding confusion; wrong planning; trust erosion.
- Recommended fix: update the three status lines (Pi attached/enrolled; RTL8812BU attached; MT7612U absent; point to `ledgers/gate_ledger.csv` + `closeout/OWNER_ACTIONS.md`); keep history only in closeout amendments.
- Suggested validation: status lines match live device and ledgers.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none
- Status: open at audit time

### falcon-build — P2 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| ND-P2-001 | P2 | Delivered repomix pack stale; packed-only verification fails (23 mismatched / 933 missing) | 01 §F-05 | Rebuild pack + verify in publication flow; fail publication if pack older than package commit |
| ND-P2-002 | P2 | `FINAL_RESPONSE.json` stale, mis-bound, hardcoded verdicts | 01 §F-06 | Generate from phase9 ledger + verdict; bind commit at generation |
| ND-P2-003 | P2 | History secret scan no longer matches recorded result (exit 1, 20 findings) | 01 §F-07 | Run history scan in publication flow; update ledger note + allowlist counts |
| ND-P2-004 | P2 | `PORT_PROTOCOL_MATRIX.md` materially out of date (host `mon`, UDP 51820 vs 5182, missing rows) | 01 §F-08 | Refresh from compose + nftables, or mark historical |
| ND-P2-005 | P2 | Tunnel test dials wrong port (51820 vs 5182); companion opens firewall | 01 §F-09 | Parameterize port from rendered config; fix checklist |
| ND-P2-006 | P2 | Synthetic probe path retired but bootstrap/pipeline test still target it | 01 §F-10 | Update bootstrap 70 + test to ens19 architecture; canary-based assertion |
| ND-P2-007 | P2 | Runbooks contain stale "current state" affecting incident response | 01 §F-11 | Append superseded notes; point to decision log |
| ND-P2-008 | P2 | Contradiction ledger shows resolved items as OPEN (C-04/05/06/08/11/22) | 01 §F-12 | Append resolution rows (append-only) |
| ND-P2-009 | P2 | Cloudflare/public-access config not reproducible from repo | 01 §F-13 | Document authoritative token/scopes; wire `bootstrap/97`; capture evidence |
| ND-P2-010 | P2 | Live services whose source of truth is outside the repo (Wazuh/IRIS/OpenCanary/edge CP) | 01 §F-14 | Live-services inventory mapping service → source → backup → runbook |
| ND-P2-011 | P2 | Evidence index paths don't resolve in the package (264/460 build-host paths) | 01 §F-15 | Regenerate index package-relative (index-time rewrite) |

### falcon-build — P3 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| ND-P3-001 | P3 | Phase 9 docs cite a non-existent `evidence/phase9/` directory | 01 §F-16 | Fix two references |
| ND-P3-002 | P3 | Broken repository references (verdict template path, review-package README, host-file links, dashboard/rule counts) | 01 §F-17 | Batch fix; counts from repo |
| ND-P3-003 | P3 | Architecture docs are Phase-0 drafts presented as current | 01 §F-18 | Historical banner or regenerate as-built |
| ND-P3-004 | P3 | Gate ledger notes carry historical counts (991/991, scan claims, N/A omission) | 01 §F-19 | Refresh notes at publication; include N/A in aggregate |
| ND-P3-005 | P3 | Exception register duplicates hard to reconcile; no current-status column | 01 §F-20 | Generated status summary (latest row per ID) |
| ND-P3-006 | P3 | No enforcement of "validate before commit" (no CI, hooks, or Makefile) | 01 §F-21 | Minimal CI workflow + pre-commit hook |
| ND-P3-007 | P3 | Sibling edge repo/program invisible at the root (Info) | 01 §F-22 | "Related repositories" section in README/REPOSITORY |

---

## Findings — falcon-edge-build

### falcon-edge-build — P2 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| ND-P2-012 | P2 | "Authoritative" OpenAPI contract missing 3 live endpoints (`renewals`, `release`, `ingest/vector`); idempotency wording drift | 03 §F-02 | Add paths/schemas; regenerate models; route-parity CI test |
| ND-P2-013 | P2 | Summary artifacts contradict the ledgers (stale FINAL_RESPONSE commit, closeout counts, P10-G05 lab6 note, phase6 counts) | 03 §F-03 | Regenerate response post-drills; append corrections |
| ND-P2-014 | P2 | Latent queue data-loss bug: `purge_expired()` deletes non-expired items | 03 §F-04; `src/falcon_agent/queue.py:126-138` | Share one cutoff; mixed-queue regression test; wire or mark unused |
| ND-P2-015 | P2 | `falcon_edge_sensor_pending_directives` never decrements (dead `consume_directive`; no expiry filter) | 03 §F-05 | Filter `expires_at > now`; or agent acknowledgement; document semantics |
| ND-P2-016 | P2 | Host maintenance units not reproducible from repo (3 services/timers host-only) | 03 §F-06 | Move unit files to `deploy/maintenance/` + install script |
| ND-P2-017 | P2 | Release/delivery artifact set not coherent with repo (bundle not in manifest; review package pre-lab7; live runs beyond lab7) | 03 §F-07 | Freeze commit; rebuild bundle/SBOM/manifest; re-verify package |
| ND-P2-018 | P2 | Shipping Vector profile hardcodes sensor identity + tunnel URL (source: LOW/MEDIUM — higher value used) | 03 §F-08; `profiles/sensor/vector/edge.toml:33,42` | Template identity/URL at deploy time; validation rule |

### falcon-edge-build — P3 findings (index)

| ID | Sev | Finding | Evidence (source) | Suggested fix |
|---|---|---|---|---|
| ND-P3-008 | P3 | Dead/duplicate first-boot script and overlay README drift (0600 vs 0640) | 03 §F-09 | Delete/deprecate script; fix README |
| ND-P3-009 | P3 | Small documentation/hygiene inaccuracies (CLI 16 vs 18, `bootstrap/` listed, empty `docs/phase10/`, missing templates dir constant) | 03 §F-10 | Batch refresh + "current state" pointer |
| ND-P3-010 | P3 | Secrets-directory hygiene: 0-byte stray `control.db`; 10 unredeemed tokens (3 expired); layout undocumented | 03 §F-11 | Remove stray; token prune helper; document layout |
| ND-P3-011 | P3 | CI validates contract but not service-vs-contract surface; "validate ALL PASS" ≠ tests pass | 03 §F-12 | Route-parity test; README/AGENTS run both |

## Cross-References

| This report ID | Related lens/domain | Related ID | Relationship |
|---|---|---|---|
| ND-P1-001, ND-P1-002 | REV-P1-001 (reviewer) | same artifacts | Reviewer sampled the same contradiction |
| ND-P1-003 | REV-P1-004/005 (security surface) | tooling vs code paths | Both are "dangerous default" classes |
| ND-P1-005 | INTG (integration) | sensor live facts | Hardware reality also pinned in the integration audit |
| ND-P2-014, ND-P2-015 | REV-P3-008 | same metric bug | Reviewer filed the same exporter issue |
| ND-P2-017 | INTG-P0-001/INTG-P1-004 | release skew | Delivery coherence is cross-repo |
| ND-P2-010 | INTG-P1-002 | worktree execution | Live services outside repo = edge CP too |

**Domain routing for the next full run:** mostly `16` (documentation/devex), `09` (testing/CI), `12` (infra drift), `21` (hygiene), with `06`/`11`/`14`/`40` for specific items; edge items route to the same domains on the edge side.

## Open Questions (from sources)

1. Which document is intended as "current state" — and who owns keeping it true? (01 §7)
2. Was the packed-only reviewer path meant to remain supported? (01 §F-05)
3. Is the pinned/released edge artifact meant to be lab5 (live) or lab7 (recommended)? (03 §F-07)
4. Which maintenance units are considered part of the released edge surface? (03 §F-06)

## Appendix

- Full narratives and reproduction commands: `source_reports/01-falcon-build-new-developer.md`, `source_reports/03-falcon-edge-new-developer.md`
- Finding counts: ND-P1 ×5, ND-P2 ×18, ND-P3 ×11
