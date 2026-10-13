# 16_documentation_devex_operator_readiness — Prompt 16 - Documentation, Developer Experience, and Operator Readiness Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `16_documentation_devex_operator_readiness.md` (area DOC, prompt)

## Verification Performed

# Documentation, Developer Experience, and Operator Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (lab host `falcon`, single KVM Ubuntu 24.04 host) — audit target `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (short `f5cb7c9`)
- Branch: `main` · Generated at: 2026-10-11T04:33Z · Auditor: repo-deep-dive subagent (prompt 16) · Area code: DOC
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/16_documentation_devex_operator_readiness.md`
- Scope limitations: read-only inspection; live evidence limited to read-only host commands (sudo value read from the owner file in a subshell, never printed); no state mutated. The quick-start commands were executed literally where read-only; no deploy stages were run. The edge repository's docs are out of scope.

## Scope

Reviewed at `f5cb7c9`: README and docs map, local setup/fresh-checkout path, environment docs, architecture/API docs, DB/migration docs, testing docs, deploy/rollback docs, incident/security docs, contribution/coding conventions, PR/release process, operator manuals, troubleshooting, ADRs/diagrams (none as formal ADRs), onboarding, script documentation and danger labeling, known limitations, AI agent instructions, prompt-pack/repo-map references.

Not reviewed: the edge repository's docs; live GitHub-side branch protection (other domain).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `README.md` | doc | Entry point, quick start, doc map | Refreshed 2026-10-10; `:30` says "85 alert rules" (source provisions 86) |
| `docs/CURRENT_STATE.md` | doc | Authoritative current-state page | Refreshed 2026-10-10; C7 DONE; `:56,:112` say 85 rules |
| `docs/phase9/ALERT_CATALOGUE.yaml` | generated | Rule inventory (claim: generated from live Grafana) | 85 entries; `falcon-wazuh-proxy-listeners` absent |
| `bootstrap/90-alerting.sh` | code | Source of truth for provisioned rules | 86 `write_rule` UIDs; `:252-253` proxy-listener rule (PR #53) |
| `docs/phase9/ALERT_FIRING_PROOFS.md` | doc | Per-rule firing-proof tracking | `:21-25` "Current coverage (authoritative)": 75 of 77 (2026-10-03) |
| `docs/architecture/EVOLUTION_GUIDE.md` | doc | Extension model + state block | `:270-279` state block still the 2026-10-01 view (C7 open; pairing drift) |
| `docs/security/RELEASE_PACK_VERIFICATION.md`; `automation/validation/verify_delivery.sh`; `PACK_VERIFICATION_NOTES.txt` | docs/code | Pack-fidelity wiring | `:81` says wiring "still open"; `verify_delivery.sh` has no `pack_fidelity` call; notes file is a list |
| `docs/runbooks/FRESH_CHECKOUT.md`, `OPERATOR_START_HERE.md`, `docs/README.md`, `REPOSITORY.md`, `AGENTS.md` | docs | Onboarding, triage, conventions, agent rules | Present and current |
| `ledgers/decision_log.md` (2026-10-10T01:20Z row) | ledger | Records the DOC-P2-002/OBS-P2-001 refresh | Catalogue regenerated at 85; PR #53 later added the 86th rule |

## Verification Performed

| Check | Type | Observed result |
|---|---|---|
| `python3 ci/validate.py` (README/FRESH_CHECKOUT Track A step 1) | literal walk | **PASS** `validation_failures=0` (incl. 50 shell suites, secret scan, digest binding, edge pin, license gate) |
| `bash automation/validation/verify_publication_chain.sh` (Track A step 2) | literal walk | **PASS** `publication_chain_failures=0` (digests bind the declared commit `3c11752`) |
| README quick-start script path existence check | inspect | All 24 `bootstrap/*` stage files and 4 `automation/validation/*` paths referenced exist |
| Markdown relative-link scan (first-party docs, read-only script) | inspect | 27 relative links checked, 0 broken |
| Catalogue runbook resolution | inspect | 85/85 catalogue entries resolve to existing runbook files |
| `write_rule` parse of `bootstrap/90-alerting.sh` (same parser as `alert_rule_lint_test.sh`) | reproduce | 86 unique UIDs; catalogue = 85; `falcon-wazuh-proxy-listeners` only in source |
| Live Grafana alert-rule API (read-only) | live | 86 rules; "Wazuh VPN proxy listener down" present — catalogue/README/CURRENT_STATE lag by one rule |
| `readme_ledger_drift_test.sh` | reproduce | PASS (28/28) — but it compares README ↔ catalogue only, so a shared stale count passes |
| Firing-proof coverage vs live rule set | inspect | Coverage section claims 75/77 (2026-10-03); live set is 86 |
| Pack-fidelity wiring grep | inspect | No `pack_fidelity` invocation anywhere in the delivery/publication scripts |

## Executive Summary

Documentation quality remains high: a clear doc map, an explicit operator triage order, runbooks per alert signal (85/85 catalogue runbooks resolve), an evidence doctrine, a fresh-checkout path whose two documented commands both pass literally at this commit, danger labels on mutating scripts, and agent rules that treat repository content as untrusted. The 2026-10-10 refresh fixed the previously stale `docs/CURRENT_STATE.md` (the register's DOC-P2-002 close is confirmed for that page). However, the same finding's other cited artifacts still lag the live state, and a new drift has appeared since PR #53: the alert catalogue/README/CURRENT_STATE say **85 rules** while `bootstrap/90-alerting.sh` provisions **86** and live Grafana serves **86** (`falcon-wazuh-proxy-listeners` is missing from the catalogue); the firing-proof coverage section still declares 75 of 77 rules proven (2026-10-03) against an 86-rule live set; and the `EVOLUTION_GUIDE.md` state block still shows the 2026-10-01 view (C7 open although C7 is DONE, pairing drift described as firing although restored). Two smaller residuals persist: pack-fidelity verification is still not wired into the delivery build (DOC-P2-001), and the README uses imprecise version shorthand (DOC-P3-001). Recommended next actions: regenerate the catalogue from live (86) and update the counts, refresh the firing-proof coverage and evolution-guide state block, wire `pack_fidelity.py` into `verify_delivery.sh`, and state exact pinned versions.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| README | `README.md` | Entry, quick start, map | Current except rule count | Low | 85 vs 86 |
| Current-state page | `docs/CURRENT_STATE.md` | Authoritative state view | Refreshed 2026-10-10; count lags | Medium | 85 vs 86 |
| Fresh checkout | `docs/runbooks/FRESH_CHECKOUT.md` | Track A/B/C paths + platform notes | Verified | Low | Both commands pass |
| Operator manual | `docs/runbooks/OPERATOR_START_HERE.md` | Triage order, health view | Verified read-only | Low | Mutating checks fenced |
| Alert catalogue | `docs/phase9/ALERT_CATALOGUE.yaml` | Generated rule inventory | 85; missing the #53 rule | Medium | Drift unguarded |
| Firing proofs | `docs/phase9/ALERT_FIRING_PROOFS.md` | Per-rule proof tracking | Stale coverage (75/77) | Medium | 9+ rules unaccounted |
| Evolution guide | `docs/architecture/EVOLUTION_GUIDE.md` | Extension model + state block | State block 2026-10-01 | Low | C7/pairing stale |
| Pack verification | `docs/security/RELEASE_PACK_VERIFICATION.md` | Repomix pack status | Wiring residual open | Medium | `:81` |
| Env docs | `docs/security/OWNER_ENV_INVENTORY.md`; `.env.example` | Credential classes, names-only | Present | Low | Values never in repo |
| Deploy/rollback | `README.md`; `docs/phase7/runbooks/UPGRADE_ROLLBACK.md` | Ordered deploy + rollback | Present | Low | `run-all.sh` caveat explicit |

## Findings

### DOC-P2-002 — Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 85 vs 86 provisioned/live, firing proofs at 75/77, evolution-guide block at 2026-10-01

- Severity: P2 · Confidence: High · Status: partially-fixed (re-emitted residual)
- Evidence:
  - `docs/phase9/ALERT_CATALOGUE.yaml` — 85 entries; `falcon-wazuh-proxy-listeners` absent (header claims generation from live Grafana)
  - `bootstrap/90-alerting.sh:252-253` — the rule is provisioned (PR #53, 2026-10-11); parsed `write_rule` set = 86 unique UIDs
  - Live Grafana `api/v1/provisioning/alert-rules` (read-only, 2026-10-11) = 86 rules incl. "Wazuh VPN proxy listener down"
  - `README.md:30` ("85 alert rules"); `docs/CURRENT_STATE.md:56` ("85-rule catalogue live"), `:112` ("85 rules live")
  - `docs/phase9/ALERT_FIRING_PROOFS.md:21-25` — "As of 2026-10-03, 75 of the 77 live rules have a firing proof" (section titled "Current coverage (authoritative)")
  - `docs/architecture/EVOLUTION_GUIDE.md:270-279` — state block dated 2026-10-01: C7 open (CURRENT_STATE: DONE 2026-10-09), pairing drift "fires until resolved" (restored 2026-10-03), C2 credential residuals (DONE)
  - `ledgers/decision_log.md` 2026-10-10T01:20Z — the refresh regenerated the catalogue at 85 and made the README drift test compare README ↔ catalogue
  - Verification register 2026-10-11: DOC-P2-002 marked verified-fixed — confirmed for `CURRENT_STATE.md` only; the other cited artifacts remain stale
- What is happening: the status/coverage artifacts that operators read are not refreshed after rule additions and capacity close-out; the drift test compares README to the catalogue, so both can carry the same stale count undetected.
- Why it matters: the new critical `falcon-wazuh-proxy-listeners` rule has no catalogue entry (alert→runbook mapping) and no firing-proof coverage; operators cannot tell which of the 9 post-refresh rules are proven; the evolution guide misstates C7 as open.
- Recommended fix: regenerate `ALERT_CATALOGUE.yaml` from live (86) and update README/CURRENT_STATE counts; refresh the firing-proof coverage section (or mark it dated and add the new rules); refresh the evolution-guide state block; extend `alert_rule_lint_test.sh` (already parses `90-alerting.sh`) to compare the parsed rule set against the catalogue (IDs/count) so source→catalogue drift fails closed.
- Suggested validation: a mutated source rule (or a removed catalogue entry) fails the extended lint; counts in README/CURRENT_STATE equal live.
- Owner suggestion: falcon maintainer · Effort: S
- Status: partially-fixed (CURRENT_STATE fixed; residuals re-emitted)

### DOC-P2-001 — Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict

- Severity: P3 · Confidence: High · Status: open
- Evidence:
  - `docs/security/RELEASE_PACK_VERIFICATION.md:81` ("Recommendation 3 above (wire `pack_fidelity.py` into `verify_delivery.sh`) is still open")
  - `docs/security/CI_GOVERNANCE_RECONCILIATION.md:63` (Pack/publication checks "partial")
  - `automation/validation/verify_delivery.sh` — no `pack_fidelity` invocation (grep over `automation/` finds only `pack_fidelity.py` itself)
  - `automation/validation/pack_fidelity.py:1-12` — writes the list files; verdict exists only on stdout/exit code
  - `PACK_VERIFICATION_NOTES.txt` — whitespace-normalisation/not-included lists; no verdict line
- What is happening: a stale repomix pack can still be archived into the delivery because `verify_delivery.sh` does not run the fidelity check.
- Recommended fix: call `python3 automation/validation/pack_fidelity.py /home/user/falcon-repomix.md` (fail closed) in `verify_delivery.sh` before archiving; optionally write the verdict/counts into `PACK_VERIFICATION_NOTES.txt`.
- Suggested validation: a fixture pack with an unexpected mismatch fails `verify_delivery.sh`.
- Status: open (same as prior full run)

### DOC-P3-001 — Imprecise version shorthand in the README vs the pinned versions

- Severity: P3 · Confidence: High · Status: open
- Evidence:
  - `README.md:27` ("Suricata 8"), `:29` ("OpenSearch 2.19")
  - `pins/images.lock:13,20,55` (`opensearchproject/opensearch:2.19.6`, `opensearch-dashboards:2.19.6`, `jasonish/suricata:8.0.7`)
- What is happening: the entry doc uses major/minor shorthand while the repo pins exact versions.
- Recommended fix: state `8.0.7` / `2.19.6` in the README table (or say "as pinned in `pins/images.lock`").
- Status: open (same as prior full run)

## Prior-Run Comparison

- Prior full run `falcon-20261009-2117-full-08e20d1` emitted DOC-P2-002 (P2), DOC-P2-001 (P3) and DOC-P3-001 (P3).
- The 2026-10-11 verification register marks DOC-P2-002 verified-fixed ("readme_ledger_drift_test 28/0 PASS; CURRENT_STATE carries the 2026-10-09/10 section"). At `f5cb7c9` that is confirmed for `docs/CURRENT_STATE.md`, but the same finding's other cited artifacts (firing proofs; evolution-guide state block) remain stale and the rule-count drift recurred after PR #53 — the finding is re-emitted as partially-fixed rather than closed. DOC-P2-001 and DOC-P3-001 remain open (register agrees).
- Prior-run fixes re-checked: DOC-P1-001 (quickstart) remains verified-fixed — both Track A commands pass literally; the relative-link scan stays clean (27/0); all README-referenced scripts exist.
- Post-08e20d1 changes reviewed (PRs #49–#54): #49 refreshed docs to 85 rules; #53 added the 86th rule without a catalogue regen (the drift above); #50–#52/#54 are ops-only for docs.
- Cross-refs (not re-filed here): `docs/RELEASE_GATE.md` remains a 2026-10-03-era opinion (HYGIENE-P2-002, open); the docs map lists the 2026-09-30 audit run as the reference run (AI-P3-001 pointers).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Operators trust a stale catalogue/coverage page | P2 | High | Missed rule/runbook mapping; false "unproven" picture | `ALERT_CATALOGUE.yaml` (85); `ALERT_FIRING_PROOFS.md:21` | Regenerate + extend the lint to compare source↔catalogue |
| Stale evolution-guide state block misleads | P3 | Medium | Wrong status (C7) in extension decisions | `EVOLUTION_GUIDE.md:270-279` | Refresh from ledgers |
| Stale pack shipped | P3 | Low | Packed-only review invalid | `RELEASE_PACK_VERIFICATION.md:81` | Wire `pack_fidelity.py` |
| Version shorthand mismatch | P3 | Low | Confusion | `README.md:27,29` | State exact versions |

## Recommendations

### Immediate / Release Blocking

None.

### This Week

1. Regenerate the catalogue from live (86) and update README/CURRENT_STATE counts; extend the rule lint to compare `90-alerting.sh` ↔ catalogue — DOC-P2-002.
2. Refresh the firing-proof coverage section and the evolution-guide state block — DOC-P2-002.

### This Month

3. Wire `pack_fidelity.py` into `verify_delivery.sh` — DOC-P2-001.
4. Correct README version shorthand — DOC-P3-001.

### Later / Platform Evolution

5. Decide whether the repo needs `CONTRIBUTING.md`/`LICENSE` (private repo; DET-P3-001 tracks LICENSE).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add the missing catalogue entry / regen | Restores alert→runbook coverage for the new rule | `docs/phase9/ALERT_CATALOGUE.yaml` | Count matches live (86) |
| One-line coverage note in the firing-proof page | Removes a false authoritative claim | `docs/phase9/ALERT_FIRING_PROOFS.md` | Dated coverage statement |
| State exact versions | Removes ambiguity | `README.md` | Grep check |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Source↔catalogue drift gate | P2 | maintainer | S | — |
| Coverage refresh cadence | P2 | maintainer | S | — |
| Pack-fidelity wiring | P3 | publication session | S | — |

## Suggested Tests

- Extend `alert_rule_lint_test.sh` (or `readme_ledger_drift_test.sh`) to compare the parsed `write_rule` UID set against `ALERT_CATALOGUE.yaml`; fail on any difference.
- Fixture: `verify_delivery.sh` fails on a mutated pack (pack-fidelity wiring).
- Link checker in CI (the read-only scan found 0 broken relative links; make it a gate).
- Literal quick-start job in CI (Track A already runs in `ci/validate.py`; keep the platform notes current).

## Suggested Documentation Updates

- `docs/phase9/ALERT_CATALOGUE.yaml` — regenerate at 86.
- `README.md`, `docs/CURRENT_STATE.md` — rule counts.
- `docs/phase9/ALERT_FIRING_PROOFS.md` — coverage refresh for the post-2026-10-03 rules.
- `docs/architecture/EVOLUTION_GUIDE.md` — state-block refresh.
- `docs/security/RELEASE_PACK_VERIFICATION.md` — close recommendation 3 when wired.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which artifact is the single rule-count source (source vs catalogue vs live)? | Prevents recurring drift | Decision recorded in the lint/test |
| Should the firing-proof page remain "authoritative" while append-only? | Operators read the top section | Dated coverage statement or regen |
| Should the repo carry a LICENSE/CONTRIBUTING? | Deterministic lens flags LICENSE | Owner decision (private repo) |

## Limitations / Appendix

- Live walk was read-only; deploy stages (Track B) were not executed (mutating; the host is live). Live Grafana rule count was read via the provisioning API with the admin credential in a subshell (never printed).
- Windows/Git-bash behavior was not re-tested; the FRESH_CHECKOUT platform notes cover it.
- Cross-ref: `docs/RELEASE_GATE.md` currency is tracked under HYGIENE-P2-002 (other domain) and is not re-filed here.

## Findings

| ID | Severity | Title |
|---|---|---|
| DOC-P2-002 | P2 | Status artifacts still lag the live state: catalogue/README/CURRENT_STATE at 85 vs 86 provisioned/live, firing proofs at 75/77, evolution-guide block at 2026-10-01 |
| DOC-P2-001 | P3 | Pack-fidelity verification is still not wired into the delivery build; the notes file carries no verdict |
| DOC-P3-001 | P3 | Imprecise version shorthand in the README vs the pinned versions |
