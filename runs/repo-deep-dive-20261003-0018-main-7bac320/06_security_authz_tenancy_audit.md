# Security, Authz, and Tenancy Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: SEC
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/06_security_authz_tenancy_audit.md
- Scope limitations: no deployed service; the security surface is the toolchain and CI workflow.

## Scope

Secrets, CI token handling, privileged execution, and repository governance. Authz/tenancy is not applicable (no users, tenants, sessions, or object storage in the pack). The reachable security surface is `.github/workflows/deep-dive-deterministic.yml` and the stdlib tools.

## Evidence Reviewed

- `.github/workflows/deep-dive-deterministic.yml` (full)
- `tools/deterministic_checks.py` (gitleaks invocation)
- `tools/repo_inventory.py` (`SECRET_NAME_PATTERNS`)
- `ci/audit.yml`
- `git ls-files` secret sweep; no `.env`/key material found

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git ls-files` grep for `.env`/keys | command | secret exposure | no secret files tracked |
| `grep "curl\|sudo\|token" workflow` | code read | privileged/untrusted exec | remote install + PAT clone URL |
| `check_run.sh`/`deterministic_checks.py` gitleaks | code read | secret scanning posture | non-gating |

## Executive Summary

No secret values are committed. The material risk is in CI: the org-wide workflow executes remotely downloaded scripts/tarballs as root and embeds a PAT in a clone URL, and its checks swallow failures. There is no SECURITY.md or CODEOWNERS. Tenant isolation is not applicable.

## Inventory

| Item | Path | Purpose | Risk |
|---|---|---|---|
| Org workflow | `.github/workflows/deep-dive-deterministic.yml` | scan org repos | High |
| PAT usage | same, lines 39, 86 | clone private repos | High |
| Remote installs | same, lines 51-56 | install lint/scan tools | High |
| Secret scan | `tools/deterministic_checks.py` | gitleaks advisory | Medium |
| Disclosure policy | absent | vuln reporting | Medium |

## Findings

### Finding ID: SEC-P1-001 - CI executes remotely downloaded scripts and archives as root without pinning

- Severity: P1
- Confidence: High
- Area: SEC
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` line 51 — `bash <(curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)`
  - lines 54-56 — `curl -sSL .../gitleaks_${GL_TAG#v}_linux_x64.tar.gz | sudo tar -xz -C /usr/local/bin`
  - line 51/56 — `|| true` mask failures
- What is happening: The runner pipes a mutable-branch remote script to `bash` and a "latest release" tarball to `sudo tar`, with no checksum or version pin.
- Why it matters: A compromise upstream (or a moved `main`/`latest` tag) yields arbitrary code execution as root in a scheduled workflow with a PAT.
- User / business impact: Org-wide repo read token and runner could be compromised.
- Security / privacy / reliability impact: Supply-chain RCE on CI infrastructure; non-reproducible tool versions.
- Recommended fix: Pin actionlint/gitleaks by version and sha256; download to a non-PATH dir; do not pipe to `sudo`; fail closed instead of `|| true`.
- Suggested validation: Workflow diff shows pinned URL+checksum; a deliberately corrupted download fails the job.
- Owner suggestion: CI owner
- Effort estimate: M
- Dependencies: none
- Status: open

### Finding ID: SEC-P1-002 - PAT is embedded in the git clone URL, risking token exposure in logs

