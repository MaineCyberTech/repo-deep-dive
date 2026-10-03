# Documentation, Developer Experience, and Operator Readiness Audit

## Audit Metadata

- Audit name: `repo-deep-dive` (profile `falcon-lab` v1.0.0, pack v1.2.1)
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repository: `falcon-build` @ `8282d3f`; `falcon-edge-build` @ `f1c5def` (moved `45dfed0`→`f1c5def` during the run; CI/evidence delta)
- Branch: `main` (both). falcon working tree: `M evidence/raw/REVIEW-FIX/20260930T035539Z_offsite-backup-env-fix.out`, `?? docs/audits/`, `??` its `.meta.json`; edge clean
- Generated at: 2026-09-30 · Auditor: wave-1 subagent (prompt 16), read-only (no root/docker/service mutation; no secret values printed)
- Area code: DOC · Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/16_documentation_devex_operator_readiness.md`
- Scope limitations: no root/owner credentials; mutating bootstrap/health steps reviewed from source, not executed. Live state = `live_snapshot.txt` (07:01:55Z) + sibling reports.

## Scope

Reviewed both repos: entry docs, quick starts/onboarding, runbooks, architecture/port/API docs, current-state and closeout artifacts, dangerous-script labeling, broken references. Not reviewed: vendor/upstream UI docs, deep source quality (09/20/21), live runtime (12). Read-only documented steps were walked literally; root steps were not executed.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| falcon `README.md`, `AGENTS.md`, `REPOSITORY.md` | entry docs | first docs trusted | README:8-13,22,37; AGENTS:71-73; REPOSITORY:39,53 |
| falcon digest, gate ledgers, `PRODUCTION_VERDICT.md` | status + records | "current state" authority | digest derived; verdict APPROVED vs :31 NOT_SUPPORTED |
| falcon runbooks/architecture | operator/arch docs | triage + diagnostics | SENSOR_SILENCE:27-28,81,170; RESTORE:181; INCIDENT:6,274; PORT_PROTOCOL_MATRIX:17-36 |
| falcon scripts: `test_closed_mode.sh`, `test_tunnel.sh`, `probe_pipeline_test.sh`, `run-all.sh` | scripts | quick start/danger labels | WARN headers added; tunnel 51820; run-all=10-40 |
| falcon records: contradiction/exception registers, OWNER_INPUTS, progress/test/index ledgers | ledgers | resolved-as-open; host paths | C-04/05/06/08/11/22; inputs REQUESTED; 264/461 paths |
| edge README/AGENTS/REPOSITORY + phase/CI docs | entry/phase docs | newcomer path | README:24 fixed; AGENTS:44-45; REPOSITORY:22 stale |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py` (falcon, run folder present) | execution | quick-start step 1 | exit 1; 2 `long_hex` hits in `01/02` reports (CI-P2-001) |
| `bash automation/validation/verify_publication_chain.sh` | execution | integrity claim | 0 failures |
| `bash automation/evidence/manifest.sh check` | execution | evidence integrity | exit 1; 1 mismatch (uncommitted REVIEW-FIX `.out`) |
| `bash automation/validation/secret_scan_history.sh` | execution | recorded scan claim | exit 1, 22 findings, `REVIEW_REQUIRED` (recorded: 16) |
| `bash ci/validate.sh` (edge); `deploy edge --help` | execution | edge quick start/CLI count | ALL PASS; 18 subcommands vs "16" |

## Executive Summary

