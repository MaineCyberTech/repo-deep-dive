# Focused security / supply-chain / CI deep-dive - falcon

## Findings

| ID | Severity | Title | Report |
|---|---|---|---|
| SEC-P2-001 | P2 | gitleaks curl-auth-user allowlist is unanchored and suppresses every curl line | lens_focused_security_supply_chain_ci.md |
| SEC-P2-002 | P2 | Retired DFIR-IRIS API key literal still committed in vendored scripts; rotation PENDING | lens_focused_security_supply_chain_ci.md |
| SEC-P2-003 | P2 | All 20 inherited credentials are PENDING rotation; vendored scripts source credential files wholesale | lens_focused_security_supply_chain_ci.md |
| DEP-P2-001 | P2 | Dependabot covers only GitHub Actions; Python dependencies and container images are unmanaged | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P2-001 | P2 | Release and SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1) | lens_focused_security_supply_chain_ci.md |
| CI-P2-001 | P2 | Branch protection and required checks are plan-gated, so validate is advisory | lens_focused_security_supply_chain_ci.md |
| PORT-P3-001 | P3 | 90 tracked shell scripts lack the executable bit | lens_focused_security_supply_chain_ci.md |
| PORT-P3-002 | P3 | CRLF committed in four markdown files despite text eol=lf | lens_focused_security_supply_chain_ci.md |
| GIT-P3-001 | P3 | No LICENSE file | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P3-001 | P3 | Vendored mct/compose images are unpinned under a blanket waiver | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P3-002 | P3 | Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P3-003 | P3 | Image/SBOM-component license allow/deny gate is not enforced | lens_focused_security_supply_chain_ci.md |
| CI-P3-001 | P3 | dependabot-merge merges without pinning the checked commit and holds broad write scope | lens_focused_security_supply_chain_ci.md |
| CONF-P3-001 | P3 | SBOM coverage doc contradicts the live validate workflow on --require-vuln | lens_focused_security_supply_chain_ci.md |

---

# Falcon — Focused Security / Supply-Chain / CI Deep-Dive

- Repo: `C:\temp\falcon` (branch `main`, HEAD `ff868e54327a5aab9c13b0a3cfa57fda339cbeed`)
- Focus: security/authz, CI/CD governance, supply chain/dependencies/secrets, SBOM/license, container runtime, secret rotation, branch protection
- Method: read-only. Every claim cites `path:line`. Secret values are never printed (path + type only).

## Summary

New findings (this pass): **14** — P1 **0**, P2 **6**, P3 **8**.

| Severity | Count | IDs |
|---|---:|---|
| P0 | 0 | — |
| P1 | 0 | — |
| P2 | 6 | SEC-001, SEC-002, SEC-003, DEP-001, SUPPLY-002, CI-001 |
| P3 | 8 | PORT-001, PORT-002, GIT-001, SUPPLY-001, SUPPLY-003, SUPPLY-004, CI-002, CONF-001 |

Deterministic-hit validation verdicts:

| DET | Title | Verdict |
|---|---|---|
| DET-P3-001 | No LICENSE file | **REAL** (P3) |
| DET-P2-002 | 90 shell scripts without exec bit | **REAL** (impact low → P3) |
| DET-P2-003 | CRLF committed for 10 files | **PARTIALLY REAL** (4 `.md` real; 6 `.out` false positives) |
| DET-P2-004 | gitleaks curl-auth-user (50) | **FALSE POSITIVE** (reviewed allowlist; but allowlist is over-broad → new SEC-001) |
| DET-P2-005 | gitleaks generic-api-key (18) | **FALSE POSITIVE** (fixtures, redacted evidence, public GPG key, classified records) |
| DET-P2-006 | gitleaks sourcegraph-access-token (36) | **FALSE POSITIVE** (CycloneDX SHA-1 component hashes under `sbom/`) |
| DET-P3-007 | 58 images without digest pin | **REAL but owner-waived** (all in vendored `mct/compose`; deployed `compose/**` fully pinned) |

