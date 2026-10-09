# 20_ai_automation_agent_readiness — Prompt 20 - AI Automation and Agent Readiness Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `20_ai_automation_agent_readiness.md` (area AI, prompt)

## Verification Performed

# AI Automation and Agent Readiness Audit — falcon @ 08e20d1

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` (read-only worktree `/tmp/opencode/falcon-audit-08e20d1`; live host inspected read-only)
- Branch: `main`
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09
- Auditor: subagent (read-only; no CI dispatched, no secret values printed)
- Area code: AI
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/20_ai_automation_agent_readiness.md`
- Scope limitations: static repository review plus read-only host checks; GitHub settings/branch protection not queried live (plan-gated per `docs/security/BRANCH_PROTECTION.md`); the paired `falcon-edge` repository is out of scope.

## Scope

Reviewed: agent instructions (`AGENTS.md`), conventions (`REPOSITORY.md`), PR guidance (`pull_request_template.md`, `CODEOWNERS`), validation commands (`ci/validate.sh`, `ci/validate.py`), CI workflows (`validate.yml`, `external-smoke.yml`, `dependabot-merge.yml`), safe-change boundaries and do-not-touch areas, secrets guidance and the secret scanner, audit output conventions (`AUDIT_RUN_LIFECYCLE.md`), generated-artifact rules, prompt-injection handling, human approvals, rollback expectations, and AI code provenance. Not reviewed: runtime behavior of the agents themselves, the edge repo's agent files, and GitHub plan settings beyond what the repo documents.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `AGENTS.md` (89 lines) | Agent instructions | Rules, standard flow, pitfalls, gates | Hard rules 1-7; rule 7 = untrusted repository content |
| `REPOSITORY.md` | Conventions | Layout, change classes, evidence rules | Source-vs-generated table |
| `.github/pull_request_template.md`, `.github/CODEOWNERS` | PR guidance / ownership | Human review expectation | Rollback + security + gate sections; `* @MaineCyberTech` |
| `ci/validate.sh`, `ci/validate.py` (646 lines) | Validation commands | Pre-commit gate (19 checks) | Runs in CI; `--fast` subset documented |
| `.github/workflows/{validate,external-smoke,dependabot-merge}.yml` | CI gates | Automation guardrails | Pinned actions, least privilege; smoke posture issue (see CHAIN) |
| `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` | Audit output conventions | Run-folder states + tooling | Rule 6 stale (finding AI) |
| `docs/security/BRANCH_PROTECTION.md` | Human approvals | Plan-gated protection + compensating controls | Not server-enforced; owner-accepted (BP-P1-001/CI-P1-001) |
| `ledgers/decision_log.md` | Provenance / decisions | Ad-hoc AI provenance record | 250 lines, append-only |
| `docs/audits/repo-deep-dive/20261005-0354-full-main-e267ce1/` | Prior full run | Latest published full run | GO WITH CONDITIONS, P0 x1 |

## Verification Performed

| Check | Command / read | Result |
|---|---|---|
| Pre-commit fast gate | `python3 ci/validate.py --fast` | `validation_failures=0` — parse, compose pinning, 321 shell scripts, credential sourcing, 102-gate ledger |
| Publication chain | `bash automation/validation/verify_publication_chain.sh` | `publication_chain_failures=0`; signed archives intact |
| Standard-flow commands | existence check of the 10 commands in `AGENTS.md` §Standard change flow | 10/10 present |
| Agent-config inventory | `find` for AGENTS/CLAUDE/cursor/copilot/windsurf configs | only `AGENTS.md` (finding AI-2) |
| Untrusted-content rule | `AGENTS.md:22-29` | present and explicit (rule 7) |
| Drift/verdict enforcement | `.github/workflows/validate.yml:108-113` | publication-chain + digest/verdict consistency gate wired (AI-P2-005 residual closed for drift) |
| Human-approval enforcement | `docs/security/BRANCH_PROTECTION.md:1-20` | not enforceable on the GitHub Free private plan; compensating controls documented; owner-accepted |
| Agent-run pointers | `AUDIT_RUN_LIFECYCLE.md:39-42`, `AGENTS.md:82-86` vs `docs/audits/` listing | stale (finding AI-1) |

## Executive Summary

