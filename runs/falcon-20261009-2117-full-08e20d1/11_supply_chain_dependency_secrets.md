# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

# Supply Chain, Dependency, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `MaineCyberTech/falcon` (private)
- Branch: `main`
- Commit SHA: `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d`
- Generated at: 2026-10-09T21:44Z
- Auditor: subagent (read-only)
- Area code: SC
- Output path: docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/11_supply_chain_dependency_secrets.md
- Scope limitations: repository + read-only GitHub API + read-only host checks (file modes only; no secret values read or printed). The vendored `mct/` tree is imported under a no-silent-patch policy; its wholesale-sourcing residual is reported, not fixed.

## Scope

Reviewed: dependency manifests (`ci/requirements-ci.txt`, `pins/images.lock`), Dependabot configuration and server-side alert state, CI secret scanning (gitleaks tree + history, `automation/validation/secret_scan.py`), credential handling (`.env.example`, `.gitignore`, `/home/user/.env` mode, `automation/validation/lib/env_key.sh`, `ci/validate.py` credential-sourcing check), rotation records (`docs/security/CREDENTIAL_ROTATION_REGISTER.md`, `INHERITED_CREDENTIAL_ROTATION.md`, `ledgers/decision_log.md`), supply-chain gates (`check_compose_digests.py`, `sbom_coverage_check.sh`, `pins/supply-chain-waivers.json`), Docker base image (`compose/central/opensearch-s3.Dockerfile`), GitHub Actions pinning, and delivery exclusions (`build_review_package.sh`, `PACKAGE_MANIFEST.sha256`). Not reviewed: image vulnerability contents themselves (SBOM domain), the edge repository's supply chain (separate repo), live process environments.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `ci/requirements-ci.txt` | manifest | only third-party Python deps | hash-pinned pyyaml 6.0.3 + zizmor 1.30.1 |
| `pins/images.lock` | lockfile | 24 pinned images | digests recorded 2026-09-20..10-01 |
| `.github/dependabot.yml` | config | dependency updates | github-actions ecosystem only |
| GitHub API: `vulnerability-alerts`, `dependabot/alerts`, `secret-scanning/alerts`, `code-scanning/alerts`, `dependency-graph/sbom`, `dependency-graph/compare` | live state | server-side dependency security | alerts disabled; secret/code scanning plan-gated |
| `.gitleaks.toml`, `automation/validation/gitleaks_history_check.sh`, `secret_scan.py` | scanners | secret detection controls | pinned gitleaks 8.30.1; allowlists documented |
| `.gitignore`, `.env.example`, live `stat` of `/home/user/.env`, `/home/user/.config/falcon/capture.env`, `/srv/falcon/secrets` | secret handling | exposure review | modes 0600/0600/0700 |
| `docs/security/CREDENTIAL_ROTATION_REGISTER.md`, `INHERITED_CREDENTIAL_ROTATION.md`, `mct/VENDORING.md` | docs | rotation + vendored residual | 20/20 PENDING (2026-10-04) |
| `automation/validation/lib/env_key.sh`, `ci/validate.py:278-303` | code | first-party single-key reads | 41 call sites; `.env` sourcing blocked |
| `pins/supply-chain-waivers.json`, `check_compose_digests.py` | gate | digest/vuln waivers | expiring 2026-12-31 |
| `build_review_package.sh`, `PACKAGE_MANIFEST.sha256` | delivery | secret exclusion check | 0 `secrets/` entries |
| `compose/central/opensearch-s3.Dockerfile` | Dockerfile | base image pinning | FROM digest matches lock |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| Local supply-chain/secret checks pass at HEAD | `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only secret-scan,credential-sourcing,compose-digests,sbom-vuln,sbom-hashes,license,lock-age` | supported: `validation_failures=0` |
| No secret files in the delivered package | grep `PACKAGE_MANIFEST.sha256` for `secrets/` and `.env` | supported: 0 `secrets/` paths; only `*.env.example` files |
| Owner credential file is protected | `stat` (mode only) | supported: `/home/user/.env` 0600 user:user; `capture.env` 0600; `/srv/falcon/secrets` 0700 root |
| Vendored wholesale sourcing reduced but open | grep reproduction `mct/**` for `set -a` + `source` | 19 files (docs still say 28) |
| Rotation estate still pending | `CREDENTIAL_ROTATION_REGISTER.md:12-13` (2026-10-04) + decision log | supported: 20/20 PENDING |
| Dependabot alerts are disabled | API GET `dependabot/alerts` | supported: 403 "Dependabot alerts are disabled for this repository" |
| Compose digest gate covers all declared roots | `check_compose_digests.py` wired in `ci/validate.py:142-158`; local run PASS | supported |
| Prior SUPPLY-P1-001/002 remain fixed | scope check + `--require-vuln` with waivers | supported (see prior-run comparison) |

