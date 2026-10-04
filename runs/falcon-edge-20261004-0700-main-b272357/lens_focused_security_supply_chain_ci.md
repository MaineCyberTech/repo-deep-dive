# Focused security / supply-chain / CI deep-dive - falcon-edge

## Findings

| ID | Severity | Title | Report |
|---|---|---|---|
| GIT-P3-001 | P3 | No repository LICENSE file (deterministic real) | lens_focused_security_supply_chain_ci.md |
| PORT-P3-001 | P3 | Four tracked shell scripts lack the executable bit (deterministic real, impact limited) | lens_focused_security_supply_chain_ci.md |
| PORT-P3-002 | P3 | False positive: '14 CRLF files' are intentional byte-exact evidence (*.out -text) | lens_focused_security_supply_chain_ci.md |
| SEC-P3-001 | P3 | False positive: gitleaks generic-api-key hits are allowlisted public/identifier values | lens_focused_security_supply_chain_ci.md |
| AUTH-P2-001 | P2 | Device mTLS private key is group-readable (0640), contradicting its documented 0600 | lens_focused_security_supply_chain_ci.md |
| SEC-P2-001 | P2 | mTLS clients never verify the control-plane hostname | lens_focused_security_supply_chain_ci.md |
| CI-P2-001 | P2 | bake-image interpolates secrets directly into shell script text | lens_focused_security_supply_chain_ci.md |
| CI-P2-002 | P2 | Branch protection / required checks cannot be enforced; main is only advisory-gated | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P2-001 | P2 | Shipped sensor image auto-applies signed updates without a per-update human gate | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P3-001 | P3 | Dependabot watches only GitHub Actions, not hash-pinned dev dependencies | lens_focused_security_supply_chain_ci.md |
| SEC-P3-002 | P3 | Lab tooling disables SSH host-key and TLS verification | lens_focused_security_supply_chain_ci.md |
| CI-P3-001 | P3 | Documentation overstates the dependabot-merge gate specificity | lens_focused_security_supply_chain_ci.md |
| SEC-P3-003 | P3 | No step-by-step emergency rotation procedure for the CA key / signing seed | lens_focused_security_supply_chain_ci.md |
| CONF-P3-001 | P3 | Lab configs ship permissive defaults (TOFU enrollment; control plane binds all interfaces) | lens_focused_security_supply_chain_ci.md |

---

# Falcon Edge — Focused Security / Supply-Chain / CI Deep-Dive (READ-ONLY)

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261004-0000-falcon-edge-manual (read-only subagent)
- Repository: `falcon-edge` (clone `C:\temp\falcon-edge`)
- Branch: `main`
- Commit SHA: `5ff59fe0b8cfe2cc0acf07de9b49b8d6afa405b2` (short `5ff59fe`, 2026-10-03)
- Commit subject: Merge pull request #16 (audit fix-trust-root branch)
- Domain: security / supply-chain / CI governance / portability
- Prompt pack: `00_SHARED_AUDIT_RULES.md`, `06`, `10`, `11`, `36`, `38`
- Output: `C:\temp\deepdive\falcon-edge\FINDINGS.md`, `findings.json`
- Scope limitations: read-only; no production/lab access; gitleaks/zizmor were not re-run (no network/tool install), so deterministic secret/determinism hits were validated by byte-level and regex evidence instead. No secret values are printed. No Dockerfiles exist in this repo (image build is a Raspberry Pi OS SD-card baker, not a container build), so prompt 36 is largely N/A.

## Scope

Reviewed: `.github/workflows/*`, `.github/dependabot.yml`, `.github/CODEOWNERS`, `.gitattributes`, `.gitleaks.toml`, `requirements-dev.txt`, `ci/secret_scan.py`, `ci/license_check.py`, `ci/validate.sh`, `deploy/*`, `docs/security/*`, `docs/runbooks/*`, `src/falcon_common/x509tools.py`, `src/falcon_control/{http_server,service,tokens,pki,store}.py`, `src/falcon_agent/{identity,client,runner}.py`, `image/overlay/...`, `automation/validation/*`, and the deterministic lens artifacts.

