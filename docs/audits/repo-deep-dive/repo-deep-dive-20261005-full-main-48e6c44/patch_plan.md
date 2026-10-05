# Patch plan

## EXEC-P1-001 - publish_audit release gate can never return NO-GO for a P0

Share one gate function; add a P0 test asserting NO-GO; regenerate affected archived focused runs.

## AI-P2-001 - emit accepts findings with no evidence or citation requirement

Require a non-empty evidence list (or an explicit Unknown marker) in emit for P0/P1 at minimum.

## API-P2-001 - Lab API has no rate limiting or request-body error signalling

Return 400 on invalid JSON and add a simple concurrency/rate guard.

## BP-P2-001 - Required checks and PR/review rules do not match the documented gates

Add the pack CI contexts to the ruleset required checks and a pull_request rule with >=1 review.

## BP-P2-002 - Required check 'Lab preflight / lab' is unobtainable for fork PRs

Make the required context a fork-safe pack check and run the lab check only on same-repo PRs/dispatch.

## CHAIN-P2-001 - Broken secret ignores + argv lab token + root lab API compose into an escalation path

Fix the ignore patterns, keep the token out of argv, bind to the overlay only, and run the API as an unprivileged user with a per-job allowlist.

## CI-P2-001 - Required lab-preflight check cannot pass on fork pull requests

Skip the lab job (with a neutral/annotation) on `github.event.pull_request.head.repo.fork`, or split the required check from the lab-dependent one.

## CI-P2-002 - CI does not run shellcheck/actionlint on the pack's own shell/yaml despite shipping the scanners