## Executive Summary

The supply chain is unusually well pinned for a private Free-plan repo: 24 container images digest-locked and cross-checked against every compose root with expiring owner-visible waivers; one hash-pinned Python requirements file; all GitHub Actions pinned to commit SHAs; gitleaks tree and full-history scans in CI plus a repo-specific scanner; a license gate for installed Python tooling; first-party credential reads migrated to single-key reads (41 call sites) with a CI check that blocks sourcing `/home/user/.env`; and delivery exclusions that keep `secrets/` out of the review package (verified: 0 entries in the 3,783-entry package manifest).

Two current gaps matter. First, server-side dependency security is off: Dependabot vulnerability alerts are disabled (a repo setting, not a plan gate) and the only Dependabot ecosystem configured is `github-actions`, so the two Python CI dependencies have no update/vulnerability path beyond manual hash bumps; code scanning/dependency review are GHAS plan-gated, leaving trivy (manual, 12 images waived until 2026-12-31) and gitleaks as the compensating controls. Second, the inherited credential estate remains unrotated (20/20 PENDING as of 2026-10-04) and 19 vendored MCT scripts still `set -a`-source credential env files wholesale (down from the 28 the docs claim), so those processes carry credential-bearing environments.

Recommended next actions: enable Dependabot alerts and add a `pip` ecosystem entry; execute the owner rotation register; migrate the vendored scripts at the next MCT import; append the corrected counts to the rotation docs.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Python CI deps | `ci/requirements-ci.txt` | pyyaml, zizmor | hash-pinned, manual bumps | Low-Medium | no Dependabot pip coverage |
| Image lock | `pins/images.lock` | 24 images | digest-pinned | Low | two floating tags kept for naming (digest-pinned in compose) |
| Compose digest gate | `automation/validation/check_compose_digests.py` | repo@digest vs lock | enforced for compose/, mct/compose/, automation/wazuh/ | Low | expiring waivers |
| Vuln-scan gate | `sbom_coverage_check.sh --require-vuln` | scan or waiver | enforced | Low-Medium | 12 images waived to 2026-12-31 |
| Dependabot | `.github/dependabot.yml` + alerts | updates + alerts | actions updates only; alerts disabled | Medium | free setting off |
| Secret scan | gitleaks + `secret_scan.py` | tree + history | enforced, fail-closed | Low | pinned 8.30.1 |
| Credential reads | `env_key.sh` | single-key reads | 41 call sites | Low | no whole-file sourcing in first-party tree |
| Vendored scripts | `mct/scripts/**` | imported ops scripts | 19 wholesale-source env files | Medium | vendored no-patch policy |
| Rotation | `CREDENTIAL_ROTATION_REGISTER.md` | 20 classes | 20/20 PENDING | Medium | owner-gated |
| Dockerfile | `compose/central/opensearch-s3.Dockerfile` | local S3-enabled image | base digest matches lock | Low | no hadolint (DET-P3-003) |
| Delivery exclusions | `build_review_package.sh` | review package | secrets excluded | Low | verified in manifest |

## Findings

### Finding ID: SC-P2-001 (new, ID provisional) - Dependabot vulnerability alerts disabled; Python CI dependencies uncovered by version updates

- Severity: P2
- Confidence: High (live API)
- Area: SC
- Evidence:
  - `GET /repos/MaineCyberTech/falcon/vulnerability-alerts` -> 404 (not enabled)
  - `GET /repos/MaineCyberTech/falcon/dependabot/alerts?state=open` -> 403 `"Dependabot alerts are disabled for this repository."` (a settings toggle, not the plan message used for branch protection)
  - `.github/dependabot.yml:1-7` (only `package-ecosystem: github-actions`)
  - `ci/requirements-ci.txt:1-8` (pyyaml 6.0.3, zizmor 1.30.1; hashes verified manually)
  - `GET /code-scanning/alerts` -> 403 GHAS; `GET /dependency-graph/sbom` -> 404; `GET /dependency-graph/compare/...` -> 403 (dependency review is plan-gated; noted, not filed)
  - Compensating controls that do exist: trivy scans for 12/24 images with the other 12 waived (`pins/supply-chain-waivers.json`, review_by 2026-12-31), gitleaks, and the Python license gate