Strengths: ND-P1-001 (digest vs ledgers) is **verified-fixed** — `publish_digests.sh:30-35` derives verdict/readiness/open-gates and the chain verifies 0 failures. Dangerous scripts gained WARNING headers and `test_closed_mode.sh` restores the captured inbound mode. Edge `ci/validate.sh` passes literally. Risks: there is still no single authoritative "current state" document — falcon README/AGENTS list closed gates as open and say production is unsupported (ND-P1-002 still-open); edge AGENTS/REPOSITORY say the hardware is absent while README+ledger say it is attached and proven (ND-P1-005 partially fixed). Falcon's quick start cannot deploy a clean host and its first command is red in this tree (CI-P2-001). Incident runbooks describe a no-VPN/no-SPAN world. Next: current-state block, fix both entries, correct deploy order, append superseded notes.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| falcon README | `README.md` | overview/quick start | stale state/counts; host links | High | :8-13,:22,:12-13 |
| falcon AGENTS/REPOSITORY | `AGENTS.md`, `REPOSITORY.md` | agent/conventions | closed gates open; index claim false | High | AGENTS:71-73; REPO:39 |
| falcon runbooks | `docs/runbooks/`, `docs/phase7/runbooks/` | triage | stale VPN/SPAN/RPO text | High | DOC-P2-001 |
| falcon arch/refs | `docs/architecture/`, phase9 docs | topology/refs | drafts as current; dead refs | Medium | DOC-P2-002 |
| edge entry docs | README/AGENTS/REPOSITORY | onboarding | README fixed; two stale | High | DOC-P1-002 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| README | 2 | README:8-13,22 | stale authority/counts | regenerate block; fix counts |
| Local setup | 2 | `run-all.sh`; compose env_file | clean-host deploy broken | `--full` or ordered steps |
| Env docs | 2 | AGENTS both; edge secrets dir | third secret store undocumented | document stores |
| Architecture/API docs | 2 | TARGET_ARCHITECTURE:1-3; PORT_PROTOCOL_MATRIX | drafts current; port drift | banner + regenerate |
| DB/migration docs | 3 | DATA_QUALITY_SCORECARD:4 | `evidence/phase9/` dead refs | fix refs |
| Testing docs | 3 | edge GITHUB_CI (163 = actual); falcon no unit tests | run instructions scattered | add sections |
| Deploy/rollback docs | 3 | PRODUCTION_CHANGE_PLAN; OWNER_ACTIONS | deploy order wrong | fix quick start |
| Incident/security docs | 2 | SENSOR_SILENCE:27-28; INCIDENT:6 | stale threat picture | superseded notes |
| Contribution standards | 2 | AGENTS/REPOSITORY rules | no CONTRIBUTING/gate map | add CONTRIBUTING |
| PR/release process | 2 | AGENTS flow; GITHUB_CI | spread across docs | release checklist |
| Operator manuals | 3 | OPERATOR_START_HERE; runbook inventory | stale sections | refresh + pointer |
| Troubleshooting | 3 | 15 edge runbooks; falcon runbook table | broken steps (51820) | parameterize |

## Detailed Review

### Item: falcon current-state authority
- Evidence: `README.md:8-13`, `AGENTS.md:71-73` vs `gate_ledger.csv` (P8-G10 PASS), `phase9_gate_ledger.csv` (13 PASS/1 N/A), `PRODUCTION_VERDICT.md` (APPROVED), digest:10-13 (APPROVED/none). No drift control ties entry docs to ledgers. Fix: generated `docs/CURRENT_STATE.md` + CI check.

### Item: falcon quick start / dangerous scripts
- Evidence: `README.md:32-41`; `run-all.sh:6-9` (10-40 only, echoes "all stages complete"); compose requires stage-50 `central.env` (`central/docker-compose.yml:55,95,126`); `ci/validate.py` exit 1. Scripts now carry WARN headers (`test_closed_mode.sh:1-9`, `probe_pipeline_test.sh:1-11`); checklist residual only. Fix: `--full`/ordered steps; scanner allowlist; checklist warning.

### Item: edge entry docs and onboarding
- Evidence: `README.md:24` correct vs `AGENTS.md:44-45`/`REPOSITORY.md:22` stale; `README.md:60-71` omits tests/CP/enroll/bake/secrets; `docs/GITHUB_CI.md:73` "every 20 minutes" vs daily cron (CI-P3-001). Fix: update lines; add QUICKSTART.md.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| DOC-001 | README accuracy | README:8-13,22 | manual | stale state/counts | High | derive + fix |
| DOC-002 | Local setup | run-all.sh; README:37 | 10-40 only | no clean-host deploy | High | `--full`/steps |
| DOC-003 | Env docs | AGENTS both | falcon documented | edge store missing | Medium | document |
| DOC-004 | Architecture/API docs | TARGET_ARCHITECTURE | partial banner | `mon`/51820 | Medium | regenerate |
| DOC-005 | DB/migration docs | DATA_QUALITY_SCORECARD:4 | phase docs | dead refs | Low | fix |
| DOC-006 | Testing docs | GITHUB_CI:22-24 | edge current | falcon run path unclear | Medium | add sections |
| DOC-007 | Deploy/rollback docs | CHANGE_PLAN/OWNER_ACTIONS | documented | README order | Medium | fix |
| DOC-008 | Incident/security docs | SENSOR_SILENCE:27-28 | rich runbooks | stale state | High | superseded notes |
| DOC-009 | Contribution standards | AGENTS/REPOSITORY | hard rules | no CONTRIBUTING | Medium | add |
| DOC-010 | PR/release process | AGENTS flow; GITHUB_CI | per-repo | no single doc | Low | checklist |
| DOC-011 | Operator manuals | OPERATOR_START_HERE | good | stale sections | Medium | refresh |
| DOC-012 | Troubleshooting | runbook inventory | good | broken steps | Medium | parameterize |

