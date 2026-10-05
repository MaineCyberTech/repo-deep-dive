# Focused security / supply-chain / CI deep-dive - repo-deep-dive

## Findings

| ID | Severity | Title | Report |
|---|---|---|---|
| EXEC-P1-001 | P1 | publish_audit release gate can never return NO-GO for a P0 | lens_focused_security_supply_chain_ci.md |
| AI-P2-001 | P2 | emit accepts findings with no evidence or citation requirement | lens_focused_security_supply_chain_ci.md |
| API-P2-001 | P2 | Lab API has no rate limiting or request-body error signalling | lens_focused_security_supply_chain_ci.md |
| BP-P2-001 | P2 | Required checks and PR/review rules do not match the documented gates | lens_focused_security_supply_chain_ci.md |
| BP-P2-002 | P2 | Required check 'Lab preflight / lab' is unobtainable for fork PRs | lens_focused_security_supply_chain_ci.md |
| CHAIN-P2-001 | P2 | Broken secret ignores + argv lab token + root lab API compose into an escalation path | lens_focused_security_supply_chain_ci.md |
| CI-P2-001 | P2 | Required lab-preflight check cannot pass on fork pull requests | lens_focused_security_supply_chain_ci.md |
| CI-P2-002 | P2 | CI does not run shellcheck/actionlint on the pack's own shell/yaml despite shipping the scanners | lens_focused_security_supply_chain_ci.md |
| DET-P2-001 | P2 | [PORT] 2 tracked shell script(s) without the exec bit | lens_focused_security_supply_chain_ci.md |
| DOC-P2-001 | P2 | README is stale: run count and tool/doc inventories omit current files | lens_focused_security_supply_chain_ci.md |
| FEAT-P2-001 | P2 | Full-domain runs omit the master runner's required companion artifacts | lens_focused_security_supply_chain_ci.md |
| FEAT-P2-002 | P2 | publish_audit relabels any run as a focused security/supply-chain/CI pass | lens_focused_security_supply_chain_ci.md |
| FINAL-P2-001 | P2 | Release gate ignores coverage and completeness | lens_focused_security_supply_chain_ci.md |
| FINAL-P2-002 | P2 | Registers are generated from report tables, so ID drift is possible across reruns | lens_focused_security_supply_chain_ci.md |
| HYGIENE-P2-001 | P2 | .gitignore is corrupted with intra-word spaces and an invalid inline comment | lens_focused_security_supply_chain_ci.md |
| INFRA-P2-001 | P2 | Lab IAC has no drift detection or locked toolchain | lens_focused_security_supply_chain_ci.md |
| OBS-P2-001 | P2 | Run-freshness signal is documentation-only (no scheduled check or alert) | lens_focused_security_supply_chain_ci.md |
| REL-P2-001 | P2 | Full-domain runs generate no release notes or changelog draft | lens_focused_security_supply_chain_ci.md |
| SC-P2-001 | P2 | Infrastructure toolchain is pinned only to lower bounds | lens_focused_security_supply_chain_ci.md |
| SEC-P2-001 | P2 | Workflows interpolate SSH secrets directly into run scripts | lens_focused_security_supply_chain_ci.md |
| SEC-P2-002 | P2 | Lab API /sync ignores the supplied token when the workspace already exists | lens_focused_security_supply_chain_ci.md |
| SECRET-P2-001 | P2 | WireGuard/lab secret ignore patterns in .gitignore are corrupted | lens_focused_security_supply_chain_ci.md |
| TEST-P2-001 | P2 | The publish release-gate logic is untested and never returns NO-GO | lens_focused_security_supply_chain_ci.md |
| ACM-P3-001 | P3 | No consolidated access-control matrix artifact is produced | lens_focused_security_supply_chain_ci.md |
| AI-P3-001 | P3 | run --agent-cmd executes a shell template with unvalidated substitutions | lens_focused_security_supply_chain_ci.md |
| API-P3-001 | P3 | Lab API contract is documented in prose only (no schema) | lens_focused_security_supply_chain_ci.md |
| ARCH-P3-001 | P3 | Lab job API server and lab-vpn scripts have no automated test in CI | lens_focused_security_supply_chain_ci.md |
| BP-P3-001 | P3 | Ruleset bypass actors permanently include the repository role and a deploy key | lens_focused_security_supply_chain_ci.md |
| DET-P3-001 | P3 | [DEP] trivy not installed (dependency vuln scan skipped) | lens_focused_security_supply_chain_ci.md |
| DOC-P3-001 | P3 | PR #49 (full-domain driver) has no CHANGELOG entry | lens_focused_security_supply_chain_ci.md |
| DR-P3-001 | P3 | No backup/restore drill plan artifact or tested lab restore | lens_focused_security_supply_chain_ci.md |
| EVOL-P3-001 | P3 | Roadmap robustness items 1-6 remain open | lens_focused_security_supply_chain_ci.md |
| EXEC-P3-001 | P3 | Executive summary lists covered domains but not uncovered/N-A domains | lens_focused_security_supply_chain_ci.md |
| HYGIENE-P3-001 | P3 | Two tracked shell scripts lack the executable bit | lens_focused_security_supply_chain_ci.md |
| INFRA-P3-001 | P3 | Example inventory is the only committed inventory | lens_focused_security_supply_chain_ci.md |
| INV-P3-001 | P3 | Inventory tool does not model this pack's own artifact families | lens_focused_security_supply_chain_ci.md |
| IR-P3-001 | P3 | No incident tabletop scenarios artifact | lens_focused_security_supply_chain_ci.md |
| OBS-P3-001 | P3 | Lab API emits request lines only; no health/metrics for job durations or failures | lens_focused_security_supply_chain_ci.md |
| ORCH-P3-001 | P3 | Full-domain driver runs the orchestrator as a flat parallel domain | lens_focused_security_supply_chain_ci.md |
| PERF-P3-001 | P3 | Full-domain passes are token-heavy with no inventory/deterministic caching | lens_focused_security_supply_chain_ci.md |
| RES-P3-001 | P3 | Lab job API is a single point of failure for lab-dependent work | lens_focused_security_supply_chain_ci.md |
| SBOM-P3-001 | P3 | No SBOM/provenance artifact or release manifest is published for the pack itself | lens_focused_security_supply_chain_ci.md |
| SC-P3-001 | P3 | gitleaks allowlist can mask real 40-hex OSQUERY keys and a token-shaped string | lens_focused_security_supply_chain_ci.md |
| SEC-P3-001 | P3 | Lab API token passed via process argv and server bound to all interfaces as root | lens_focused_security_supply_chain_ci.md |
| TEST-P3-001 | P3 | run_toolchain writes CSV to a fixed shared temp path | lens_focused_security_supply_chain_ci.md |
| TEST-P3-002 | P3 | The documented exec-bit invariant is not tested | lens_focused_security_supply_chain_ci.md |
| USE-P3-001 | P3 | The end-to-end pass remains ~8 manual phases | lens_focused_security_supply_chain_ci.md |

---

# repo-deep-dive-20261005-full-main-48e6c44