Overall posture: this is an unusually mature, evidence-first repository. The deterministic scan over-reports because it ignores `.gitleaks.toml` allowlists, `.gitattributes` byte-exact evidence flags, and the documented supply-chain waivers. The genuinely new signal is in *residuals the repo itself documents but has not closed*: an over-broad gitleaks allowlist, a committed retired IRIS API-key literal pending rotation, 20/20 inherited credentials pending rotation, incomplete dependency automation, missing artifact signing, plan-gated branch protection, and a docs↔workflow drift.

---

## Deterministic-hit validation (evidence)

### DET-P3-001 — No LICENSE file — REAL (P3)
- `git ls-files` shows no `LICENSE`/`COPYING`/`NOTICE`; the only "license" paths are `ci/license_check.py` (dependency gate) and docs reports.
- `README.md:121` `## License / ownership` names the owner ("Owner: Maine Cyber Tech") but states no license terms. Third parties have no grant.

### DET-P2-002 — 90 shell scripts without the exec bit — REAL (impact low → P3)
- `git ls-files --stage`: **90** `.sh` at mode `100644`, **536** at `100755`. Examples: `automation/alerting/do_watcher/install.sh`, `automation/validation/rotate_wazuh_vt_key.sh`, `automation/validation/lib/abort.sh`, `automation/validation/tests/*.sh`.
- Mitigation check: the tracked callers that invoke `./script.sh` point at **100755** files (`automation/validation/export_monitor_metrics.sh`, `bootstrap/90-alerting.sh`, `automation/validation/silence_alert_test.sh`, `automation/validation/phase9_data_quality.sh`). `ci/validate.py` runs suites via `bash`/`bash -n`, so CI is not broken today. Downgraded from P2 to P3.

### DET-P2-003 — CRLF committed for 10 files — PARTIALLY REAL
- `git ls-files --eol` → `i/mixed attr/text eol=lf` for the 4 `docs/phase8/reviews/*.md`. HEAD blobs carry CRLF: `INDEPENDENT_REVIEW_2026-09-23.md` = 255 CRLF / 268 LF; `_UPDATE` 174/185; `_UPDATE2` 147/155; `_UPDATE3` 137/146. `.gitattributes:28` sets `*.md text eol=lf`; the blobs were not renormalized → **REAL** for these 4.
- The 6 `.out` files (`evidence/raw/P9-G09/*.out`, `review-package/...`) show `attr/-text` and are deliberately byte-exact evidence captures (`.gitattributes:34 *.out -text`). Their CRLF is expected → **FALSE POSITIVE**.

### DET-P2-004 — gitleaks `curl-auth-user` (50) — FALSE POSITIVE
- `.gitleaks.toml:20-24` allowlists rule `curl-auth-user` for lines matching `.*curl.*`; `docs/security/SCANNER_ALLOWLIST_CHANGES.md:100` documents the classification ("command lines, not literals").
- Sampled evidence: `compose/central/docker-compose.yml:89` `curl -sk -u falcon-healthcheck:$$OPENSEARCH_HEALTHCHECK_PASSWORD ...` (env var); `automation/validation/central_health.sh:62` `-u kibanaserver:kibanaserver` (the public OpenSearch demo user, used to prove it is *rejected*); `docs/runbooks/WAZUH_INTEGRATION.md:119` `-u "falcon-healthcheck:$(cat /srv/falcon/secrets/opensearch_healthcheck.pw)"`. No literal secret.
- Note: the allowlist itself is too broad — see new **falcon-SEC-001**.