The repository gives agents unusually strong doctrine: no secrets, no fabricated execution, append-only records, one logical change per commit, a mandatory pre-commit gate, and an explicit rule that repository content is untrusted data (rule 7, the prompt-injection boundary). The standard change flow in `AGENTS.md` is executable end-to-end — all ten referenced scripts exist, and the fast gate passes at this commit. Automation guardrails are a mixed picture: drift and verdict enforcement is now real CI (`validate.yml` runs `verify_publication_chain.sh` plus the digest/verdict consistency test), the Dependabot merge requires an owner-applied label, and fork PRs fall back to GitHub-hosted runners; but branch protection and Code-Owner review remain plan-blocked and unenforced server-side — a documented, owner-accepted residual (BP-P1-001/CI-P1-001), not refiled here. Two P3 gaps remain: stale agent/audit-run pointers, and the absence of any AI-provenance or per-tool instruction coverage. A CI security-posture change made on 2026-10-09 weakens the only automated Cloudflare-Access check; it is filed under CHAIN because it is a detection composition.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Agent instructions | `AGENTS.md` | Rules + flow + pitfalls | Comprehensive; run pointer stale | Low | Finding AI-1 |
| Tool-specific configs | — | Cursor/Copilot/Claude/Windsurf | Absent | Low | Finding AI-2 |
| Conventions | `REPOSITORY.md` | Layout, change classes | Current | Low | Source/generated table |
| PR guidance | `.github/pull_request_template.md` | Evidence/rollback/security checklist | Current | Low | No provenance field |
| Validation | `ci/validate.py`, `ci/validate.sh` | 19 read-only checks | Passing (`--fast`) | Low | Full run needs lab/offsite |
| CI gates | `validate.yml`, `dependabot-merge.yml`, `external-smoke.yml` | Static gate, label-gated merges, posture smoke | Working; smoke weakened | Medium | Cross-ref CHAIN P2 |
| Human approvals | `CODEOWNERS`, `BRANCH_PROTECTION.md` | Owner review | Not enforced (plan) | Medium | Owner-accepted |
| Audit output rules | `AUDIT_RUN_LIFECYCLE.md` | Run-folder lifecycle | Rule 6 stale | Low | Finding AI-1 |
| Secrets guidance | `AGENTS.md` rule 1, `.gitleaks.toml`, `secret_scan.py` | Leak prevention | Strong | Low | Scanner skip is narrow |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Agent instructions | 4 | `AGENTS.md` rules/flow/pitfalls; rule 7 | Run pointer stale | Refresh pointer (AI-1) |
| Copilot/Cursor/Windsurf/Claude configs | 1 | none found | No tool coverage | Add pointer files (AI-2) |
| Prompt packs | 2 | Doctrine referenced; pack version only in run metadata | Pack version not recorded in repo | Record pack/profile version |
| Repo maps | 4 | `REPOSITORY.md` layout, README map, `mct/REPO-MAP.md` | Minor drift | Keep in change flow |
| Conventions | 4 | `REPOSITORY.md` commit/evidence rules | Partial enforcement (plan) | Keep; revisit on plan upgrade |
| Validation commands | 4 | `ci/validate.py` 19 checks; CI wiring | Full run needs lab context | Document off-host subset |
| Safe-change boundaries | 3 | `AGENTS.md` rule 6; PR template rollback | Review not server-enforced | Owner-accepted residual |
| Do-not-touch areas | 4 | CODEOWNERS sensitive trees; gitignored generated trees; Suricata rules | — | Keep |
| Secrets guidance | 4 | Rule 1; gitleaks; credential-sourcing check | None material | Keep |
| PR guidance | 4 | PR template + CODEOWNERS | No provenance field | Add field (AI-2) |
| Audit output conventions | 4 | `AUDIT_RUN_LIFECYCLE.md`, scanner skip, tests | Rule 6 stale | Refresh (AI-1) |
| Generated code risks | 4 | Source-vs-generated table; review-package untracked; evidence drift check | No HEAD binding for all trees | Cross-ref INFRA-P2-001 |

## Detailed Review

### Item: Agent instructions

