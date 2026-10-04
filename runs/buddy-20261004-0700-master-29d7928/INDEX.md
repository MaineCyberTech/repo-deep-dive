# Audit run 20261004-0700-master-29d7928 - buddy

Focused security / supply-chain / CI deep-dive (`master` @ `29d7928`).

Counts: P0 x0, P1 x2, P2 x3, P3 x4

| File | Contents |
|---|---|
| FOCUSED_SECURITY_SUPPLY_CHAIN_CI.md | Full findings write-up |
| findings.json | Machine-readable findings |
| EXECUTIVE_SUMMARY.md | Summary |
| risk_register.md / follow_up_register.md | Findings register |
| RELEASE_GATE.md | Gate verdict |
| roadmap.md / patch_plan.md | Remediation plan |
| audit_manifest.json | Run manifest |

## P0/P1
- **DEP-P1-001** (P1) Next.js 14.2.35 is EOL and ships unpatched known CVEs
- **SUPPLY-P1-001** (P1) Release workflow runs install scripts and unpinned actions with a write token

