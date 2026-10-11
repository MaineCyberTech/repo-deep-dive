# 23_executive_summary_release_gate — Prompt 23 - Executive Summary and Release Gate

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `23_executive_summary_release_gate.md` (area EXEC, prompt)

## Verification Performed

# Executive Summary and Release Gate — EXEC domain

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `MaineCyberTech/mainecybertech` (`/tmp/opencode/mct-audit-target`, read-only)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (`8d299b8d`, merged 2026-10-11)
- Generated at: 2026-10-11
- Auditor: repo-deep-dive subagent (domain 23, area EXEC)
- Area code: EXEC
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/23_executive_summary_release_gate.md` (pack-side twin of this body)
- Scope limitations: read-only clone; GitHub Environments settings, workflow runs, alert deliveries and branch-protection live state are **not observable from the clone** and are marked `unverified` / operator-gated. No production system was contacted.

## Scope

Reviewed: the repository's own release-gate and verdict artifacts, and the gate criteria themselves at `8d299b8d`.

In scope:

- `docs/RELEASE_GATE.md` — the in-repo release gate (exit criteria, fail-closed decisions register, operator checklist).
- `docs/RELEASE.md`, `docs/RELEASING.md` — deploy-gate reference and promotion procedure (gate-adjacent).
- `docs/audits/repo-deep-dive/*/EXECUTIVE_SUMMARY.md` and `RELEASE_GATE.md` — published run verdicts (`178b91c`, `9c0b88c`).
- `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md` — the repo's own re-audit rollup.
- `prompts/portal-alignment/engine/outputs/release_gate.json` + `release_decision.json` — committed machine-readable gate outputs.
- The current code state for each gate exit criterion and each fail-closed decision-register row.

Out of scope: per-domain technical verification of every P1/P2 (owned by the other domains in this run); the final aggregate `EXECUTIVE_SUMMARY.md` / `RELEASE_GATE.md` for this run (written by the aggregator from all findings). REL-area rows (version identity, changelog) are left to domain `40_release_notes_changelog_generator`; FINAL-area rows to `22_final_risk_register_roadmap` — this report re-verifies only their release-gate aspects.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/RELEASE_GATE.md` | Gate artifact | The declared release authority: exit criteria + decision register + operator checklist | Bound to run `20261003-0018` @ `2295958d`; last touched 2026-10-03 (`c11f40ad`); 286 commits behind HEAD |
| `docs/RELEASING.md:93-103,136-148` | Ops doc | States prod env unprovisioned, `prod-approval` reviewers not configured | Current at 8d299b8d (`4bbc17ec`, 2026-10-04) |
| `docs/FINAL_OPERATOR_MAP.md:42`, `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:100` | Ops docs | Live-state claims for the approval gate | Both say reviewers "not yet configured" (last touched 2026-10-02) |
| `docs/audits/repo-deep-dive/mainecybertech-20261004-full-main-9c0b88c/{EXECUTIVE_SUMMARY,RELEASE_GATE,findings}.{md,json}` | Published verdict | The repo's existing published gate/verdict — must be reconciled, never granted/revoked | Verdict "GO WITH CONDITIONS", raw counts; findings.json: 336 rows, P0 6/6 verified-fixed, P1 48 verified-fixed / 7 partially-fixed / 2 open / 2 still-open |
| `docs/audits/repo-deep-dive/20261004-0700-main-178b91c/RELEASE_GATE.md` | Published verdict | Earlier same-week focused run | "Verdict: GO", P0 x0/P1 x0; `178b91c` is an ancestor of `9c0b88c` |
| `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md:69-74,135-136` | Re-audit rollup | The repo's own status of record for FINAL-P1-001 | Says FINAL-P1-001 "stays open pending a successful dry `main` deploy"; claims prod reviewers were configured (no committed artifact) |
| `prompts/portal-alignment/engine/outputs/release_gate.json`, `release_decision.json` | Machine gates | Committed approval artifacts | APPROVED (score 91, 2026-08-06) vs BLOCKED (score 21, 2026-06-30); commit binding not a SHA |
| Gate exit criteria code paths | Code | Reproduce each criterion at HEAD | `orphan-cleanup.ts`, `env.ts`, `field-encryption.ts`, `public.ts`, `search.ts`, `api-key.ts`, `branch-protection/main.json`, `db-restore-test.yml`, `alertmanager.tmpl.yml`, `deploy-do.yml` |
| Previous-run `follow_up_register.md` | Register | Verification duty | No `EXEC-` rows; nearest in-domain rows: FINAL-P1-001, FINAL-P2-001, FINAL-P2-002 |

## Verification Performed

| Command / method | Observed result |
|---|---|
| `git -C /tmp/opencode/mct-audit-target log -1 --format='%h %ad %s' --date=short HEAD` | `8d299b8d 2026-10-11 Merge PR #168: promote develop to main (metrics scrape fixes + register sync)` |
| `git log --oneline 2295958d..HEAD \| wc -l` | **286** commits since the gate was issued |
| `git log -1 -- docs/RELEASE_GATE.md` | `c11f40ad 2026-10-03 fix(release): close final release-gate findings` — gate never re-issued |
| `grep -c 'EXEC-' follow_up_register.md` (previous run) | **0** — no EXEC-prefixed rows; in-domain subjects live under FINAL/REL |
| `python3` status count over the 9c0b88c published `findings.json` | 336 rows: P0 6/6 `verified-fixed`; P1 48 `verified-fixed`, 7 `partially-fixed`, 2 `open`, 2 `still-open`; P2 79/166 closed; P3 26/105 closed |
| `git merge-base --is-ancestor 178b91c 9c0b88c` | true — the "GO / P0 x0" focused run precedes the "GO WITH CONDITIONS / P0 x6" full run |
| Criterion 1: `grep` `apps/worker/src/tasks/orphan-cleanup.ts` + `apps/worker/src/__tests__/orphan-cleanup.test.ts` | Guard present (`isFolderEntry`, `isFolderLike`, pre-remove abort) and 11 regression tests; **code-side green** |
| Criterion 2: `grep FIELD_ENCRYPTION_KEY apps/api/src/config/env.ts apps/api/src/lib/field-encryption.ts` | `assertProductionSecrets` refuses prod boot (env.ts:103-106); `encryptField` throws in prod (field-encryption.ts:46-49); dev/test `plain:` fallback documented; **green** |
| Criterion 3: `grep TURNSTILE apps/api/src/config/env.ts apps/api/src/routes/public.ts` | Prod boot refuses without the secret (env.ts:88-91); `/public/submit` throws `CAPTCHA_REQUIRED`/`CAPTCHA_FAILED` (public.ts:136-142); **green** |
| Criterion 4: `grep prod-approval .github/workflows/deploy-do.yml` + `docs/RELEASING.md` | Workflow attaches `prod-approval` (deploy-do.yml:571); docs say reviewers not configured and prod env lacks secrets — **operator-gated, unverified** |
| Criterion 5: `grep watchdog infra/digitalocean/alertmanager.tmpl.yml` + `deploy-do.yml` | External dead-man receiver routed (lines 19-20, 87-94); prod deploy fails closed when the watchdog URL is empty (deploy-do.yml:739-741); synthetic delivery **not recorded** |
| Criterion 6: `grep -E 'Verify database integrity\|::error\|Notify' .github/workflows/db-restore-test.yml` | Integrity assertions (lines 135-224), failure notifier (241-242), weekly schedule (3-4); dated green run **not committed** |
| Criterion 7: `cat .github/branch-protection/main.json` | `enforce_admins: true` (line 12), `require_code_owner_reviews: true` (line 15); live application **unverified** |
| Register rows: `grep` migrations / middleware / routes for the five fail-open defaults | All five now fail closed in code; `docs/RELEASE_GATE.md:43-49` still records all five `open` |
| `git tag \| wc -l`; `grep -rn deleted_at apps --include='*.ts' \| wc -l` | 0 tags; 0 soft-delete reads/writes — P1 residuals confirmed still open (owned by REL/DATA domains) |
| `git ls-files prompts/portal-alignment/engine/outputs/` + `cat release_gate.json` | Committed APPROVED artifact; `commit` field is a subject string; sibling BLOCKED artifact disagrees |

## Executive Summary

The repository is in a **pre-go-live** state and its gate artifacts do not yet reflect that state honestly.

What is strong: the code-side work from the 2026-10-03/04 remediation cycle is real and reproducible at `8d299b8d` — the P0 data-loss path is guarded with regression tests, PII encryption and CAPTCHA fail closed in production, search fails closed without an org scope, API keys actually authenticate, demo migrations are gated off by default, branch protection is committed with `enforce_admins: true` + CODEOWNERS review, the restore test asserts integrity, and the Alertmanager watchdog is fail-closed on prod deploys. No unresolved P0 was found.

What is weak — and this is the EXEC finding — is the **decision layer**: the in-repo release gate is 286 commits stale and its decision register contradicts current code (all five rows stale); its exit criteria are partly unsatisfiable before the first deploy and it defines no GO/GO-WITH-CONDITIONS/NO-GO rules; the published run verdicts are unreconciled stubs (raw counts, no statuses) and two published gates in the same week appear to contradict ("GO / P0 x0" then "GO WITH CONDITIONS / P0 x6"); the operator checklist has zero recorded evidence and the repo's own documents disagree about whether `prod-approval` reviewers are configured; and two committed machine-readable gates give opposite decisions without a verifiable SHA.

**Gate recommendation at `8d299b8d` (EXEC): GO WITH CONDITIONS for continued `main`-branch development; NO-GO for the first production go-live.** This does not revoke the repository's existing published verdict (`9c0b88c`: GO WITH CONDITIONS) — it records the delta: that verdict cannot be carried to `8d299b8d` because it is an unreconciled stub and every operator-side condition remains unmet. No unresolved P0 exists; P1 mitigation is incomplete (2 still-open, 2 open, 7 partially-fixed in the latest full register), so "GO only with no P0/P1 blockers and validation evidence" is not satisfied, and the gate's own line — "A prod release is blocked until every row below is green or owner-accepted" (`docs/RELEASE_GATE.md:28`) — is not met.

Conditions to flip to GO (each needs a committed artifact, not an assertion):

1. Provision `prod`/`prod-approval` (secrets/vars + ≥1 required reviewer) and record the `gh api` capture; reconcile `RELEASING.md`/`FINAL_OPERATOR_MAP.md`/`REAUDIT_REPORT_20261004.md` to one live-state record.
2. One dry `main` deploy green (run URL), including the watchdog and worker health gates.
3. Synthetic alert delivered to the external receiver + a dated green `db-restore-test` run with row assertions.
4. Close or owner-accept the open/still-open P1s (`CI-P1-001`, `CI-P1-003`, `DATA-P1-003`, `IR-P1-006`) and record the partially-fixed residuals.
5. Re-issue `docs/RELEASE_GATE.md` bound to the go-live SHA with per-criterion status and verdict rules; reconcile the published summaries.

Investment view: the remediation trajectory (P0 6/6 and P1 48/59 closed at the last full pass, with this run's spot checks reproducing the fixes) supports continued investment. The remaining risk is operationalization and evidence discipline, not code volume.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| In-repo release gate | `docs/RELEASE_GATE.md` | Exit criteria + decisions register + go-live checklist | Stale (bound to `2295958d`, 286 commits behind) | High | Register rows all `open`; no verdict rules/owner/expiry |
| Deploy gate reference | `docs/RELEASE.md` | Fail-closed deploy-job conditions | Current, accurate | Low | Documents prod-approval dependency |
| Promotion doc | `docs/RELEASING.md` | Branch model, approval gate, caveats | Current; says gate not in force | Medium | Conflicts with REAUDIT claim on reviewers |
| Published verdict `9c0b88c` | `docs/audits/.../mainecybertech-…-9c0b88c/RELEASE_GATE.md` | Verdict for last full run | Stub: "GO WITH CONDITIONS", raw counts | High | Does not reconcile statuses; per gate rule unresolved-P0 text is misleading |
| Published summary `9c0b88c` | `…/EXECUTIVE_SUMMARY.md` | Leadership summary | Stub: one count line | Medium | No strengths/risks/actions |
| Published verdict `178b91c` | `…/20261004-0700-main-178b91c/RELEASE_GATE.md` | Focused run verdict | "GO", P0 x0 | Medium | Ancestor of `9c0b88c`; no cross-run reconciliation |
| Re-audit rollup | `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md` | Post-merge verification | Says FINAL-P1-001 open; claims reviewers configured | Medium | Evidence files outside repo (`file:///C:/temp/…`) |
| Machine gate outputs | `prompts/portal-alignment/engine/outputs/*.json` | Engine decisions | APPROVED vs BLOCKED; no SHA binding | Medium | Historical per `prompts/PROVENANCE.md`; no in-file marker |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Current state | 3 | P0 6/6 and P1 48/59 closed per last full register; gate code criteria reproducible at HEAD | Decision artifacts stale/unreconciled | Re-issue gate bound to HEAD |
| Strengths | 4 | Fail-closed prod boot, orphan-cleanup guard + tests, watchdog fail-closed deploy, attestations | None material | Keep; cite in exec summary |
| Biggest risks | 2 | Operator evidence absent; docs contradict on reviewer state; prod env unprovisioned | "Configured ≠ exercised" | Commit evidence artifacts |
| Release blockers | 2 | Gate criteria 4/6 (and 5's delivery) unmet; 4 P1s open/still-open | No closure artifacts | Operator checklist execution |
| Business/security/ops/UX impact | 3 | Security defaults now fail closed; ops go-live path still manual | Ops readiness unproven | Dry deploy + drills |
| Investment recommendation | 4 | Trajectory: 286 commits of remediation, most P0/P1 closed | Evidence discipline weak | Continue investment |
| Next actions | 2 | Checklist exists but unchecked; no owner/date | No tracked plan at HEAD | Assign owners + review-by |
| Risk counts/themes | 2 | Published counts are raw, statuses absent; cross-run deltas unstated | Aggregates not reconciled | Status-aware summary |

## Detailed Review

### Item: `docs/RELEASE_GATE.md` (in-repo gate)

- Evidence: `docs/RELEASE_GATE.md:3-6,8-11,20-24,28-36,43-49,56-72,74-79`.
- What it does: consolidates the `20261003-0018` run's final findings into three exit conditions, seven release-blocking criteria, a five-row fail-closed decisions register, and a six-item operator checklist.
- How it appears to work: as a human-run gate; statuses are recorded as decision/owner/evidence-required, deliberately not as "fixed".
- Current controls: explicit "no production environment yet" statement; owner column; evidence column in the checklist.
- Missing controls: commit/version binding to current HEAD; verdict rules (GO/GO-WITH-CONDITIONS/NO-GO); gate owner; review-by/expiry; per-criterion status tracking; a place to record owner-accepted decisions; re-validation procedure.
- Risks: readers cannot tell closed vs open; five register rows contradict code; criterion 1 is unsatisfiable pre-deploy; criterion 4 is circular.
- Recommended improvement: re-issue at HEAD with the fields above and a supersession header.
- Suggested tests: a CI docs guard that fails when the gate's bound SHA is not an ancestor of HEAD or older than N days (mirrors `scripts/check-docs-counts.mjs` style).
- Suggested docs: this file plus `docs/RELEASING.md` link-through.

### Item: Published run verdicts (`EXECUTIVE_SUMMARY.md` / `RELEASE_GATE.md`)

- Evidence: `docs/audits/…-9c0b88c/EXECUTIVE_SUMMARY.md:5`; `…/RELEASE_GATE.md:3-5`; same folder `findings.json` (336 rows, statuses above); `…-178b91c/RELEASE_GATE.md:3-5`; `INDEX.md:5`.
- What they do: give a per-run headline verdict + counts.
- How they work: aggregator-generated stubs; the 9c0b88c gate delegates detail to the lens report and registers.
- Current controls: commit and run recorded in each file; counts match the machine findings.
- Missing controls: status-aware counts (open vs verified-fixed vs owner-accepted); evidence links; cross-run reconciliation; explicit statement that raw counts include already-closed findings.
- Risks: "P0 x6" next to "GO WITH CONDITIONS" reads as an unresolved-P0 contradiction; the earlier "GO / P0 x0" makes the later run look like a regression; a reader cannot tell that all six P0s were verified-fixed.
- Recommended improvement: regenerate from `findings.json` with status counts and a delta table; add a "supersedes" line.
- Suggested tests: an aggregator check that fails when `RELEASE_GATE.md` cites severity totals without status totals.
- Suggested docs: run `INDEX.md` + pack prompt 23 quality bar.

### Item: Committed machine-readable gates (portal-alignment)

- Evidence: `prompts/portal-alignment/engine/outputs/release_gate.json:2-14`; `…/release_decision.json`; `prompts/portal-alignment/engine/run_alignment_engine.py:533-570`; `prompts/PROVENANCE.md:3-7`.
- What they do: record phase-7 decisions of a historical alignment engine.
- How they work: decision = f(findings list); commit field falls back to `git log --oneline -1` (subject string).
- Current controls: PROVENANCE.md declares `prompts/` historical/untrusted.
- Missing controls: in-file historical marker; SHA binding; run id.
- Risks: an APPROVED_FOR_PROD_DEPLOY artifact with no binding can be cited as release evidence.
- Recommended improvement: mark or remove; emit full SHA on re-run.

### Item: The gate criteria themselves (GO / GO-WITH-CONDITIONS / NO-GO test at `8d299b8d`)

- Evidence: `docs/RELEASE_GATE.md:28-36`; per-criterion reproduction table in "Verification Performed".
- Result: 5 of 7 criteria are green code-side (1, 2, 3, 7, and 5's configuration); criterion 4 (prod env + reviewers + dry deploy) and criterion 6 (dated green restore run) lack required operator artifacts; criterion 5's synthetic delivery is unrecorded.
- Verdict mapping (per pack rules): no unresolved P0 → not NO-GO on P0 grounds; P1 mitigation incomplete → not GO; **GO WITH CONDITIONS for development, NO-GO for prod go-live** (the gate's own line 28 blocks prod release until every row is green or owner-accepted).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EXEC-001 | Current state | `docs/RELEASE_GATE.md:3-6`; 286 commits behind | Gate doc exists | Not bound to HEAD | P2 | Re-issue at HEAD |
| EXEC-002 | Strengths | Code spot checks (orphan guard, fail-closed boot, watchdog) | Fail-closed defaults + tests | Not surfaced in exec artifacts | P3 | Cite in summary |
| EXEC-003 | Biggest risks | `docs/RELEASING.md:141-148`; `FINAL_OPERATOR_MAP.md:42`; `REAUDIT_REPORT…:136` | Operator checklist | Contradictory live-state records | P2 | Single evidence record |
| EXEC-004 | Release blockers | Criteria 4/5/6 unmet | Pre-go-live gate | No closure artifacts | P1/P2 | Execute checklist |
| EXEC-005 | Business/security/ops impact | Fail-closed code; manual ops path | Security defaults fixed | Ops readiness unproven | P2 | Dry deploy + drills |
| EXEC-006 | Investment recommendation | Remediation trajectory (P0 6/6, P1 48/59) | Continued investment justified | Evidence discipline | P3 | Status-aware reporting |
| EXEC-007 | Next actions | `docs/RELEASE_GATE.md:56-72` | Checklist exists | Unchecked, no owner/date | P2 | Assign + track |
| EXEC-008 | Risk counts/themes | Stub counts vs `findings.json` statuses | Counts present | Statuses/deltas absent | P2 | Regenerate summaries |

## Findings

### Finding: Residual authorization/secret defaults need explicit decisions (EXEC, P2)

- Severity: P2 — Confidence: High — Area: EXEC
- Evidence: `docs/RELEASE_GATE.md:43-49`; `apps/api/src/middleware/api-key.ts:24,38-77`; `apps/api/src/middleware/auth.ts:63-69`; `supabase/migrations/5302119_demo_test_data.sql:25-26` (+5302120/21/23/26); `apps/api/src/config/env.ts:88-91,103-106,139`; `apps/api/src/lib/field-encryption.ts:46-49`; `apps/api/src/routes/public.ts:26-42,133-142`; `apps/api/src/routes/search.ts:77-97,118-161`
- What is happening: all five fail-open defaults now fail closed in code, but the gate's decision register still shows all five `open` with pre-fix text and records no owner-accepted decisions.
- Why it matters: the decision record cannot close the item or show what was fixed vs accepted.
- Impact: duplicate work or unrecorded risk acceptance; auditability gap.
- Recommended fix: update the register with per-control closure evidence and status; add a dated decision-record section.
- Suggested validation: a docs guard asserting every register row has a status of `fixed-in-prod` or `owner-accepted` plus an evidence link.
- Owner: security/API + release owner — Effort: S — Status: `partially-fixed` (previous FINAL-P2-002 re-verification)

### Finding: In-repo release gate binds a stale commit and cannot produce a verdict (EXEC, P2)

- Severity: P2 — Confidence: High — Area: EXEC
- Evidence: `docs/RELEASE_GATE.md:3-6,8,30,33,56-72,74-79`; `git log --oneline 2295958d..HEAD` = 286; `c11f40ad` 2026-10-03.
- What is happening: the gate has never been re-issued; criteria 1 and 4 are unsatisfiable/circular before the first deploy; there are no GO/GO-WITH-CONDITIONS/NO-GO rules, owner, or expiry.
- Why it matters: no single current artifact can support a release decision.
- Impact: decision quality depends on reconciling four disagreeing artifacts.
- Recommended fix: re-issue bound to the go-live SHA; add verdict rules, owner, review-by, supersession header; staging equivalent for deployed-commit criteria.
- Suggested validation: docs guard on bound SHA freshness (see above).
- Owner: release owner/ops — Effort: S — Status: `open` (new)

### Finding: P0 data-loss path and unverified "fixed" claim block a clean release (EXEC, P1)

- Severity: P1 — Confidence: High — Area: EXEC
- Evidence: `apps/worker/src/tasks/orphan-cleanup.ts:52-53,63-66,221-235`; `apps/worker/src/__tests__/orphan-cleanup.test.ts:179-210`; `docs/RELEASE_GATE.md:30`; `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md:69-74,135`; previous `follow_up_register.md:47`.
- What is happening: the code fix is present and tested, but the gate's deployed-commit closure artifact does not exist and the repo's own re-audit still says the item is open, while the register says verified-fixed.
- Why it matters: the release-blocking claim is still not evidence-closed, and the two status records contradict.
- Impact: leadership cannot tell whether the blocker is closed or carried.
- Recommended fix: record the deployed-commit regression artifact after a dry deploy, or owner-accept the code-level tests, cite them in the gate, and reconcile the two records to one status.
- Suggested validation: re-run the orphan-cleanup suite and attach the output to the gate row.
- Owner: worker/data + release owner — Effort: S/M — Status: `partially-fixed` (previous FINAL-P1-001 re-verification)

### Finding: Governance and observability gaps mean the platform cannot yet detect or control production failure (EXEC, P2)

- Severity: P2 — Confidence: High (code/config) / Medium (live state) — Area: EXEC
- Evidence: `docs/RELEASE_GATE.md:23,56-72`; `infra/digitalocean/alertmanager.tmpl.yml:19-20,87-94`; `.github/workflows/deploy-do.yml:739-741`; `.github/workflows/db-restore-test.yml:3-4,135-224,241-242`; `docs/RELEASING.md:141-148`; `docs/FINAL_OPERATOR_MAP.md:42`; `docs/FINAL_DEPLOYMENT_OPERATIONS_HANDBOOK.md:100`; `REAUDIT_REPORT_20261004.md:136`.
- What is happening: configuration is in place and fail-closed, but no dry deploy, synthetic alert delivery, or dated restore-test result is recorded, and repo documents contradict each other about `prod-approval` reviewers.
- Why it matters: "configured" is not "exercised"; the platform cannot yet demonstrate detection/recovery/control of production failure.
- Impact: go-live risk is unquantified; the approval gate may not be in force.
- Recommended fix: commit the operator evidence under the run/audit folder; reconcile the live-state docs.
- Suggested validation: link each exit row to its artifact (run URL, capture, delivery receipt).
- Owner: ops/release + infra — Effort: M — Status: `partially-fixed` (previous FINAL-P2-001 re-verification)

### Finding: Committed portal-alignment gate outputs disagree and bind no verifiable SHA (EXEC, P3)

- Severity: P3 — Confidence: High — Area: EXEC
- Evidence: `prompts/portal-alignment/engine/outputs/release_gate.json:2-14`; `…/release_decision.json`; `prompts/portal-alignment/engine/run_alignment_engine.py:533-570`; `prompts/PROVENANCE.md:3-7`.
- What is happening: APPROVED (score 91) and BLOCKED (score 21) artifacts coexist; the approval binds a commit subject, not a SHA.
- Why it matters: an automated consumer could cite the APPROVED artifact as current evidence.
- Recommended fix: mark/remove the outputs; emit full SHA + run id on any re-run.
- Suggested validation: repo-hygiene check for `decision: APPROVED*` outside an evidence folder.
- Owner: repo maintainer (prompt pack) — Effort: S — Status: `open` (new)

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Go-live attempted with an approval gate that is not in force | P1 | Medium | Unapproved prod change | `docs/RELEASING.md:141-148`; `FINAL_OPERATOR_MAP.md:42` | Configure reviewers; record capture; verify pause |
| Release decision made from stale/unreconciled artifacts | P2 | High | Wrong go/no-go | `docs/RELEASE_GATE.md:3-6`; stubs | Re-issue gate; status-aware summaries |
| Undetected production failure (alerting/restore unexercised) | P2 | Medium | Extended outage/data loss | `docs/RELEASE_GATE.md:23`; no artifacts | Synthetic alert + restore drill with evidence |
| Blocker status ambiguity (FINAL-P1-001 contradiction) | P2 | High | Mis-sequenced remediation | `REAUDIT_REPORT…:135` vs `follow_up_register.md:47` | One status of record |
| Stale APPROVED machine artifact cited as evidence | P3 | Low | Misleading approval | `release_gate.json:2-14` | Mark/remove artifact |

## Recommendations

### Immediate / Release Blocking

- Do not execute the first prod go-live until criteria 4-6 have committed artifacts and the open/still-open P1s are closed or owner-accepted (gate line 28).

### This Week

- Re-issue `docs/RELEASE_GATE.md` at HEAD with per-criterion status, evidence links, verdict rules, owner, and review-by date; mark the `2295958d` version superseded.
- Assign owners/dates to the operator checklist; start the `prod`/`prod-approval` provisioning action.
- Reconcile FINAL-P1-001 to one status across the register, gate, and re-audit report.

### This Month

- Commit operator evidence (dry deploy, synthetic alert, dated restore run) and reconcile the live-state docs.
- Regenerate published `EXECUTIVE_SUMMARY.md`/`RELEASE_GATE.md` from `findings.json` with status counts and deltas.
- Update the decision register with closure evidence for the five fail-closed defaults.

### Later / Platform Evolution

- Add a gate-freshness/status docs guard to CI; extend it to verdict artifacts.
- Decide the fate of the portal-alignment outputs (mark or remove).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add a supersession + bound-SHA header to the gate | Stops stale-gate reuse immediately | `docs/RELEASE_GATE.md` | Rendered doc review |
| Add status counts to the two published stubs | Kills the apparent P0 contradiction | run `EXECUTIVE_SUMMARY.md`, `RELEASE_GATE.md` | Counts match `findings.json` |
| Add in-file `historical: true` to the machine gates | Prevents misuse as evidence | `release_gate.json`, `release_decision.json` | grep for marker |
| Reconcile reviewer live-state wording | Removes contradictory records | `RELEASING.md`, `FINAL_OPERATOR_MAP.md`, `REAUDIT_REPORT…` | One statement across three files |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Gate freshness/status CI guard | P2 | release owner | S | Docs guard pattern exists (`check-docs-counts.mjs`) |
| Verdict artifact schema (status counts, evidence links, supersedes) | P2 | audit tooling | M | Aggregator changes |
| Operator evidence folder + linking convention | P2 | ops | S | Go-live attempt scheduled |
| Owner-accepted decision record format | P3 | security/release | S | None |

## Suggested Tests

- Docs guard: fail CI when `docs/RELEASE_GATE.md`'s bound SHA is not an ancestor of HEAD or the file is older than 30 days.
- Aggregator check: fail when a `RELEASE_GATE.md` reports severity totals without status totals.
- Regression: re-run `apps/worker/src/__tests__/orphan-cleanup.test.ts` and attach output to the gate row.
- CI/manual: dispatch `db-restore-test` and archive the run URL as the dated drill artifact.
- Manual: dispatch `deploy-do deploy_target=prod` after reviewer configuration and confirm the pause at "Waiting for approval".
- Repo hygiene: fail when a committed JSON contains `APPROVED_FOR_PROD_DEPLOY` without a 40-hex `commit` field.

## Suggested Documentation Updates

- `docs/RELEASE_GATE.md` — re-issue at HEAD (statuses, verdict rules, owner, expiry, supersession).
- `docs/RELEASING.md` / `docs/FINAL_OPERATOR_MAP.md` — one reconciled live-state statement.
- `docs/audits/repo-deep-dive/REAUDIT_REPORT_20261004.md` — correct the reviewer claim or cite a committed artifact.
- Run `EXECUTIVE_SUMMARY.md` / `RELEASE_GATE.md` — status-aware regeneration (aggregator change).
- `prompts/PROVENANCE.md` (or the JSONs themselves) — bind the machine-gate outputs.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are `prod-approval` reviewers configured today? | Decides whether the approval gate is in force | `gh api repos/:owner/:repo/environments` capture |
| Has any dry `main` prod deploy been run since 2026-10-04? | Criterion 4 | Run URL / workflow history |
| Has the synthetic alert been delivered and the restore test run green since the gate was issued? | Criteria 5-6 | Delivery receipt; dated run URL |
| Which FINAL-P1-001 status is of record: register (verified-fixed) or re-audit (open)? | Blocker sequencing | Owner decision + artifact |
| Does the aggregator intend status-aware verdict artifacts? | Fixes the stub-contradiction class | Pack/aggregator design |

## Appendix

### Gate-criteria reproduction summary at `8d299b8d`

| Criterion | Code/config state | Operator evidence | Assessment |
|---|---|---|---|
| 1. Orphan cleanup cannot delete folders/prefixes + deployed-commit regression test | Guard + 11 tests present | No deployed commit exists | Code-side green; closure artifact absent |
| 2. Prod boot requires 32-byte `FIELD_ENCRYPTION_KEY`; no `plain:` in prod | `assertProductionSecrets` + `encryptField` throw | n/a | Green |
| 3. Prod requires `TURNSTILE_SECRET_KEY`; `/public/submit` fails closed | Boot refusal + 400s | n/a | Green |
| 4. Prod env provisioned + reviewers + dry deploy green | `prod-approval` attached | Docs say not configured; no run URL | Operator-gated, unverified |
| 5. Alertmanager receiver wired + synthetic alert delivered | Receivers + watchdog fail-closed | No delivery record | Config green; evidence absent |
| 6. Dated green `db-restore-test` with row assertions | Integrity assertions + notifier + weekly schedule | No dated run committed | Config green; evidence absent |
| 7. Branch protection `enforce_admins` + CODEOWNERS review | JSON correct (`main.json:12,15`) | Live application unverified | Code-side green; live unverified |

### Verification-duty outcome (previous run, EXEC-related rows)

No `EXEC-` rows existed in the previous `follow_up_register.md` (`grep -c` = 0). The in-domain subject matter lived under FINAL: FINAL-P1-001, FINAL-P2-001 and FINAL-P2-002 were re-verified at `8d299b8d` above — all three downgraded from the carried `verified-fixed` to `partially-fixed`, because the closure evidence each cites (deployed-commit regression artifact, operator drill evidence, recorded decisions) does not exist at this commit. REL-area rows (`REL-P1-001`, `REL-P1-002`, `REL-P2-*`) are left to domain `40_release_notes_changelog_generator`.

## Findings

| ID | Severity | Title |
|---|---|---|
| EXEC-P2-001 | P2 | Residual authorization/secret defaults need explicit decisions |
| EXEC-P2-002 | P2 | In-repo release gate binds a stale commit and cannot produce a verdict |
| EXEC-P1-001 | P1 | P0 data-loss path and unverified "fixed" claim block a clean release |
| EXEC-P2-003 | P2 | Governance and observability gaps mean the platform cannot yet detect or control production failure |
| EXEC-P3-001 | P3 | Committed portal-alignment gate outputs disagree and bind no verifiable SHA |