### DET-P2-005 — gitleaks `generic-api-key` (18) — FALSE POSITIVE
- `automation/validation/tests/secret_scan_test.sh:28` `public key: dGhpcyBpcyBub3QgYSByZWFsIGtleSBidXQgbG9uZyBlbm91Z2g=` (fake fixture; the literal is assembled so the test file scans clean).
- `evidence/raw/P4-G06/20260921T203941Z_ntfy-single-contact.out:2` `url=https://ntfy.sh/[REDACTED-NTFY-TOPIC]` and `url=http://172.30.1.1:9099/grafana/<token>` (already redacted; recorded in `ledgers/redactions.md:7`).
- `mct/deploy-scripts/endpoint-deploy/install-wazuh-linux.sh:446` `OSQUERY_KEY=1484120AC4E9F8A1A577AEEE97A80C63C9D8B80B` (public osquery APT GPG key, allowlisted in `secret_scan.py:123-124`).
- `docs/audits/.../21_repo_hygiene_maintainability.md:106` and `ledgers/test_execution.csv:491,492,513` quote `REDACTED` markers / scanner regex text; allowlisted at `.gitleaks.toml:45-48`.

### DET-P2-006 — gitleaks `sourcegraph-access-token` (36) — FALSE POSITIVE
- All sampled hits are CycloneDX component hashes, e.g. `sbom/traefik_v3.7.13.cdx.json:160-166` `"name": "alpine-baselayout-data" ... "alg": "SHA-1", "content": "c6f9bded17d844b6f1b0bb5766d2c35c0d5c8508"`. Allowlisted by path `.gitleaks.toml:26-29` (`sbom/.*`, `evidence/.*`) and excluded by `secret_scan.py` (`/sbom/`, `.cdx.json`).

### DET-P3-007 — 58 images without a digest pin — REAL but owner-waived
- Every unpinned ref is in the vendored MCT tree: `mct/compose/docker-compose.velociraptor.yml:14` `velociraptor:latest`; `mct/compose/docker-compose.misp.yml:61` `ghcr.io/misp/misp-docker/misp-modules:latest`; `mct/compose/docker-compose.greenbone.yml:152` `gvm-config:latest`, `:161` `nginx:latest`, `:76` `pg-gvm:stable`; plus tag-only/pseudo-tag refs (no tag) in `docker-compose.greenbone.yml:5-293`.
- `pins/supply-chain-waivers.json:4-10` waives `root: mct/compose`, `ref: *` ("TB-8: the vendored MCT compose tree is imported and not deployed"), `review_by: 2026-12-31`.
- The deployed tree is clean: a scan of `compose/**` found no `image:` without `@sha256:`; `automation/validation/check_compose_digests.py` enforces it. Also waived: `automation/wazuh/multi-node/generate-indexer-certs.yml:4` `wazuh-certs-generator:0.0.4`.

---

## Findings

### falcon-SEC-001 — gitleaks `curl-auth-user` allowlist is unanchored and suppresses every curl line
- Severity: P2 · Confidence: high · Area: SEC · `deterministic_ref`: DET-P2-004
- Evidence:
  - `.gitleaks.toml:20-24` — `[[allowlists]] rules = ["curl-auth-user"] regexTarget = "line" regexes = ['.*curl.*']`
  - `docs/security/SCANNER_ALLOWLIST_CHANGES.md:100` — rationale says "command lines, not literals"
  - `automation/validation/central_health.sh:62` — `curl ... -u kibanaserver:kibanaserver` (the DET hits the allowlist is meant to cover)
- What is happening: the allowlist matches any line containing `curl`, with no scope on path or the credential token. A hardcoded credential in a `curl -u user:PASSWORD` / `--user` / `-H "Authorization: ..."` call would be silently whitelisted.
- Why it matters: the independent gitleaks gate is one of two secret controls; blunting a whole rule on a substring weakens detection for exactly the pattern (`curl`-embedded credentials) that appears throughout this repo.
- Recommendation: drop the `regexTarget = "line"`/`.*curl.*` entry and instead allowlist by path (`docs/`, `automation/validation/*.sh`, `compose/**`) or, better, add a `regexTarget = "match"` allowlist that requires the credential value to be a variable/`$(cat ...)` reference. Add a negative fixture: a literal `curl -u user:realsecret https://...` must still be flagged.
- Impact: silent false-negative risk in CI secret scanning.

