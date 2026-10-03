# Supply Chain, Dependencies, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-fix-backup-abort-markers-20b5e57
- Repository: `falcon` (`C:\temp\falcon`)
- Branch: fix/backup-abort-markers
- Commit SHA: 20b5e57
- Generated at: 2026-10-03
- Auditor: repo-deep-dive subagent (DeepSeek V4.1 Flash)
- Area code: SUPPLY
- Output path: docs/audits/{name}/{run}/11_supply_chain_dependency_secrets.md
- Scope limitations: no network/CVE DB access; scan dates are `unverified` beyond file content. No secret values printed.

## Scope

Reviewed image pinning and digest verification, SBOM/vulnerability coverage, `.gitleaks.toml`, `secret_scan.py`, CI dependency pinning, and secret handling adjacency. Secret values are not reproduced.

## Evidence Reviewed

- `pins/images.lock` (26 images), `pins/verify-digests.sh`, `automation/validation/check_compose_digests.py`.
- `sbom/` (39 JSON), `automation/validation/sbom_coverage_check.sh`, `sbom_hashes.sh`.
- `.gitleaks.toml`, `automation/validation/secret_scan.py`, `ci/requirements-ci.txt`.

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `check_compose_digests.py` L54-85 | Source | Digest gate scope | globs `compose/**` only |
| `ci/validate.py` check_compose_digests | Source | Invocation | no `--max-lock-age-days` |
| `sbom_coverage_check.sh` | Source | Vuln gating | informal unless `--require-vuln` |
| `validate.yml` L96-99 | Config | SBOM step | no `--require-vuln` |
| `.gitleaks.toml` | Config | Allowlists | `ledgers/.*`, `docs/audits/.*` |
| `pins/images.lock` | Generated | Freshness | `generated_utc` 2026-09-20 |

## Executive Summary

Image pinning is a strength: 26 images carry explicit `tag@digest`, CI cross-checks compose references against the lock, and actions/tools are hash-pinned. Two coverage holes remain: the digest gate only globs `compose/`, so `automation/wazuh/**` and `mct/compose/**` are ungated; and lock freshness plus vulnerability coverage are not enforced in CI (`--require-vuln` and `--max-lock-age-days` unset). `.gitleaks.toml` allowlists entire `ledgers/` and `docs/audits/` subtrees, wider than the documented classified set.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Image lock | `pins/images.lock` | pins | Functional | Medium | 2026-09-20 |
| Digest verify | `pins/verify-digests.sh` | runtime check | Functional | Low | first RepoDigest |
| Compose gate | `check_compose_digests.py` | CI check | Partial | High | scope hole |
| SBOM | `sbom/*.cdx.json` | provenance | Partial | Medium | unsigned |
| Vuln | `sbom/vuln/*` | CVE data | Not gated | High | `--require-vuln` off |
| gitleaks | `.gitleaks.toml` | secret scan | Broad allowlist | Medium | subtree allowances |
| Scanner | `secret_scan.py` | in-repo scan | Strong | Low | value-aware |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dependency pinning | 5 | images/lock, actions SHA | — | — |
| Digest gating | 3 | check_compose_digests | scope hole | SUPPLY-P1-001 |
| Vulnerability coverage | 2 | sbom/vuln | not gated/stale | SUPPLY-P1-002 |
| SBOM provenance | 2 | unsigned | no signature | — |
| Secret scanning | 4 | secret_scan.py + gitleaks | allowlist breadth | SUPPLY-P2-001 |
| Lock freshness | 2 | no age gate | stale risk | SUPPLY-P2-002 |

## Findings

### Finding ID: SUPPLY-P1-001 - Container digest gate scope hole: vendored `mct/compose` and `automation/wazuh` are ungated

- Severity: P1
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `automation/validation/check_compose_digests.py` lines 57-59 / 114 — globs `compose/**` only (`--compose-dir` defaults to `repo/compose`)
  - `automation/wazuh/multi-node/docker-compose.yml` — image refs outside `compose/`
  - `mct/compose/` — vendored compose outside `compose/`
- What is happening: Compose files outside `compose/` are not checked against `pins/images.lock`.
- Why it matters: Floating or drifted images in the imported stacks bypass the gate.
- User / business impact: Uncontrolled supply chain for internet-facing services.
- Security / privacy / reliability impact: CVE/drift exposure.
- Recommended fix: Run the checker over `compose/`, `mct/compose/` and `automation/wazuh/`, or add a separate invocation per root; assert every compose image resolves in the lock.
- Suggested validation: Extend `compose_digest_check_test.sh` with a mutated `automation/wazuh` ref.
- Owner suggestion: supply-chain
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SUPPLY-P1-002 - Vulnerability scanning is not gated and coverage is partial

