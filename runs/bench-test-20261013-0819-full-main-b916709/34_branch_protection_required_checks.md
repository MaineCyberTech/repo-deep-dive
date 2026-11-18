# 34_branch_protection_required_checks — Prompt 34 - Branch Protection and Required Checks Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `34_branch_protection_required_checks.md` (area BP, prompt)

## Verification Performed

# 34_branch_protection_required_checks - 34_branch_protection_required_checks.md

Domain subagent `34_branch_protection_required_checks` (area BP), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - No test/CI workflow exists, so no required status check can gate merges to main** (confidence: High)
  - `.github/workflows/ contains only build-app.yml, build-iso.yml and release.yml (git ls-files .github) - all three are build/release jobs; none runs the test suite`
  - `tests/run_all.py:1 - the stdlib suite exists and is invoked only by hand; no workflow references it (grep for 'pytest|test|unittest' in .github/workflows/*.yml returns no job step)`
  - `AGENTS.md:164-174 - 'Testing - required before every commit' is an honor-system instruction ('Never commit with a failing suite'), not an enforced gate`
  - `docs/audits/.../20261007-1731-main-4ecee97/patch_plan.md:25 - a prior audit already asked to 'make the workflow a required status check on main'; it is still absent`
  - Impact: main carries a public toolkit that downloads and executes third-party binaries (LibreHardwareMonitor/nvfancontrol) and a control plane exposing remote exec/shell/shutdown commands; every merge lands with zero automated lint/compile/test/secret-scan verification, so a regression or malicious change reaches the default branch and the auto-release with no machine check.
  - Recommendation: Add a pinned CI workflow (`.github/workflows/ci.yml`) that runs `python tests/run_all.py`, `python -m py_compile bench/*.py server/*.py` and `bash -n` on the shell scripts, then enable it (and any PSScriptAnalyzer/gitleaks jobs) as required status checks on the protected main branch.
- **P1 - Release workflow writes directly to main and cuts tags with no approval or documented bypass** (confidence: High)
  - `.github/workflows/release.yml:22-23 - triggers on `push` to `branches: [main]``
  - `.github/workflows/release.yml:25-26 - `permissions: contents: write``
  - `.github/workflows/release.yml:81-94 - rewrites VERSION, commits as 'bench-test release bot' and runs `git push` straight to main`
  - `.github/workflows/release.yml:96-107 - creates an annotated tag and runs `git push origin "$tag"``
  - `.github/workflows/release.yml:14-21,97 - workflow_dispatch with bump_kind minor|patch|major, no environment/approval gate`
  - `No `environment:` key and no break-glass/hotfix procedure anywhere in the tree (grep for 'environment:' in workflows, 'hotfix|break-glass|bypass' in tracked docs)`
  - Impact: Automation commits to and tags the default branch on every qualifying push without human review. If protected-branch rules with required reviews are (or become) enabled, this job cannot push unless an undocumented bypass actor is granted; if rules are absent, every feat/fix merge silently publishes a release and public artifacts. Either way the actual branch policy is unknowable and untestable, and there is no defined emergency-change path.
  - Recommendation: Decide the branch model explicitly and document it (main/develop/release/hotfix + break-glass). Move the release mutation behind a protected `environment: release` with required reviewers (or grant a narrowly-scoped, audited bypass actor), and document how the automated VERSION commit reconciles with required reviews.
- **P2 - Secret-bearing public-release workflows run with no environment approval gate** (confidence: High)
  - `.github/workflows/build-iso.yml:62-82 - writes secrets.BENCH_UPLOAD_CONF and secrets.BENCH_AGENT_CONF into live/private/*.conf and bakes them into the published ISO`
  - `.github/workflows/build-app.yml:57-64 - bakes secrets.BENCH_AGENT_CONF into the PyInstaller bundles published as public app-<n> releases`
  - `No `environment:` key on any job in any workflow (grep 'environment:' returns nothing); triggers are push-to-main and unauthenticated workflow_dispatch`
  - `README.md:359-363 and AGENTS.md:176-186 - the repo and ISO releases are public, so any baked token is world-readable`
  - Impact: Anyone who can push to main, or click Run workflow, can cause control-plane/upload credentials to be embedded into world-readable release artifacts, with no reviewer sign-off or protected-environment approval before publication.
  - Recommendation: Attach a protected GitHub `environment` (required reviewers + deployment branch/tag rules) to the release/attach jobs in build-iso.yml and build-app.yml so secret exposure requires approval; prefer short-lived, rotatable, least-privilege tokens and consider not baking them for public releases at all.