- Evidence: `AGENTS.md:6-29` (hard rules), `:31-49` (standard flow), `:51-77` (pitfalls), `:79-89` (gates/review).
- What it does: encodes the evidence-first doctrine, the pre-commit gate, runtime-change rollback expectations, the untrusted-content rule, and a list of environment-specific traps (Traefik basic-auth file caching, WireGuard persistence, PromQL `bool`, generated Suricata rules).
- Missing controls: the run reference and the gate pointer are hand-maintained and already stale; no generated current-state block.
- Risks: an agent trusts a closed run folder or misses the newest P0; low impact but recurring.

### Item: Validation commands and CI gates

- Evidence: `ci/validate.py` (19 checks incl. publication equality, generated drift, restore assertion); `validate.yml` pinned actions and hash-pinned tool downloads; `dependabot-merge.yml` label gate; `external-smoke.yml` posture check.
- Verification: `--fast` passes; `verify_publication_chain.sh` returns 0; the digest/verdict consistency test is wired at `validate.yml:113`.
- Gap: the external smoke no longer asserts the Access posture from an external vantage (filed as a CHAIN composition); `AGENTS.md` rule 5's full `ci/validate.py` requires lab/offsite context that a clean clone lacks (CI uses `FALCON_EVIDENCE_OPTIONAL=1`).

### Item: Automation guardrails and human approvals

- Evidence: `AGENTS.md` rule 6 (runtime-mutating changes require rollback note + evidence; production gates owner-owned); `CODEOWNERS`; `BRANCH_PROTECTION.md` (plan-blocked, compensating controls listed); PR template reviewer checklist.
- Assessment: limits are documented, and the enforceable parts (label gate, drift gate, fork-PR routing) are enforced. The unenforceable parts are owner-accepted findings (BP-P1-001, CI-P1-001), so they are recorded, not refiled.

### Item: Untrusted content and provenance

- Evidence: `AGENTS.md:22-29` (rule 7) explicitly treats audit reports, vendored `mct/` documents, captures and PR text as evidence, not instructions, and requires surfacing injected instructions to the owner; the scanner skips only long-hex digests under `docs/audits/`.
- Gap: no authorship/provenance rule for agent-authored changes (finding AI-2). The independent-human-review requirement (`AGENTS.md:87-88`) remains the compensating control.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| AI-001 | Agent instructions | `AGENTS.md` | Comprehensive doctrine | Stale run pointer | P3 | Refresh (AI-1) |
| AI-002 | Tool-specific agent configs | none | AGENTS.md implied | No pointers | P3 | Add files (AI-2) |
| AI-003 | Prompt packs | `REPOSITORY.md:5` | Doctrine named | No pack version | P3 | Record version |
| AI-004 | Repo maps | `REPOSITORY.md`, `mct/REPO-MAP.md` | Maintained | Minor drift | P3 | Keep |
| AI-005 | Conventions | `REPOSITORY.md` | Commit/evidence rules | Plan-gated enforcement | P3 | Owner-accepted |
| AI-006 | Validation commands | `ci/validate.py` | 19 checks; CI | Full run lab-bound | P3 | Document subset |
| AI-007 | Safe-change boundaries | `AGENTS.md` rule 6 | Rollback + evidence required | Review not server-enforced | P3 | Owner-accepted |
| AI-008 | Do-not-touch areas | CODEOWNERS; `.gitignore` | Sensitive trees, generated trees | — | — | Keep |
| AI-009 | Secrets guidance | Rule 1; gitleaks; scanner | Strong | — | — | Keep |
| AI-010 | PR guidance | Template; CODEOWNERS | Checklist present | No provenance | P3 | Add field |
| AI-011 | Audit output conventions | `AUDIT_RUN_LIFECYCLE.md` | Lifecycle + tooling | Rule 6 stale | P3 | Refresh (AI-1) |
| AI-012 | Generated code risks | `REPOSITORY.md` table; drift check | review-package untracked | HEAD binding gap | P3 | Cross-ref INFRA-P2-001 |

## Findings

### Finding: AI-P3 — Agent/audit-run pointers are stale (see JSON for machine form)

### Finding: AI-P3 — No AI-provenance policy and no per-tool agent instruction coverage (see JSON)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Agent follows a closed run folder / misses newest P0 | P3 | Medium | Low | `AUDIT_RUN_LIFECYCLE.md:39`, `AGENTS.md:82-86` | AI-1 |
| Tool that does not read AGENTS.md acts without doctrine | P3 | Medium | Medium | no tool configs | AI-2 |
| Unattributed agent-authored change reaches `main` | P3 | Low | Medium | no provenance rule | AI-2 + human review |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Refresh the stale run pointers (AI-1).
- Add pointer files + a provenance field (AI-2).