Add a pack CI job that runs shellcheck on tools/**/*.sh and actionlint on .github/workflows/*.yml.

## DET-P2-001 - [PORT] 2 tracked shell script(s) without the exec bit

TBD

## DOC-P2-001 - README is stale: run count and tool/doc inventories omit current files

Regenerate the layout/counts (or generate the table) as part of the changelog checklist.

## FEAT-P2-001 - Full-domain runs omit the master runner's required companion artifacts

Have aggregate render each companion (even as an explicit N/A stub) or add them to the run schema and `check_run.sh`.

## FEAT-P2-002 - publish_audit relabels any run as a focused security/supply-chain/CI pass

Derive profile/prompts/report name from the run's `audit_manifest.json` mode instead of hardcoding the focused set.

## FINAL-P2-001 - Release gate ignores coverage and completeness

Fail or downgrade the gate when any selected domain has not emitted, and record coverage in the gate basis.

## FINAL-P2-002 - Registers are generated from report tables, so ID drift is possible across reruns

Write findings.json and the registers from the same in-memory list, and use findings.json as the source of truth.

## HYGIENE-P2-001 - .gitignore is corrupted with intra-word spaces and an invalid inline comment

Restore the intended patterns and add a `git check-ignore` assertion to CI.

## INFRA-P2-001 - Lab IAC has no drift detection or locked toolchain

Commit the lock file and add a scheduled read-only plan/check job against the lab.

## OBS-P2-001 - Run-freshness signal is documentation-only (no scheduled check or alert)

Add a scheduled job that runs the freshness check and alerts (reuse the lab ntfy workflow pattern).

## REL-P2-001 - Full-domain runs generate no release notes or changelog draft

Have aggregate emit both drafts and make the pack changelog entry part of the completion checklist.

## SC-P2-001 - Infrastructure toolchain is pinned only to lower bounds

Commit `.terraform.lock.hcl` and pin Ansible collections to exact versions committed alongside requirements.

## SEC-P2-001 - Workflows interpolate SSH secrets directly into run scripts

Pass the secret via `env:` (e.g. `SSH_KEY: ${{ secrets... }}`) and reference `"$SSH_KEY"` in the script.

## SEC-P2-002 - Lab API /sync ignores the supplied token when the workspace already exists

Apply the same `-c http.extraheader=...` (or `GIT_CONFIG_*`) to the fetch, and fail when the requested ref does not resolve.

## SECRET-P2-001 - WireGuard/lab secret ignore patterns in .gitignore are corrupted

Restore the intended patterns ('*.swp', 'lab-audit-*.conf', '*.wgkey', 'deterministic-out/') and add a CI check that `git check-ignore` matches a sample secret file.

## TEST-P2-001 - The publish release-gate logic is untested and never returns NO-GO

Make publish_audit reuse the shared gate function and add a P0 test asserting NO-GO.

## ACM-P3-001 - No consolidated access-control matrix artifact is produced

Generate access_control_matrix.md from the ruleset/CODEOWNERS/workflow permissions during aggregate.

## AI-P3-001 - run --agent-cmd executes a shell template with unvalidated substitutions

Pass arguments as an argv list instead of a formatted shell string.

## API-P3-001 - Lab API contract is documented in prose only (no schema)

Add a small JSON schema or shared constants module used by both server and client.

## ARCH-P3-001 - Lab job API server and lab-vpn scripts have no automated test in CI

Add a unit test around Handler dispatch with a temp ROOT, or a lab smoke test in the preflight.

## BP-P3-001 - Ruleset bypass actors permanently include the repository role and a deploy key

Scope bypass to the digest deploy key only, and record owner-authorized exceptions.

## DET-P3-001 - [DEP] trivy not installed (dependency vuln scan skipped)

TBD

## DOC-P3-001 - PR #49 (full-domain driver) has no CHANGELOG entry

Add the full-domain driver entry and a version note.

## DR-P3-001 - No backup/restore drill plan artifact or tested lab restore

Add the drill plan (git-as-source-of-truth + lab rebuild) and an annual restore test.

## EVOL-P3-001 - Roadmap robustness items 1-6 remain open

Close items 1-3 (deterministic LF digest, run schema, idempotent publish) first.

## EXEC-P3-001 - Executive summary lists covered domains but not uncovered/N-A domains

Add a coverage line (emitted/NA/pending) to the summary.

## HYGIENE-P3-001 - Two tracked shell scripts lack the executable bit

`git update-index --chmod=+x` both files and add a hygiene check.

## INFRA-P3-001 - Example inventory is the only committed inventory

Document the variable source (env/secret) and validate the example against the Terraform outputs.

## INV-P3-001 - Inventory tool does not model this pack's own artifact families

Add prompts/lenses/runs sections to `repo_inventory.py` output.

## IR-P3-001 - No incident tabletop scenarios artifact

Author scenarios (leaked token, bad digest, runner down) with expected detections/actions.

## OBS-P3-001 - Lab API emits request lines only; no health/metrics for job durations or failures

Log auth/job results with duration and expose counters.

## ORCH-P3-001 - Full-domain driver runs the orchestrator as a flat parallel domain

Either implement wave ordering/verification gates in `full_domain.py` or document explicitly that 00 is advisory when the driver is used.

## PERF-P3-001 - Full-domain passes are token-heavy with no inventory/deterministic caching

Cache per-repo inventory/deterministic output and feed it into the domain subagents.

## RES-P3-001 - Lab job API is a single point of failure for lab-dependent work

Document a local MODE=local fallback per audit, or add a second runner/queue.

## SBOM-P3-001 - No SBOM/provenance artifact or release manifest is published for the pack itself

Emit a CycloneDX SBOM and a signed release manifest per tagged pack release.

## SC-P3-001 - gitleaks allowlist can mask real 40-hex OSQUERY keys and a token-shaped string

Scope allowlists to the exact file/line of the archived evidence rather than a global regex/literal.

## SEC-P3-001 - Lab API token passed via process argv and server bound to all interfaces as root

Pass credentials through the environment or a temporary askpass, bind to the overlay interface, and run as a dedicated non-root user.

## TEST-P3-001 - run_toolchain writes CSV to a fixed shared temp path

Use tempfile.mkdtemp()/NamedTemporaryFile for the CSV.

## TEST-P3-002 - The documented exec-bit invariant is not tested

Add a lint/test check over `git ls-files -s '*.sh'`.

## USE-P3-001 - The end-to-end pass remains ~8 manual phases

Implement the documented `tools/post_audit.py run` orchestrator.

