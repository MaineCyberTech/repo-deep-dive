# Audit run 20261004-0700-main-49f46a8 - repo-deep-dive

Focused security / supply-chain / CI deep-dive (`main` @ `49f46a8`).

Counts: P0 x0, P1 x1, P2 x5, P3 x6

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
- **CI-P1-001** (P1) P1 secret gate in the org scan is inert: it matches 'SEC-' IDs but deterministic findings are namespaced 'DET-'