- Severity: P1
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `.github/workflows/validate.yml` lines 96-99 — `sbom_coverage_check.sh` invoked without `--require-vuln`
  - `automation/validation/sbom_coverage_check.sh` — "vulnerability column is informational unless `--require-vuln` is given"
  - `sbom/vuln/` — per-image JSON present for only a subset
- What is happening: CVE data exists but a high-severity finding does not fail CI.
- Why it matters: Known vulnerabilities can ship unnoticed.
- User / business impact: Security exposure.
- Security / privacy / reliability impact: Supply-chain vulnerability.
- Recommended fix: Run a scheduled vulnerability scan with `--require-vuln` and a severity threshold; refresh the vuln set on a cadence.
- Suggested validation: `bash automation/validation/sbom_coverage_check.sh --require-vuln` returns non-zero on a planted CVE fixture.
- Owner suggestion: security/owner
- Effort estimate: M
- Dependencies: scanner availability
- Status: open

### Finding ID: SUPPLY-P2-001 - `.gitleaks.toml` allowlists are broader than the documented classified set

- Severity: P2
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `.gitleaks.toml` — allowlist entries with `paths = ['docs/audits/.*', 'ledgers/.*']` (whole subtrees)
  - Decoy `[[allowlists]]` for `sbom/.*`, `evidence/.*`
- What is happening: Secret scanning skips entire provenance subtrees, so a real credential committed under `ledgers/` or a new audit folder would not be caught by gitleaks (though `secret_scan.py` still scans some paths).
- Why it matters: The allowlist is wider than the "classified false positives" it documents.
- User / business impact: Potential undetected secret commit.
- Security / privacy / reliability impact: Detection gap.
- Recommended fix: Narrow allowlists to specific rule IDs and file patterns; keep `secret_scan.py` as the primary value-aware scan and record each allowance in `docs/security/SCANNER_ALLOWLIST_CHANGES.md`.
- Suggested validation: Planted hex64/apikey under `ledgers/` is flagged.
- Owner suggestion: supply-chain
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SUPPLY-P2-002 - Image lock freshness is not gated

- Severity: P2
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `pins/images.lock` — `generated_utc` 2026-09-20
  - `ci/validate.py` `check_compose_digests` — calls the checker without `--max-lock-age-days`
  - `check_compose_digests.py` — age only fails when `max_age_days` is supplied
- What is happening: The lock can age indefinitely without failing CI.
- Why it matters: Stale base images accumulate unpatched CVEs.
- User / business impact: Security debt.
- Security / privacy / reliability impact: Outdated dependencies ship.
- Recommended fix: Pass a maximum lock age and refresh the lock on schedule.
- Suggested validation: `check_compose_digests.py --max-lock-age-days 30` fails on the stale lock.
- Owner suggestion: supply-chain
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SUPPLY-P3-001 - `pins/verify-digests.sh` compares only the first RepoDigest entry

- Severity: P3
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `pins/verify-digests.sh` — `docker image inspect ... --format '{{index .RepoDigests 0}}'`
- What is happening: Multi-arch images with several RepoDigest entries are compared against index 0 only.
- Why it matters: A legitimate or malicious alternate digest could be missed.
- User / business impact: Low.
- Security / privacy / reliability impact: Minor verification gap.
- Recommended fix: Compare the full RepoDigests set for membership of the pinned digest.
- Suggested validation: Fixture image with two RepoDigests passes/fails correctly.
- Owner suggestion: supply-chain
- Effort estimate: S
- Dependencies: None
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Ungated compose images | P1 | Medium | High | checker scope | SUPPLY-P1-001 |
| Vulnerable image ships | P1 | Medium | High | --require-vuln off | SUPPLY-P1-002 |
| Secret allowlist too broad | P2 | Medium | High | gitleaks | SUPPLY-P2-001 |
| Stale base images | P2 | High | Medium | lock age | SUPPLY-P2-002 |

## Recommendations

### Immediate / Release Blocking
- Gate vulnerabilities (`--require-vuln`) and close the compose scope hole.

### This Week
- Narrow gitleaks allowlists; add lock-age gate.

### This Month
- Sign the SBOM/provenance set.

### Later / Platform Evolution
- Continuous SBOM regeneration.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `--compose-dir` invocations | Closes scope hole | ci/validate.py | mutated test |
| `--max-lock-age-days 30` | Forces refresh | ci/validate.py | stale lock fails |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Vuln gate | P1 | security | M | scanner |
| Allowlist narrowing | P2 | supply-chain | S | — |

## Suggested Tests

- Mutated `automation/wazuh` image ref fails the digest gate.
- Planted secret under `ledgers/` is flagged.

## Suggested Documentation Updates

- `docs/security/SCANNER_ALLOWLIST_CHANGES.md` — record each gitleaks allowance.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Actual vuln scan date? | Freshness | scanner log |

## Appendix
Not applicable.
