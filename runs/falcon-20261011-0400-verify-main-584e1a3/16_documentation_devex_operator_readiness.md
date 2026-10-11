# 16_documentation_devex_operator_readiness — Prompt 16 - Documentation, Developer Experience, and Operator Readiness Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `16_documentation_devex_operator_readiness.md` (area DOC, prompt)

## Verification Performed

# Documentation, Developer Experience, and Operator Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d` (short `08e20d1`)
- Branch: `main` (target pinned at 08e20d1; the clone's `main` ref now points at `6e4fccd` and `ops/20261009-snapshot-repo-relocate-clean` at `c13a416` — both used only as post-audit context, never as the audited tree)
- Generated at: 2026-10-09T21:50:40Z · Auditor: repo-deep-dive subagent (prompt 16) · Area code: DOC
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/16_documentation_devex_operator_readiness.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo password read from the owner file in a subshell, never printed); no state mutated; no formal compliance claimed — SOC2/ISO27001/NIST/CIS/OWASP/GDPR/CCPA/HIPAA/PCI/CMMC are used as readiness lenses only. Edge-repository surfaces (sensor images, edge delivery directory, edge SQLite store) are outside this repository and are referenced through owner-action C13. The quick-start commands were executed literally where read-only; no deploy stages were run.


## Scope

