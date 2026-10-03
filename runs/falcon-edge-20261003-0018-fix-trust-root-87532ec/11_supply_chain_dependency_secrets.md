# Supply Chain, Dependency, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge`
- Branch: fix/trust-root
- Commit SHA: 87532ec
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: SC
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/11_supply_chain_dependency_secrets.md
- Scope limitations: no network; secret values never read or printed. Findings name paths/types only.

## Scope

Reviewed dependency posture (stdlib-first), CI tool acquisition, lockfiles, secret scanning (both scanners), release/delivery artifacts, SBOM, and license gate.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `docs/security/DEPENDENCY_POLICY.md` | Doc | Policy | stdlib-first, pinning |
| `.github/workflows/validate.yml` | Workflow | Tool install | curl downloads, pip installs |
| `ci/secret_scan.py` | Scanner | Tree scan | patterns + allowlist |
| `.gitleaks.toml` | Scanner | gitleaks config | reviewed allowlist |
| `ci/license_check.py` | Gate | License denylist | in `validate.sh` |
| `automation/validation/build_sbom.py` | Tool | SBOM | bake step |
| `inventory.json` secret_adjacent_files | Inventory | Sensitive paths | 15 files |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| Scanner scope read | Static | History vs tree | `gitleaks --no-git` → SC-P2-002 |
| Tool acquisition read | Static | Integrity | curl without checksum → SC-P2-003 |
| pip install read | Static | Pinning | pyyaml/coverage/zizmor unpinned |
| Secret-adjacent inventory | Static | Sensitive paths | all redacted/benign per scanner |

## Executive Summary

The runtime is deliberately stdlib-only (`DEPENDENCY_POLICY.md`), which removes almost all language-level supply-chain risk. Two secret scanners run (gitleaks + `ci/secret_scan.py`) with reviewed allowlists, and an independent license gate exists. The gaps are in tool/build integrity: CI downloads actionlint/shellcheck/ruff/gitleaks via `curl` without checksum verification, pip installs `pyyaml`/`coverage`/`zizmor` unpinned, and neither secret scanner inspects git history (`--no-git`). Release image assets are credential-bearing by design and protected only by repo access (owner-accepted).

## Inventory

| Item | Path | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Runtime deps | `src/**` | stdlib only | Strong | Low | no requirements.txt |
| CI Python deps | `validate.yml` | test/tool deps | Unpinned | Med | pyyaml/coverage/zizmor |
| CI tools | `validate.yml` | lint/scan | curl, no checksum | Med | SC-P2-003 |
| gitleaks | `.gitleaks.toml` | secret scan | allowlist | Med | no history |
| secret_scan | `ci/secret_scan.py` | secret scan | allowlist | Med | no history |
| License gate | `ci/license_check.py` | licensing | denylist | Low | present |
| SBOM | `build_sbom.py` | image SBOM | built in bake | Low | — |
| Actions | `.github/workflows` | CI | SHA-pinned | Low | strong |
| Release assets | `publish-release.yml` | delivery | credential-bearing | Med | owner-accepted |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 4 | stdlib-only | no pyproject | add metadata |
| Lockfiles | 3 | none (stdlib) | CI deps unpinned | pin CI deps |
| Workspace deps | 4 | stdlib | — | — |
| Unused/duplicate deps | 4 | none | — | — |
| Native/build deps | 4 | openssl/sqlite system | — | — |
| Transitive risk | 3 | low | tool downloads | verify checksums |
| Dependabot/renovate | 4 | actions only | no pip ecosystem | add pip |
| Package scripts/postinstall | N/A | none | — | — |
| Docker base images | N/A | no containers | — | — |
| GitHub Actions deps | 5 | SHA-pinned | — | — |
| Environment examples | 3 | `*.example.json` | — | — |
| Secret-like strings | 4 | scanners clean | history not scanned | SC-P2-002 |
| SBOM/provenance/signing | 4 | SBOM + manifest sig | no cosign/attestation | minor |
| Container scanning | N/A | none | — | — |
| License risk | 4 | license gate | no repo LICENSE | HYG |

## Detailed Review

### Item: CI tool acquisition

- Evidence: `validate.yml` — `curl -sL ... -o actionlint.tgz`, `shellcheck.tar.xz`, `ruff.tgz`, `gitleaks.tgz`; no `sha256sum -c`.
- Gap: a compromised release or MITM of the download would execute attacker code in CI with repo secrets for bake? (verify job has no bake secrets, but still `GITHUB_TOKEN`).
- Risk: SC-P2-003.

### Item: Secret scanning history

- Evidence: `gitleaks detect --no-git`; `ci/secret_scan.py` walks the working tree only.
- Gap: a secret committed and later removed stays in history and is never scanned.
- Risk: SC-P2-002.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SC-001 | Manifests | stdlib | strong | — | — | — |
| SC-002 | Lockfiles | none | N/A | CI deps | P2 | pin |
| SC-003 | Deps | stdlib | strong | — | — | — |
| SC-004 | Dependabot | actions | weekly | no pip | P3 | add |
| SC-005 | Tool download | curl | none | no checksum | P2 | SC-P2-003 |
| SC-006 | Secret scan | scanners | tree clean | no history | P2 | SC-P2-002 |
| SC-007 | Release assets | credential-bearing | repo access | no encryption | P2 | owner-accepted |
| SC-008 | SBOM | bake | present | no attestation | P3 | optional |
| SC-009 | License | `license_check.py` | present | no repo LICENSE | P3 | add |

## Findings