### falcon-SEC-002 — Retired DFIR-IRIS API key literal still committed in vendored scripts; rotation PENDING
- Severity: P2 (would be P1 if the key is still valid) · Confidence: medium · Area: SEC · `deterministic_ref`: null
- Evidence:
  - `mct/scripts/p61-agents-ci.sh:23` and `mct/scripts/p62-agents-ci.sh:20` contain a 40+ hex credential-shaped literal (value not printed; located by regex only).
  - `ledgers/redactions.md:25-26` — "retired DFIR-IRIS API key retained as the literal-detector value ('old IRIS key must be absent from reports')".
  - `docs/security/SCANNER_ALLOWLIST_CHANGES.md:181-184` — hash-only `ALLOW_VALUE_SHA256` entry added; "rotation owner-side".
  - `mct/runbooks/credential-rotation-checklist.md:41` — row 12 "DFIR-IRIS API credential ... PENDING".
- What is happening: a cleartext credential literal remains in the tree and is suppressed by a hash allowlist rather than removed. The records simultaneously call it "retired" and "rotation PENDING", which is contradictory.
- Impact: if the key was never revoked it is a live credential committed to a shipped repo; the scanner cannot see it by design.
- Recommendation: confirm revocation with IRIS; then replace the literal in both scripts with a placeholder/runtime read (these are "old key must be absent" detectors — the comparison value can be hashed, e.g. compare SHA-256). Remove the `ALLOW_VALUE_SHA256` entry once gone. Record rotation evidence (date + negative test) per `docs/security/INHERITED_CREDENTIAL_ROTATION.md`.

### falcon-SEC-003 — All 20 inherited credentials are PENDING rotation; vendored scripts source credential files wholesale
- Severity: P2 · Confidence: high · Area: SEC · `deterministic_ref`: null
- Evidence:
  - `docs/security/INHERITED_CREDENTIAL_ROTATION.md:7` — "20/20 PENDING as of 2026-10-01"; `:88` — "20 items, 0 rotated, 20 pending".
  - `docs/security/INHERITED_CREDENTIAL_ROTATION.md:69-75` — "28 scripts under `mct/scripts/` and `mct/deploy-scripts/` still `set -a`-source `ops/creds.env`, `wazuh-local.env` or the legacy `.env` (22 use `set -a`) ... treat their process environments as credential-bearing."
  - `mct/runbooks/credential-rotation-checklist.md:9-49` — rows 1-20 all `PENDING` (DO Spaces, Wazuh admin/indexer/API, VirusTotal, PVE, Security Onion, Cloudflare tunnel, IRIS, MISP, Shuffle, DB/Redis).
- What is happening: the inherited MCT/Wazuh credential estate has no completed rotation evidence, and the credential-bearing scripts export whole secret files into their process environments.
- Impact: shared/legacy credentials have large blast radius; a capture or crash dump from those scripts can expose every sourced key. No rotation means any historical exposure remains exploitable.
- Recommendation: execute the documented order (DO Spaces → Wazuh admin/indexer → Cloudflare → IRIS/MISP/Shuffle → VT), capturing name-only evidence and negative tests; migrate the 28 vendored scripts to single-key reads (`automation/validation/lib/env_key.sh`) or gate them behind the interactive account.

### falcon-DEP-001 — Dependabot covers only GitHub Actions; Python deps and container images are unmanaged
- Severity: P2 · Confidence: high · Area: DEP · `deterministic_ref`: null
- Evidence:
  - `.github/dependabot.yml:2-7` — the only `updates` entry is `package-ecosystem: github-actions`, `directory: /`, weekly.
  - `ci/requirements-ci.txt` — hash-pinned `pyyaml`, `zizmor` (manual updates only).
  - `pins/images.lock` — 24 pinned images refreshed only by the manual `pins/pull-and-record.sh` + `pins/verify-digests.sh`.
- What is happening: no automated PR for Python dependencies or container base images.
- Impact: CVEs in `pyyaml`/`zizmor` or stale base images go unnoticed until a human runs the manual pin refresh; the weekly cron in `validate.yml` checks environment rot but does not raise update PRs.
- Recommendation: add `pip` (or `uv`) and `docker` ecosystems to `.github/dependabot.yml`; or add a `renovate.json` with digest pinning. Keep the existing hash-pin policy for CI deps.

