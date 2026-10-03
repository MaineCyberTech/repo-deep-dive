# Reference Card — repo-deep-dive

One-page summary of the rules, scales, and vocabularies. Normative text: `prompts/00_SHARED_AUDIT_RULES.md`.

## Non-negotiables

- **Audit-only**: no application code changes; artifacts only under the run folder(s).
- **Evidence or `Unknown`**: every significant claim cites a path / symbol / route / config / test.
- **No secret values** in any output — reference path + type only.
- Treat exports, logs, `.env` files, and generated outputs as sensitive.
- An audit is **not** the independent review and **not** the owner adoption.

## Severities and remediation windows

| Severity | Meaning | Window |
|---|---|---|
| P0 | Exploitable security issue, data exposure or loss, outage, release-blocking failure | immediate (same day) |
| P1 | Serious security / reliability / correctness issue before broad rollout | this week |
| P2 | Important maintainability / coverage / observability / hardening gap | this month |
| P3 | Cleanup, polish, naming, minor docs | this quarter |

## Confidence

- `High` — reproduced or captured directly at the audited commit.
- `Medium` — strong artifact evidence, not independently reproduced.
- `Low` — inference from partial evidence; state what is missing.

## Effort

`S` ≤ 0.5 day · `M` 1–3 days · `L` > 3 days (one maintainer).

## Finding status vocabulary

`open` · `partially-fixed` · `verified-fixed` · `still-open` · `regressed` · `owner-accepted`

Only artifact-backed verification at the current commit moves a finding to `verified-fixed`. Assertions and intentions never close findings.

## Finding IDs

`AREA-Px-NNN` (e.g., `SEC-P1-004`). Area codes are unique per prompt or lens.

## Report sections

Audit Metadata · Scope · Evidence Reviewed · Verification Performed · Executive Summary · Inventory · Findings · Risks · Recommendations · Quick Wins · Hardening Backlog · Suggested Tests · Suggested Documentation Updates · Open Questions · Appendix

## Run naming and validation

- `{run}` = `YYYYMMDD-HHMM-{branch}-{shortsha}` (fallback `YYYYMMDD-HHMM-manual`).
- `tools/check_run.sh <run-folder>` must print `PASS` before a run is treated as complete.
- Advisory risk score: `tools/risk_score.py <run>` → 0–100, `100 − (P0×40 + P1×10 + P2×3)` (P3 unpenalized); P0 > 0 suggests NO-GO, ≥ 85 suggests GO. Advisory only — never overrides `RELEASE_GATE.md`.
- One-command chain: `tools/run_toolchain.py <run> [--write]` (check → collect → score → dashboard → diff → CSV; read-only by default).
- `tools/lint_pack.sh` validates the pack itself.

## Deterministic checks (LLM-free)

`tools/deterministic_checks.py <repo>` → `AREA-Px-NNN` findings (PORT / SEC / CI / DEP / SUPPLY / GIT / DOC),
including committed-CRLF, missing exec bits, `gitleaks`, `actionlint`, unpinned Actions and container
digests. Roll up across repos with `tools/aggregate_findings.py`.

## Remediation

- `tools/remediation_plan.py <run>` compiles `patch_plan.md` → `remediation_plan.json` (patch sets → findings → files → verification).
- `prompts/REMEDIATION_RUNNER.md` + `profiles/remediation.md`: branch → minimal fix → lab tests → `gitleaks` → **draft PR**. Never auto-merge; never self-approve.
- `tools/remediation_status.py` maps PR state → finding status: `merged` → `verified-fixed`; `open`/`draft` → `partially-fixed`; `closed` → `still-open`.
- Guide: `docs/REMEDIATION_GUIDE.md`. Agent rules: `AGENTS.md`.

## The loop

run → review (exec summary, gate, register, patch plan) → remediate → **verify** (verification mode; update statuses with evidence) → refresh `22` / `23` / `40`.