Not reviewed: live GitHub repository settings/API, lab hosts, real secrets, `evidence/` payload bodies (only line- and byte-level checks), third-party CVE databases.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git ls-files -s`, `git ls-files --eol`, raw `git cat-file` bytes | git index | Validate exec-bit and CRLF deterministic hits | Reproduced directly at `5ff59fe` |
| `.gitleaks.toml:18-23` + `.github/workflows/validate.yml:141` | secret scan | Validate gitleaks deterministic hits | Allowlist regexes match both hits (regex test = True) |
| `.github/workflows/*.yml` | CI | Permissions, pins, secret handling, triggers | All actions SHA-pinned; `pull_request` only, no `pull_request_target` |
| `requirements-dev.txt:11-17` | supply chain | Hash pinning | `--hash=sha256:` on pyyaml/coverage/zizmor |
| `src/falcon_agent/identity.py:44,66,79` | AUTH | Device key file modes | Private key written `0o640` |
| `src/falcon_common/x509tools.py:101-112` | TLS | Client identity verification | `check_hostname = False` always |
| `image/overlay/etc/falcon-agent/agent.json:17` + `src/falcon_agent/runner.py:791` | SUPPLY | Unattended update gate | `update_auto_apply: true` shipped |
| `automation/validation/ab_device_drill.sh:33`, `release_skew_check.sh:193`, `unifi_networks.py:57` | lab tooling | TLS/SSH verification | Verification disabled |

## Verification Performed

- `git ls-files -s` — confirmed four `*.sh` files are mode `100644` (no exec bit).
- Raw `git cat-file blob` byte reads — the named `*.out` files do contain embedded CRLF pairs (e.g. 15 pairs in `ED-20/...zero-inventory-scan.out`), while `git ls-files --eol` reports `i/lf` for all 1,113 tracked text entries; `.gitattributes:38` sets `*.out -text` deliberately.
- Python regex test against the embedded allowlist patterns — both gitleaks hits match `raw section key part: ...` / `token_id: ...` allowlist rules (`True`, `True`).
- Confirmed no `LICENSE`/`COPYING`/`UNLICENSE` in `git ls-files`.
- Confirmed no `Dockerfile` / `docker-compose` tracked.
- Reproduced prior-audit fixes still present: hash-pinned `requirements-dev.txt`; gitleaks full-history scan; curl tool downloads SHA-256 verified; `publish-release` fail-closed provenance; `falcon-update-verify.py` root-side signature/archive verification; `_authorize` role checks from certificate fingerprint.

## Executive Summary

`falcon-edge` is a security-mature private lab repository. Actions are SHA-pinned with `persist-credentials: false`; every workflow declares least-privilege `permissions`; CI downloads tools pinned by embedded SHA-256; `requirements-dev.txt` is hash-pinned; gitleaks scans full history; release publishing is fail-closed on a signed ed25519 manifest; and the root-side updater (`falcon-update-verify.py`) is a genuinely hardened privileged-consumer of agent-written input (signature verify against a root-owned key, path confinement, `O_NOFOLLOW` TOCTOU copy, archive-member/setuid rejection, rollback). The control plane resolves operator/sensor roles from certificate fingerprints, not CN strings, with fail-closed trust-root pinning.

The remaining gaps are narrow and mostly about *residual* trust and documentation: TLS clients do not verify the server hostname; the device mTLS private key is deliberately group-readable (`0640`) while the docstring says `0600`; the shipped image auto-applies signed agent updates (no per-update human gate); one CI workflow interpolates secrets directly into shell text; lab tooling disables SSH/TLS verification; and branch protection/required checks remain unenforceable on the free private plan (owner-accepted). No P0/P1 was found. All four deterministic hits were validated: two are real-but-low, two are false positives already triaged.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Workflows | `.github/workflows/{validate,bake-image,publish-release,dependabot-merge,boot-smoke}.yml` | CI/deploy | `validate` on push/PR; others manual/scheduled | Low | No `pull_request_target`; no `curl \| bash` |
| Action pinning | `validate.yml:40,44,...` | Supply chain | All `uses:` SHA-pinned | Low | Dependabot keeps pins current |
| Permissions | each workflow | Least privilege | `contents: read`; write only for publish/merge | Low | — |
| pip dev deps | `requirements-dev.txt` | CI tooling | Pinned `==` + `--hash=sha256` | Low | Installed `--require-hashes --only-binary` |
| Secret scan | `.gitleaks.toml`, `ci/secret_scan.py`, `validate.yml:130-141` | Secrets | gitleaks full history + working tree | Low | Reviewed allowlists |
| Operator authz | `src/falcon_control/service.py:334-380,599-635` | AUTH | Role from SHA-256 cert fingerprint; path/identity match | Low | CN never grants operator |
| Sensor TLS | `src/falcon_common/x509tools.py` | TLS | CA verified; hostname not verified | Medium | `check_hostname=False` |
| Device key | `src/falcon_agent/identity.py:44` | AUTH | `device.key.pem` mode `0640` | Medium | Docstring says `0600` |
| Update apply | `image/overlay/.../falcon-update-verify.py` | SUPPLY | Root-side signed verify + safe extract | Low | Strong; auto gate is the concern |
| Auto update | `image/overlay/etc/falcon-agent/agent.json:17` | SUPPLY | `update_auto_apply: true` | Medium | Unattended root code swap on valid signature |
| Container build | none | CTR | No Dockerfile/compose | N/A | SD-card image baker instead |
| License | none tracked | GIT | No repo LICENSE | Low | `ci/license_check.py` checks installed dists only |
| Branch protection | `docs/security/BRANCH_PROTECTION.md` | CI governance | Not enforceable on Free private | Medium | Owner-accepted (D-011) |

## Findings

### Finding ID: falcon-edge-GIT-001 — No repository LICENSE file (deterministic real)

- Severity: P3
- Confidence: High
- Area: GIT
- Evidence:
  - `git ls-files` at `5ff59fe`: no `LICENSE`, `LICENCE`, `COPYING`, or `UNLICENSE` tracked.
  - `ci/license_check.py:1` is the only license-named file; it inspects *installed Python distributions*, not the repository.
- What is happening: the repository ships no license/notice, so the default "all rights reserved" applies.
- Why it matters / impact: downstream reuse, redistribution, and SBOM/license provenance are legally ambiguous.
- Recommended fix: add an explicit `LICENSE` (and optionally `NOTICE`) matching the intended distribution terms; reference it from `README.md`.
- Deterministic ref: DET-P3-001
- Status: open

### Finding ID: falcon-edge-PORT-001 — Four tracked shell scripts lack the executable bit (deterministic real, low impact)

- Severity: P3
- Confidence: High
- Area: PORT
- Evidence:
  - `git ls-files -s` mode `100644` for `automation/evidence/growth.sh`, `automation/validation/p9_drop_budget.sh`, `automation/validation/p9_hard_reset_endurance.sh`, `image/overlay/usr/local/sbin/falcon-log-export.sh`.
  - `automation/validation/bake_lab_test_image.sh:249` installs `falcon-log-export.sh` with `install -m 0755 ...` (image copy is executable regardless).
  - Invocations use an explicit interpreter (`ledgers/test_execution.csv:130` `bash automation/evidence/growth.sh`; `.../P9-G04/*.meta.json` `bash automation/validation/p9_hard_reset_endurance.sh 10`).
- What is happening: the git mode is missing, but every in-repo invocation uses `bash <script>` and the deployed copy is force-chmod'ed. The deterministic tool's stated failure (`./script.sh` fails) is not exercised anywhere in the tree.
- Impact: cosmetic/portability-only; no deployed failure reproduced. The DET severity (P2) overstates impact.
- Recommended fix: `git update-index --chmod=+x <file>` for the four paths (and add a CI check for `*.sh` modes) for consistency.
- Deterministic ref: DET-P2-002
- Status: open (downgraded)

### Finding ID: falcon-edge-PORT-002 — "14 CRLF files" is a false positive (intentional byte-exact evidence)

- Severity: P3 (informational)
- Confidence: High
- Area: PORT
- Evidence:
  - `.gitattributes:36-41` — `*.out -text` / `*.sha256 -text` / `MANIFEST.sha256 -text`: explicitly **no** end-of-line normalization, because "the recorded SHA-256 is over exact bytes".
  - Raw blob check on the named files (e.g. `evidence/raw/ED-20/20261002T043729Z_zero-inventory-scan.out`) shows embedded CRLF pairs, but `git ls-files --eol` reports `i/lf` for all 1,113 tracked text entries.
  - `ci/check_evidence.py` verifies content hashes over exact bytes.
- What is happening: the flagged `*.out` files are captured tool output; CR characters are part of the payload, not an accidental Windows commit. The recommended remediation (`* text=auto eol=lf` + `git add --renormalize .`) is already largely present for text files and would **break** the `*.out` hash checks if applied to them.
- Impact: none; renormalizing would cause false evidence-integrity failures. False positive.
- Recommended fix: none for these files; leave the `-text` policy. If reviewers want to reduce noise, scope any renormalization to text config/scripts only.
- Deterministic ref: DET-P2-003
- Status: false-positive (accepted)

### Finding ID: falcon-edge-SEC-001 — gitleaks `generic-api-key` hits are allowlisted public/identifier values (deterministic false positive)

- Severity: P3 (informational)
- Confidence: High
- Area: SEC
- Evidence:
  - `.gitleaks.toml:15-23` allowlists regex-scoped against the finding line: `raw section key part: .[A-Za-z0-9+/=_-]{43,44}.` and `token_id:\s*[0-9a-fA-F-]{36}`.
  - `.github/workflows/validate.yml:141` runs `./gitleaks detect --source . --redact --config .gitleaks.toml --log-opts=--all`.
  - Hit 1 (`evidence/raw/EDGE-ONBOARD/20260929T071159Z_inspect-v2-wg-section.out:5`) is a WireGuard **public** key in a NetworkManager section header (no private key in the file).
  - Hit 2 (`evidence/raw/P2-G03/20260929T045055Z_live-mtls-walkthrough.out:4`) is a bootstrap **token_id** (a UUID audit identifier), not the token value.
  - A Python regex test against the embedded allowlist patterns returns `True` for both lines.
- What is happening: the deterministic scan appears to have run gitleaks without `--config .gitleaks.toml`; under the repository's configured scan these are suppressed, were manually reviewed (`.gitleaks.toml:1-10`), and contain no secret. No secret value is reproduced here.
- Impact: none. False positive already triaged and CI-covered.
- Recommended fix: none required; keep the allowlist line-scoped so a real secret on another line still alerts.
- Deterministic ref: DET-P2-004
- Status: false-positive (accepted)

### Finding ID: falcon-edge-AUTH-001 — Device mTLS private key is group-readable (`0640`), contradicting its documented `0600`

- Severity: P2
- Confidence: High
- Area: AUTH
- Evidence:
  - `src/falcon_agent/identity.py:4` docstring: `identity/device.key.pem    Ed25519 private key (0600, PKCS#8)`.
  - `src/falcon_agent/identity.py:44` `os.chmod(self.key_path, 0o640)  # group-read for sibling collectors (Vector)`; also `:66` (rotation) and `:79` for the cert.
  - `deploy/falcon-agent.service:15` `Group=falcon-agent`; Vector is the intended sibling reader (`ledgers/contradiction_ledger.md:7`, `closeout/AUDIT-2026-09-30.md:38`).
- What is happening: the device identity private key that authenticates every sensor mTLS call is readable by every process in the `falcon-agent` group, while the module documents `0600`.
- Why it matters / impact: any co-resident process granted that group (or a future collector) can read the key and impersonate the sensor — submit heartbeats/inventory/events and renew the certificate until revocation. This is a deliberate tradeoff for Vector TLS, but it contradicts the stated control and widens the identity's trust boundary.
- Recommended fix: keep the sensor identity key `0600`; give Vector its own client certificate (or a dedicated relay identity) and only widen the *certificate* (not the private key) to `0640`. Update the docstring and record the control in `SECURITY_BOUNDARY.md`.
- Suggested validation: assert `oct(stat(device.key.pem).st_mode & 0o777) == "0o600"` in `tests/phase3` and that Vector starts with a dedicated credential.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-SEC-002 — mTLS clients never verify the control-plane hostname

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `src/falcon_common/x509tools.py:105-112` loads the CA bundle, then unconditionally sets `ctx.check_hostname = False  # lab certificates carry SANs; hostname policy is the caller's`.
  - `src/falcon_agent/client.py:42-47` and `src/falcon_cli/__main__.py` both build contexts through this function; no caller re-enables hostname checking or pins the server certificate/keyId.
- What is happening: the client validates that the server certificate chains to the private edge CA, but accepts a CA-signed certificate for **any** name. Server identity is not bound to the configured `control_plane_url`.
- Why it matters / impact: within the private CA, any other CA-issued certificate (e.g. a sensor or operator cert) is a valid server certificate; a rogue/mis-issued cert enables MITM of heartbeats, inventories, updates and directives. Impact is bounded by the private-CA trust model but the SAN check is trivially available.
- Recommended fix: set `check_hostname = True` with SANs on the control-plane certificate, or explicitly pin the control-plane certificate fingerprint / signing `keyId` at enrollment; document the chosen policy in `docs/security/SECURITY_BOUNDARY.md`.
- Suggested validation: a test that a CA-signed cert with a wrong CN/SAN is rejected by `ControlPlaneClient`.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-CI-001 — `bake-image` interpolates secrets directly into shell script text

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/bake-image.yml:101-104`:
    `printf 'wifi_ssid=%s\nwifi_key=%s\nsudo=%s\n' "${{ secrets.WIFI_SSID }}" "${{ secrets.WIFI_KEY }}" "${{ secrets.PI_PASSWORD }}"` and `printf '%s' "${{ secrets.LAB_CA_CERT }}"`.
  - The same workflow passes other secrets through `env:` instead (`.github/workflows/bake-image.yml:61-63` `FALCON_EDGE_SERVER_WG_PUB` / `CLAIM_TOKEN` / `CLAIM_TOKEN_EXPIRES`), showing the safer pattern is available.
- What is happening: GitHub substitutes secret text into the run script before bash parses it. A secret containing `"`, backtick, `$(...)` or a newline can break out of the quoted argument and inject shell commands (or corrupt the credentials file). Rotation of a WiFi passphrase containing such characters could silently alter the bake.
- Why it matters / impact: secret-to-shell injection in the one workflow that holds the owner's WiFi PSK, WireGuard key, claim token and password hash; also raises accidental-log-exposure risk.
- Recommended fix: pass these values via step `env:` and reference `"$WIFI_SSID"` etc. inside the script (as done at `:61-63`), or use `printf '%s' "$VAR"`. Never place `${{ secrets.* }}` inside run text.
- Suggested validation: a workflow test/lint (zizmor already runs) plus a review rule; bake a test image with a passphrase containing a quote to prove no breakage.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-CI-002 — Branch protection / required checks cannot be enforced; `main` is only advisory-gated

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `docs/security/BRANCH_PROTECTION.md:3-9`: every protection/ruleset API call returns `403 Upgrade to GitHub Pro...`; plan-blocked on a private Free repository.
  - `docs/security/BRANCH_PROTECTION.md:71-84`: owner decision to stay on Free; "a bad change can reach `main` without green CI — re-affirmed as accepted".
  - `verify` is only triggered by push/PR (`.github/workflows/validate.yml:14-21`), and nothing blocks a red push.
- What is happening: the strong `validate` pipeline is visibility-only; no branch protection, required checks, or force-push block exists.
- Why it matters / impact: a compromised/erroneous maintainer push can modify workflows or credential-bearing bake code and land on `main` without passing gates. The `bake` environment reviewer gate is also plan-blocked (`.github/workflows/bake-image.yml:53-56`).
- Recommended fix: upgrade to GitHub Pro/Team (or make a non-credential-bearing mirror public) and apply the ready payload in `BRANCH_PROTECTION.md:53-64`; until then keep the compensating controls and re-review at each plan/cost review.
- Deterministic ref: null
- Status: owner-accepted (open residual)

### Finding ID: falcon-edge-SUPPLY-001 — Shipped sensor image auto-applies signed updates (no per-update human gate)

- Severity: P2
- Confidence: High (config) / Medium (risk)
- Area: SUPPLY
- Evidence:
  - `image/overlay/etc/falcon-agent/agent.json:17` `"update_auto_apply": true` (carried into every baked image via `image/overlay`).
  - `src/falcon_agent/runner.py:791-792` `if self.config.get("update_auto_apply"): result["update_apply"] = self.apply_update()`.
  - Root-side verify is strong: `image/overlay/usr/local/sbin/falcon-update-verify.py:224-248` verifies the manifest signature against `/etc/falcon-agent/update-signing.pub.pem` (root-owned, non-writable) and `:310-347` rejects symlinks/traversal/setuid members.
  - `docs/security/DEPENDENCY_POLICY.md:18-19` states the sensor policy is "No auto-upgrades on the sensor" (framed for kernel/package upgrades).
- What is happening: a validly signed update manifest served by the control plane causes fleet-wide application of new agent code with no per-device/per-update operator approval. Signature verification protects integrity but not the *decision* to ship.
- Why it matters / impact: compromise of the control-plane signing seed (or a malformed operator-issued manifest) yields unattended root code swap across the fleet; there is no human "hold" between control-plane issuance and device execution.
- Recommended fix: default `update_auto_apply` to `false` for `stable`/production (keep `true` only for lab/canary), or gate application on an explicit operator release action; align `DEPENDENCY_POLICY.md` with the actual behavior.
- Suggested validation: a test that a signed manifest offered to a default-config agent is staged but not applied until opt-in.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-SUPPLY-002 — Dependabot watches only GitHub Actions, not hash-pinned dev dependencies

- Severity: P3
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `.github/dependabot.yml:7-14` has a single `package-ecosystem: github-actions` (no `pip`).
  - `requirements-dev.txt:11-17` pins `pyyaml`, `coverage`, `zizmor` with hashes; security advisories for these require manual bumps (version + every hash).
- What is happening: the runtime is deliberately stdlib-only (`.git`-tracked policy `docs/security/DEPENDENCY_POLICY.md:7-10`), but CI-only `pip` deps are not monitored.
- Impact: delayed security updates for the linters/scanners that are themselves part of the security toolchain.
- Recommended fix: add a `pip` ecosystem entry for `/` (and optionally the Docker/RPi base URL) to `dependabot.yml`; document the hash-update procedure.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-SEC-003 — Lab tooling disables SSH host-key and TLS verification

- Severity: P3
- Confidence: High
- Area: SEC
- Evidence:
  - `automation/validation/ab_device_drill.sh:33` `SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=no ...)` and `:40` pipes a sudo password over that channel.
  - `automation/validation/release_skew_check.sh:193-194` `context.check_hostname = False; context.verify_mode = ssl.CERT_NONE`.
  - `automation/validation/unifi_networks.py:57-58` same disablement.
- What is happening: lab/ops validation scripts accept any SSH host key and any TLS certificate while sending credentials (`ab_device_drill.sh:34` reads `sudo=` from `/home/user/.env`).
- Impact: MITM/spoofing during drills or skew checks; limited to lab tooling, but it runs privileged remote commands.
- Recommended fix: pin lab host keys via a managed `known_hosts` and verify TLS with the lab CA (as `automation/validation/inventory_metrics.py:66-75` already does).
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-CI-003 — Documentation overstates `dependabot-merge` gate specificity

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - `docs/security/BRANCH_PROTECTION.md:41-45` claims the sweep "requires the `validate`, `tests (3.12)` and `tests (3.13)` check-runs ... only for `dependabot/*` branches".
  - `.github/workflows/dependabot-merge.yml:44-45,81` filters by `--author app/dependabot` and `gh pr checks` (all checks green); there is no explicit dependency on the three named contexts or a branch-name filter. It does correctly re-read the head (`:88-92`) and merge with `--match-head-commit` (`:95-96`).
- What is happening: "all checks green" is a weaker contract than "these three named required checks passed", and it is misdescribed in the security doc.
- Impact: low (head-binding is present), but the documentation/control drift undermines auditability.
- Recommended fix: either implement the named-check gate in the workflow, or correct the doc to match the implemented behavior.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-SEC-004 — No step-by-step emergency rotation procedure for the CA key / signing seed

- Severity: P3
- Confidence: Medium
- Area: SEC
- Evidence:
  - `docs/runbooks/certificate-renewal-revocation.md:18-19` ends with "the CA private key never leaves owner custody; emergency rotation owner is the program owner (ED-08)" — a responsibility note, not a procedure.
  - `docs/runbooks/retirement-key-destruction.md` covers per-sensor key destruction; `docs/runbooks/backup-restore.md:7,135` covers backing up `ca/ca.key.pem` and `signing.seed` but not rotating them.
- What is happening: there is no committed runbook for the CA/signing-seed compromise case (impact, re-issuance, fleet re-enrollment, notification).
- Impact: slow, ad-hoc response if the trust root is compromised; rotation is exactly when an operator needs a written procedure.
- Recommended fix: add `docs/runbooks/root-key-compromise.md` covering CA + signing-seed rotation, fleet re-enrollment, and evidence preservation; link it from `runbooks/INDEX.md`.
- Deterministic ref: null
- Status: open

### Finding ID: falcon-edge-CONF-001 — Lab configs ship permissive defaults (TOFU enrollment; control plane binds all interfaces)

- Severity: P3
- Confidence: High
- Area: CONF
- Evidence:
  - `deploy/falcon-agent.lab.json` `"allow_insecure_enrollment": true` ("lab trust-on-first-use for the first enrollment").
  - `deploy/edge-control-plane.lab.json` `"bind": "0.0.0.0"` with a comment relying on the host firewall default-deny.
  - The shipped image config is the safer opposite: `image/overlay/etc/falcon-agent/agent.json` `"allow_insecure_enrollment": false`.
- What is happening: the committed lab configs are intentionally permissive; safety depends on the lab firewall and on operators not reusing them.
- Impact: accidental reuse on a non-isolated host would expose the control plane broadly or permit unauthenticated TOFU enrollment.
- Recommended fix: add prominent "LAB ONLY" headers/validation guards (e.g. refuse `allow_insecure_enrollment` unless an explicit `--lab` flag) and a startup warning when binding `0.0.0.0`.
- Deterministic ref: null
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Rogue CA-signed cert MITMs agent/CLI | P2 | Low-Med | High | `x509tools.py:112` | Enable hostname/pin |
| Co-resident process reads device key | P2 | Low-Med | High | `identity.py:44` | Dedicated Vector cert; key `0600` |
| Secret-to-shell injection in bake | P2 | Low | High | `bake-image.yml:101-104` | Pass secrets via `env:` |
| Unattended fleet root code swap | P2 | Low-Med | High | `agent.json:17`, `runner.py:791` | Default auto-apply off |
| Ungated push to `main` | P2 | Low | High | `BRANCH_PROTECTION.md:3-9` | Plan upgrade / required checks |
| Stale/missed dev-dep CVE fix | P3 | Low | Med | `dependabot.yml:8` | Add pip ecosystem |
| Lab MITM during drills | P3 | Low | Med | `ab_device_drill.sh:33` | Pin host keys/TLS |

## Recommendations

### Immediate / Release Blocking
None (no P0/P1 identified).

### This Week
- Pass bake secrets via `env:` (CI-001).
- Enable control-plane hostname verification or cert pinning (SEC-002).
- Decide/implement `update_auto_apply` default (SUPPLY-001).

### This Month
- Fix the device-key mode/doc mismatch, ideally via a dedicated Vector credential (AUTH-001).
- Add the pip ecosystem to Dependabot (SUPPLY-002).
- Pin lab host keys/TLS in validation tooling (SEC-003).
- Add `LICENSE` (GIT-001).

### Later / Platform Evolution
- Apply branch protection when the plan allows (CI-002).
- Correct or implement the dependabot-merge gate description (CI-003).
- Write `root-key-compromise` runbook (SEC-004).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `git update-index --chmod=+x` ×4 | Repo-mode consistency | the four `*.sh` | `git ls-files -s` |
| Add `LICENSE` | Legal clarity | repo root | `git ls-files` |
| Secrets via `env:` | Removes shell-injection surface | `.github/workflows/bake-image.yml` | zizmor + test bake |
| Correct `BRANCH_PROTECTION.md:41-45` | Removes doc drift | docs/security | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Dedicated Vector client cert; sensor key `0600` | P2 | edge maintainer | M | image re-bake |
| Hostname verification / server pin | P2 | edge maintainer | S-M | cert SANs |
| `update_auto_apply` policy default | P2 | owner + maintainer | S | decision |
| pip Dependabot ecosystem | P3 | maintainer | S | — |
| Root-key-compromise runbook | P3 | owner | M | — |

## Suggested Tests

- Unit: reject a CA-signed server certificate with a wrong SAN in `ControlPlaneClient`.
- Unit: assert `device.key.pem` mode `0600` and that Vector uses a distinct credential.
- Unit: default-config agent stages but does not apply a signed update; opt-in required.
- CI/lint: workflow rule forbidding `${{ secrets.* }}` inside `run:` bodies (zizmor custom rule or grep gate).
- Regression: keep `ci/check_evidence.py` green after any `.gitattributes` change to prove `*.out` bytes stay untouched.
- Portability: a CI assertion that every tracked `*.sh` is mode `100755`.

## Suggested Documentation Updates

- `docs/security/SECURITY_BOUNDARY.md`: server-identity verification policy and the Vector credential model.
- `docs/security/BRANCH_PROTECTION.md`: align the dependabot-merge description with the workflow.
- `docs/security/DEPENDENCY_POLICY.md`: state the actual auto-update behavior.
- `docs/runbooks/root-key-compromise.md` (new) + `docs/runbooks/INDEX.md` link.
- `README.md` / repo root: license.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Does the control-plane cert carry correct SANs for the configured URL? | Determines whether hostname verification can be enabled as-is | `openssl x509 -text` on the issued server cert |
| Is Vector the *only* process in group `falcon-agent`? | Bounds the `0640` key exposure | Image `/etc/group` dump |
| Was the deterministic gitleaks run configured with `.gitleaks.toml`? | Explains the false-positive noise | The lens command line (not present in artifacts) |
| Is a Pro-plan upgrade planned? | Closes CI-002 | Owner decision ledger |

## Appendix

- Commit audited: `5ff59fe0b8cfe2cc0acf07de9b49b8d6afa405b2`.
- No `Dockerfile`/`docker-compose` exists; container-runtime review (prompt 36) is N/A — the deliverable is a Raspberry Pi OS SD image built by `automation/validation/bake_lab_test_image.sh` and verified by `image/verify-pi-image.sh` (45 checks).
- Prior-audit findings verified as fixed at this commit: pip hash pinning, gitleaks full-history scan, curl-tool SHA-256 verification, coverage gate, rate limiting/security headers/slow-client guard (`src/falcon_control/http_server.py:19-34,51-94`), re-enrollment refusing REVOKED/RETIRED (`service.py:766-775`), `create-token` requiring `--out` (`falcon_cli/__main__.py:154-156`), strict SSH host-key checking in inventory metrics (`inventory_metrics.py:66-75`).
