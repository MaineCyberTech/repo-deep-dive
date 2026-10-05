# Follow-up register

| Finding | Severity | Title | Owner | Target | Status | Note |
|---|---|---|---|---|---|---|
| EXEC-P1-001 | P1 | publish_audit release gate can never return NO-GO for a P0 | @owner | EXEC | open | Share one gate function; add a P0 test asserting NO-GO; regenerate affected archived focused runs. |
| AI-P2-001 | P2 | emit accepts findings with no evidence or citation requirement | @owner | AI | open | Require a non-empty evidence list (or an explicit Unknown marker) in emit for P0/P1 at minimum. |
| API-P2-001 | P2 | Lab API has no rate limiting or request-body error signalling | @owner | API | open | Return 400 on invalid JSON and add a simple concurrency/rate guard. |
| BP-P2-001 | P2 | Required checks and PR/review rules do not match the documented gates | @owner | BP | open | Add the pack CI contexts to the ruleset required checks and a pull_request rule with >=1 review. |
| BP-P2-002 | P2 | Required check 'Lab preflight / lab' is unobtainable for fork PRs | @owner | BP | open | Make the required context a fork-safe pack check and run the lab check only on same-repo PRs/dispatch. |
| CHAIN-P2-001 | P2 | Broken secret ignores + argv lab token + root lab API compose into an escalation path | @owner | CHAIN | open | Fix the ignore patterns, keep the token out of argv, bind to the overlay only, and run the API as an unprivileged user w |
| CI-P2-001 | P2 | Required lab-preflight check cannot pass on fork pull requests | @owner | CI | open | Skip the lab job (with a neutral/annotation) on `github.event.pull_request.head.repo.fork`, or split the required check  |
| CI-P2-002 | P2 | CI does not run shellcheck/actionlint on the pack's own shell/yaml despite shipping the scanners | @owner | CI | open | Add a pack CI job that runs shellcheck on tools/**/*.sh and actionlint on .github/workflows/*.yml. |
| DET-P2-001 | P2 | [PORT] 2 tracked shell script(s) without the exec bit | @owner | DET | open | remediation |
| DOC-P2-001 | P2 | README is stale: run count and tool/doc inventories omit current files | @owner | DOC | open | Regenerate the layout/counts (or generate the table) as part of the changelog checklist. |
| FEAT-P2-001 | P2 | Full-domain runs omit the master runner's required companion artifacts | @owner | FEAT | open | Have aggregate render each companion (even as an explicit N/A stub) or add them to the run schema and `check_run.sh`. |
| FEAT-P2-002 | P2 | publish_audit relabels any run as a focused security/supply-chain/CI pass | @owner | FEAT | open | Derive profile/prompts/report name from the run's `audit_manifest.json` mode instead of hardcoding the focused set. |
| FINAL-P2-001 | P2 | Release gate ignores coverage and completeness | @owner | FINAL | open | Fail or downgrade the gate when any selected domain has not emitted, and record coverage in the gate basis. |
| FINAL-P2-002 | P2 | Registers are generated from report tables, so ID drift is possible across reruns | @owner | FINAL | open | Write findings.json and the registers from the same in-memory list, and use findings.json as the source of truth. |
| HYGIENE-P2-001 | P2 | .gitignore is corrupted with intra-word spaces and an invalid inline comment | @owner | HYGIENE | open | Restore the intended patterns and add a `git check-ignore` assertion to CI. |
| INFRA-P2-001 | P2 | Lab IAC has no drift detection or locked toolchain | @owner | INFRA | open | Commit the lock file and add a scheduled read-only plan/check job against the lab. |
| OBS-P2-001 | P2 | Run-freshness signal is documentation-only (no scheduled check or alert) | @owner | OBS | open | Add a scheduled job that runs the freshness check and alerts (reuse the lab ntfy workflow pattern). |
| REL-P2-001 | P2 | Full-domain runs generate no release notes or changelog draft | @owner | REL | open | Have aggregate emit both drafts and make the pack changelog entry part of the completion checklist. |
| SC-P2-001 | P2 | Infrastructure toolchain is pinned only to lower bounds | @owner | SC | open | Commit `.terraform.lock.hcl` and pin Ansible collections to exact versions committed alongside requirements. |
| SEC-P2-001 | P2 | Workflows interpolate SSH secrets directly into run scripts | @owner | SEC | open | Pass the secret via `env:` (e.g. `SSH_KEY: ${{ secrets... }}`) and reference `"$SSH_KEY"` in the script. |
| SEC-P2-002 | P2 | Lab API /sync ignores the supplied token when the workspace already exists | @owner | SEC | open | Apply the same `-c http.extraheader=...` (or `GIT_CONFIG_*`) to the fetch, and fail when the requested ref does not reso |
| SECRET-P2-001 | P2 | WireGuard/lab secret ignore patterns in .gitignore are corrupted | @owner | SECRET | open | Restore the intended patterns ('*.swp', 'lab-audit-*.conf', '*.wgkey', 'deterministic-out/') and add a CI check that `gi |
| TEST-P2-001 | P2 | The publish release-gate logic is untested and never returns NO-GO | @owner | TEST | open | Make publish_audit reuse the shared gate function and add a P0 test asserting NO-GO. |
| ACM-P3-001 | P3 | No consolidated access-control matrix artifact is produced | @owner | ACM | open | Generate access_control_matrix.md from the ruleset/CODEOWNERS/workflow permissions during aggregate. |
| AI-P3-001 | P3 | run --agent-cmd executes a shell template with unvalidated substitutions | @owner | AI | open | Pass arguments as an argv list instead of a formatted shell string. |
| API-P3-001 | P3 | Lab API contract is documented in prose only (no schema) | @owner | API | open | Add a small JSON schema or shared constants module used by both server and client. |
| ARCH-P3-001 | P3 | Lab job API server and lab-vpn scripts have no automated test in CI | @owner | ARCH | open | Add a unit test around Handler dispatch with a temp ROOT, or a lab smoke test in the preflight. |
| BP-P3-001 | P3 | Ruleset bypass actors permanently include the repository role and a deploy key | @owner | BP | open | Scope bypass to the digest deploy key only, and record owner-authorized exceptions. |
| DET-P3-001 | P3 | [DEP] trivy not installed (dependency vuln scan skipped) | @owner | DET | open | remediation |
| DOC-P3-001 | P3 | PR #49 (full-domain driver) has no CHANGELOG entry | @owner | DOC | open | Add the full-domain driver entry and a version note. |
| DR-P3-001 | P3 | No backup/restore drill plan artifact or tested lab restore | @owner | DR | open | Add the drill plan (git-as-source-of-truth + lab rebuild) and an annual restore test. |
| EVOL-P3-001 | P3 | Roadmap robustness items 1-6 remain open | @owner | EVOL | open | Close items 1-3 (deterministic LF digest, run schema, idempotent publish) first. |
| EXEC-P3-001 | P3 | Executive summary lists covered domains but not uncovered/N-A domains | @owner | EXEC | open | Add a coverage line (emitted/NA/pending) to the summary. |
| HYGIENE-P3-001 | P3 | Two tracked shell scripts lack the executable bit | @owner | HYGIENE | open | `git update-index --chmod=+x` both files and add a hygiene check. |
| INFRA-P3-001 | P3 | Example inventory is the only committed inventory | @owner | INFRA | open | Document the variable source (env/secret) and validate the example against the Terraform outputs. |
| INV-P3-001 | P3 | Inventory tool does not model this pack's own artifact families | @owner | INV | open | Add prompts/lenses/runs sections to `repo_inventory.py` output. |
| IR-P3-001 | P3 | No incident tabletop scenarios artifact | @owner | IR | open | Author scenarios (leaked token, bad digest, runner down) with expected detections/actions. |
| OBS-P3-001 | P3 | Lab API emits request lines only; no health/metrics for job durations or failures | @owner | OBS | open | Log auth/job results with duration and expose counters. |
| ORCH-P3-001 | P3 | Full-domain driver runs the orchestrator as a flat parallel domain | @owner | ORCH | open | Either implement wave ordering/verification gates in `full_domain.py` or document explicitly that 00 is advisory when th |
| PERF-P3-001 | P3 | Full-domain passes are token-heavy with no inventory/deterministic caching | @owner | PERF | open | Cache per-repo inventory/deterministic output and feed it into the domain subagents. |
| RES-P3-001 | P3 | Lab job API is a single point of failure for lab-dependent work | @owner | RES | open | Document a local MODE=local fallback per audit, or add a second runner/queue. |
| SBOM-P3-001 | P3 | No SBOM/provenance artifact or release manifest is published for the pack itself | @owner | SBOM | open | Emit a CycloneDX SBOM and a signed release manifest per tagged pack release. |
| SC-P3-001 | P3 | gitleaks allowlist can mask real 40-hex OSQUERY keys and a token-shaped string | @owner | SC | open | Scope allowlists to the exact file/line of the archived evidence rather than a global regex/literal. |
| SEC-P3-001 | P3 | Lab API token passed via process argv and server bound to all interfaces as root | @owner | SEC | open | Pass credentials through the environment or a temporary askpass, bind to the overlay interface, and run as a dedicated n |
| TEST-P3-001 | P3 | run_toolchain writes CSV to a fixed shared temp path | @owner | TEST | open | Use tempfile.mkdtemp()/NamedTemporaryFile for the CSV. |
| TEST-P3-002 | P3 | The documented exec-bit invariant is not tested | @owner | TEST | open | Add a lint/test check over `git ls-files -s '*.sh'`. |
| USE-P3-001 | P3 | The end-to-end pass remains ~8 manual phases | @owner | USE | open | Implement the documented `tools/post_audit.py run` orchestrator. |