## Findings
### Finding ID: DOC-P1-001 - Falcon entry docs still contradict the ledgers on current state
- Severity: P1 · Confidence: High · Area: DOC (falcon-build)
- Evidence: `README.md:8-13` ("Current state (2026-09-24) … not supported … remain open"; host-file links); `AGENTS.md:71-73` (P8-G10/P9-G02/G10/G11/G12/G14 "open"/"BLOCKED"); `ledgers/gate_ledger.csv` P8-G10 PASS 2026-09-29; `phase9_gate_ledger.csv` 13 PASS/1 N/A; `PACKAGE_DIGEST.txt:10-13` APPROVED/`open_gates=none`
- What is happening: the three most-read documents were not refreshed after the 2026-09-29 closure; they disagree with the digest the project calls authoritative.
- Why it matters: agents/engineers chase finished gates, miss the real backlog, may regenerate stale artifacts.
- User / business impact: wasted first-week effort; false external statements; trust erosion.
- Security / privacy / reliability impact: indirect (misdirected operational effort).
- Recommended fix: replace static paragraphs with a generated `docs/CURRENT_STATE.md` block referenced from README/AGENTS/REPOSITORY; add a CI drift check.
- Suggested validation: CI fails when entry-doc fields diverge from ledger-derived values.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: none
- Status: still-open (prior ND-P1-002)
### Finding ID: DOC-P1-002 - Edge entry docs state the hardware is absent; it is attached, enrolled, and proven
- Severity: P1 · Confidence: High · Area: DOC (falcon-edge-build)
- Evidence: `AGENTS.md:44-45` ("RTL8812BU/MT7612U … NOT attached … gates stay BLOCKED"); `REPOSITORY.md:22` ("HARDWARE … not present"); `README.md:24` contradicts both ("RTL8812BU proven"); `ledgers/gate_ledger.csv` P6-G05 PASS 2026-09-30, P6-G06 BLOCKED (MT7612U)
- What is happening: README corrected; AGENTS/REPOSITORY not — AGENTS contradicts itself within one bullet.
- Why it matters: agents may skip executable device work; this run's task brief repeated the stale claim.
- User / business impact: onboarding confusion; wrong planning for adapter gates.
- Security / privacy / reliability impact: none direct.
- Recommended fix: update `AGENTS.md:44-45`, `REPOSITORY.md:22` to README wording; point to the ledger.
- Suggested validation: grep for "NOT attached"/"not present" returns zero; lines match ledger.
- Owner suggestion: edge maintainer · Effort estimate: S · Dependencies: none
- Status: partially-fixed (prior ND-P1-005)
### Finding ID: DOC-P1-003 - Falcon README quick start cannot deploy, and its first step fails in-tree
- Severity: P1 · Confidence: High · Area: DOC (falcon-build)
- Evidence: `README.md:32-41` (`sudo bootstrap/run-all.sh # or the individual 10-…98- steps`); `bootstrap/run-all.sh:6-9` runs only 10/20/30/40 and echoes "all stages complete"; `compose/central/docker-compose.yml:55,95,126` requires `central.env` from stage 50; literal walk `python3 ci/validate.py` exit 1 (CI-P2-001)
- What is happening: the documented deploy entry is host prep only; the safe static step is red because run folders are scanned as content.
- Why it matters: a clean-host newcomer concludes the repo is broken; AGENTS rule 5 is unhonorable without a real defect.
- User / business impact: onboarding failure; support load; gate-bypass habit.
- Security / privacy / reliability impact: improvised deploy order may skip secrets/firewall stages.
- Recommended fix: `run-all.sh --full` or ordered 10→50→60→70→90→91→95-99 steps; allowlist `docs/audits/**` 40-hex IDs (CI-P2-001).
- Suggested validation: staged clean-host rehearsal reaches healthy compose; `ci/validate.py` green with run folder.
- Owner suggestion: falcon maintainer · Effort estimate: S/M · Dependencies: CI-P2-001
- Status: still-open (prior ND-P1-004)
### Finding ID: DOC-P2-001 - Falcon runbooks and VPN checklist carry stale/mutating state affecting operations
- Severity: P2 · Confidence: High · Area: DOC (falcon-build)
- Evidence: `SENSOR_SILENCE.md:27-28,81,170` ("no VPN", synthetic veth, OD-05/OD-07 open); `RESTORE.md:181` (OD-10 pending); `INCIDENT_RESPONSE.md:6,274` (OD-12/OD-18 pending) — all resolved per `PRODUCTION_VERDICT.md`/ledgers (P9-G03/G04, P6-G09, P9-G07); `VPN_ONBOARDING_CHECKLIST.md:17-18` runs `test_tunnel.sh`/`test_closed_mode.sh` bare (scripts now warn; checklist does not)
- What is happening: append-only remediation never reached these sections; the checklist was missed when ND-P1-003 was fixed.
- Why it matters: wrong triage during incidents; operators may run mode-switching tests as routine steps.
- User / business impact: slower MTTR; unnecessary firewall churn.
- Security / privacy / reliability impact: missed tunnel/SPAN diagnostics; low residual firewall-mode risk.
- Recommended fix: append dated "superseded 2026-09-29 — see X" notes + "state as of" headers; add checklist warnings and the `phase9_vpn_do_tests.sh` pointer; fix the 51820 port (INFRA-P2-002).
- Suggested validation: stale phrases appear only in superseded notes; warnings adjacent to mutating commands.
- Owner suggestion: falcon maintainer · Effort estimate: M · Dependencies: none
- Status: still-open (prior ND-P2-007 + partially-fixed ND-P1-003)
### Finding ID: DOC-P2-002 - Records and references contradict current state (index paths, registers, broken refs/counts, drafts)
- Severity: P2 · Confidence: High · Area: DOC (falcon-build)
- Evidence: `ledgers/evidence_index.csv` 264/461 rows start `../monitoring-build/evidence/...` (copied into `review-package/`); `REPOSITORY.md:39` claims package-relative paths; `contradiction_ledger.md:8-16,26` C-04/05/06/08/11/22 OPEN though complete; `OWNER_INPUTS_REQUIRED.md:10-14,29-62` many inputs **REQUESTED** while P9-G01/G11/G12 PASS; `DATA_QUALITY_SCORECARD.md:4`/`CERTIFICATE_AND_TIME_CONTROLS.md:4` cite `evidence/phase9/`; `PHASE9_CHARTER.md:91` points at `closeout/PRODUCTION_VERDICT_TEMPLATE.md`; `review-package/README.md:8,34,36` (mon, Phase 1-8, SPAN/VPN out of scope); `README.md:22` counts vs 3/72/31; `TARGET_ARCHITECTURE.md:1-3,21-28` draft linked as current
- What is happening: append-only records lack resolution rows/"latest row wins"; drafts and small errors accumulated; refs were never updated.
- Why it matters: reviewers hit dead paths; agents see completed work as open; diagnostics may use stale ports/architecture.
- User / business impact: review/onboarding time loss; false open-items list.
- Security / privacy / reliability impact: firewall/diagnostic decisions can use the stale matrix.
- Recommended fix: package-relative index rewrite; append resolution rows + latest-row headers; batch-fix paths/counts; banner the drafts; regenerate the port matrix.
- Suggested validation: index paths resolve inside `review-package/`; link checker + count assertions; no OPEN row lacks a later resolution.
- Owner suggestion: falcon maintainer · Effort estimate: M · Dependencies: package rebuild
- Status: still-open (prior ND-P2-008/011, ND-P3-001/002/003, ND-P2-004)
### Finding ID: DOC-P2-003 - Edge onboarding lacks a quick start and a secrets map; phase/CI docs drift; process docs absent
- Severity: P2 · Confidence: High · Area: DOC (falcon-edge-build)
- Evidence: `README.md:60-71` (validate/capture/index only; no tests/CP/enroll/bake); `AGENTS.md:26-36` flow omits the 163-test suite; `/home/user/falcon-edge-secrets` (CA, signing seed, DB, spool) not documented; `docs/GITHUB_CI.md:73` "every 20 minutes" vs daily cron (CI-P3-001); `docs/phase4/CLOSEOUT.md:38` "16 commands" vs 18; `docs/README.md` lists empty `phase10/`; `README.md:53` lists missing `bootstrap/`; `docs/phase5/CLOSEOUT.md:6-9` vs `:43`; `docs/phase6/CLOSEOUT.md:42-43` vs ledger 6 PASS/2 BLOCKED; no CONTRIBUTING/CHANGELOG in either repo (BP-P3-001)
- What is happening: prerequisites/process are tribal knowledge; phase docs are append-only stale.
- Why it matters: first-week friction; wrong secret store risk; wrong counts quoted.
- User / business impact: slower onboarding; review errors.
- Security / privacy / reliability impact: secrets work could start in the wrong location.
- Recommended fix: add `QUICKSTART.md` (validate+tests+CP+token/enroll+bake/verify; PYTHONPATH/PyYAML/openssl/docker; secrets map); batch-correct phase counts with superseded markers; add "related repositories"; add CONTRIBUTING/CHANGELOG.
- Suggested validation: new account follows QUICKSTART to green validate+tests; counts match ledger/repo.
- Owner suggestion: edge maintainer · Effort estimate: S/M · Dependencies: none
- Status: partially-fixed (prior ND-P3-007/009; ND-P2-013 doc items still-open)
### Finding ID: DOC-P2-004 - Published verdict binds a superseded package and still says NOT_SUPPORTED
- Severity: P2 · Confidence: High · Area: DOC (falcon-build)
- Evidence: `PRODUCTION_VERDICT.md:7-9` binds `c312ab7` (1,168 package/918 evidence entries) vs `PACKAGE_DIGEST.txt:2-8` `3ac6cd4` (2,067/933); `PRODUCTION_VERDICT.md:31` "Production readiness: `NOT_SUPPORTED`" inside an APPROVED verdict (:49); no scope statement for post-verdict commits
- What is happening: the signed verdict references an older artifact set and carries a contradictory readiness line.
- Why it matters: governance ambiguity about what is approved.
- User / business impact: reviewer/auditor scope confusion.
- Security / privacy / reliability impact: none direct.
- Recommended fix: append a scope/readiness amendment (or derive the readiness line from the digest); state the re-review trigger.
- Suggested validation: verdict commit == digest delivered commit or an explicit scope statement exists.
- Owner suggestion: owner/falcon maintainer · Effort estimate: M · Dependencies: owner decision
- Status: still-open (prior REV-P1-001/003; cross-ref FEAT-P1-002/INV-P0-002, not duplicated)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Agents act on stale gate lists | High | High | wasted work; false status | README:8-13; AGENTS:71-73 | DOC-P1-001 |
| Incident responder follows stale runbook | High | Medium | wrong triage | SENSOR_SILENCE:27-28 | DOC-P2-001 |
| Clean-host deploy fails from docs | High | Medium | onboarding failure | run-all.sh; compose env_file | DOC-P1-003 |