### falcon-SUPPLY-002 — Release/SBOM artifacts are integrity-checked but unsigned (SLSA ~0-1)
- Severity: P2 · Confidence: high · Area: SUPPLY · `deterministic_ref`: null
- Evidence:
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:99-105` — "All are SHA-256 integrity bindings; **none is cryptographically signed** and falcon has no published signing key ... SLSA ~0-1 remains."
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:115-120` — recommended control (owner decision D1) not implemented: sign `sbom/SBOM_MANIFEST.sha256` or use `actions/attest-build-provenance`.
- What is happening: verification proves integrity of the set, not authorship. A party who can rewrite the tree and the `*.sha256` manifests produces a self-consistent, "valid" delivery.
- Impact: a downstream reviewer cannot distinguish an owner-built delivery from a tampered one.
- Recommendation: pick D1 option (a) owner-held ed25519/GPG key signing `sbom/SBOM_MANIFEST.sha256` and binding the manifest hash in `PACKAGE_DIGEST.txt`, or (b) GitHub artifact attestations; publish the verification key with the delivery.

### falcon-CI-001 — Branch protection / required checks are plan-gated, so `validate` is advisory
- Severity: P2 (owner-accepted) · Confidence: high · Area: CI · `deterministic_ref`: null
- Evidence:
  - `docs/security/BRANCH_PROTECTION.md:3-8` — status "not enforceable on the current GitHub plan"; the apply attempt returned `403 Upgrade to GitHub Pro ...`; captured at `evidence/raw/REVIEW-FIX/20260930T202746Z_bp-branch-protection.*` (exit 1).
  - `docs/security/BRANCH_PROTECTION.md:90-97` — enforcement matrix: required status checks **No**; force-push/deletion/linear history **No**; "[skip ci] can skip a push/PR run"; bypass audit trail **No**.
  - `.github/CODEOWNERS:1-14` — CODEOWNERS + PR template are advisory only.
- What is happening: `validate.yml` runs on push/PR but nothing server-enforces it; owner direct pushes and `[skip ci]` can land changes unchecked, with no server-side bypass audit.
- Impact: a red or skipped `validate` does not block a merge to `main`; the compensating controls are manual discipline.
- Recommendation: owner decision — either upgrade to GitHub Pro/Team and apply the ready payload (`BRANCH_PROTECTION.md:16-51`), or record a periodic attestation that `validate` was green at each merge and treat any direct push as break-glass with the documented record template.

### falcon-PORT-001 — 90 tracked shell scripts lack the executable bit
- Severity: P3 · Confidence: high · Area: PORT · `deterministic_ref`: DET-P2-002
- Evidence: `git ls-files --stage` → 90 `.sh` at `100644` (e.g. `automation/alerting/do_watcher/install.sh`, `automation/validation/migrate_docker_volumes.sh`, `automation/validation/tests/*.sh`); 536 at `100755`.
- Impact: `./script.sh` fails on Linux for these files; a Windows checkout/transfer can silently keep dropping the bit.
- Recommendation: `git update-index --chmod=+x` on the intended entrypoints (and add a CI check asserting exec bits on files under `automation/**` that carry a shebang). Invocations that remain `bash <script>` are unaffected.

### falcon-PORT-002 — CRLF committed in four markdown files despite `text eol=lf`
- Severity: P3 · Confidence: high · Area: PORT · `deterministic_ref`: DET-P2-003
- Evidence: `git ls-files --eol` → `i/mixed attr/text eol=lf`; HEAD blob CRLF counts: `docs/phase8/reviews/INDEPENDENT_REVIEW_2026-09-23.md` 255, `_UPDATE.md` 174, `_UPDATE2.md` 147, `_UPDATE3.md` 137. `.gitattributes:28` `*.md text eol=lf`.
- Impact: inconsistent hashes/line-based tooling; the files were never renormalized after `.gitattributes` landed.
- Recommendation: `git add --renormalize .` for the affected paths (the 6 `.out` files are `-text` byte-exact evidence and must be left alone).

