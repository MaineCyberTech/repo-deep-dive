# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

# Supply Chain, Dependency, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` (private)
- Branch: `main`
- Commit SHA: `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b`
- Generated at: 2026-10-11T04:31Z
- Auditor: subagent (read-only)
- Area code: SC
- Output path: docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/11_supply_chain_dependency_secrets.md
- Scope limitations: repository + read-only GitHub API + read-only host checks (file modes only; no secret values read or printed). The vendored `mct/` tree is imported under a no-silent-patch policy; its wholesale-sourcing residual is reported, not fixed. Secret values were never printed.

## Scope

Reviewed: dependency manifests (`ci/requirements-ci.txt`, `pins/images.lock`), Dependabot configuration and server-side alert/update state, CI secret scanning (gitleaks tree + history, `automation/validation/secret_scan.py`, `.gitleaks.toml`), credential handling (`.env.example`, `.gitignore`, live modes of `/home/user/.env`, `/home/user/.config/falcon/capture.env`, `/srv/falcon/secrets`), rotation records (`docs/security/CREDENTIAL_ROTATION_REGISTER.md`, `INHERITED_CREDENTIAL_ROTATION.md`), supply-chain gates (`check_compose_digests.py`, `sbom_coverage_check.sh`, `pins/supply-chain-waivers.json`), Docker base image (`compose/central/opensearch-s3.Dockerfile`), GitHub Actions pinning, and delivery artifacts (`PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `review-package/MANIFEST.sha256`, `PACK_*`). Not reviewed: image vulnerability contents (SBOM domain), the edge repository's supply chain, live process environments.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `ci/requirements-ci.txt` | manifest | only third-party Python deps | hash-pinned pyyaml 6.0.3 + zizmor 1.30.1 (`--require-hashes`) |
| `pins/images.lock` | lockfile | 24 pinned images (JSON) | digests recorded 2026-09-20..10-01 |
| `.github/dependabot.yml` | config | dependency updates | github-actions + pip (/ci), weekly |
| GitHub API: `vulnerability-alerts`, `dependabot/alerts`, `automated-security-fixes`, `secret-scanning/alerts`, `code-scanning/alerts`, `dependency-graph/sbom` | live state | server-side dependency security | alerts on; security updates off; secret/code scanning plan-gated; dependency graph available |
| `.gitleaks.toml`, `gitleaks_history_check.sh`, `secret_scan.py` | scanners | secret detection | pinned gitleaks 8.30.1 in CI; curl allowlist regression test |
| `docs/security/{CREDENTIAL_ROTATION_REGISTER,INHERITED_CREDENTIAL_ROTATION}.md` | docs | rotation + vendored residual | 20/20 PENDING (2026-10-04); docs claim 28 scripts |
| `automation/validation/lib/env_key.sh`, `ci/validate.py:278-303` | code | first-party single-key reads | 41 call sites; `.env` sourcing blocked |
| `pins/supply-chain-waivers.json`, `check_compose_digests.py` | gate | digest/vuln waivers | expiring 2026-12-31 |
| `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `review-package/MANIFEST.sha256`, `PACK_*.txt`, `verify_delivery.sh` | delivery | artifact binding | published copy stale (SC-P3-001) |
| Live modes: `/home/user/.env`, `capture.env`, `/srv/falcon/secrets` | host | secret handling | 0600/0600/0700 |

## Verification Performed

| Claim | Method | Outcome |
|---|---|---|
| Local supply-chain/secret checks pass at f5cb7c9 | `FALCON_EVIDENCE_OPTIONAL=1 python3 ci/validate.py --only secret-scan,credential-sourcing,compose-digests,sbom-vuln,sbom-hashes,license,lock-age,digest-binding` | supported: `validation_failures=0` |
| Dependabot alerts are enabled (SC-P2-001 fixed) | API GET `vulnerability-alerts` + `dependabot/alerts` | supported: 204; 200 with 0 open alerts |
| pip ecosystem is configured and running | `.github/dependabot.yml` + dynamic runs | supported: 'pip in /ci' update runs completed 2026-10-09/10 |
| Dependabot security updates are off | API GET `automated-security-fixes` | supported: {enabled:false} (new finding SC-P3-002) |
| No secret files in the delivered package | grep PACKAGE_MANIFEST.sha256 for `secrets/` and `.env` | supported: 0 `secrets/` paths; only `*.env.example` |
| Owner credential files are protected | `stat` (mode only) | supported: `/home/user/.env` 0600 user:user; capture.env 0600; `/srv/falcon/secrets` 0700 root |
| Rotation estate still pending | register + decision log | supported: 20/20 PENDING (2026-10-04) |
| Vendored wholesale sourcing persists (count changed) | grep `set -a` + source under mct/scripts | supported: 20 files (prior run: 19; docs claim 28) |
| Published manifest copy is stale | sha256sum + diff + git log | supported: PACKAGE_MANIFEST.sha256=4ea4a08f vs declared 749dae85; 14 entries differ (SC-P3-001) |
| gitleaks is absent on this host but present in CI | `command -v gitleaks`; validate.yml:69-85 + run 38110410254 | supported: host MISSING; CI downloads+verifies 8.30.1 and both scans passed |
| Secret scanning / code scanning are plan-gated | API GET | supported: secret-scanning 404; code-scanning 403 (GHAS); compensating gitleaks |
| Dependency graph SBOM available | API GET `dependency-graph/sbom` | supported: 200, 5 packages (zizmor, pyyaml, 2 actions, repo) |

## Executive Summary

The supply chain remains unusually well pinned for a private Free-plan repo: 24 container images digest-locked and cross-checked against every compose root with expiring owner-visible waivers; one hash-pinned Python requirements file; all GitHub Actions pinned to commit SHAs; gitleaks tree and full-history scans in CI plus a repo-specific scanner; a license gate for installed Python tooling; first-party credential reads migrated to single-key reads; and delivery exclusions that keep `secrets/` out of the review package. The SC-P2-001 fix is confirmed live: Dependabot vulnerability alerts are enabled and the pip ecosystem covers ci/requirements-ci.txt (0 open alerts at audit time).

Three gaps are current. First, the inherited credential estate is still 20/20 PENDING and the vendored wholesale-sourcing residual grew from 19 to 20 scripts (a new p40 script), while the docs still claim 28 - the highest-impact secret-handling residual. Second, the published root PACKAGE_MANIFEST.sha256 is stale relative to the declared package manifest and the tree (14 entries; last refreshed at the 2026-10-10 publication), and no CI check compares the two, so a packed-only reviewer gets mismatches (SC-P3-001). Third, Dependabot security updates remain disabled: alerts fire but no automated fix PRs are opened (SC-P3-002). Secret scanning and code scanning are GHAS plan-gated (404/403); gitleaks remains the compensating control, and it is absent on the local check host (DET-P3-003) even though CI runs it pinned.

Recommended next actions: refresh PACKAGE_MANIFEST.sha256 in the publication flow and add the equality check; enable Dependabot security updates (or record the decision); execute the owner rotation register and migrate the 20 vendored scripts at the next MCT import; correct the doc counts.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Python CI deps | `ci/requirements-ci.txt` | pyyaml, zizmor | hash-pinned, Dependabot pip coverage | Low | manual bumps no longer required |
| Image lock | `pins/images.lock` | 24 images | digest-pinned | Low | two floating tags kept for naming (digest-pinned in compose) |
| Compose digest gate | `automation/validation/check_compose_digests.py` | repo@digest vs lock | enforced for compose/, mct/compose/, automation/wazuh/ | Low | expiring waivers |
| Vuln-scan gate | `sbom_coverage_check.sh --require-vuln` | scan or waiver | enforced | Low-Medium | 12 images waived to 2026-12-31 |
| Dependabot | `.github/dependabot.yml` + alerts | updates + alerts | actions+pip updates; alerts on; security updates off | Medium | SC-P3-002 |
| Secret scan | gitleaks + `secret_scan.py` | tree + history | enforced in CI, fail-closed | Low | host lacks gitleaks (DET-P3-003) |
| Credential reads | `env_key.sh` | single-key reads | 41 call sites | Low | no whole-file sourcing in first-party tree |
| Vendored scripts | `mct/scripts/**` | imported ops scripts | 20 wholesale-source env files | Medium | vendored no-patch policy |
| Rotation | `CREDENTIAL_ROTATION_REGISTER.md` | 20 classes | 20/20 PENDING | Medium | owner-gated |
| Dockerfile | `compose/central/opensearch-s3.Dockerfile` | local S3-enabled image | base digest matches lock | Low | no hadolint (DET-P3-005) |
| Delivery manifests | `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `review-package/MANIFEST.sha256` | binding | digest+package manifest consistent; published copy stale | Low-Medium | SC-P3-001 |
| Delivery exclusions | `build_review_package.sh` | review package | secrets excluded | Low | verified in manifest |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 4 | ci/requirements-ci.txt hash-pinned | single Python manifest only (by design) | keep |
| Lockfiles | 4 | pins/images.lock 24 digest entries; requirements hashes | two floating tag names retained | owner/policy decision |
| Workspace dependencies | 3 | no workspaces; vendored mct tree | vendored policy not enforced (EVOL-P1-002) | MCT import policy |
| Unused/duplicate/deprecated deps | 3 | small dependency surface | vendored tree unmanaged | periodic review |
| Native/build deps | 3 | docker/compose on host; no build deps in CI | n/a | keep |
| Transitive risk indicators | 3 | trivy scans static/committed; 12 waived to 2026-12-31 | stale scans (2026-09-22) | refresh before waiver expiry |
| Dependabot/Renovate | 4 | alerts on; 2 ecosystems; runs succeeded | security updates off | enable or record decision |
| Package scripts/postinstall | 4 | none | n/a | keep |
| Docker base images | 4 | Dockerfile base digest matches lock | vendored mct compose unpinned under waiver | waiver review 2026-12-31 |
| GitHub Actions deps | 5 | SHA-pinned actions in validate.yml | none | keep Dependabot actions updates |
| Environment examples | 4 | .env.example names only | none | keep |
| Secret-like strings | 3 | gitleaks tree+history+allowlist regression PASS at f5cb7c9 | secret scanning plan-gated; gitleaks missing on check host | install gitleaks on the check runner |

## Detailed Review

### Item: Dependency manifests and lockfiles
- Evidence: `ci/requirements-ci.txt:7-8`; `pins/images.lock` (24 images); `.github/dependabot.yml`.
- What it does: hash-pinned Python tooling; digest-locked images cross-checked by `check_compose_digests.py`.
- Current controls: `--require-hashes`; compose-digest gate with expiring waivers; Dependabot version updates.
- Missing controls: security-update PRs; dependency-review enforcement (GHAS).
- Risks: a vulnerable dependency alerts but does not auto-fix (SC-P3-002).

### Item: Secret handling and scans
- Evidence: `.gitleaks.toml`; validate.yml:69-85; run 38110410254 steps 8-10; `.env.example`; live modes.
- What it does: gitleaks tree + full-history scans with documented allowlists; `secret_scan.py` in validate; curl allowlist regression test.
- Current controls: fail-closed scans in CI; 0600/0700 file modes; delivery exclusions.
- Missing controls: GitHub secret scanning (GHAS); gitleaks on the check host.
- Risks: rotation debt + wholesale sourcing (SC-P2-002).

### Item: Delivery artifact binding
- Evidence: PACKAGE_DIGEST.txt; review-package/MANIFEST.sha256 (749dae85); PACKAGE_MANIFEST.sha256 (4ea4a08f); verify_delivery.sh:38; check_digest_binding.
- What it does: binds evidence/package manifests to the declared commit; verify_publication_chain passes (0 failures).
- Missing controls: equality check between the published copy and the bound manifest.
- Risks: packed-only reviewer mismatches (SC-P3-001).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SC-001 | Package manifests | requirements-ci.txt | hash pins | none | P3 | keep |
| SC-002 | Lockfiles | images.lock | digest pins + gate | waivers expire 2026-12-31 | P3 | refresh |
| SC-003 | Workspace deps | mct vendored | import policy docs | not enforced | P2 (EVOL-P1-002, owner-accepted) | policy wave |
| SC-004 | Dependabot | dependabot.yml; API | alerts + 2 ecosystems | security updates off | P3 | enable/record |
| SC-005 | Secret scans | gitleaks; secret_scan.py | fail-closed in CI | host tool missing; GHAS gated | P3 | install on check host |
| SC-006 | Rotation estate | register | none (20/20 pending) | owner windows | P2 | execute rotations |
| SC-007 | Vendored sourcing | grep 20 files | documented residual | 20 scripts wholesale-source | P2 | single-key migration |
| SC-008 | Delivery binding | digest/manifests | digest binding in CI | published copy stale | P3 | refresh + equality check |

## Findings

### SC-P2-002 - Inherited credential estate still pending rotation; 20 vendored scripts source credential files wholesale
- Severity: P2; Confidence: High; Area: SC; Status: still-open (prior SECRET-P2-001)
- Evidence: register 20/20 PENDING; grep 20 files; docs claim 28; first-party tree remediated; live modes verified.
- Impact: inherited credentials remain valid indefinitely; one captured process environment leaks every key.
- Fix: execute the owner rotations; migrate the 20 scripts; correct the docs. Owner: owner + vendored maintainer. Effort: L. Dependencies: owner windows; MCT import policy.

### SC-P3-001 - Published PACKAGE_MANIFEST.sha256 is stale vs the declared package manifest; no CI check compares them
- Severity: P3; Confidence: High (reproduced); Area: SC; Status: open (new)
- Evidence: digest 749dae85 vs shipped 4ea4a08f; 14 differing entries; last refresh 75c3466; verify_delivery.sh:38; check_digest_binding scope.
- Impact: packed-only verification of the delivery fails; the delivered artifact set is not self-consistent.
- Fix: refresh in the publication round; add the equality check; decide the pack-verification cadence. Owner: CI/delivery owner. Effort: S.

### SC-P3-002 - Dependabot security updates remain disabled after alerts were enabled
- Severity: P3; Confidence: High (live API); Area: SC; Status: open (new)
- Evidence: automated-security-fixes {enabled:false}; alerts enabled; no decision record.
- Impact: vulnerable dependencies alert but do not produce fix PRs.
- Fix: enable the setting or record the decision. Owner: repo owner. Effort: S.

## Prior-Run Comparison (falcon-20261009-2117-full-08e20d1 @ 08e20d1, statuses per the 2026-10-11 verification register)

| Prior item | Prior status | Current verification (f5cb7c9, 2026-10-11) | Disposition |
|---|---|---|---|
| SC-P2-001 Dependabot alerts disabled; no pip ecosystem | verified-fixed (2026-10-09) | alerts enabled (204); pip ecosystem present and running; 0 open alerts | verified-fixed holds; residual security-updates toggle filed as SC-P3-002 |
| SC-P2-002 (SECRET-P2-001) rotation pending + vendored sourcing | open | 20/20 PENDING; 20 vendored files (was 19); docs still claim 28 | re-filed as SC-P2-002 |
| DET-P3-003 gitleaks not installed (secret scan skipped) | open | host `command -v gitleaks` MISSING; CI runs pinned gitleaks and passed at f5cb7c9 | tracked (DET area); not re-filed |
| DET-P3-004 unpinned vendored images | open | 29 unpinned refs in mct/compose covered by the expiring blanket waiver | tracked; not re-filed |
| DET-P3-005 hadolint not installed | open | host MISSING; single Dockerfile base digest matches lock | tracked; not re-filed |
| SUPPLY-P1-001/002 digest + vuln gates | verified-fixed (earlier) | local `--require-vuln --vuln-waivers` PASS; 24/24 covered | holds |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unrotated inherited credentials | Medium | Medium | credential misuse | register 20/20 PENDING | owner rotation windows |
| Vendored whole-file env sourcing | Medium | Low-Medium | full-file secret leak | 20 files grep | single-key migration |
| Stale published manifest misleads reviewers | Low | Medium | delivery verification fails | SC-P3-001 | refresh + check |
| Vulnerable dependency with no fix PR | Medium | Low-Medium | known-vulnerable dependency in use | SC-P3-002 | enable security updates |
| Stale/waived vuln scans | Low-Medium | Medium | vulnerable image deployed | waivers to 2026-12-31 | refresh before expiry |
| Secret-scan tool gap on the check host | Low | Low | local scan skipped | DET-P3-003 | install gitleaks |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- SC-P3-002: enable Dependabot security updates (or record the decision).
- SC-P3-001: refresh PACKAGE_MANIFEST.sha256 from the declared package manifest and add the equality check to the publication/CI flow.

### This Month
- SC-P2-002: start the owner rotation register (highest-value classes first); schedule the vendored migration at the next MCT import; correct the 28->20 doc counts.
- Refresh the 12 waived trivy scans before 2026-12-31.

### Later / Platform Evolution
- Install gitleaks on the local check host; consider `docker` ecosystem in Dependabot; keep the dependency graph enabled for future dependency review.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Refresh PACKAGE_MANIFEST.sha256 | restores packed-only verification | PACKAGE_MANIFEST.sha256 (from review-package/MANIFEST.sha256) | sha256 equals PACKAGE_DIGEST value |
| Enable Dependabot security updates | automated fix path | repo settings | API enabled:true |
| Update rotation docs 28 -> 20 | docs match reality | INHERITED_CREDENTIAL_ROTATION.md | grep |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Rotate the 20 inherited credential classes | P2 | owner | L | owner windows |
| Vendored single-key migration | P2 | vendored maintainer | M | next MCT import |
| Scheduled trivy refresh job | P3 | CI owner | M | runner with docker+network |
| Published-manifest equality check | P3 | delivery owner | S | none |

## Suggested Tests

- A validate check that fails when the published PACKAGE_MANIFEST.sha256 differs from the bound review_package_manifest_sha256.
- A regression test asserting no tracked script combines `set -a` with a credential-file source (extend the existing `/home/user/.env` rule to `/srv/falcon/secrets`).
- A waiver-expiry test (exists) plus a calendar reminder fixture.

## Suggested Documentation Updates

- `docs/security/CREDENTIAL_ROTATION_REGISTER.md` and `INHERITED_CREDENTIAL_ROTATION.md`: update the vendored count (28 -> 20) and the 2026-10-11 status.
- `docs/security/OWNER_ENV_INVENTORY.md`: note the Dependabot security-updates decision once made.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was the published PACKAGE_MANIFEST.sha256 meant to be refreshed in every publication round? | fixes SC-P3-001 direction | owner/delivery statement |
| Are the two floating tag names (`cloudflared:latest`, `nginx:stable`) acceptable long-term given digest pins? | policy consistency | owner/policy decision |
| Which MCT import will carry the single-key migration? | closes the vendored residual | mct/VENDORING.md plan |

## Limitations

- No secret values were read or printed; checks were structural (modes, names, patterns, API toggles).
- The vendored MCT tree is imported under a no-silent-patch policy; the count is a grep reproduction, not an execution test.
- The GitHub API cannot show whether Dependabot security updates were ever enabled in the past.

## Appendix

Vendored files that combine `set -a` with sourcing a credential env file (grep reproduction, 2026-10-11; 20 files):

```
mct/scripts/active-response-audit.sh
mct/scripts/alert-volume-by-rule.sh
mct/scripts/backup-dr-audit.sh
mct/scripts/credential-rotation-validation.sh
mct/scripts/full-stack-healthcheck.sh
mct/scripts/iris-db-dump.sh
mct/scripts/p33-core-alert.sh
mct/scripts/p39-iris-delivery-check.sh
mct/scripts/p40-field-growth-check.sh   (new since the prior run)
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

Manifest divergence (SC-P3-001) samples:

```
entry                              review-package/MANIFEST.sha256   PACKAGE_MANIFEST.sha256   actual tree
automation/validation/export_monitor_metrics.sh   7aaff286...        92a26b2a...               7aaff286...
automation/validation/phase6_backup_restore.sh    0595b2ba...        60b6ec78...               0595b2ba...
bootstrap/80-offsite-backup.sh                    47fa22b6...        108de2c7...               47fa22b6...
```

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P2-002 | P2 | Inherited credential estate is still pending rotation and 20 vendored scripts source credential files wholesale |
| SC-P3-001 | P3 | Published PACKAGE_MANIFEST.sha256 is stale vs the declared package manifest; no CI check compares them |
| SC-P3-002 | P3 | Dependabot security updates (automated fix PRs) remain disabled after alerts were enabled |