- Severity: P1
- Confidence: Medium
- Area: SEC
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` line 39 — `GH_TOKEN: ${{ secrets.ORG_READ_TOKEN || github.token }}`
  - line 86 — `git clone -q "https://x-access-token:${GH_TOKEN}@github.com/${ORG}/${r}.git" "work/$r"`
- What is happening: The token is placed in the remote URL. Git and the shell can echo this URL in error/diagnostic output, and any future `set -x`/debug run would print it.
- Why it matters: CI logs are broadly readable; a leaked PAT grants org repo read.
- User / business impact: Credential exposure requires rotation.
- Security / privacy / reliability impact: Secret exfiltration via logs.
- Recommended fix: Use `actions/checkout` with `token:` per repo, or `git -c http.extraheader="AUTHORIZATION: bearer $GH_TOKEN"` without the URL; add `::add-mask::$GH_TOKEN`.
- Suggested validation: Induce a clone failure and confirm no token appears in logs; add a log grep for `x-access-token`.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SEC-P2-003 - CI security checks are non-gating and there is no secret-scan allowlist

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` line 88 — `python3 tools/deterministic_checks.py "work/$r" -o "out/$r" || true`
  - `tools/deterministic_checks.py` lines 120-122 — gitleaks runs with `--exit-code 0`
  - no `.gitleaks.toml` in tree (though lines 145-147 instruct allowlisting there)
- What is happening: gitleaks findings are advisory-only and never fail the workflow; the recommended allowlist file does not exist.
- Why it matters: A new secret can be committed and the scheduled scan stays green.
- User / business impact: Detection without enforcement.
- Security / privacy / reliability impact: Secret leakage can persist.
- Recommended fix: Add `.gitleaks.toml`, make P1 secret findings fail (or open an issue), and remove the blanket `|| true`.
- Suggested validation: A fixture secret causes a non-zero result and the job fails.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: SEC-P1-001
- Status: open

### Finding ID: SEC-P3-004 - No vulnerability-disclosure policy or code ownership file

- Severity: P3
- Confidence: High
- Area: SEC
- Evidence:
  - `git ls-files` — no `SECURITY.md`, no `.github/CODEOWNERS`
  - `CONTRIBUTING.md` discusses extension but not security reporting
- What is happening: There is no documented way to report a vulnerability and no owner mapping.
- Why it matters: Security reports may go unhandled; findings lack accountable owners.
- User / business impact: Slower response; audit findings hard to route.
- Security / privacy / reliability impact: Governance gap.
- Recommended fix: Add `SECURITY.md` and `.github/CODEOWNERS`.
- Suggested validation: Files exist and are referenced from README.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SEC-P3-005 - Internal org and repository identifiers are hardcoded as workflow defaults

- Severity: P3
- Confidence: High
- Area: SEC
- Evidence:
  - `.github/workflows/deep-dive-deterministic.yml` lines 15, 23, 34, 36 — default org `MaineCyberTech`; exclude list `soc,infra,AWS-WWW,www,www-dev`
- What is happening: Internal infrastructure names are committed in a public-oriented pack.
- Why it matters: Information disclosure of org structure; makes the pack non-portable.
- User / business impact: Minor.
- Security / privacy / reliability impact: Reconnaissance aid.
- Recommended fix: Move defaults to repository variables or a config file; document expected overrides.
- Suggested validation: grep shows no org-specific literals.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Supply-chain RCE in CI | P1 | Medium | High | SEC-P1-001 | pin + checksum |
| PAT leak via logs | P1 | Medium | High | SEC-P1-002 | mask + header auth |
| Undetected secret commit | P2 | Medium | Medium | SEC-P2-003 | gate gitleaks |

## Recommendations

### Immediate / Release Blocking
- Pin/checksum CI tool downloads; stop piping to `sudo`.
- Remove the PAT from the clone URL and mask it.

### This Week
- Make secret scanning fail; add `.gitleaks.toml`.

### This Month
- Add `SECURITY.md` and `CODEOWNERS`.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `::add-mask::` token + header auth | stops log leak | workflow | clone-failure log inspection |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Gating secret scan | P2 | CI owner | S | SEC-P1-001 |

## Suggested Tests

- Negative test: fixture secret fails the workflow.
- Log scan asserting `x-access-token` never appears.

## Suggested Documentation Updates

- `SECURITY.md`; README "reporting".

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `ORG_READ_TOKEN` scoped read-only org-wide? | blast radius | token settings (not in repo) — `Unknown` |

## Appendix

Tenancy/authz: not applicable — the pack has no runtime accounts or tenant data.