### falcon-GIT-001 — No LICENSE file
- Severity: P3 · Confidence: high · Area: GIT · `deterministic_ref`: DET-P3-001
- Evidence: no `LICENSE`/`COPYING`/`NOTICE` tracked; `README.md:121` names the owner but grants no terms.
- Impact: default "all rights reserved" is ambiguous for a repository shipped to third parties/reviewers.
- Recommendation: add a `LICENSE` (or a proprietary "review only, no redistribution" notice) consistent with the owner decision; `ci/license_check.py` governs dependencies only.

### falcon-SUPPLY-001 — Vendored `mct/compose` images are unpinned under a blanket waiver
- Severity: P3 · Confidence: high · Area: SUPPLY · `deterministic_ref`: DET-P3-007
- Evidence:
  - `mct/compose/docker-compose.velociraptor.yml:14` `velociraptor:latest`; `mct/compose/docker-compose.misp.yml:61` `.../misp-modules:latest`; `mct/compose/docker-compose.greenbone.yml:152` `gvm-config:latest`, `:161` `nginx:latest`, `:76` `pg-gvm:stable`.
  - `pins/supply-chain-waivers.json:4-10` — `root: mct/compose`, `ref: *`, reason "TB-8: imported and not deployed", `review_by: 2026-12-31`.
  - Deployed `compose/**` is fully digest-pinned (scan via `automation/validation/check_compose_digests.py`).
- Impact: if the MCT stack is ever imported/deployed, floating tags plus `docker.sock` mounts (`mct/compose/docker-compose.shuffle.yml:48,87`) create a supply-chain and container-escape risk.
- Recommendation: keep the waiver but scope it (list the specific refs) and add an explicit "do not deploy from mct/compose" guard; remove `docker.sock` mounts or document them as deploy-blocking.

### falcon-SUPPLY-003 — Vulnerability scan coverage for 12 images is stale/pending, gated only by expiring waivers
- Severity: P3 · Confidence: high · Area: SUPPLY · `deterministic_ref`: null
- Evidence:
  - `.github/workflows/validate.yml:96-99` — `sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json`.
  - `pins/supply-chain-waivers.json:33-45` — 12 images listed as `vuln_scan_pending`, `review_by: 2026-12-31` (e.g. `falcon-opensearch-s3`, the IRIS trio, Wazuh trio, `cloudflared`, `nginx`).
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:52-59` — vuln JSONs are from 2026-09-22; 12 newly pinned images have no scan.
- Impact: the gate passes only because of waivers; a HIGH/CRITICAL CVE in an unscanned or stale-scanned image is not caught until the review-by date forces a re-review.
- Recommendation: run `automation/validation/vuln-summary.sh` in the next patch window, refresh the waivers to real dispositions, and keep the DD-15 threshold. Recommend a scheduled scan job (runner with Docker + network).

### falcon-SUPPLY-004 — Image/SBOM-component license allow/deny gate is not enforced
- Severity: P3 · Confidence: high · Area: SUPPLY · `deterministic_ref`: null
- Evidence:
  - `docs/security/LICENSE_GATE.md:18-21` — the Python gate is "deliberately stricter"; "Manual/collection-side coverage (SBOMs, image licenses) remains the follow-up in SBOM-P2-001/002/003."
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:88-92,143` — "the image/SBOM license allow-deny gate ... is the remaining SBOM-P1-001 follow-up"; SBOMs carry license fields for 38-98% of components.
- Impact: copyleft or unknown-license components inside shipped images are not gated; only installed Python distributions are.
- Recommendation: add `pins/licenses.allow` + a check over `sbom/*.cdx.json` license fields (allow MIT/BSD/Apache/ISC/etc.; deny GPL/AGPL/LGPL/SSPL unless the documented self-hosted-service exception applies).