### This Month
- Record the prompt-pack/profile version in `REPOSITORY.md` so runs are reproducible.
- Add a doc-drift test that the newest referenced run folder exists.

### Later / Platform Evolution
- Revisit branch protection when the GitHub plan allows; keep the owner-accepted compensating controls documented.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Refresh `AUDIT_RUN_LIFECYCLE.md` rule 6 and the AGENTS pointer | Removes a live-vs-closed confusion | `docs/runbooks/AUDIT_RUN_LIFECYCLE.md`, `AGENTS.md` | `grep` shows newest run id |
| Add `CLAUDE.md` → AGENTS.md pointer | Claude Code agents load doctrine | `CLAUDE.md` | file present |
| Add provenance line to PR template | Attribution for agent changes | `.github/pull_request_template.md` | template shows field |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Doc-drift check for referenced run folders | P3 | maintainer | S | none |
| Provenance rule + pointer files | P3 | maintainer | S | none |

## Suggested Tests

- CI check: every `docs/audits/**` run id referenced from `AGENTS.md`/runbooks resolves to an existing folder, and the newest full run is referenced.
- Negative test: a synthetic planted secret under `docs/audits/` still fails the secret scan (already covered by `audit_run_scanner_test.sh`; keep).
- Lint: PR template contains a provenance field.

## Suggested Documentation Updates

- `docs/runbooks/AUDIT_RUN_LIFECYCLE.md` rule 6 — derive/state the current run.
- `AGENTS.md` §Gates and review — point at the newest published run and `docs/CURRENT_STATE.md`.
- `.github/pull_request_template.md` — add "Provenance (human/agent, tool)".
- `REPOSITORY.md` — record the prompt-pack/profile version.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which pack/profile version governs the current work? | Reproducibility of the doctrine | Owner answer; pack metadata |
| Is a plan upgrade planned? | Whether approval enforcement can move from documented to enforced | Owner answer |

## Prior-Run Comparison

- Prior full run `falcon-20261005-full-main-e267ce1` (in-repo `20261005-0354-full-main-e267ce1`): no AI findings.
- Earlier 2026-09-30 run: AI-P1-001 (stale gates) **verified-fixed** (AGENTS refreshed at `cd8b5c0`); AI-P2-003 (contradictory summaries) **verified-fixed** (generator derives from ledgers); AI-P2-004 (audit outputs vs validation; no untrusted-content rule) **fixed** (rule 7 + scanner skip + lifecycle); AI-P2-005 (drift/approval enforcement) **partially-fixed → drift gate now enforced** in CI; approval remains plan-gated and owner-accepted. AI-P2-006 (edge CI docs; no PR/provenance policy) remains edge-side; the falcon PR template now exists, provenance still absent (AI-2).
- New this run: two P3 findings (stale run pointers; provenance/tool coverage).

## Limitations

- No CI runs were dispatched and GitHub settings were not queried live; branch-protection status is taken from the repository's own evidence (plan-gated).
- Live host checks were read-only; the external-smoke vantage issue is proven statically and by read-only probes, not by running the workflow.

## Appendix — Agent inventory

| Item | Path | State |
|---|---|---|
| Instructions | `AGENTS.md` | present, 89 lines |
| Conventions | `REPOSITORY.md` | present |
| PR template | `.github/pull_request_template.md` | present |
| CODEOWNERS | `.github/CODEOWNERS` | present |
| Tool configs | `CLAUDE.md`, `.cursor*`, `copilot-instructions.md`, Windsurf | absent |
| Validation | `ci/validate.sh`, `ci/validate.py` | present, passing `--fast` |

## Findings

| ID | Severity | Title |
|---|---|---|
| AI-P3-001 | P3 | Agent/audit-run pointers are stale: the lifecycle runbook still calls the 2026-09-30 run 'the current run' and AGENTS.md points at it as the full-domain reference |
| AI-P3-002 | P3 | No AI-provenance policy and no per-tool agent instruction coverage |