## Recommendations

### Immediate / Release Blocking
- Fix falcon entry-doc current state (DOC-P1-001) and edge AGENTS/REPOSITORY hardware lines (DOC-P1-002).
- Fix deploy order/`run-all.sh --full` (DOC-P1-003) and the scanner allowlist (CI-P2-001).

### This Week
- Append superseded notes to stale runbooks/checklist (DOC-P2-001); resolve records/reference batch (DOC-P2-002).
- Edge QUICKSTART + secrets map + phase-doc corrections (DOC-P2-003).

### This Month
- `docs/CURRENT_STATE.md` + CI drift checks; verdict scope amendment (DOC-P2-004); CONTRIBUTING/CHANGELOG (DOC-P2-003).

### Later / Platform Evolution
- Generate port matrix/inventory from compose/nftables; add a staged onboarding rehearsal path.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Replace AGENTS.md gate list with digest/ledger pointer | removes high-traffic misinformation | `AGENTS.md:71-73` | no stale gate IDs |
| Fix edge AGENTS/REPOSITORY hardware lines | matches README/ledger | `AGENTS.md`, `REPOSITORY.md` | grep clean |
| README deploy order or `--full` | clean-host onboarding | `README.md`, `run-all.sh` | staged rehearsal |
| Fix `evidence/phase9/` + charter template refs | broken links closed | phase9 docs | link checker |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| `docs/CURRENT_STATE.md` + doc-drift CI | P1 | falcon maintainer | M | digest derivation |
| Clean-host deploy rehearsal documented+executed | P1 | falcon maintainer | M | owner window |
| Runbook superseded notes + state headers + checklist warning | P2 | falcon maintainer | M | none |
| Evidence-index relative rewrite + register resolution rows | P2 | falcon maintainer | S/M | package rebuild |
| Verdict scope amendment | P2 | owner | S | owner decision |
| Edge QUICKSTART + secrets map + phase corrections | P2 | edge maintainer | S/M | none |

