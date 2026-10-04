# Patch Plan — post-merge verification

**Repo:** `MaineCyberTech/mainecybertech` · **Commit:** `a97425db` · **Date:** 2026-10-04

## No new patch sets

Every finding with a code-side remediation is merged and verified at
`a97425db`. The 16 original patch sets were reconciled via
`tools/remediation_status.py` with the integration merge commit
`a97425dbefc54b7db2a4e3ebe42470364dac0fab` as evidence.

## Completed integration

| Patch set | PR | State |
|---|---|---|
| PATCH-001…003, 005, 008…012 | #43, #53, #56, #57, #62, #59, #60, #58, #61 | merged → verified-fixed |
| PATCH-004 | #54 | open — deploy gate merged; prod environment is operator work |
| PATCH-013 | #63 | open — code merged; owner decisions outstanding |
| PS-U01 | #64 | open — startup guard merged; RLS rollout operational |
| PS-U02…U05 | #55, #65, #66, #67 | merged → verified-fixed |
| PATCH-006, 007 | — | already verified-fixed at base |

## Optional follow-up patches (not blocking)

1. `git update-index --chmod=+x` for the 17 tracked shell scripts (`DET-P2-002`).
2. Pin the 4 container images by digest (`DET-P3-004`).
3. Remove the on-disk Supabase temp secrets once the operator confirms they are
   not needed (`SUPPLY-P3-002` residual).