- What is happening: GitHub-native vulnerability alerting is switched off, and the two Python CI dependencies have no update bot. A vulnerable pyyaml/zizmor release would only be noticed by a human re-reading the pin notes.
- Why it matters: dependency vulnerability detection is the core of supply-chain hygiene; the image side has a (waived/stale) path, the Python side has none.
- User / business impact: potential use of a vulnerable CI dependency without a signal.
- Security / privacy / reliability impact: blind spot in dependency risk management.
- Recommended fix: enable Dependabot alerts in repository settings (no plan change needed per the API message); add a `pip` ecosystem entry for `/ci` (and consider `docker` for `compose/central`); keep the trivy refresh path.
- Suggested validation: `gh api repos/.../dependabot/alerts` returns 200; a Dependabot PR appears for a deliberately outdated test pin.
- Owner suggestion: repo owner + supply-chain owner.
- Effort estimate: S
- Dependencies: none.
- Status: open

### Finding ID: SECRET-P2-001 (prior, still-open) - Inherited credential estate pending rotation; vendored scripts still source credential files wholesale

- Severity: P2
- Confidence: High (register + grep reproduction; file modes verified live)
- Area: SC
- Evidence:
  - `docs/security/CREDENTIAL_ROTATION_REGISTER.md:12-13` - "Status as of 2026-10-04: 20/20 PENDING (none rotated by this change)"; `automation/validation/rotation_status.py --fail-if-pending` exists
  - `docs/security/CREDENTIAL_ROTATION_REGISTER.md:50-60` and `docs/security/INHERITED_CREDENTIAL_ROTATION.md:20,72-75` - vendored wholesale-sourcing residual (docs say 28 scripts)
  - grep reproduction: 19 files under `mct/scripts/**` combine `set -a` with sourcing a credential env file (e.g., `full-stack-healthcheck.sh`, `p33-core-alert.sh`, `p39-iris-delivery-check.sh`, `iris-db-dump.sh`, `shuffle-workflow-export.sh`); list in the appendix
  - First-party tree is remediated: `automation/validation/lib/env_key.sh` (single-key reads, 41 call sites) and `ci/validate.py:278-303` (no script may source `/home/user/.env`)
  - Live modes: `/home/user/.env` 0600 user:user; `/home/user/.config/falcon/capture.env` 0600; `/srv/falcon/secrets` 0700 root
- What is happening: the inherited MCT/Wazuh credential classes have no rotation evidence, and imported scripts still load whole credential files into their process environments (`set -a`), so any captured `env` from those processes would leak every key in the file.
- Why it matters: unrotated inherited credentials + environment-wide exposure is the highest-impact secret-handling residual in the repo.
- User / business impact: inherited credentials remain valid indefinitely; a single process-environment leak is a full-file leak.
- Security / privacy / reliability impact: credential compromise blast radius.
- Recommended fix: execute the 20 owner rotations per the register (each with capture id + negative test); migrate the 19 vendored scripts to `env_key.sh` at the next MCT import or an owner-approved vendored patch wave; update the docs from 28 to the current count.
- Suggested validation: `rotation_status.py --fail-if-pending` returns 0; a re-grep shows no `set -a` + credential-source combination; capture rows exist for each class.
- Owner suggestion: owner (rotations are owner-only) + vendored-tree maintainer.
- Effort estimate: L (owner windows; rotations are live-host operations)
- Dependencies: owner decisions/windows; MCT import policy (`mct/VENDORING.md` P2).
- Status: still-open (prior SECRET-P2-001)

## Prior-Run Comparison (falcon-20261005-full-main-e267ce1)

| Prior item | Prior status | Current verification | Disposition |
|---|---|---|---|
| SUPPLY-P1-001 digest-gate scope hole | verified-fixed (earlier run) | `check_compose_digests.py` covers `compose/`, `mct/compose/`, `automation/wazuh/` with fail-closed expiring waivers; wired at `ci/validate.py:142-158`; local PASS | verified-fixed holds |
| SUPPLY-P1-002 vuln-scan gating | verified-fixed (earlier run) | `sbom_coverage_check.sh --require-vuln --vuln-waivers` enforced in CI (`validate.yml:103-106`); 12 images waived to 2026-12-31 | verified-fixed holds |
| DET-P3-002 58 unpinned vendored images | open (deterministic lens) | blanket `mct/compose` waiver in `pins/supply-chain-waivers.json` (review_by 2026-12-31) | tracked; not re-filed |
| DET-P3-003 hadolint unavailable | open | still no hadolint anywhere; the single Dockerfile base digest matches the lock | tracked; not re-filed |
| DET-P3-004 trivy unavailable on the check runner | open | CI verifies committed scans (static) rather than running trivy; refresh remains manual/waived | tracked; not re-filed |
| SECRET-P2-001 rotation + wholesale sourcing | still-open | 20/20 PENDING (2026-10-04); 19 vendored files still source wholesale (down from 28) | re-filed as SECRET-P2-001 |
| SC domain findings (2026-10-05) | none | new Dependabot-alerts finding | new SC-P2-001 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Vulnerable CI dependency unnoticed | Medium | Medium | compromised/broken CI | alerts disabled; no pip bot | enable alerts + pip ecosystem |
| Unrotated inherited credentials | Medium | Medium | credential misuse | register 20/20 PENDING | owner rotation windows |
| Vendored whole-file env sourcing | Medium | Low-Medium | full-file secret leak | 19 files grep | single-key migration at import |
| Stale/waived vuln scans | Low-Medium | Medium | vulnerable image deployed | waivers to 2026-12-31 | refresh at patch window |
| Waiver expiry breaks CI without a plan | Low | Low | CI red | fail-closed waiver check | calendar reminder; renewal decision |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- SC-P2-001: enable Dependabot alerts; add the pip ecosystem entry.