### falcon-CI-002 — `dependabot-merge` merges without pinning the checked commit and holds broad write scope
- Severity: P3 · Confidence: medium · Area: CI · `deterministic_ref`: null
- Evidence:
  - `.github/workflows/dependabot-merge.yml:17-19` — workflow-level `permissions: contents: write`, `pull-requests: write`.
  - `.github/workflows/dependabot-merge.yml:46-48` — `gh pr checks "$pr" ... && gh pr merge "$pr" --squash --delete-branch` (no `--match-head-commit`).
  - `:42-45` — merges only `app/dependabot` PRs carrying the owner-applied `dependabot-approved` label.
- Impact: author + label gating is good, but a head changed between the `gh pr checks` query and `gh pr merge` is not pinned; `contents: write` is broader than the merge action strictly needs.
- Recommendation: add `--match-head-commit "$(gh pr view ... --json headRefOid)"`; scope `permissions` to the minimum (`contents: write` is required for merge; consider moving `pull-requests: write` to job level). CI-P2-002 guard (`automation/validation/tests/ci_governance_guard_test.sh:63-73`) should pin the new flag too.

### falcon-CONF-001 — SBOM coverage doc contradicts the live `validate` workflow on `--require-vuln`
- Severity: P3 · Confidence: high · Area: CONF · `deterministic_ref`: null
- Evidence:
  - `docs/security/SBOM_COVERAGE_AND_PROVENANCE.md:71-83` — shows the applied CI step as `sbom_coverage_check.sh` / `sbom_hashes.sh verify` and states "`--require-vuln` stays off until the vulnerability refresh in §5 lands."
  - `.github/workflows/validate.yml:96-99` — the workflow actually runs `sbom_coverage_check.sh --require-vuln --vuln-waivers pins/supply-chain-waivers.json`.
- Impact: a reviewer reading the doc believes vuln coverage is unenforced; the live gate is actually stricter (and waiver-backed). This is the "docs ↔ records" drift class the repo tracks (CI-P3-001).
- Recommendation: append a dated correction section (append-only doctrine) stating that `--require-vuln --vuln-waivers` is live and listing the waiver file as the compensating control.

---

## Strengths observed (for balance)

- All GitHub Actions are commit-SHA pinned with version comments (`.github/workflows/validate.yml:29,34`); tool downloads are SHA-256 verified (`:45,53,63,71`); `persist-credentials: false` and `fetch-depth: 0` (`:31-32`); workflow-level `permissions: contents: read` (`:17-18`); no `pull_request_target`.
- Hash-pinned CI Python deps with `--require-hashes` (`ci/requirements-ci.txt`; `validate.yml:39`).
- Fail-closed secret controls: `secret_scan.py` (fails closed on bad invocation), gitleaks tree + history scans, `secret_scan_history.sh`; scanners record their own SHA-256; allowlist changes documented in `docs/security/SCANNER_ALLOWLIST_CHANGES.md`.
- Container hardening: deployed images digest-pinned; `no-new-privileges` and `cap_drop: ALL` on several services (`compose/central/docker-compose.yml:26,58,246,249-252`); non-root `USER 1000` in `compose/central/opensearch-s3.Dockerfile`; loopback-only publication for internal services.
- SBOM coverage 24/24 digest-bound with an integrity manifest and a fail-closed verify tool; Python license gate enforced in CI.

## Not verified / limitations

- `gitleaks` is not installed in this environment; the DET-P2-004/005/006 verdicts are based on `.gitleaks.toml`, `secret_scan.py` semantics, and direct reading of the cited lines, not a re-run of gitleaks 8.30.1.
- Liveness of the retired IRIS API key (falcon-SEC-002) cannot be confirmed from the repo; records call it "retired" while the rotation tracker says PENDING.
- GitHub branch-protection server state (falcon-CI-001) is not observable from the repo; the verdict relies on the recorded apply-attempt evidence (`docs/security/BRANCH_PROTECTION.md`).
- Running-container vs declared-compose drift (container runtime) is a live-host check and was not performed read-only.
