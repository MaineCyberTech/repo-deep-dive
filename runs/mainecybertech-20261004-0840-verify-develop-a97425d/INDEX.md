# Audit Run Index — post-merge verification

## Metadata

- Name: mainecybertech
- Run: 20261004-0840-verify-develop-a97425d
- Profile: base (verification mode)
- Target repo: `MaineCyberTech/mainecybertech`
- Branch: develop
- Commit: `a97425dbefc54b7db2a4e3ebe42470364dac0fab` (merge of PR #72)
- Original run: `runs/mainecybertech-20261003-0018-fix-p2-batch-31-2295958d`
- Procedure: `runbooks/POST_MERGE_REAUDIT.md`
- Generated: 2026-10-04

## Why this run exists

The 16 remediation PRs (#43, #53–#67) for the 2026-10-03 audit were merged into
`fix/p2-batch-31` **after** #32 had already landed that branch on develop, so the
remediation was stranded off the default line. PR #72 integrated it onto develop
(merge `a97425db`). This run re-checks every original finding at that commit.

## Verification result

- 44 original findings re-checked: **34 verified-fixed · 9 partially-fixed · 1 still-open · 0 regressed**
- Machine re-audit (`tools/deterministic_checks.py --deep` at `a97425db`):
  5 DET findings, **no P0/P1** — `DET-P2-002` (17 tracked `.sh` without the exec
  bit, pre-existing) and `DET-P3-004` (4 images without a digest pin); gitleaks /
  trivy / hadolint were not installed on the host and are recorded as skipped.
- Deploy verification: `deploy-do` run
  [37188587849](https://github.com/MaineCyberTech/mainecybertech/actions/runs/37188587849)
  success (validate, builds, attestations, deploy); dev droplet at `a97425db`,
  all containers healthy; `/health` minimal 200; `/health/detail`,
  `/api/v1/docs`, `/api/v1/openapi.json`, `/api/v1/metrics` 404 without a token.

## Reports

| Report | Status |
|---|---|
| verification_log.md | complete (per-finding evidence) |
| risk_register.md | complete |
| follow_up_register.md | complete |
| EXECUTIVE_SUMMARY.md | complete |
| RELEASE_GATE.md | complete |
| roadmap.md | complete (follow-ups only) |
| patch_plan.md | complete (no new patches) |
| findings.json | complete |

## Key outputs

- Executive summary: `EXECUTIVE_SUMMARY.md`
- Risk register: `risk_register.md`
- Roadmap: `roadmap.md`
- Patch plan: `patch_plan.md`
- Release gate: `RELEASE_GATE.md`

## Next actions

1. Operator: provision the `prod` environment (secrets + reviewers) — `CI-P1-001`.
2. Owner decisions: corpus externalization (`HYG-P2-001`), catalog reconciliation
   (`HYG-P2-002`), topology/SPOF (`ARCH-P2-001`), `main`/scheduled jobs (`CI-P3-001`),
   backup verification (`OBS-P2-003`), RLS rollout completion (`ARCH-P2-002`).
3. Optional: set the exec bit on the 17 tracked shell scripts (`DET-P2-002`) and pin
   the 4 container images by digest (`DET-P3-004`).