## Suggested Tests

- CI doc-drift: README/AGENTS current-state fields vs ledger-derived values.
- Link/path checker over `docs/**/*.md` + review-package README (detects `evidence/phase9/`, `closeout/PRODUCTION_VERDICT_TEMPLATE.md`).
- Count assertions: dashboards/panels/alert catalogue vs README/verdict.
- Onboarding smoke: staged clean host follows README steps with recorded capture; runbook freshness check for "OD-"/"pending" text.

## Suggested Documentation Updates

- falcon: `docs/CURRENT_STATE.md` (new), README/AGENTS/REPOSITORY, phase7 runbooks ×3, architecture banner, phase9 refs/VPN checklist, review-package README, CONTRIBUTING/CHANGELOG.
- edge: AGENTS/REPOSITORY, `QUICKSTART.md` (new), GITHUB_CI cadence, phase{4,5,6} corrections, docs/README.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `docs/CURRENT_STATE.md` the intended authority, or the digest only? | where drift checks attach | owner/maintainer decision |
| Does APPROVED extend to post-`c312ab7` commits? | approval scope | owner/reviewer statement |
| Who updates entry docs after closures? | recurrence prevention | process decision |
| Is `mct/` an import or maintained code? | competing docs cleanup | owner decision |

## Appendix A — Prior-run (20260930-0320) status at current commits

