# Follow-up register

Run: `repo-deep-dive-20261005-full-main-48e6c44` · Target: `repo-deep-dive` @ `48e6c44` · Profile: base

Register mirrored 1:1 with `risk_register.md` so `tools/check_run.sh` passes.

| Finding | Severity | Title | Owner | Target | Status | Post-audit note |
|---|---|---|---|---|---|---|
| EXEC-P1-001 | P1 | publish_audit release gate can never return NO-GO for a P0 | @owner | EXEC | verified-fixed | merged repo-deep-dive PR #58 commit 1e2a0869c95d23ac79c7a0f6b54053223e22e7d5 (single shared lib_findings.compute_gate; a P0 yields NO-GO) |
| AI-P2-001 | P2 | emit accepts findings with no evidence or citation requirement | @owner | AI | open |  |
| API-P2-001 | P2 | Lab API has no rate limiting or request-body error signalling | @owner | API | open |  |
| BP-P2-001 | P2 | Required checks and PR/review rules do not match the documented gates | @owner | BP | open |  |
| BP-P2-002 | P2 | Required check 'Lab preflight / lab' is unobtainable for fork PRs | @owner | BP | open |  |
| CHAIN-P2-001 | P2 | Broken secret ignores + argv lab token + root lab API compose into an escalation path | @owner | CHAIN | open |  |
| CI-P2-001 | P2 | Required lab-preflight check cannot pass on fork pull requests | @owner | CI | open |  |
| CI-P2-002 | P2 | CI does not run shellcheck/actionlint on the pack's own shell/yaml despite shipping the scanners | @owner | CI | open |  |
| DET-P2-002 | P2 | [PORT] 2 tracked shell script(s) without the exec bit | @owner | DET | open |  |
| DOC-P2-001 | P2 | README is stale: run count and tool/doc inventories omit current files | @owner | DOC | open |  |
| FEAT-P2-001 | P2 | Full-domain runs omit the master runner's required companion artifacts | @owner | FEAT | open |  |
| FEAT-P2-002 | P2 | publish_audit relabels any run as a focused security/supply-chain/CI pass | @owner | FEAT | open |  |
| FINAL-P2-001 | P2 | Release gate ignores coverage and completeness | @owner | FINAL | open |  |
| FINAL-P2-002 | P2 | Registers are generated from report tables, so ID drift is possible across reruns | @owner | FINAL | open |  |
| HYGIENE-P2-001 | P2 | .gitignore is corrupted with intra-word spaces and an invalid inline comment | @owner | HYGIENE | verified-fixed | merged repo-deep-dive PR #58 commit 1e2a0869c95d23ac79c7a0f6b54053223e22e7d5 (.gitignore patterns restored; lint_pack asserts git check-ignore matches sample secrets) |
| INFRA-P2-001 | P2 | Lab IAC has no drift detection or locked toolchain | @owner | INFRA | open |  |
| OBS-P2-001 | P2 | Run-freshness signal is documentation-only (no scheduled check or alert) | @owner | OBS | open |  |
| REL-P2-001 | P2 | Full-domain runs generate no release notes or changelog draft | @owner | REL | open |  |
| SC-P2-001 | P2 | Infrastructure toolchain is pinned only to lower bounds | @owner | SC | open |  |
| SEC-P2-001 | P2 | Workflows interpolate SSH secrets directly into run scripts | @owner | SEC | verified-fixed | merged repo-deep-dive PR #58 commit 1e2a0869c95d23ac79c7a0f6b54053223e22e7d5 (SSH key passed via env: and referenced as "$LAB_ENDPOINT_SSH_KEY" in lab workflows) |
| SEC-P2-002 | P2 | Lab API /sync ignores the supplied token when the workspace already exists | @owner | SEC | verified-fixed | merged repo-deep-dive PR #58 commit 1e2a0869c95d23ac79c7a0f6b54053223e22e7d5 (lab /sync applies the auth header to the existing-workspace fetch; unresolvable ref returns 404; redeployed + verified) |
| SECRET-P2-001 | P2 | WireGuard/lab secret ignore patterns in .gitignore are corrupted | @owner | SECRET | verified-fixed | merged repo-deep-dive PR #58 commit 1e2a0869c95d23ac79c7a0f6b54053223e22e7d5 (.gitignore restores *.swp, lab-audit-*.conf, *.wgkey, deterministic-out/ and tfstate ignores) |
| TEST-P2-001 | P2 | The publish release-gate logic is untested and never returns NO-GO | @owner | TEST | verified-fixed | merged repo-deep-dive PR #58 commit 1e2a0869c95d23ac79c7a0f6b54053223e22e7d5 (PublishGateTest/ComputeGateTest assert a P0 yields NO-GO; gate now returns NO-GO) |
| ACM-P3-001 | P3 | No consolidated access-control matrix artifact is produced | @owner | ACM | open |  |
| AI-P3-001 | P3 | run --agent-cmd executes a shell template with unvalidated substitutions | @owner | AI | open |  |
| API-P3-001 | P3 | Lab API contract is documented in prose only (no schema) | @owner | API | open |  |
| ARCH-P3-001 | P3 | Lab job API server and lab-vpn scripts have no automated test in CI | @owner | ARCH | open |  |
| BP-P3-001 | P3 | Ruleset bypass actors permanently include the repository role and a deploy key | @owner | BP | open |  |
| DET-P3-001 | P3 | [DEP] trivy not installed (dependency vuln scan skipped) | @owner | DET | open |  |
| DOC-P3-001 | P3 | PR #49 (full-domain driver) has no CHANGELOG entry | @owner | DOC | open |  |
| DR-P3-001 | P3 | No backup/restore drill plan artifact or tested lab restore | @owner | DR | open |  |
| EVOL-P3-001 | P3 | Roadmap robustness items 1-6 remain open | @owner | EVOL | open |  |
| EXEC-P3-001 | P3 | Executive summary lists covered domains but not uncovered/N-A domains | @owner | EXEC | open |  |
| HYGIENE-P3-001 | P3 | Two tracked shell scripts lack the executable bit | @owner | HYGIENE | open |  |
| INFRA-P3-001 | P3 | Example inventory is the only committed inventory | @owner | INFRA | open |  |
| INV-P3-001 | P3 | Inventory tool does not model this pack's own artifact families | @owner | INV | open |  |
| IR-P3-001 | P3 | No incident tabletop scenarios artifact | @owner | IR | open |  |
| OBS-P3-001 | P3 | Lab API emits request lines only; no health/metrics for job durations or failures | @owner | OBS | open |  |
| ORCH-P3-001 | P3 | Full-domain driver runs the orchestrator as a flat parallel domain | @owner | ORCH | open |  |
| PERF-P3-001 | P3 | Full-domain passes are token-heavy with no inventory/deterministic caching | @owner | PERF | open |  |
| RES-P3-001 | P3 | Lab job API is a single point of failure for lab-dependent work | @owner | RES | open |  |
| SBOM-P3-001 | P3 | No SBOM/provenance artifact or release manifest is published for the pack itself | @owner | SBOM | open |  |
| SC-P3-001 | P3 | gitleaks allowlist can mask real 40-hex OSQUERY keys and a token-shaped string | @owner | SC | open |  |
| SEC-P3-001 | P3 | Lab API token passed via process argv and server bound to all interfaces as root | @owner | SEC | open |  |
| TEST-P3-001 | P3 | run_toolchain writes CSV to a fixed shared temp path | @owner | TEST | open |  |
| TEST-P3-002 | P3 | The documented exec-bit invariant is not tested | @owner | TEST | open |  |
| USE-P3-001 | P3 | The end-to-end pass remains ~8 manual phases | @owner | USE | open |  |
