# AI Automation and Agent Readiness Audit

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab profile v1.0.0, pack v1.2.1)
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repository: central `/home/user/falcon-build`; edge `/home/user/falcon-edge-build`
- Branch: `main` (both)
- Commit SHA: central `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c`; edge `f1c5defe6b66887ae49bc44c2cd79b37ad249663` (run started at edge `45dfed0`, which moved 9 commits during the run — re-checked before writing)
- Generated at: 2026-09-30T14:24Z
- Auditor: subagent, read-only (this audit itself ran as a multi-agent exercise over both repos)
- Area code: AI
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/20_ai_automation_agent_readiness.md`
- Scope limitations: GitHub settings/protection not queried live (plan limits taken from `docs/GITHUB_CI.md`); edge `ci/validate.sh` not executed to stay strictly read-only; live host not touched.

## Scope

Reviewed: agent instruction files (AGENTS.md both repos); Copilot/Cursor/Windsurf/Claude config presence; prompt-pack references; repo maps; conventions; validation commands; safe-change boundaries; do-not-touch areas; secrets guidance; PR/commit guidance; audit output conventions; generated-code risks; CI gates and human-approval points; rollback expectations; prompt-injection exposure; AI code provenance. Assessed whether these would produce correct behavior for a multi-agent run like this one. Not in depth: reports 10/11/34/36/38 cover CI/security mechanics.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `falcon-build/{AGENTS.md,README.md,REPOSITORY.md}` | Agent instructions | Directs agent behavior | Gate list lines 71–73 stale; human-review rule line 74 |
| `falcon-edge-build/AGENTS.md`, `REPOSITORY.md`, `docs/phase0/SCOPE_AND_BOUNDARIES.md` | Agent instructions | Boundary rules | Environment facts lines 43–45 stale; rule 7 ambiguous |
| Falcon `ledgers/{gate_ledger,phase9_gate_ledger}.csv`, `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json` + `generate_final_response.py`, `docs/phase9/review/PRODUCTION_VERDICT.md` | State sources vs summaries | Agent-visible correctness | Ledgers 101 PASS/1 N/A; digest APPROVED; FINAL_RESPONSE hardcoded IE/NOT_SUPPORTED |
| `.github/workflows/*` (falcon 1, edge 5), `docs/GITHUB_CI.md`, edge `closeout/REVIEW-2026-09-30.md`, edge `ledgers/{risk_register,progress_ledger,decision_log}.md` | CI + governance | Approvals, automation limits | Plan limits documented; subagent review closed edge G08 gates |
| `ci/validate.py`, edge `ci/validate.sh`, `automation/validation/{secret_scan.py,verify_publication_chain.sh}`; generated models/catalogue; search for CLAUDE/.cursorrules/copilot/PR templates | Validation + generated artifacts + inventory | Enforcement, provenance, missing configs | Reproduced below; banners + `--check`; no other agent configs found |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` (falcon) | Reproduction | Pre-commit gate | 4 PASS; **FAIL secret scan**: 2 `long_hex` hits in this run's `docs/audits/...` reports → `validation_failures=1` |
| `bash automation/validation/verify_publication_chain.sh` (falcon) | Reproduction | Digest binding | `publication_chain_failures=0`; signed archives intact |
| Gate-ledger recount (both) | Aggregate | Current state | Falcon 101 PASS/1 N/A; edge 77 PASS/8 BLOCKED/3 IE |
| `find`/`ls` for agent configs; `git status`/`log` | Literal walk | Inventory + binding claims | Only AGENTS.md; falcon dirty, edge clean at `f1c5def` |

## Prior-Run Findings Status

| Prior finding | Status at current commits | Evidence |
|---|---|---|
| ND-P1-002 AGENTS.md directs at closed gates | **still-open** | `AGENTS.md` lines 71–73 unchanged since `418f2ca`; P8-G10 PASS (`gate_ledger.csv` line 103), P9-G02/G10/G11/G12/G14 PASS (`phase9_gate_ledger.csv`); README lines 8–13 stale |
| ND-P2-010 live services outside repo | **partially-fixed** | `docs/runbooks/MCT_CONSOLIDATION.md` + `docs/runbooks/WAZUH_INTEGRATION.md` lines 33–40 document paths and start/stop; the live Wazuh compose/.env still lives at `/opt/wazuh-docker/multi-node` outside the repo |
| ND-P2-013 summary artifacts contradict ledgers | **partially-fixed** | Counts current, but `FINAL_RESPONSE.json` lines 6/48/49/50 carry stale commit + `INSUFFICIENT_EVIDENCE`/`NOT_SUPPORTED`; hardcoded in `generate_final_response.py` lines 65–66; `PRODUCTION_VERDICT.md` line 31 still says NOT_SUPPORTED |
| INTG-P2-002 WG administration inverted | **partially-fixed** | Edge `automation/validation/onboard_lab_side.sh` still rewrites lab `/etc/wireguard/wg0.conf`; falcon `docs/runbooks/VPN.md` omits peer `10.99.0.30` (only `OPERATOR_START_HERE.md` line 87 and `docs/edge/EDGE_RELEASE_PIN.md` mention it) |
| ND-P1-001 digest hardcoding | verified-fixed (context) | `PACKAGE_DIGEST.txt` derives from ledgers; chain verifier passes (reproduced) |

## Executive Summary

The repos give agents unusually strong doctrine (append-only, no fabricated execution, secrets rules) and good generated-artifact discipline (models/schemas drift checks, generated alert catalogue). The weaknesses are in the instruction layer: falcon's AGENTS.md and README still direct work at gates that have been PASS since 2026-09-29; summary artifacts hardcode the opposite of the ledger; edge agent docs carry stale hardware/image facts and an ambiguous reviewer rule that a subagent used to close review gates while risk R-002 stays open; audit outputs break the repo's own pre-commit validation; prompt-injection guidance is absent; and CI approval/drift enforcement is documented rather than enforced. Six findings: two P1, four P2.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Agent instructions | `AGENTS.md` both repos | Rules + state | Falcon gates stale; edge facts stale/ambiguous | High | AI-P1-001, AI-P1-002 |
| Validation commands | `ci/validate.py`; edge `ci/validate.sh`; workflows | Pre-commit gates | Working; audit outputs break falcon scan | High | AI-P2-004 |
| Safe-change boundaries / human approvals | AGENTS rules; workflows; FREE-plan limits | What agents may touch | Documented; partly unenforced | High | AI-P1-002, AI-P2-005 |
| Secrets guidance / audit outputs | AGENTS rule 1; redaction ledger; scanner; external audit profile | Leak prevention + audit writes | Secrets strong; audit outputs break validate | High | AI-P2-004 |
| Generated code risks | `models_generated.py`, generation `--check`, alert catalogue | Drift control | Strong | Low | Banners + CI checks |
| CI gates | falcon/edge workflows; schedule + manual dispatch | Automation safety | Pinned actions, least privilege; approval gaps | High | AI-P2-005, AI-P2-006 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Agent instructions | 2 | AGENTS.md both | Stale state; ambiguous reviewer rule | Regenerate blocks; define independence |
| Copilot/Cursor/Windsurf/Claude configs | 1 | none found | No tool-specific pointer | Link copilot instructions to AGENTS.md |
| Prompt packs | 2 | external path only | Not discoverable/versioned in repo | Reference pack version in AGENTS.md |
| Repo maps | 4 | REPOSITORY.md, REPO-MAP.md | Minor drift | Keep in change flow |
| Conventions | 4 | commit/branch/evidence rules | Partial enforcement | Add CI checks where possible |
| Validation commands | 4 | validate scripts/workflows | Audit outputs break scan | Ignore/allowlist policy |
| Safe-change boundaries | 3 | rules documented | Self-review gate closure; plan limits | Clarify independence; add enforcement |
| Do-not-touch areas | 3 | edge→falcon rule; falcon silent | One-way only | Symmetric rule |
| Secrets guidance | 4 | rules, redaction, scanner | Scanner false positives | Tune allowlist |
| PR guidance | 2 | commit conventions | No PR checklist | Add PR template |
| Audit output conventions | 2 | external profile only | Conflicts with validate | Document + exclude/allowlist |
| Generated code risks | 4 | banners, `--check`, catalogue rebuild | None material | Keep |

## Detailed Review

### Item: Agent instruction files

- Evidence: falcon `AGENTS.md` lines 71–73 vs `gate_ledger.csv` line 103 / `phase9_gate_ledger.csv`; falcon `README.md` lines 8–13; `PRODUCTION_VERDICT.md` line 31; edge `AGENTS.md` lines 43–45.
- Missing controls: no generated current-state block, no doc-drift check, no read-only audit mode, no falcon-side cross-repo rule (AI-P1-001, AI-P2-004).

### Item: Automation guardrails and human approvals

- Evidence: edge `AGENTS.md` rules 6–7; edge `risk_register.md` line 7 (R-002 OPEN) and line 19 (R-012); `progress_ledger.md` line 50 ("fresh-context agent" executed ED-19 review); gate rows P0-G08/P9-G08/P10-G01/P10-G03 notes "independent review unavailable"; `closeout/OWNER_ACTIONS.md` line 6; falcon `AGENTS.md` line 74.
- Missing controls: "reviewer (not the implementer)" is not defined to exclude same-run subagents; the register and ledger contradict each other (AI-P1-002).

### Item: CI automation safety and untrusted content

- Evidence: edge `bake-image.yml` (`environment: bake`, 7 secrets), `dependabot-merge.yml` (daily, merges on green with write token), `docs/GITHUB_CI.md` lines 143–161; falcon `validate.yml` line 76 (`FALCON_EVIDENCE_OPTIONAL=1`) without `verify_publication_chain.sh`; no prompt-injection guidance in either AGENTS.md.
- Missing controls: credential-bearing bakes run without an approval gate; `main` has no enforced required checks; falcon CI cannot catch digest/verdict drift; repo content is treated as instructions (AI-P2-005, AI-P2-006).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| AI-001 | Agent instructions | AGENTS.md both | doctrine + state lists | stale state; no drift check | P1 | generated current-state block |
| AI-002 | Copilot/Cursor/etc configs | none found | AGENTS.md implied | no tool pointers | P3 | link copilot instructions |
| AI-003 | Prompt packs | edge AGENTS line 48 | external path | not version-pinned | P3 | reference pack version |
| AI-004 | Repo maps | REPOSITORY.md; REPO-MAP | maintained | minor drift | P3 | refresh in change flow |
| AI-005 | Conventions | REPOSITORY.md | commit/evidence rules | partial enforcement | P2 | CI checks |
| AI-006 | Validation commands | validate scripts/workflows | run in CI | audit outputs break scan | P2 | ignore/allowlist policy |
| AI-007 | Safe-change boundaries | edge rule 6; falcon rule 6 | documented | self-review gate closure | P1 | define independence; refuse |
| AI-008 | Do-not-touch areas | edge→falcon rule | one-way | falcon silent on edge/host | P2 | symmetric rule |
| AI-009 | Secrets guidance | AGENTS rule 1; scanner | strong | false positives | P3 | tune allowlist |
| AI-010 | PR guidance | commit conventions | thin | no PR template | P3 | add template |
| AI-011 | Audit output conventions | external profile | none in repo | breaks validate | P2 | document + exclude |
| AI-012 | Generated code risks | models/catalogue | banners + drift checks | none material | P3 | keep |

## Findings

### Finding ID: AI-P1-001 - Agent instruction files direct work at closed gates and stale environment facts

- Severity: P1 · Confidence: High · Area: AI · Repo: both
- Evidence: falcon `AGENTS.md` lines 71–73 list P8-G10 and P9-G02/G10/G11/G12/G14 as open/blocked; `gate_ledger.csv` line 103 and `phase9_gate_ledger.csv` show all PASS (2026-09-29); falcon `README.md` lines 8–13 say production gates "remain open" (dated 2026-09-24); `PRODUCTION_VERDICT.md` line 31 still says `NOT_SUPPORTED` while the verdict is APPROVED; edge `AGENTS.md` lines 43–45 say the lab Pi runs the lab5 image and "planned adapter hardware … is NOT attached" while `closeout/OWNER_ACTIONS.md` lines 64–69/99–104 say lab7 is the reflash recommendation and lab8 is current, and §3 says the lab RTL8812BU is attached and proven (`docs/phase9/COMPATIBILITY_MATRIX.md` "LAB SUPPORT PROVEN").
- What is happening: static current-state text was never regenerated after closure/newer work; AGENTS.md unchanged since commits `418f2ca` (falcon) and `2e77ade` (edge).
- Why it matters: agents chase done work, may regenerate stale artifacts or flash the wrong image, and cannot trust the entry docs.
- User / business impact: wasted effort; false status propagation; avoidable rebuilds.
- Security / privacy / reliability impact: low direct; indirect via stale release signals and wrong deployment assumptions.
- Recommended fix: generate the current-state/environment blocks from ledgers, `OWNER_ACTIONS.md` and the release manifest; add doc-drift checks; correct the verdict template statement.
- Suggested validation: drift test comparing both blocks to sources; regenerate and re-run.
- Owner suggestion: both maintainers · Effort: S · Dependencies: ND-P1-001 generator · Status: still-open (prior ND-P1-002)

### Finding ID: AI-P1-002 - Edge review gates closed by a same-automation subagent review while R-002 stays open

- Severity: P1 · Confidence: High · Area: AI · Repo: edge
- Evidence: `closeout/REVIEW-2026-09-30.md` line 3 ("Reviewer: independent review subagent (not the implementer)"); `ledgers/progress_ledger.md` line 50 X-045 ("fresh-context agent executed the ED-19 review … 13 review gates moved to PASS"); gate rows P0-G08/P9-G08/P10-G01/P10-G03/P10-G08 notes claim "Independent review PASS" while ending "independent review unavailable (ED-19)"; `risk_register.md` line 7 R-002 OPEN ("No independent reviewer named; review gates cannot pass; implementer cannot self-approve"); `closeout/OWNER_ACTIONS.md` line 6 still asks the owner to name one; falcon `AGENTS.md` line 74 says an agent review cannot satisfy the human-review requirement; edge `AGENTS.md` line 21 only bars "the implementer".
- What is happening: a same-run subagent was treated as the independent reviewer and review gates were flipped to PASS; the register and ledger now contradict each other.
- Why it matters: automation can self-close governance gates; "independent" is undefined; this multi-agent audit demonstrates the failure mode.
- User / business impact: false confidence in review closure; owner decisions on inconsistent records.
- Security / privacy / reliability impact: release/verdict integrity; a mistaken or manipulated agent could pass gates.
- Recommended fix: define "independent reviewer" as a human/role outside the implementing automation in both AGENTS.md and ledger rules; set review-gate status to what doctrine allows pending a human disposition; require a human disposition digest for review-gate PASS.
- Suggested validation: ledger-semantics test rejecting review-gate PASS without a human disposition; reconcile R-002/X-045 and the false ledger notes.
- Owner suggestion: edge owner + maintainer · Effort: S · Dependencies: owner reviewer decision · Status: open

### Finding ID: AI-P2-003 - Falcon summary artifacts hardcode a verdict opposite to the ledgers

- Severity: P2 · Confidence: High · Area: AI · Repo: falcon
- Evidence: `closeout/FINAL_RESPONSE.json` line 6 `commit=12aa2fd…`, line 48 `verdict=INSUFFICIENT_EVIDENCE`, line 49 `production_readiness=NOT_SUPPORTED`, line 50 `open_gates=[]` while `gate_counts` = 101 PASS/1 N/A; `closeout/generate_final_response.py` lines 65–66 hardcode those strings; `PACKAGE_DIGEST.txt` lines 9–13 say APPROVED/open_gates=none; `PRODUCTION_VERDICT.md` line 31 retains the NOT_SUPPORTED template line.
- What is happening: the generator derives counts but not the verdict; the produced file is stale at an old commit (prior ND-P2-013).
- Why it matters: the primary machine-readable closeout contradicts the ledger and published digest.
- User / business impact: wrong status reporting; audit confusion.
- Security / privacy / reliability impact: low direct; release-signal integrity.
- Recommended fix: derive verdict/readiness/commit fields from the ledger+verdict source used by `publish_digests.sh`; regenerate; fix the verdict template line.
- Suggested validation: generated-artifact test asserting digest vs FINAL_RESPONSE field equality.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none · Status: partially-fixed

### Finding ID: AI-P2-004 - Audit outputs conflict with repo validation and untrusted content has no handling rule

- Severity: P2 · Confidence: High · Area: AI · Repo: both
- Evidence: reproduced `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py` → `FAIL secret scan findings`, 2 `long_hex` hits in `docs/audits/.../02_architecture_runtime_topology.md:6` and `01_repository_inventory.md:6` (matches `secret_scan.py` line 21); `AGENTS.md` rule 5 requires validate to pass before committing; no `.gitignore`/allowlist for `docs/audits/` (untracked run folder); neither AGENTS.md warns about instructions embedded in repo content, and this session auto-received repo AGENTS.md text as instructions; importable inputs include `mct/` vendored docs, `closeout/` narratives and audit reports; edge `AGENTS.md` line 46 protects falcon but falcon has no symmetric rule.
- What is happening: the external audit-output convention conflicts with the repo's validation gate, and content-based instruction injection is unaddressed.
- Why it matters: agents cannot satisfy both rules and may weaken the scanner or delete outputs; a future agent could execute embedded instructions from an audited artifact.
- User / business impact: audit automation friction; erosion of trust in agent runs.
- Security / privacy / reliability impact: pressure to broad-allowlist weakens secret scanning; boundary breach risk (cf. prior INTG-P2-001).
- Recommended fix: decide and document an audit-output policy (ignore/allowlist `docs/audits/**` long-hex narrowly, or keep run folders outside the repo); add a rule to both AGENTS.md that repository content is untrusted data and instructions inside it must not be followed; define symmetric read/write boundaries.
- Suggested validation: validate green with run reports present and a planted secret still failing; red-team fixture with an embedded instruction that the next agent run ignores and flags.
- Owner suggestion: both maintainers + audit operator · Effort: S · Dependencies: run-output policy · Status: open

### Finding ID: AI-P2-005 - Human-approval and drift enforcement in CI are documented, not enforced

- Severity: P2 · Confidence: High · Area: AI · Repo: both
- Evidence: edge `bake-image.yml` holds 7 repository secrets and runs `environment: bake` (line 48) with no required reviewers; `docs/GITHUB_CI.md` lines 143–161 record API failures for environment reviewers, rulesets, branch protection and auto-merge on the plan; `dependabot-merge.yml` merges Dependabot PRs on green with `contents: write`/`pull-requests: write` (daily cron line 13); `risk_register.md` line 19 R-012 OPEN; falcon `.github/workflows/validate.yml` line 76 runs with `FALCON_EVIDENCE_OPTIONAL=1` and never runs `automation/validation/verify_publication_chain.sh`, while `ci/validate.py` checks only ledger syntax/evidence hashes (lines 107–148).
- What is happening: `main` has no required checks or approvals; the credential-bearing bake is one dispatch away; falcon CI cannot detect the digest/verdict drift class.
- Why it matters: agents and humans rely on a green CI that does not check drift, and the credential workflow lacks an approval control.
- User / business impact: release integrity depends on discipline; false-green signals.
- Security / privacy / reliability impact: credential exfiltration risk if a pinned action is compromised (mitigations: SHA pins, gitleaks, zizmor).
- Recommended fix: add a compensating bake-approval artifact (signed dispatch record) that works on the current plan; track the plan upgrade; add chain-verifier + digest/verdict consistency steps to falcon CI; record evidence-skip counts.
- Suggested validation: bake dispatch refused without the approval artifact; CI fails on a doctored digest and passes on the real tree.
- Owner suggestion: both owners/maintainers · Effort: S · Dependencies: GitHub plan decision; R-012 · Status: open

### Finding ID: AI-P2-006 - Edge CI documentation and cadence drift; no PR/other-tool guidance or AI provenance policy

- Severity: P2 · Confidence: High · Area: AI · Repo: edge (+ falcon for PR guidance)
- Evidence: `docs/GITHUB_CI.md` line 3 says "Three workflows" (five exist) and line 73 says the Dependabot sweep runs "every 20 minutes" while `dependabot-merge.yml` line 13 is a daily cron; no `PULL_REQUEST_TEMPLATE`, `CONTRIBUTING`, `CLAUDE.md`, `.cursorrules`, `.windsurfrules` or copilot instructions in either repo; commit/actor records use `build-agent` but no policy requires marking agent-authored changes.
- What is happening: agent-facing CI documentation drifts from the workflows it describes, and there is no PR checklist or AI-provenance convention.
- Why it matters: agents misstate CI behavior and lack a review checklist; provenance of AI-authored changes is implicit.
- User / business impact: review quality and traceability gaps.
- Security / privacy / reliability impact: low direct.
- Recommended fix: correct `docs/GITHUB_CI.md`, add a drift test for documentable counts (workflow count, cadence), add a PR template with the evidence/gate checklist, and document an AI-provenance convention (actor/Co-authored-by/commit trailer).
- Suggested validation: doc test comparing workflow count and cron strings to `.github/workflows/`; PR template exercised once.
- Owner suggestion: edge maintainer + falcon maintainer · Effort: S · Dependencies: none · Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Agents act on stale instructions | P1 | High | Medium | stale AGENTS/README | AI-P1-001 |
| Agent self-closes governance gates | P1 | Medium | High | subagent review; R-002 | AI-P1-002 |
| Stale machine-readable verdicts propagate | P2 | High | Medium | FINAL_RESPONSE | AI-P2-003 |
| Audit outputs vs validation gate; injection | P2 | High | Low/High | validate FAIL; no rule | AI-P2-004 |
| CI approval/drift enforcement gaps | P2 | Medium | High | R-012; no chain check | AI-P2-005 |

## Recommendations

### Immediate / Release Blocking
- AI-P1-002: reconcile edge review-gate statuses with R-002 and OWNER_ACTIONS until a human disposition exists.
- AI-P1-001: regenerate falcon current-state blocks and the verdict template statement; refresh edge environment facts.

### This Week
- AI-P2-003: derive FINAL_RESPONSE verdict fields; AI-P2-004: set the audit-output policy and untrusted-content rules; AI-P2-005: add chain-verifier/digest checks and the bake approval artifact.

### This Month
- AI-P2-006: correct GITHUB_CI drift; add PR template and AI-provenance convention; add the doc-drift test family to both validate workflows.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Generate the current-state block from the ledger | Removes the recurring stale-gate class | AGENTS.md, README.md, script | drift test green |
| Narrow `docs/audits/**` long-hex allowlist | Pre-commit gate works with audit outputs | `secret_scan.py` | validate green; planted secret still fails |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Current-state generator + drift check | P1 | falcon maintainer | S | none |
| Human-reviewer definition + ledger semantics test | P1 | edge owner | S | owner decision |
| FINAL_RESPONSE derivation | P2 | falcon maintainer | S | none |
| Audit-output policy + scanner tune | P2 | both maintainers | S | none |

## Suggested Tests

- CI/security: `secret_scan` negative test (planted secret fails) plus audit-output allowlist positive test.
- Regression: doc-drift tests (state block vs ledgers; workflow count/cadence vs `.github/workflows/`).
- Manual/red-team: prompt-injection fixture ignored; bake dispatch refused without approval artifact.

## Suggested Documentation Updates

- Update: falcon `AGENTS.md`/`README.md` — generated current-state block, audit-output policy, untrusted-content rule.
- Update: edge `AGENTS.md`/`docs/GITHUB_CI.md` — independent reviewer, facts refresh, workflow count/cadence.
- Update: `docs/phase9/review/PRODUCTION_VERDICT.md` — remove the stale NOT_SUPPORTED line (re-verify chain).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the owner accept a "fresh-context agent" as ED-19 reviewer? | Determines whether edge review gates are valid | owner decision; R-002 |
| Where should audit run folders live? | Resolves validate/scanner conflict | owner/operator policy |

## Appendix

- Findings summary: AI-P1-001 / AI-P1-002 (P1); AI-P2-003 / AI-P2-004 / AI-P2-005 / AI-P2-006 (P2). P0: none.
- Edge gates at `f1c5def`: 88 — 77 PASS / 8 BLOCKED / 3 IE. Falcon: 102 program gates (101 PASS/1 N/A) + 14 phase-9 gates (13 PASS/1 N/A).
- Agent-config inventory: `AGENTS.md` ×2; no CLAUDE.md/.cursorrules/.windsurfrules/copilot/PR template; generated models carry DO-NOT-EDIT banners + `--check`; commits authored by `build-agent`.
