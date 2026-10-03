# Supply Chain, Dependency, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: `falcon-build` (central), `falcon-edge-build` (edge), `/home/user/falcon-edge-delivery`
- Branch: `main` (both). Commits: falcon `8282d3f`; edge `f1c5def` (run anchored at edge `45dfed0`; edge advanced 5 commits mid-audit)
- Generated at: 2026-09-30 · Auditor: DeepSeek V4.1 Flash (subagent, prompts 11 + 35) · Area code: SC
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/11_supply_chain_dependency_secrets.md`
- Scope limitations: read-only; no live-host/Docker/network execution; no GitHub API (CI status unverified); root-owned delivery files unreadable; secret values redacted (path + type only).

## Scope

Reviewed: manifests/lockfiles (none by design — stdlib Python), image pins and compose digests, GitHub Actions pins, Dependabot, base images/Dockerfiles, SBOM/vuln artifacts, CI secret scanners and their allowlists, release/delivery artifacts (central archive; edge delivery: images, credentials, SSH keys, secrets backups, SBOM, signed manifest), redaction/exception ledgers, and prior-run findings REV-P3-009/010, ND-P2-001/003/017, INTG-P2-003. Not reviewed: live host, root-only backup contents, GitHub-side settings/runs, credential liveness (no calls made).

## Evidence Reviewed

- `falcon-build/automation/validation/{secret_scan.py,secret_scan_history.sh,scan_disposition.py,verify_pack.py,verify_delivery.sh,verify_publication_chain.sh,sbom-and-vuln.sh,install-trivy.sh}`; `ci/validate.py`; `.github/workflows/validate.yml`; `.github/dependabot.yml`; `.gitleaks.toml`
- `falcon-build/pins/{images.lock,verify-digests.sh,pull-and-record.sh}`; `compose/**/*.yml`; `compose/central/opensearch-s3.Dockerfile`
- `falcon-build/sbom/**`; `PACKAGE_DIGEST.txt`; `PACKAGE_MANIFEST.sha256`; `PACK_VERIFICATION_NOTES.txt`; `review-package/MANIFEST.sha256`
- `falcon-build/automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf`, `.../wazuh_dashboard/wazuh.yml`; `ledgers/{redactions.md,exception_register.md,decision_log.md,gate_ledger.csv}`; `docs/security/SCANNER_ALLOWLIST_CHANGES.md`
- `/home/user/falcon-review-delivery-2026-09-30.tar.gz` (+ `.sha256`); `falcon-edge-build/ci/{secret_scan.py,validate.sh}`; `.gitleaks.toml`; `docs/security/*`; `.github/workflows/*`; `automation/validation/{bake_lab_test_image.sh,build_release_manifest.py,build_review_package.sh,verify_review_package.sh,check_upstream_drift.sh}`
- `/home/user/falcon-edge-delivery/*` (45 files); prior-run `runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/{findings.json,lens_*.md,source_reports/*}`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `secret_scan.py` on `ossec.conf` | execution | Blind-spot check | `NO_FINDINGS` — 64-hex `<api_key>`, 32-char `<key>`, UUID key unmatched |
| `secret_scan_history.sh` (falcon) | execution | ND-P2-003 | exit 1, 22 findings, `REVIEW_REQUIRED`, 1 unclassified file (`wazuh.yml`) |
| `verify_pack.py` (tree manifests) | execution | ND-P2-001 | `mismatched=37 missing_from_pack=957 INCOMPLETE` (prior 23/933) |
| `verify_pack.py` (pack-embedded manifests) | execution | Packed-only path | 16 mismatched / 3 missing; embedded manifests 1,109 entries vs 2,067 current |
| `sha256sum -c` all edge delivery sidecars | execution | Release binding | Manifest sidecar **FAIL** (`18681751…` vs actual `3fa4a49c…`); lab8 SBOM sidecar non-portable (`/home/runner/...`) |
| `sha256sum -c MANIFEST.sha256` (repo + archive review-package); archive digest; `tar tzf` | execution | Package integrity | PASS both (2,067 entries); archive digest OK; `PACKAGE_DIGEST` byte-identical; `ossec.conf` shipped (hash == HEAD); 0 `.cdx.json` |
| Edge `verify_review_package.sh` on `…044418-0b83acc` | execution | Package + scan | PASS manifest (876), PASS exclusions, PASS secret scan (856 files) |
| Secrets-backup `file`/`tar tzf` | inspection | REV-P3-010 | User backup = plain gzip tar of `ca/ca.key.pem`, operator keys, `control.db`; newer root backup unreadable |
| `uses:` pin grep; compose-vs-lock compare; `git grep PRIVATE KEY` | inspection | Supply-chain pins/keys | All actions SHA-pinned; 18 images digest-pinned, 6 without SBOM; only detector strings found |

## Executive Summary

The dependency surface is small and deliberately pinned: stdlib-only Python, no vendored code, every compose image digest-pinned and locked, every GitHub Action SHA-pinned with weekly Dependabot, and the edge base image verified against its official checksum. The risk sits in secrets and verification. The Wazuh config round shipped integration credentials inside the central delivery (API-P0-001 — scope re-confirmed, not duplicated here), and the scanners that should have caught them have systemic blind spots (XML values unmatched; any 64-hex value allowlisted; history scan outside CI; gitleaks suppresses whole trees). The history scan now exits 1 with an unclassified file while the gate ledger claims a clean run. The edge delivery is still a credential-bearing surface (SSH keys, credentials, unencrypted backups containing the CA private key) with hashes published in the signed manifest, the newer root-owned backup excluded from the artifact list, the shipped repomix pack stale, and a manifest sidecar that fails verification. Fixes are scoped and mostly small.

## Inventory

| Item | Path / symbol | Purpose | State | Risk | Notes |
|---|---|---|---|---|---|
| Runtime manifests | (none) | stdlib Python 3.11+ | Intentional | Low | Edge `DEPENDENCY_POLICY.md` §1 |
| Image lock | `pins/images.lock` | 18 digest-pinned images | Fresh 09-27; no license field | Medium | 6 lack SBOM |
| GitHub Actions | both workflows | CI | All SHA-pinned + Dependabot | Low | Strength |
| CI tool fetches | `validate.yml` (both) | actionlint/shellcheck/ruff/gitleaks | Version URLs, no checksum | Medium | `install-trivy.sh` verifies (contrast) |
| Secret scanners | falcon/edge `secret_scan.py`, gitleaks | tree/history scans | Pattern gaps; gitleaks CI-only | High | SC-P1-001 |
| Delivery secrets (edge) | `falcon-edge-secrets-backup-*.tar.gz`, `-ssh-key`, `-credentials.txt` | restore/admin | 0600, **unencrypted**, hashed in manifest | High | SC-P2-001 |
| Repomix pack | `/home/user/falcon-repomix.md` | packed-only review | Stale 09-27; INCOMPLETE | Medium | SC-P2-002 |
| Secrets store | `/home/user/falcon-edge-secrets/` | CA/operator/signing | Stray 0-byte `control.db`; 10 unredeemed tokens | Low | SC-P3-001 |
| Redactions ledger | `ledgers/redactions.md` | redaction record | No Wazuh-config entry | High | API-P0-001 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 4 | No runtime deps; stdlib-first policy | No CI assertion | Add invariant check |
| Lockfiles | 4 | `pins/images.lock` digest-pinned | No digest cross-check; manual verify | Extend pin check |
| Workspace dependencies | 5 | Two repos + pin docs | Manual cross-repo updates | Keep drift checks |
| Unused/duplicate/deprecated | 3 | Images audited; reserved redis | No usage automation | Patch-window review |
| Native/build deps | 3 | Pi image apt in SBOM | Versions only in image | Keep SBOM source |
| Transitive risk | 2 | Trivy 09-20/22 | Stale; 6/18 images unscanned; no gate | Prompt 35 |
| Dependabot/Renovate | 4 | Weekly actions PRs both repos | No other ecosystems | Optional docker ecosystem |
| Package scripts/postinstall | 4 | No npm; overlay no downloads | apt unpinned by design | Document baseline |
| Docker base images | 4 | Digest pins + lock | SBOM/vuln gaps | SBOM report |
| GitHub Actions deps | 5 | 100% SHA-pinned + zizmor + drift | Tool checksums | SC-P2-004 |
| Environment examples | 2 | None; prose docs only | No `.env.example` | Add examples |
| Secret-like strings | 1 | API-P0-001 shipped; scan clean | Blind spots + process | SC-P1-001 |

## Detailed Review

### Item: Secret scanning
- Evidence: `secret_scan.py:14-24` patterns, `:32` `ALLOW_VALUE=^[0-9a-f]{64}$`, `:26-31` path allowlist; edge `ci/secret_scan.py:74` skips `evidence/**/P0-G07/**` in code; falcon `.gitleaks.toml` tree-wide `review-package/.*` plus `evidence/.*`/`sbom/.*`; history scan absent from local/CI validation. Gap: demonstrated inability to catch Wazuh-style XML credentials; undispositioned history drift. Fix/tests: SC-P1-001 / SC-P2-003 + fixture tests.

### Item: Delivery/release secret material (edge)
- Evidence: manifest artifact list; `build_release_manifest.py:26-27,58-62` (secret suffixes included, unreadable backup skipped); `bake_lab_test_image.sh:365-456`; backup tar index (CA/operator keys). Gap: unencrypted key material in the release surface; newer backup unbound. Fix: move/encrypt backups; fail or explicitly exclude unreadable artifacts.

### Item: Packed-only review (falcon)
- Evidence: `verify_pack.py`; pack dated 09-27 (sha `22487ccc…`) shipped in the delivery; P8-G01 claims packed-only PASS (991/991) with 2,067 entries current. Gap: pack never rebuilt in the publication flow. Fix: rebuild at package commit; wire into `verify_publication_chain.sh`.

### Item: Prior-run finding re-verification

| Prior finding | Status | Evidence |
|---|---|---|
| REV-P3-009 (no public key in delivery) | `still-open` (bundle part fixed) | No pubkey file in delivery; `falcon-agent-0.1.1-lab.tar.gz` now in manifest |
| REV-P3-010 (keys + unencrypted backups in delivery; INTG-P2-003) | `still-open` | 0600 files present; CA key in gzip tar; hashes in signed manifest; `build_release_manifest.py:58-62` skips the root-owned newer backup (only its `.sha256` listed) |
| ND-P2-017 (release set not coherent) | `partially-fixed` | Bundle in manifest; review package includes `image/`; residual: stale sidecar, review pkg `0b83acc` precedes release `155f244` |
| ND-P2-003 (history scan mismatch) | `still-open` (22 vs 20) | exit 1, `REVIEW_REQUIRED`; ledger says `history_scan_exit=0` |
| ND-P2-001 (stale pack) | `still-open` / regressed | 37 mismatched / 957 missing (prior 23/933) |

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SC-001 | Package manifests | stdlib-first policy | Documented | No CI invariant | P3 | Assert no runtime deps |
| SC-002 | Lockfiles | `pins/images.lock` | Digest-pinned | No full-ref compare | P3 | Extend pin check |
| SC-003 | Workspace deps | Two repos, pin docs | Documented pairing | Cross-repo drift | P3 | Keep drift checks |
| SC-004 | Unused/deprecated | Images audited | Phase-gate review | No automation | P3 | Patch-window review |
| SC-005 | Native/build deps | Pi apt in SBOM | SBOM records | Image-only | P3 | Keep SBOM |
| SC-006 | Transitive risk | `vuln-summary.csv` 09-22 | One trivy run | Stale/partial | P2 | SBOM report |
| SC-007 | Dependabot | Both configs | Weekly actions | No other ecosystems | P3 | Optional docker |
| SC-008 | Package scripts | No npm; overlay clean | Review | apt unpinned | P3 | Document |
| SC-009 | Docker bases | Compose digests | All pinned | 6 unscanned | P2 | SBOM-P2-002 |
| SC-010 | GHA deps | SHA pins + drift | Strong | Tool checksums | P2 | SC-P2-004 |
| SC-011 | Env examples | (absent) | Docs prose | No samples | P3 | Add examples |
| SC-012 | Secret-like strings | API-P0-001; scanners | Redaction + scans | Blind spots; shipped literals | P1 | SC-P1-001 |

## Findings

### Finding ID: SC-P1-001 - Secret-scan controls have systemic false-negative blind spots; a P0 credential set shipped through them

- Severity: P1 · Confidence: High · Area: SC (secret scanning)
- Evidence: `automation/validation/secret_scan.py:19` (`api_key_assignment` needs `[:=]`, so XML `<api_key>…</api_key>` never matches), `:32` (`ALLOW_VALUE = ^[0-9a-f]{64}$` permits every 64-hex value); `ossec.conf:38,329,349` (64-hex API key, 32-char cluster key, UUID key) scanned `NO_FINDINGS`; falcon `.gitleaks.toml` tree-wide allowlist `review-package/.*` plus `evidence/.*`/`sbom/.*`; edge `ci/secret_scan.py:74` skips `evidence/**/P0-G07/**` undocumented; history scan not in `ci/validate.py`/workflows. Cross-reference **API-P0-001** (do not duplicate).
- What is happening: the only automatic scans cannot see Wazuh-style XML credentials and suppress whole trees, so a committed credential set passed every check and reached the 2026-09-30 delivery archive.
- Why it matters / User / business impact: the "scans pass" control is weaker than believed and the production-verdict evidence chain relies on it; repeats of API-P0-001 ship silently · Security / privacy / reliability impact: confirmed credential disclosure in repo + delivery; systemic detection failure.
- Recommended fix: rotate/redact per API-P0-001; add XML tag, `K:<hex>` and 32-char key patterns; restrict the 64-hex allowlist to digest lines; run tree+history+gitleaks in CI; scope gitleaks allowlists to lines; document the P0-G07 skip.
- Suggested validation: injected fixtures (`<api_key>` 64-hex, `<key>` 32-char, `K:` hex) are caught in tree and history modes.
- Owner suggestion: falcon + edge maintainers (security) · Effort estimate: M · Dependencies: API-P0-001 rotation
- Status: open

### Finding ID: SC-P2-001 - Private keys, credentials, and unencrypted secrets backups remain inside the edge release surface; one backup is outside the signed artifact list

- Severity: P2 · Confidence: High · Area: SC (delivery secrets)
- Evidence: `falcon-edge-secrets-backup-20260930T011054Z.tar.gz` is a plain gzip tar (no encryption) containing `ca/ca.key.pem`, `operator.key.pem`, `control.db`; `...lab8-ssh-key` (OpenSSH private key) and `...credentials.txt` in the same directory; `build_release_manifest.py:26-27` includes these suffixes and `:58-62` skips the root-owned `…T011356Z.tar.gz` as unreadable while its `.sha256` is listed; all hashes published in the signed manifest; also stray 0-byte `control.db` in `/home/user/falcon-edge-secrets/`.
- What is happening: the delivery directory doubles as the secrets-backup destination; one backup is unencrypted and one is not bound by the manifest it partly describes.
- Why it matters / User / business impact: a single directory copy leaks CA/operator keys and device credentials, and delivery/review copies must be treated as credential material · Security / privacy / reliability impact: high-value exposure surface; prior REV-P3-010 / INTG-P2-003 unresolved.
- Recommended fix: move backups out of the delivery dir or encrypt (age/gpg) with keys stored separately; fail (not skip) on unreadable artifacts or record explicit exclusions; clean the stray file and document the secrets layout.
- Suggested validation: delivery-set test fails when a secret file is present; manifest covers every artifact or lists exclusions; `sha256sum -c` passes portably.
- Owner suggestion: edge maintainer · Effort estimate: M · Dependencies: owner backup-storage decision
- Status: still-open (prior REV-P3-010, INTG-P2-003)

### Finding ID: SC-P2-002 - The delivered repomix pack is stale; packed-only verification is INCOMPLETE and the P8-G01 claim is unsupported

- Severity: P2 · Confidence: High · Area: SC (release integrity)
- Evidence: `/home/user/falcon-repomix.md` dated 2026-09-27, embedded byte-identical in `/home/user/falcon-review-delivery-2026-09-30.tar.gz`; `verify_pack.py` at `f1c5def`: `mismatched=37 missing_from_pack=957 INCOMPLETE` (prior 23/933); pack-embedded manifests 1,109 entries vs 2,067 current; P8-G01 note claims packed-only PASS (991/991).
- What is happening: the pack was not rebuilt for the 09-30 publication and the publication flow never runs `verify_pack.py`.
- Why it matters / User / business impact: a pack-only reviewer cannot reproduce the delivered tree; the ledger claim contradicts the artifact; external review reproducibility fails · Security / privacy / reliability impact: trust/auditability, not direct exploit.
- Recommended fix: rebuild the pack at the package commit; add `verify_pack.py` to `verify_publication_chain.sh`/`verify_delivery.sh`; fail publication when the pack predates the package commit.
- Suggested validation: CI step asserting pack verification PASS against `PACKAGE_MANIFEST.sha256` at HEAD.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: repomix tool
- Status: regressed (prior ND-P2-001)

### Finding ID: SC-P2-003 - History secret-scan drift is not detected by the change flow; the gate ledger still records a clean history scan

- Severity: P2 · Confidence: High · Area: SC (scan enforcement)
- Evidence: `secret_scan_history.sh` at `f1c5def`: `history_scan_exit=1`, 22 findings, `disposition_conclusion=REVIEW_REQUIRED`, 1 unexpected file (`automation/wazuh/.../wazuh.yml`); `ledgers/gate_ledger.csv` P1-G06 claims `history_scan_exit=0, NO_FINDINGS`; `ci/validate.py`/workflows run the tree scan only; the 2 `wazuh.yml` hits are redaction markers matching the password pattern (false positives, undispositioned).
- What is happening: history results degrade silently between runs; the ledger claim contradicts the current artifact.
- Why it matters / User / business impact: "scans pass" cannot be trusted at the current commit; real findings could hide in undispositioned noise; auditability gap for historical leaks · Security / privacy / reliability impact: coverage/evidence-integrity gap.
- Recommended fix: add the history scan (or gitleaks `--log-opts`) to `ci/validate.py`/publication; disposition the 22 findings in `SCANNER_ALLOWLIST_CHANGES.md`; append a corrected P1-G06 note.
- Suggested validation: CI fails when history findings lack disposition; ledger note matches the artifact.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: none
- Status: still-open (prior ND-P2-003)

### Finding ID: SC-P2-004 - CI tool downloads are executed without checksum verification and some CI dependencies are unpinned

- Severity: P2 · Confidence: High · Area: SC (CI supply chain)
- Evidence: `falcon-build/.github/workflows/validate.yml:39,46,58,65` and `falcon-edge-build/.github/workflows/validate.yml` fetch actionlint/shellcheck/ruff/gitleaks tarballs and execute them with no `sha256sum -c`; `pyyaml` (both) and `coverage` (edge) installed unpinned; `zizmor==1.30.1` version-only pin; contrast `install-trivy.sh` (version + checksum).
- What is happening: integrity of CI-critical binaries rests on TLS + release immutability.
- Why it matters / User / business impact: a replaced upstream asset runs in CI with build credentials, creating a CI/build compromise path · Security / privacy / reliability impact: supply-chain compromise of build infrastructure.
- Recommended fix: verify published checksums (or vendor binaries); pin pip installs with `==` + `--require-hashes`.
- Suggested validation: workflow step fails when a tool checksum is altered.
- Owner suggestion: both maintainers · Effort estimate: S · Dependencies: upstream checksum files
- Status: open

### Finding ID: SC-P3-001 - Pin verification is manual and does not compare digests between compose and the lock; no environment examples exist

- Severity: P3 · Confidence: High · Area: SC (pinning/onboarding)
- Evidence: `ci/validate.py:77-104` accepts any `repo@sha256` whose repo name is in `pins/images.lock`; `pins/verify-digests.sh` is manual and not in CI; lock entries carry `version_label: unknown`; no `.env.example` in either repo.
- What is happening: a compose digest that disagrees with the lock (and with SBOM/vuln scope) passes validation; env keys are documented only in prose.
- Why it matters / User / business impact: deployed digests can diverge from scanned digests; onboarding cannot reproduce required variables · Security / privacy / reliability impact: low-direct; documentation/coverage gap.
- Recommended fix: compare full `repo@digest` against the lock in `check_compose_pins`; add a lock-freshness date; add redacted `.env.example` files.
- Suggested validation: mutated digest fixture fails; examples parse against the documented key set.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Repeat of API-P0-001 class ships | High | Medium | Credential disclosure | SC-P1-001 | Scanner + CI fix, rotation |
| Delivery-dir copy leaks CA/operator keys | High | Medium | Full lab trust compromise | SC-P2-001 | Encrypt/move backups |
| Pack-only reviewer cannot verify | Medium | High | Review invalidated | SC-P2-002 | Rebuild + CI gate |
| Ledger claims diverge from artifacts | Medium | Medium | False "scans pass" | SC-P2-003 | CI enforcement + append-only notes |

## Recommendations

### Immediate / Release Blocking
1. Execute API-P0-001 remediation (rotate keys, redact, record SHA-256s, rebuild package + delivery).
2. Edge: regenerate manifest sidecar atomically; publish `signing.pub.pem` + keyId; make SBOM checksums basename-only.
### This Week
3. SC-P1-001: extend both scanners (XML, `K:<hex>`, 32-char keys, tightened 64-hex allowlist); add history scan + gitleaks to the local flow.
4. SC-P2-001: encrypt or relocate secrets backups; fix manifest skip/exclusion rules.
5. SC-P2-002: rebuild the pack; add `verify_pack.py` to the publication chain.
6. SC-P2-004: add tool checksums; pin pip installs with hashes.
### This Month
7. SC-P2-003: disposition 22 history findings; append corrected P1-G06 note.
8. SC-P3-001: strengthen digest comparison, lock freshness, env examples.
### Later / Platform Evolution
9. Adopt the SBOM/license gates from prompt 35; add release attestations once a key is published.

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| XML-aware scanner patterns | Catches the Wazuh class | both `secret_scan.py` | Fixture tests |
| Restrict 64-hex allowlist | Closes broadest bypass | `secret_scan.py:32` | Config fixture fails |
| Checksum CI tool downloads | Blocks replaced binaries | both `validate.yml` | Mutated checksum fails |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| History scan in CI + disposition file | P1 | falcon | M | none |
| Secrets-backup encryption/move | P1 | edge | M | owner decision |
| Pack rebuild in publication flow | P2 | falcon | S | repomix |
| Digest cross-check + lock freshness | P3 | falcon | S | none |
| Env example files | P3 | both | S | none |

## Suggested Tests

- Unit: scanner fixtures (XML `<api_key>`/`<key>`, `K:` hex, 64-hex off-digest, marker strings) both scanners.
- CI: `verify_pack.py` gate; weekly digest verify; tool-checksum assertions; history-scan job.
- Security/regression: edge delivery-set test (no private keys/credentials; sidecars match; manifest verifies).
- Manual: Wazuh key rotation drill once redacted.

## Suggested Documentation Updates

- `ledgers/redactions.md`: post-fix Wazuh redactions + rotated fingerprints.
- `docs/security/SCANNER_ALLOWLIST_CHANGES.md` (both): patterns, allowlist tightening, P0-G07 skip rationale, 22-finding disposition.
- Edge `docs/security/DEPENDENCY_POLICY.md`: tool-checksum rule + secrets-backup storage decision.
- New edge `docs/security/DELIVERY_ARTIFACTS.md`: what may appear in the release surface.
- Falcon `docs/architecture/IDENTITY_AND_SECRETS.md`: delivery-dir vs secrets-store boundary.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are the ossec.conf credentials still live? | Rotation scope | Owner/provider check |
| Where may backups live if not the delivery dir? | SC-P2-001 fix | Owner decision |
| Is the stale sidecar consumed anywhere? | Re-sign vs delete | Search scripts/docs |

## Appendix

- Dependency inventory: no runtime manifests; 18 digest-pinned images; 13 SHA-pinned action uses across 5 workflows; Dependabot (actions) both repos.
- Script inventory (supply-chain): `ci/validate.{py,sh}`, `pins/*`, `automation/validation/{secret_scan*,verify_pack,verify_delivery,verify_publication_chain,sbom-and-vuln,install-trivy}.*`, edge `automation/validation/{build_sbom,build_release_manifest,build_review_package,verify_review_package,check_upstream_drift,bake_lab_test_image}.*`.
- Secrets exposure summary: edge delivery (unencrypted backups, keys, credentials — SC-P2-001); falcon Wazuh configs (API-P0-001); no private keys committed outside evidence/detectors.