- **verified-fixed:** ND-P1-001 (digest now derived: APPROVED/none; `publish_digests.sh:30-35`; chain 0 failures; residual N/A omission = HYGIENE-P2-002); ND-P3-006 (falcon `validate.yml` exists; caveat CI-P2-001).
- **partially-fixed:** ND-P1-003 (script WARN headers + mode restore; checklist residual = DOC-P2-001); ND-P1-005 (README:24 fixed; AGENTS:44-45/REPOSITORY:22 stale = DOC-P1-002); ND-P3-007 (REPOSITORY:58 only = DOC-P2-003).
- **still-open:** ND-P1-002 → DOC-P1-001; ND-P1-004 → DOC-P1-003; ND-P2-001 (worse: verify_pack 37/957) → HYGIENE-P2-002; ND-P2-002 → HYGIENE-P2-003; ND-P2-003 (exit 1, 22 findings) → HYGIENE-P2-002; ND-P2-007 → DOC-P2-001; ND-P2-011 (264/461) → DOC-P2-002; ND-P2-004/ND-P3-001/002/003 → DOC-P2-002; ND-P3-004 (digest:14 N/A omission; P8-G01 991/991) → HYGIENE-P2-002; ND-P3-005 (EX-01/14/19 duplicates) → HYGIENE-P3-002; ND-P3-008 (dead firstboot) → HYGIENE-P3-002; ND-P3-009 → DOC-P2-003; ND-P3-010 (0-byte `control.db`; tokens ACM-P2-001) → HYGIENE-P3-002; ND-P3-011 (16 contract paths vs live routes) → CI-P2-004; REV-P3-002 (progress ledger:17-18; R-29:38) → HYGIENE-P2-003.
- **not re-adjudicated:** REV-P3-001/003..012 — outside this prompt; see sibling reports.

## Appendix B — Literal walk log (read-only)

- `python3 ci/validate.py` (falcon): exit 1 — 2 `long_hex` in this run's `01:6`, `02:6`.
- `bash automation/validation/verify_publication_chain.sh`: 0 failures.
- `bash automation/evidence/manifest.sh check`: exit 1 — 1 mismatch (uncommitted REVIEW-FIX `.out`).
- `bash automation/validation/secret_scan_history.sh`: exit 1, 22 findings, `REVIEW_REQUIRED`.
- `bash ci/validate.sh` (edge): ALL PASS. `deploy edge --help`: 18 subcommands.