### Finding ID: SC-P2-001 - CI installs Python dependencies and tools without version pinning or hashes

- Severity: P2
- Confidence: High
- Area: SC
- Evidence:
  - `.github/workflows/validate.yml` — `python3 -m pip install --quiet pyyaml`, `--quiet coverage`, `--quiet "zizmor==1.30.1"`
  - `docs/security/DEPENDENCY_POLICY.md` — requires `==` with `--hash=` for accepted deps
- What is happening: `pyyaml` and `coverage` are unpinned; the policy's own pinning rule is not enforced for CI test tooling.
- Why it matters: a malicious/updated transitive package can execute in the validate job; contradicts the documented policy.
- User / business impact: CI supply-chain integrity.
- Security / privacy / reliability impact: code execution in CI (no bake secrets on this job, mitigates blast radius).
- Recommended fix: pin exact versions with hashes in a `requirements-dev.txt` and enforce with a CI check, or use a hash-pinned constraints file.
- Suggested validation: add a policy check that rejects unpinned/`>=` installs.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SC-P2-002 - Secret scanning covers only the working tree, never git history

- Severity: P2
- Confidence: High
- Area: SC
- Evidence:
  - `.github/workflows/validate.yml` — `./gitleaks detect --no-git --source . --redact --config .gitleaks.toml`
  - `ci/secret_scan.py` — `iter_files(root)` walks the filesystem, not history
- What is happening: a secret that was committed and later deleted is neither detected nor flagged.
- Why it matters: the program's central rule is "no secrets in commits"; history is where committed secrets persist.
- User / business impact: a leaked key can remain recoverable in clone history.
- Security / privacy / reliability impact: credential exposure.
- Recommended fix: run gitleaks in git mode (default, or `--log-opts=--all`) on a schedule, and add a `git filter-repo` rotation runbook if a finding is confirmed.
- Suggested validation: inject a dummy secret into a temp branch, confirm detection.
- Owner suggestion: security owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SC-P2-003 - CI downloads lint/scan binaries via curl without checksum verification

- Severity: P2
- Confidence: High
- Area: SC
- Evidence:
  - `.github/workflows/validate.yml` — `curl -sL --retry 3 -o actionlint.tgz https://github.com/rhysd/actionlint/releases/download/v1.7.12/...`
  - same pattern for shellcheck v0.10.0, ruff 0.16.9, gitleaks 8.30.1
- What is happening: version-tagged artifacts are fetched but their SHA-256 is never checked.
- Why it matters: a hijacked release asset executes in CI; version tags alone are not integrity controls.
- User / business impact: CI compromise.
- Security / privacy / reliability impact: supply-chain code execution.
- Recommended fix: embed and verify the SHA-256 of each downloaded tool, or use a verified action/marketplace wrapper.
- Suggested validation: corrupt the download and assert CI fails.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SC-P2-004 - Credential-bearing image artifacts and releases rely solely on private-repo access (owner-accepted)

- Severity: P2
- Confidence: High
- Area: SC
- Evidence:
  - `.github/workflows/bake-image.yml` — image contains WiFi PSK, WireGuard key, claim token, password hash
  - `.github/workflows/publish-release.yml` — publishes those assets as a GitHub Release
  - `ledgers/risk_register.md` — R-007, R-012
- What is happening: the delivery artifact is itself a credential bundle; the only control is repository visibility and access-controlled artifacts/releases.
- Why it matters: any repo access leak exposes site credentials; workflow artifacts expire but releases are durable.
- User / business impact: site credential exposure.
- Security / privacy / reliability impact: high impact if access is lost.
- Recommended fix: encrypt credential side-files, scope releases to a protected environment, and rotate baked credentials after first boot; document an access-revocation drill.
- Suggested validation: access review; rotation drill.
- Owner suggestion: owner
- Effort estimate: M
- Dependencies: plan/environment protection
- Status: owner-accepted

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unpinned CI deps | P2 | Medium | CI RCE | validate.yml | pin+hash |
| No history secret scan | P2 | Medium | Credential exposure | gitleaks --no-git | git-mode scan |
| Unverified tool downloads | P2 | Low | CI RCE | validate.yml | checksum |
| Credential-bearing releases | P2 | Low | Site creds | bake/publish | encryption/scoping |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Checksum-verify CI tool downloads; run gitleaks in git mode.

### This Month
Pin CI Python deps with hashes; add a policy check.

### Later / Platform Evolution
Artifact attestation (cosign/SLSA); encrypted credential side-files.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| gitleaks git-mode weekly | catches history leaks | `validate.yml` | dummy secret test |
| Tool checksums | integrity | `validate.yml` | corrupted download |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Hash-pinned CI deps | P2 | build-agent | S | none |
| Release credential encryption | P2 | owner | M | key mgmt |
| Provenance attestation | P3 | build-agent | M | tooling |

## Suggested Tests

- CI: policy check rejecting unpinned/`>=` installs.
- Security: history-scan detection test.
- Integrity: corrupted tool download fails.

## Suggested Documentation Updates

- `docs/security/DEPENDENCY_POLICY.md`: mark CI tooling enforcement as implemented or link the check.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is git history already clean? | backlog priority | gitleaks full run |
| Are credentials rotated after first boot today? | exposure window | owner docs |

## Appendix

`inventory.json` flagged 15 secret-adjacent files (token lifecycle/backup/schema paths, prior audit reports). All were declared handled by the two scanners and no values were printed in this audit. The runtime has no `requirements.txt`; system tools are `openssl`, `sqlite3`, `git`, `nmap`, `ssh`.