Reviewed at `08e20d1`: README and docs map, local setup/fresh-checkout path, environment docs, architecture/API docs, DB/migration docs, testing docs, deploy/rollback docs, incident/security docs, contribution/coding conventions, PR/release process, operator manuals, troubleshooting, ADRs/diagrams (none as formal ADRs), onboarding, script documentation and danger labeling, known limitations, AI agent instructions, prompt-pack/repo-map references. Not reviewed: the edge repository's docs; live GitHub-side branch protection (other domain).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md` | doc | Entry point, quick start, doc map | Updated 2026-10-04; 79 alert rules at `:30` |
| `docs/CURRENT_STATE.md` | doc | Claimed authoritative current-state page | Last modified 2026-10-03 (`29f75b4`); title says 2026-09-30 |
| `docs/README.md`, `docs/GLOSSARY.md`, `REPOSITORY.md`, `AGENTS.md` | docs | Doc map, vocabulary, conventions, agent rules | Complete |
| `docs/runbooks/{FRESH_CHECKOUT,OPERATOR_START_HERE,RUNTIME_AND_SCHEDULE,SCHEMA_AND_RETENTION,AUDIT_RUN_LIFECYCLE}.md` | docs | Onboarding, triage, schedules, retention, audit lifecycle | Walked read-only |
| `docs/security/{RELEASE_PACK_VERIFICATION,CI_GOVERNANCE_RECONCILIATION}.md` | docs | Publication/pack verification status | Open wiring residual documented |
| `docs/RELEASE_GATE.md` | doc | Release-gate reconciliation | Updated 2026-10-04/05 |
| `docs/phase9/{ALERT_CATALOGUE.yaml,ALERT_FIRING_PROOFS.md,OWNER_INPUTS_REQUIRED.md,TEST_PROCEDURES.md}` | docs | Generated status artifacts | Counts drift (see finding) |
| `automation/validation/{central_health,disk_guard,retire_migrated_docker_volumes,probe_pipeline_test,pack_fidelity}.sh` | code | Operator scripts + danger labels | Labels present |
| `ci/validate.py`, `automation/validation/verify_publication_chain.sh` | code | Quick-start verification commands | Executed |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py` (README/FRESH_CHECKOUT Track A step 1) | literal walk | The documented gate must pass | **PASS** `validation_failures=0` (incl. 50 shell suites, secret scan, digest binding, edge pin) |
| `bash automation/validation/verify_publication_chain.sh` (Track A step 2) | literal walk | Publication binding promised at 0 failures | **PASS** `publication_chain_failures=0` (review-package binding skipped as generated/not committed per HYG-P1-001) |
| `systemctl is-active falcon-{metrics,service-probe,disk-guard,backup,cold-copy}.timer` | literal walk | OPERATOR_START_HERE read-only view | all `active` |
| `df -h / /srv/falcon /boot`; `grep -h '^falcon_' /srv/falcon/textfile/*.prom` | literal walk | Read-only health view | works; 385 metric lines; `falcon_eve_last_event_age_seconds=867`; backup/offsite stamps present |
| `curl -o /dev/null -w %{http_code} https://falcon.mainecybertech.us/` and `/dash` | literal walk | Public reachability check | `302`/`302` (Access/login redirect — expected) |
| Markdown relative-link scan over the repo (read-only script) | inspect | Broken references | 27 relative links checked, 0 broken |
| Cross-check README/docs counts vs generated catalogue | inspect | Status-artifact consistency | README 79 rules vs CURRENT_STATE 77 (finding) |
| Dangerous-script inventory (bootstrap stages; validation scripts with delete/stop/network mutation) | inspect | Warning labels + blast radius | dry-run defaults, WARNING blocks, opt-in placement all present (`probe_pipeline_test.sh` WARNING; `retire_migrated_docker_volumes.sh` refuses before 2026-10-08; `disk_guard.sh` safe reclaim order) |

## Executive Summary

Documentation quality remains high: a clear doc map, an explicit operator triage order, runbooks per alert signal (79/79 catalogue runbooks resolve to existing files), an evidence doctrine, a fresh-checkout path whose two documented commands both pass literally at this commit, danger labels on mutating scripts, and agent rules that treat repository content as untrusted data. The defects are currency, not coverage: the page that calls itself authoritative (`docs/CURRENT_STATE.md`) has not been refreshed since 2026-10-03 and now contradicts the README/catalogue (77 vs 79 alert rules) and the ops commits landed on 2026-10-09 (C7 volume retirement, snapshot-repo relocation, DO forwarder restore); the generated firing-proof table still shows the 77-rule coverage; and two smaller residuals remain (pack-fidelity verification is still not wired into the delivery build; the README uses imprecise version shorthand). Recommended next actions: refresh the current-state page from the ledgers and catalogue, refresh the firing-proof coverage after the two OBS-P0-001 rules, wire `pack_fidelity.py` into `verify_delivery.sh`, and state exact pinned versions.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| README | `README.md` | Entry, quick start, map | Current (2026-10-04) | Low | 79 rules |
| Current-state page | `docs/CURRENT_STATE.md` | Authoritative state view | Stale (2026-10-03) | Medium | Contradicts README/catalogue |
| Fresh checkout | `docs/runbooks/FRESH_CHECKOUT.md` | Track A/B/C paths + platform notes | Verified | Low | Both commands pass |
| Operator manual | `docs/runbooks/OPERATOR_START_HERE.md` | Triage order, health view | Verified read-only | Low | Mutating checks fenced |
| Release gate | `docs/RELEASE_GATE.md` | Lab vs production reconciliation | Current | Low | 2026-10-05 addendum |
| Alert catalogue | `docs/phase9/ALERT_CATALOGUE.yaml` | Generated rule inventory | 79 rules; runbooks resolve | Low | Firing-proof coverage lags |
| Pack verification | `docs/security/RELEASE_PACK_VERIFICATION.md` | Repomix pack status | Open wiring residual | Medium | `:81` |
| Env docs | `docs/security/OWNER_ENV_INVENTORY.md`; `.env.example` | Credential classes, names-only | Present | Low | Values never in repo |
| Testing docs | `docs/phase9/TEST_PROCEDURES.md`; `FRESH_CHECKOUT.md` Track C | Suites and commands | Present | Low | No Python unit suite (documented) |
| Deploy/rollback | `README.md` quick start; `docs/phase7/runbooks/{UPGRADE_ROLLBACK,RESTORE}.md` | Ordered deploy + rollback | Present | Low | `run-all.sh` caveat explicit |
| AI instructions | `AGENTS.md` (rule 7), `REPOSITORY.md` | Agent boundaries | Present | Low | Repo content untrusted |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| README | 4 | `README.md` | Version shorthand | State 8.0.7/2.19.6 |
| Local setup | 5 | FRESH_CHECKOUT Track A passes | — | Keep |
| Env docs | 4 | `OWNER_ENV_INVENTORY.md`, `.env.example` | `.env` monolith (other domain) | Split (SECRET-P2-002) |
| Architecture/API docs | 4 | `docs/architecture/*` | Edge API lives in edge repo (declared) | Keep |
| DB/migration docs | 4 | `SCHEMA_AND_RETENTION.md`, `DOCKER_VOLUME_MIGRATION.md` | — | Keep |
| Testing docs | 4 | `TEST_PROCEDURES.md` | — | Keep |
| Deploy/rollback docs | 4 | README, run-all-deploy, UPGRADE_ROLLBACK | — | Keep |
| Incident/security docs | 4 | `docs/security/*`, incident playbook | Breach procedure unexercised | Exercise |
| Contribution/coding standards | 4 | `REPOSITORY.md`, `AGENTS.md` | No root `CONTRIBUTING.md`/LICENSE (private repo) | Optional |
| PR/release process | 4 | `.github/pull_request_template.md`, `RELEASE_GATE.md` | Branch protection plan-gated (other domain) | Owner decision |
| Operator manuals | 5 | OPERATOR_START_HERE verified | — | Keep |
| Troubleshooting | 4 | signal→runbook table; runbooks resolve | 37/79 rules map to INCIDENT_RESPONSE (IR domain) | Improve mapping (IR-P1-001) |

## Detailed Review

### Item: Quick start / fresh checkout (literal walk)

- Evidence: `README.md:38-93`; `docs/runbooks/FRESH_CHECKOUT.md:18-58`.
- Result: `python3 ci/validate.py` → 0 failures; `verify_publication_chain.sh` → 0 failures; the read-only operator view works (`systemctl is-active`, `df`, textfile metrics, public 302s). The platform notes added after the 20261002 DOC-P1-001 (OS/bash/clone-depth matrix at `:18-38`) match what the walk required. No missing steps found in Track A.

### Item: Current-state and generated status artifacts

- Evidence: `docs/CURRENT_STATE.md:1,53-70,100-115`; `README.md:30`; `docs/phase9/ALERT_CATALOGUE.yaml` (79 alerts); `docs/phase9/ALERT_FIRING_PROOFS.md:472-482`; `docs/architecture/EVOLUTION_GUIDE.md:268-295`.
- Finding: the page (and the evolution guide's state block) lag the sources: 77 vs 79 rules; C7 listed pending although the retirement executed 2026-10-09 on `main`/ops refs; pairing drift described as firing although it was restored 2026-10-03; C2 described as credential residuals although `CURRENT_STATE.md:54` records it DONE.

### Item: Publication/pack verification docs

- Evidence: `docs/security/RELEASE_PACK_VERIFICATION.md:81`; `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63`; `automation/validation/pack_fidelity.py:66-83`; `automation/validation/verify_delivery.sh` (no `pack_fidelity` call).
- Finding: the residual recommendation (wire pack-fidelity into the delivery build; verdict-bearing artifact) is still open; the notes file itself now matches its documented purpose (regenerated list).

### Item: Danger labels and script docs

- Evidence: `automation/validation/probe_pipeline_test.sh:8-10` (WARNING, outage drill); `disk_guard.sh:1-16` (safe reclaim order); `retire_migrated_docker_volumes.sh:1-12` (dry-run default, refuses before 2026-10-08); `OPERATOR_START_HERE.md` ("Mutating checks are opt-in … never run them as routine health checks").
- Result: no unlabeled destructive tooling found; bootstrap stages are root-gated and numbered; rollback notes are required by `AGENTS.md` rule 6.

### Item: Version shorthand

- Evidence: `README.md:27,29` vs `pins/images.lock` (`jasonish/suricata:8.0.7`, `opensearchproject/opensearch:2.19.6`).
- Finding: minor imprecision persists (prior DOC-P3-001).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DOC-001 | README | `README.md` | Complete | Version shorthand | P3 | DOC-P3-001 |
| DOC-002 | Local setup | Track A executed | Works | — | — | Keep |
| DOC-003 | Env docs | `.env.example`; OWNER_ENV_INVENTORY | Names-only docs | — | — | Keep |
| DOC-004 | Architecture/API | `docs/architecture/*` | Present | — | — | Keep |
| DOC-005 | DB/migration | `SCHEMA_AND_RETENTION.md` | Present | — | — | Keep |
| DOC-006 | Testing | `TEST_PROCEDURES.md`; gate suites | Present | — | — | Keep |
| DOC-007 | Deploy/rollback | README; UPGRADE_ROLLBACK | Present | — | — | Keep |
| DOC-008 | Incident/security | `docs/security/*` | Present | Breach drill unexercised | P2 | Exercise |
| DOC-009 | Contribution standards | `REPOSITORY.md`; AGENTS | Present | No CONTRIBUTING/LICENSE | P3 | Optional |
| DOC-010 | PR/release | templates; RELEASE_GATE | Present | Plan-gated enforcement | P2 | Owner decision |
| DOC-011 | Operator manuals | OPERATOR_START_HERE | Verified | — | — | Keep |
| DOC-012 | Troubleshooting | signal→runbook | All runbooks resolve | Generic mapping for 37 rules | P2 | IR-P1-001 |

## Findings

### DOC-P2-002 - The "authoritative" current-state page lags its sources (rule count, condition status, follow-up list)

- Severity: P2
- Confidence: High
- Area: DOC
- Evidence:
  - `docs/CURRENT_STATE.md:1` (title "Falcon current state (2026-09-30)"), `:56` ("**77-rule catalogue live** (75 proven; 2026-10-03)"), `:61-62` (C7 "Pending: the 7-day observation to ~2026-10-08 and the old named-volume deletion then"), `:64-70` (active follow-ups), last modified `29f75b4` 2026-10-03
  - `README.md:30` ("79 alert rules"); `docs/phase9/ALERT_CATALOGUE.yaml` (79 alerts; regenerated by `483f878`, 2026-10-04)
  - `docs/phase9/ALERT_FIRING_PROOFS.md:472-482` (77 live rules; 75/77 coverage — pre-#46)
  - `docs/architecture/EVOLUTION_GUIDE.md:274-279` (state block: C2 credential residuals; C7 open; pairing drift "fires until resolved") vs `docs/CURRENT_STATE.md:54` (C2 DONE) and `:106-114` (pairing restored 2026-10-03)
  - Post-audit ops commits in this clone: `main` `6e4fccd` and `ops/20261009-snapshot-repo-relocate-clean` `c13a416` ("ops: retire C7 volumes + relocate the OpenSearch snapshot repo off the data LV (2026-10-09)", "ops: restore the DO host-log TLS forwarder over the VPN")
  - Prior finding: 20260930 run DOC-P2-002 (same class: records/references contradict current state)
- What is happening: the page that declares itself the authoritative current-state view (and the evolution guide's state block) has not been refreshed for the 2026-10-04..09 changes; it contradicts the README, the generated catalogue, and the ops commits that have landed in the same clone.
- Why it matters: operators and agents reading the "authoritative" page get stale status (rule count, C7, C2, pairing) and cannot tell which artifact wins; the page itself says "the ledger wins", so the fix is a refresh from the ledgers.
- User / business impact: triage/maintenance decisions based on stale status; reviewer confusion.
- Security / privacy / reliability impact: low direct risk; process integrity.
- Recommended fix: refresh `docs/CURRENT_STATE.md` from `ledgers/` + the generated catalogue (append a 2026-10-09 section: C7 retirement executed, snapshot repo relocated, DO forwarder restored, 79 rules) and refresh the `ALERT_FIRING_PROOFS.md` coverage after the OBS-P0-001 rules; refresh the evolution-guide state block after each wave (its own rule).
- Suggested validation: a drift test that README/CURRENT_STATE rule counts match the generated catalogue (extend `readme_ledger_drift_test.sh`).
- Owner suggestion: falcon maintainer · Effort: S
- Status: open (same class as prior partially-fixed DOC-P2-002)

### DOC-P2-001 - Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict

- Severity: P3
- Confidence: High
- Area: DOC
- Evidence:
  - `docs/security/RELEASE_PACK_VERIFICATION.md:81` ("Recommendation 3 above (wire `pack_fidelity.py` into `verify_delivery.sh`) is still open")
  - `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` (Pack/publication checks "**partial**")
  - `automation/validation/pack_fidelity.py:66-83` (writes the list files; prints counts/verdict to stdout and exits non-zero on unexpected mismatch)
  - `automation/validation/verify_delivery.sh` (no `pack_fidelity` invocation; grep)
  - Prior finding: 20261002 run DOC-P2-001 / HYG-P2-003 (same issue; the notes-file purpose mismatch itself is fixed)
- What is happening: a stale repomix pack can still be archived into the delivery because `verify_delivery.sh` does not run the fidelity check; the notes file is a list, and the verdict exists only on stdout/exit code.
- Why it matters: the delivered pack is the reviewer's packed-only view; a stale pack undermines packed-only verification.
- Recommended fix: call `python3 automation/validation/pack_fidelity.py /home/user/falcon-repomix.md` (fail closed) in `verify_delivery.sh` before archiving; optionally write the verdict/counts into `PACK_VERIFICATION_NOTES.txt`.
- Suggested validation: a fixture pack with an unexpected mismatch fails `verify_delivery.sh`.
- Owner suggestion: publication session / coordinator · Effort: S
- Status: partially-fixed (documented residual)

### DOC-P3-001 - Imprecise version shorthand in the README vs the pinned versions

- Severity: P3
- Confidence: High
- Area: DOC
- Evidence:
  - `README.md:27` ("Suricata 8"), `:29` ("OpenSearch 2.19")
  - `pins/images.lock` (`jasonish/suricata:8.0.7`, `opensearchproject/opensearch:2.19.6`, `opensearchproject/opensearch-dashboards:2.19.6`)
  - Prior finding: 20261002 run DOC-P3-001 (same issue)
- What is happening: the entry doc uses major/minor shorthand while the repo pins exact versions.
- Why it matters: low; an operator matching versions against the lock file must resolve the shorthand.
- Recommended fix: state `8.0.7` / `2.19.6` in the README table (or say "as pinned in `pins/images.lock`").
- Suggested validation: grep the README for the pinned versions.
- Owner suggestion: maintainer · Effort: S
- Status: open

## Prior-Run Comparison

- Prior full run `falcon-20261005-full-main-e267ce1` emitted **no DOC findings**; its same-domain report said "Documentation is unusually complete … Fresh-checkout Track A is documented. No active finding." This run confirms that at `08e20d1` and adds currency findings.
- Lineage checks at `08e20d1`:
  - `DOC-P1-001` (quickstart commands failed; preconditions undocumented) — **verified-fixed**: `python3 ci/validate.py` → 0 failures, `verify_publication_chain.sh` → 0 failures, and the platform notes exist (`FRESH_CHECKOUT.md:18-38`).
  - `DOC-P2-001` (pack notes content vs purpose) — **partially-fixed**: notes regenerated by `pack_fidelity.py`; the wiring residual remains (re-emitted).
  - `DOC-P2-002` (records contradict current state) — **partially-fixed**; new instance re-emitted as DOC-P2-002.
  - `DOC-P2-003` (edge onboarding quick start) — edge-repo scope, not re-assessed here.
  - `DOC-P2-004` (verdict binds superseded package) — **still-open**, cross-ref PRIV-P2-003 (emitted once, in PRIV, to avoid double counting).
  - `DOC-P3-001` (stale links/version shorthand) — **partially-fixed** (relative links all resolve); version shorthand re-emitted.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale "authoritative" page drives decisions | P2 | High | Operator error | `CURRENT_STATE.md:1,56,61-62` | Refresh from ledgers |
| Stale pack shipped | P2 | Low | Packed-only review invalid | `RELEASE_PACK_VERIFICATION.md:81` | Wire `pack_fidelity.py` |
| Version shorthand mismatch | P3 | Low | Confusion | `README.md:27,29` | State exact versions |

## Recommendations

### Immediate / Release Blocking

None.

### This Week

1. Refresh `docs/CURRENT_STATE.md` and the evolution-guide state block — DOC-P2-002.
2. Wire `pack_fidelity.py` into `verify_delivery.sh` — DOC-P2-001.

### This Month

3. Correct README version shorthand — DOC-P3-001.
4. Refresh the firing-proof coverage table after the two new OBS rules.

### Later / Platform Evolution

5. Decide whether the repo needs `CONTRIBUTING.md`/`LICENSE` (private repo; currently AGENTS/REPOSITORY serve the purpose; DET-P3-001 tracks LICENSE).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add a 2026-10-09 state section | Removes contradictions | `docs/CURRENT_STATE.md` | Counts match catalogue |
| State exact versions | Removes ambiguity | `README.md` | Grep check |
| Extend the drift test to rule counts | Prevents recurrence | `automation/validation/tests/readme_ledger_drift_test.sh` | Test passes/fails on mutation |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Current-state refresh cadence | P2 | maintainer | S | — |
| Pack-fidelity wiring | P2 | publication session | S | — |
| Runbook mapping for generic rules | P2 | maintainer | M | IR-P1-001 |
| Exercise the breach procedure | P2 | owner | M | Owner |

## Suggested Tests

- `readme_ledger_drift_test.sh` extension: README/CURRENT_STATE rule count vs `ALERT_CATALOGUE.yaml`.
- Fixture: `verify_delivery.sh` fails on a mutated pack (pack-fidelity wiring).
- Link checker in CI (the read-only scan found 0 broken relative links; make it a gate).
- Literal quick-start job in CI (Track A already runs in `ci/validate.py`; keep the platform notes current).

## Suggested Documentation Updates

- `docs/CURRENT_STATE.md` — 2026-10-09 refresh.
- `docs/phase9/ALERT_FIRING_PROOFS.md` — coverage refresh (79 live).
- `docs/architecture/EVOLUTION_GUIDE.md` — state block refresh.
- `docs/security/RELEASE_PACK_VERIFICATION.md` — close recommendation 3 when wired.
- `README.md` — exact versions.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which artifact is the single current-state source after 2026-10-09? | The page claims authority but lags | Refreshed page or a new canonical artifact |
| Should the repo carry a LICENSE/CONTRIBUTING? | Deterministic lens flags LICENSE | Owner decision (private repo) |

## Limitations / Appendix

- Live walk was read-only; deploy stages (Track B) were not executed (they are mutating and the host is live). The live host currently shows `falcon-backup.service` failed and repeated vector OOM kills (journal) — recorded for the OBS/RES domains.
- Windows/Git-bash behavior was not re-tested; the FRESH_CHECKOUT platform notes cover it and the 20261002 run tested it.

## Findings

| ID | Severity | Title |
|---|---|---|
| DOC-P2-002 | P2 | The 'authoritative' current-state page lags its sources (rule count, condition status, follow-up list) |
| DOC-P2-001 | P3 | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict |
| DOC-P3-001 | P3 | Imprecise version shorthand in the README vs the pinned versions |
