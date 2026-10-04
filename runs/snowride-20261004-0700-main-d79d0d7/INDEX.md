# Audit run 20261004-0700-main-d79d0d7 - snowride

Focused security / supply-chain / CI deep-dive (`main` @ `d79d0d7`).

Counts: P0 x0, P1 x1, P2 x3, P3 x6

| File | Contents |
|---|---|
| lens_focused_security_supply_chain_ci.md | Full findings write-up |
| findings.json | Machine-readable findings |
| EXECUTIVE_SUMMARY.md | Summary |
| risk_register.md / follow_up_register.md | Findings register |
| RELEASE_GATE.md | Gate verdict |
| roadmap.md / patch_plan.md | Remediation plan |
| audit_manifest.json | Run manifest |

## P0/P1
- **SUPPLY-P1-001** (P1) Vulnerable runtime transitive dependency @grpc/grpc-js 1.14.4 with a non-blocking audit gate

