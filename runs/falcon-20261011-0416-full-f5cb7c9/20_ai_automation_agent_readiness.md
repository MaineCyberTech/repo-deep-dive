# 20_ai_automation_agent_readiness — Prompt 20 - AI Automation and Agent Readiness Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `20_ai_automation_agent_readiness.md` (area AI, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (branch `main`), read-only worktree `/tmp/opencode/falcon-audit-f5cb7c9`; live host inspected read-only
- Generated at: 2026-10-11 (UTC) · Auditor: subagent (read-only; no CI dispatched, no secret values printed)
- Area code: AI
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/20_ai_automation_agent_readiness.md`
- Scope limitations: static repository review plus read-only host checks; GitHub plan settings taken from the repository's own evidence; the paired `falcon-edge` repository is out of scope.

## Scope

Reviewed: agent instructions (`AGENTS.md`), tool-specific configs (CLAUDE/cursor/copilot/Windsurf), prompt packs, repo maps (`REPOSITORY.md`, `mct/REPO-MAP.md`), conventions, validation commands (`ci/validate.py`, `ci/validate.sh`), CI gates (`.github/workflows/`), safe-change boundaries, do-not-touch areas (`CODEOWNERS`, `.gitignore`), secrets guidance and the secret scanner, PR guidance (`pull_request_template.md`), audit output conventions (`AUDIT_RUN_LIFECYCLE.md`), generated-code risks, human approvals (`BRANCH_PROTECTION.md`), rollback expectations, prompt-injection handling (rule 7), and AI code provenance. Not reviewed: agent runtime behavior, GitHub plan settings beyond documented evidence, edge-repo agent files.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `AGENTS.md` (89 lines) | Agent instructions | Hard rules, standard flow, pitfalls, gates | Rule 7 = untrusted repository content; run pointer stale (AI-P3-001) |
| `REPOSITORY.md` | Conventions | Layout, change classes, source-vs-generated table | review-package "not committed" wording vs tracked manifest (HYGIENE-P2-003) |
| `.github/pull_request_template.md`, `.github/CODEOWNERS` | PR guidance / ownership | Human review expectation | No provenance field; `* @MaineCyberTech` (BP-P2-001 open) |
| `ci/validate.py` (fast subset) | Validation command | Pre-commit gate | `validation_failures=0` at f5cb7c9 (322 shell scripts, 102-gate ledger) |
| `.github/workflows/validate.yml` | CI gate | Static gate, pinned actions, publication-chain + equality gate | Wired; `contents: read`; fork PRs to hosted |
| `.github/workflows/external-smoke.yml` | CI gate | Access-posture check | Weakened (accepts any 302 on the lab runner) - cross-ref CHAIN-P2-001 |
| `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` | Audit output conventions | Run-folder lifecycle | Rule 6 stale: calls the closed 2026-09-30 run "the current run" (lines 39-42) |
| `docs/security/BRANCH_PROTECTION.md` | Human approvals | Plan-gated protection + compensating controls | Not server-enforced; owner-accepted (BP-P1-001 / CI-P1-001) |
| `ledgers/decision_log.md`, `git log` | Provenance | Authorship evidence | 749 commits authored by `build-agent <build-agent@localhost>`; PRs #51-#54 co-authored ad hoc; no policy |
| `docs/audits/repo-deep-dive/` listing | Prior runs | Newest published full run | Newest in-repo: `20261005-0354-full-main-e267ce1`; the 20261009/20261011 runs are not published in-repo |
| `docs/CURRENT_STATE.md` | State page | Authoritative current state | Carries the 2026-10-09/10 section (DOC-P2-002 verified-fixed) but its records table still points at the 2026-09-30 run |

## Verification Performed

| Check | Command / read | Result |
|---|---|---|
| Tool-config inventory | `find` for AGENTS/CLAUDE/cursor/copilot/windsurf/*.mdc | only `AGENTS.md` (AI-P3-002) |
| Standard-flow commands | existence check of the 10 commands in `AGENTS.md` section Standard change flow | 10/10 present |
| Fast gate | `python3 ci/validate.py --fast` | `validation_failures=0` |
| Publication chain | `bash automation/validation/verify_publication_chain.sh` | `publication_chain_failures=0` |
| Publication equality | `python3 automation/validation/check_publication_equality.py` | PASS (but note the tracked-manifest fail-open skip when the manifest is absent; HYGIENE-P2-003) |
| Run pointers | `AGENTS.md:82-86`, `AUDIT_RUN_LIFECYCLE.md:39-42`, `README.md:8-11` vs `docs/audits/` listing | stale: 2026-09-30 run presented as current/live; newest full run 20261005 unreferenced |
| Untrusted-content rule | `AGENTS.md:22-29` (rule 7) | present and explicit |
| Provenance field | `pull_request_template.md` read | absent |
| Human-approval enforcement | `BRANCH_PROTECTION.md` | plan-blocked, compensating controls documented, owner-accepted |

## Executive Summary

Agent doctrine remains strong: the evidence-first rules, the untrusted-content boundary (rule 7), the append-only discipline, the pre-commit gate and the standard change flow are all present and executable at f5cb7c9 (all ten flow commands exist; `ci/validate.py --fast` and the publication chain pass). The two P3 gaps from the prior full run persist unchanged: (1) the agent/audit-run pointers are stale - `AGENTS.md`, `README.md` and `AUDIT_RUN_LIFECYCLE.md` still present the closed 2026-09-30 run as "current", while the newest published full run is `20261005-0354-full-main-e267ce1` (GO WITH CONDITIONS, P0 x1) and the 2026-10-09/11 remediation runs are not published in-repo; (2) there is still no AI-provenance policy and no per-tool instruction coverage (only `AGENTS.md` exists; the PR template has no provenance field, even though `build-agent` authors 749 commits and PRs #51-#54 carry an ad-hoc co-author trailer). One cross-domain caution for agents: `AGENTS.md:44` instructs agents that the review package is gitignored and "do NOT commit", while the publication flow now depends on the tracked `review-package/MANIFEST.sha256` declared-manifest commit (HYGIENE-P2-003) - an agent following the instructions literally can break the publication equality gate (as already happened once, CI-P2-004).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Agent instructions | `AGENTS.md` | Rules + flow + pitfalls | Comprehensive; run pointer stale | Low | AI-P3-001 |
| Tool-specific configs | - | Cursor/Copilot/Claude/Windsurf | Absent | Low | AI-P3-002 |
| Prompt packs | `REPOSITORY.md:5`, `README.md:3-5` | Doctrine naming | Named, no pack version recorded | Low | unchanged |
| Repo maps | `REPOSITORY.md`, `mct/REPO-MAP.md` | Layout | Maintained | Low | - |
| Validation commands | `ci/validate.py`, `ci/validate.sh` | 19 read-only checks | Passing (`--fast`) | Low | full run needs lab context |
| Safe-change boundaries | `AGENTS.md` rule 6; PR template | Rollback + evidence for runtime changes | Documented; review not server-enforced | Medium | owner-accepted residual |
| Do-not-touch areas | `CODEOWNERS`, `.gitignore` | Sensitive/generated trees | Present; CODEOWNERS handle unresolvable (BP-P2-001) | Low | cross-ref BP-P2-001 |
| Secrets guidance | Rule 1; `.gitleaks.toml`; `secret_scan.py` | Leak prevention | Strong | Low | - |
| PR guidance | `.github/pull_request_template.md` | Evidence/rollback/security checklist | Current; no provenance field | Low | AI-P3-002 |
| Audit output conventions | `AUDIT_RUN_LIFECYCLE.md` | Run-folder lifecycle | Rule 6 stale | Low | AI-P3-001 |
| Generated code risks | `REPOSITORY.md` table; drift checks | Source-vs-generated | review-package contradiction | Medium | HYGIENE-P2-003 cross-ref |
| CI gates | `validate.yml`, `dependabot-merge.yml`, `external-smoke.yml` | Static gate, label merge, smoke | Working; smoke weakened | Medium | CHAIN-P2-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Agent instructions | 4 | `AGENTS.md` rules/flow/pitfalls; rule 7 | Run pointer stale; review-package instruction contradicts enforced flow | Refresh pointers (AI-P3-001); fix the commit instruction (HYGIENE-P2-003) |
| Copilot/Cursor/Windsurf/Claude configs | 1 | none found | No tool coverage | Add pointer files (AI-P3-002) |
| Prompt packs | 2 | Doctrine named; no pack version in repo | Pack version not recorded | Record pack/profile version |
| Repo maps | 4 | `REPOSITORY.md`, `mct/REPO-MAP.md` | Minor drift | Keep in change flow |
| Conventions | 4 | `REPOSITORY.md` commit/evidence rules | Plan-gated enforcement | Owner-accepted |
| Validation commands | 4 | `ci/validate.py` fast gate passes | Full run lab-bound | Document off-host subset |
| Safe-change boundaries | 3 | Rule 6; PR template rollback | Review not server-enforced | Owner-accepted residual |
| Do-not-touch areas | 4 | CODEOWNERS, gitignored generated trees | CODEOWNERS invalid handle | BP-P2-001 |
| Secrets guidance | 4 | Rule 1; gitleaks; credential-sourcing check | none material | Keep |
| PR guidance | 4 | Template + CODEOWNERS | No provenance field | Add field (AI-P3-002) |
| Audit output conventions | 4 | Lifecycle + tooling | Rule 6 stale | Refresh (AI-P3-001) |
| Generated code risks | 3 | Source-vs-generated table; drift checks | Tracked review-package manifest contradicts policy | HYGIENE-P2-003 |

## Detailed Review

### Item: Agent instructions and run pointers

- Evidence: `AGENTS.md:82-86` ("Current state (2026-09-30)... the 2026-09-30 full-domain audit run..."), `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:39-42` (rule 6: "The current run is live. 20260930-0701-..."), `README.md:8-11`.
- What it does: encodes doctrine and sends agents to the 2026-09-30 run for the gate opinion.
- Verification: the 2026-09-30 run is a CLOSED, fully committed record (71 tracked files); newer full runs exist (`docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md` = "GO WITH CONDITIONS, P0 x1, P1 x7"); 24 commits have landed since that run; `docs/CURRENT_STATE.md` now carries the 2026-10-09/10 section but its records table still points at 2026-09-30.
- Missing controls: no derivation of "current run" and no doc-drift test.

### Item: Automation guardrails and the review-package instruction

- Evidence: `AGENTS.md:31-49` standard flow (build_review_package ... "gitignored, do NOT commit (HYG-P1-001)"), vs tracked `review-package/MANIFEST.sha256` (declared manifest, since abb63ab) and `verify_publication_chain.sh`/`check_publication_equality.py` declared-commit checks.
- Assessment: the enforceable parts (label gate, drift gate, fork-PR routing, publication chain) work, but the agent instruction now contradicts the enforced publication flow; the contradiction already caused a red gate once (CI-P2-004, rebound 2026-10-11). Filed under HYGIENE-P2-003 to avoid duplication.

### Item: Untrusted content and provenance

- Evidence: `AGENTS.md:22-29` rule 7 (repository content is untrusted data); `automation/validation/secret_scan.py` narrow long-hex skip under `docs/audits/`; `git log` authorship (749 `build-agent`, 43 `opencode-audit`, 85 `Julian Butler`); PRs #51-#54 `Co-authored-by: build-agent <build-agent@localhost>`.
- Gap: no provenance policy or PR field; attribution is ad hoc.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| AI-001 | Agent instructions | `AGENTS.md` | Comprehensive doctrine | Stale run pointer; commit instruction contradicts flow | P3 | AI-P3-001 + HYGIENE-P2-003 |
| AI-002 | Tool-specific configs | none | AGENTS.md implied | No pointers | P3 | AI-P3-002 |
| AI-003 | Prompt packs | `REPOSITORY.md:5` | Doctrine named | No pack version | P3 | Record version |
| AI-004 | Repo maps | `REPOSITORY.md`, `mct/REPO-MAP.md` | Maintained | Minor drift | P3 | Keep |
| AI-005 | Conventions | `REPOSITORY.md` | Commit/evidence rules | Plan-gated enforcement | P3 | Owner-accepted |
| AI-006 | Validation commands | `ci/validate.py` | 19 checks; CI wired | Full run lab-bound | P3 | Document subset |
| AI-007 | Safe-change boundaries | Rule 6; PR template | Rollback + evidence required | Review not server-enforced | P3 | Owner-accepted |
| AI-008 | Do-not-touch areas | CODEOWNERS; `.gitignore` | Sensitive trees | Invalid CODEOWNERS handle | P3 | BP-P2-001 |
| AI-009 | Secrets guidance | Rule 1; gitleaks; scanner | Strong | - | - | Keep |
| AI-010 | PR guidance | Template; CODEOWNERS | Checklist present | No provenance | P3 | Add field |
| AI-011 | Audit output conventions | `AUDIT_RUN_LIFECYCLE.md` | Lifecycle + tooling | Rule 6 stale | P3 | AI-P3-001 |
| AI-012 | Generated code risks | `REPOSITORY.md` table; drift checks | Drift checks wired | review-package contradiction | P2 | HYGIENE-P2-003 |

## Findings

### AI-P3-001 - Agent/audit-run pointers are stale: the lifecycle runbook still calls the closed 2026-09-30 run "the current run" and AGENTS.md/README point at it as the full-domain reference

- Severity: P3
- Confidence: High
- Area: AI
- Evidence:
  - `AGENTS.md:82-86`
  - `docs/runbooks/AUDIT_RUN_LIFECYCLE.md:39-42`
  - `README.md:8-11`
  - `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/RELEASE_GATE.md` (GO WITH CONDITIONS; P0 x1, P1 x7)
  - `git log --oneline e267ce1..HEAD | wc -l` = 24 commits since the newest published full run
- What is happening: the pointers were not refreshed after the 2026-10-02/10-05/10-09/10-11 runs. The 2026-09-30 run is a closed, fully committed record; the newest in-repo full run is 20261005-0354, and the 20261009-2117 / current 20261011-0416 runs are not published in-repo. `docs/CURRENT_STATE.md` partially compensates (2026-10-09/10 section) but its records table still names the 2026-09-30 run.
- Why it matters: an agent or operator following AGENTS.md/README/lifecycle reads a closed run as live and misses the newer P0/conditions and the remediation record.
- User / business impact: wrong gate opinion referenced in change decisions.
- Security / privacy / reliability impact: low direct; indirect via stale gate awareness.
- Recommended fix: derive or state the current run (newest published full run, or date), update rule 6 + AGENTS.md + README + CURRENT_STATE records table, and add a doc-drift check that referenced run ids resolve and the newest run is referenced.
- Suggested validation: CI test that parses run ids referenced from AGENTS.md/README/lifecycle and fails when the newest `docs/audits/repo-deep-dive/*` run is newer.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### AI-P3-002 - No AI-provenance policy and no per-tool agent instruction coverage

- Severity: P3
- Confidence: High
- Area: AI
- Evidence:
  - `find . -name AGENTS.md -o -name CLAUDE.md -o -name '.cursor*' -o -name 'copilot*' -o -name '*.mdc'` -> only `./AGENTS.md`
  - `.github/pull_request_template.md` (no provenance/authorship field)
  - `git log --format=%an | sort | uniq -c` -> 749 `build-agent <build-agent@localhost>`, 43 `opencode-audit`, 85 `Julian Butler`
  - PRs #51-#54 carry `Co-authored-by: build-agent <build-agent@localhost>` (ad hoc, no policy)
- What is happening: tools that do not read AGENTS.md (Claude Code without a pointer, Copilot, Cursor, Windsurf) get no doctrine; agent-authored changes are not disclosed under a policy, though the co-author trailer appears ad hoc in recent PRs.
- Why it matters: silent divergence from doctrine and no attributable provenance for agent changes.
- User / business impact: review quality risk for AI-assisted changes.
- Security / privacy / reliability impact: low; attribution and doctrine coverage gap.
- Recommended fix: add pointer files (CLAUDE.md/copilot-instructions.md/.cursor rules) referencing AGENTS.md; add a one-line provenance rule (commit trailer or PR field "Provenance (human/agent, tool)"); keep the independent-human-review requirement (AGENTS.md:87-88).
- Suggested validation: lint that the PR template contains the provenance field; presence check for pointer files.
- Owner suggestion: maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Agent treats a closed run as live / misses newer P0 | P3 | Medium | Low | `AUDIT_RUN_LIFECYCLE.md:39`, `AGENTS.md:82-86` | AI-P3-001 |
| Tool that does not read AGENTS.md acts without doctrine | P3 | Medium | Medium | no tool configs | AI-P3-002 |
| Agent follows "do NOT commit review-package" and breaks the publication gate | P2 | Medium | Medium | `AGENTS.md:44` vs tracked manifest | HYGIENE-P2-003 |

## Recommendations

### Immediate / Release Blocking
- None (no P0/P1/P2 findings in this domain).

### This Week
- Refresh the run pointers (AI-P3-001).
- Fix the review-package commit instruction and align it with the enforced flow (HYGIENE-P2-003).
- Add pointer files + a provenance field (AI-P3-002).

### This Month
- Record the prompt-pack/profile version; add a doc-drift test for referenced runs.

### Later / Platform Evolution
- Revisit branch protection on plan upgrade; keep the owner-accepted compensating controls documented.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Refresh lifecycle rule 6 + AGENTS/README pointers | Removes live-vs-closed confusion | `docs/runbooks/AUDIT_RUN_LIFECYCLE.md`, `AGENTS.md`, `README.md` | newest run referenced |
| Add `CLAUDE.md` -> AGENTS.md pointer | Claude Code agents load doctrine | `CLAUDE.md` | file present |
| Provenance line in PR template | Attribution for agent changes | `.github/pull_request_template.md` | template shows field |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Doc-drift check for referenced run folders | P3 | maintainer | S | none |
| Provenance rule + pointer files | P3 | maintainer | S | none |

## Suggested Tests

- CI: every `docs/audits/**` run id referenced from `AGENTS.md`/`README.md`/runbooks resolves, and the newest full run is referenced.
- Negative test: a synthetic planted secret under `docs/audits/` still fails the secret scan (existing `audit_run_scanner_test.sh`; keep).
- Lint: PR template contains a provenance field.

## Suggested Documentation Updates

- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` rule 6 - derive/state the current run.
- `AGENTS.md` and `README.md` - point at the newest published run and `docs/CURRENT_STATE.md`.
- `.github/pull_request_template.md` - add "Provenance (human/agent, tool)".
- `REPOSITORY.md` - record the prompt-pack/profile version.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which pack/profile version governs the current work? | Reproducibility | Owner answer; pack metadata |
| Is a plan upgrade planned? | Whether approval enforcement can become server-side | Owner answer |

## Prior-Run Comparison

- `AI-P3-001` (stale run pointers): prior open -> **still open** at f5cb7c9; the pointer set is unchanged and the newest in-repo run is still 20261005. `docs/CURRENT_STATE.md` now carries a 2026-10-09/10 section (partial improvement).
- `AI-P3-002` (no provenance/tool coverage): prior open -> **still open**; only `AGENTS.md` exists, PR template unchanged. Recent PRs add an ad-hoc `Co-authored-by: build-agent` trailer but no policy.
- No AI P0/P1/P2 existed in the prior full run; none found now.

## Limitations

- No CI runs were dispatched; GitHub settings were not queried live (plan-gated per the repository's evidence).
- Live host checks were read-only and used only to confirm the tree/binding state referenced here.

## Appendix - agent inventory

| Item | Path | State |
|---|---|---|
| Instructions | `AGENTS.md` | present, 89 lines |
| Conventions | `REPOSITORY.md` | present |
| PR template | `.github/pull_request_template.md` | present, no provenance field |
| CODEOWNERS | `.github/CODEOWNERS` | present, `@MaineCyberTech` unresolvable (BP-P2-001) |
| Tool configs | `CLAUDE.md`, `.cursor*`, `copilot-instructions.md`, Windsurf | absent |
| Validation | `ci/validate.sh`, `ci/validate.py` | present; `--fast` passes at f5cb7c9 |

## Findings

| ID | Severity | Title |
|---|---|---|
| AI-P3-001 | P3 | Agent/audit-run pointers are stale: the lifecycle runbook still calls the closed 2026-09-30 run 'the current run' and AGENTS.md/README point at it as the full-domain reference |
| AI-P3-002 | P3 | No AI-provenance policy and no per-tool agent instruction coverage |