- **P2 - No Dependabot and all third-party actions are referenced by mutable tags** (confidence: High)
  - `No .github/dependabot.yml (git ls-files .github returns only the three workflow files)`
  - `Mutable refs in use: .github/workflows/build-app.yml:39,41,87,96,100,104 and build-iso.yml:56,116 and release.yml:36 (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, `softprops/action-gh-release@v2`)`
  - `docs/audits/.../patch_plan.md:25 - the prior audit's request to add Dependabot and pin actions remains unimplemented`
  - Impact: A compromised or retagged upstream action can execute in a job that holds `contents: write` and release secrets; stale/broken action versions are never surfaced as update PRs, and there is no automated dependency-update review trail.
  - Recommendation: Add `.github/dependabot.yml` (github-actions ecosystem, weekly) and pin every `uses:` to a full commit SHA with a Dependabot-maintained version comment; make the Dependabot PRs pass the CI check added for the P1 no-CI finding.
- **P2 - No documented branch/release/hotfix model or break-glass process** (confidence: High)
  - `Tracked docs are only README.md, AGENTS.md and docs/{CONTROL_PLANE,DATA,FUTURE_WORK,METHODOLOGY,PHASE_TIMINGS}.md (git ls-files '*.md' excluding audits)`
  - `grep for 'hotfix|break-glass|bypass|branch protection|required check|review|approv' across tracked non-audit markdown returns no policy - the closest is AGENTS.md:279-285 'Do not' and README.md release-tag prose`
  - `release.yml:1-12 documents how tagging works mechanically but states no review, branch or emergency-change policy`
  - Impact: Required special checks ('include main/develop/release/hotfix rules', 'define break-glass process') cannot be satisfied: reviewers and future agents have no reference for what a protected branch requires, who may bypass it, or how an urgent fix is shipped. Branch protection therefore cannot be audited against a documented process.
  - Recommendation: Add a short docs/BRANCHING.md (or CONTRIBUTING.md) that names the branches (main/release/hotfix or a documented main-only model), the required checks and review count, tag/release authority, and a break-glass procedure (who may merge/tag without review, how it is recorded and back-filled).
- **P3 - No CODEOWNERS file** (confidence: High)
  - `git ls-files for CODEOWNERS returns nothing; no CODEOWNERS anywhere in the tree`
  - `LICENSE/README declare the material proprietary while the repo is public (README.md:365-367; prior GOV-P3-007)`
  - Impact: There is no ownership metadata to drive review routing or required code-owner review, so sensitive paths (server/benchd.py remote-exec, .github/workflows/, live/private credentials handling) have no enforced owner review.
  - Recommendation: Add `.github/CODEOWNERS` assigning the workflow/CI files, server/benchd.py and packaging/release paths to maintainers, and enable 'Require review from Code Owners' in the branch rules alongside the required checks.
- **P3 - No pull-request template or contributing guide** (confidence: High)
  - `No .github/PULL_REQUEST_TEMPLATE.md or .github/PULL_REQUEST_TEMPLATE/ and no .github/ISSUE_TEMPLATE/ (git ls-files .github returns only the three workflows)`
  - `No CONTRIBUTING.md (git ls-files root shows only .gitattributes, .gitignore, AGENTS.md, LICENSE, README.md, VERSION, bench-*.cmd)`
  - Impact: Contributors get no checklist for the repo's load-bearing constraints (preset parity across GUI/TUI/web, LF + exec bits, no secrets, run tests/run_all.py), which AGENTS.md:279-285 says must hold before pushing - weakening any review gate that is later enabled.
  - Recommendation: Add `.github/PULL_REQUEST_TEMPLATE.md` listing the test command, the AGENTS.md ground rules, and a 'no secrets / no CRLF .sh' confirmation; reference it from a short CONTRIBUTING.md.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| BP-P1-001 | P1 | No test/CI workflow exists, so no required status check can gate merges to main |
| BP-P1-002 | P1 | Release workflow writes directly to main and cuts tags with no approval or documented bypass |
| BP-P2-001 | P2 | Secret-bearing public-release workflows run with no environment approval gate |
| BP-P2-002 | P2 | No Dependabot and all third-party actions are referenced by mutable tags |
| BP-P2-003 | P2 | No documented branch/release/hotfix model or break-glass process |
| BP-P3-001 | P3 | No CODEOWNERS file |
| BP-P3-002 | P3 | No pull-request template or contributing guide |