### This Month
- SECRET-P2-001: start the owner rotation register (highest-value classes first); schedule the vendored migration at the next MCT import.
- Refresh trivy scans for the 12 waived images before 2026-12-31.

### Later / Platform Evolution
- Consider `docker` ecosystem in Dependabot for the local Dockerfile; consider signed provenance (SBOM domain).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Enable Dependabot alerts | restores native vuln signal | repo settings | API 200 |
| Add `pip` to dependabot.yml | covers pyyaml/zizmor | `.github/dependabot.yml` | Dependabot PR for a test bump |
| Update rotation docs count 28 -> 19 | docs match reality | rotation docs | grep |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rotate the 20 inherited credential classes | P2 | owner | L | owner windows |
| Vendored single-key migration | P2 | vendored maintainer | M | next MCT import |
| Scheduled trivy refresh job | P3 | CI owner | M | runner with docker+network |

## Suggested Tests

- A validate check that fails when `dependabot.yml` lacks the ecosystems present in the repo (pip/github-actions).
- A regression test asserting no tracked first-party script sources a whole env file (exists for `/home/user/.env`; extend to `/srv/falcon/secrets`).
- A waiver-expiry test (exists: `sbom_coverage_and_hashes_test.sh`) plus a calendar reminder test fixture.

## Suggested Documentation Updates

- `docs/security/CREDENTIAL_ROTATION_REGISTER.md`: update the vendored count and the 2026-10-09 status.
- `docs/security/INHERITED_CREDENTIAL_ROTATION.md:20,72-75`: same correction.
- `docs/security/OWNER_ENV_INVENTORY.md`: note the Dependabot-alerts decision once made.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Why is Dependabot alerts off - deliberate or default? | determines remediation urgency | decision-log search: none found |
| Which MCT import (or patch wave) will carry the single-key migration? | closes the vendored residual | `mct/VENDORING.md` plan |
| Are the two floating tag names (`cloudflared:latest`, `nginx:stable`) acceptable long-term given the digest pins? | policy consistency with pins/README rule 1 | owner/policy decision |

## Limitations

- No secret values were read or printed; checks were structural (modes, names, patterns).
- The vendored MCT tree is imported under a no-silent-patch policy; the count is a grep reproduction, not an execution test.
- GitHub API cannot show whether Dependabot alerts were ever enabled in the past.

## Appendix

Vendored files that combine `set -a` with sourcing a credential env file (grep reproduction, 2026-10-09):

```
mct/scripts/active-response-audit.sh
mct/scripts/alert-volume-by-rule.sh
mct/scripts/backup-dr-audit.sh
mct/scripts/credential-rotation-validation.sh
mct/scripts/full-stack-healthcheck.sh
mct/scripts/iris-db-dump.sh
mct/scripts/p33-core-alert.sh
mct/scripts/p39-iris-delivery-check.sh
mct/scripts/p63-agents-ci.sh
mct/scripts/p64-agents-ci.sh
mct/scripts/p65-agents-ci.sh
mct/scripts/p66-agents-ci.sh
mct/scripts/p67-agents-ci.sh
mct/scripts/phase2-healthcheck.sh
mct/scripts/phase5-credential-postcheck.sh
mct/scripts/pve-api-healthcheck.sh
mct/scripts/render-virustotal-integration.sh
mct/scripts/shuffle-workflow-export.sh
mct/scripts/zeek-classa-guardrail.sh
```

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-001 | P2 | Dependabot vulnerability alerts disabled; Python CI dependencies uncovered by version updates |
| SC-P2-002 | P2 | Inherited credential estate is still pending rotation and 19 vendored scripts source credential files wholesale |
