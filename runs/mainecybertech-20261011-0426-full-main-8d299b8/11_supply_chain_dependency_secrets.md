# 11_supply_chain_dependency_secrets — Prompt 11 - Supply Chain, Dependency, and Secrets Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `11_supply_chain_dependency_secrets.md` (area SC, prompt)

## Verification Performed

# Supply Chain, Dependency, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8d`
- Generated at: 2026-10-11
- Auditor: domain subagent (`11_supply_chain_dependency_secrets`, area SC)
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/11_supply_chain_dependency_secrets.md`
- Scope limitations: read-only; no `pnpm install`, no `pnpm audit`, no gitleaks binary available locally, no GitHub API/repo-settings access. Findings that need those are marked `Unknown` or `medium` confidence. Secret values were never printed.

## Scope

Reviewed at `8d299b8d`: root and workspace manifests, the single pnpm lockfile, overrides and postinstall controls, Dependabot config, all GitHub Actions workflows and composite actions, Dockerfiles and both compose files, `.gitleaks.toml` + the secret-scan composite + history-scan workflow, the rotation policy, SBOM generation/validation/attestation, container scanning, license policy, `.env.example` files and generated-artifact tracking, and the previous run's SC/SUPPLY/SEC/CI secret-scanning rows.

Not reviewed: live GitHub settings (branch protection application, Dependabot PR state, environment secrets/reviewers), actual advisory database contents (no install), Terraform apply behavior, and application runtime.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `package.json`, `apps/*/package.json`, `packages/*/package.json`, `pnpm-workspace.yaml` | Manifests/workspace | Dependency, override, script and license inventory | 7 manifests; single workspace model |
| `pnpm-lock.yaml` (492 KB, lockfileVersion 9.0) | Lockfile | Single source of resolved versions; override mirror | Only JS lockfile; `.terraform.lock.hcl` committed too |
| `scripts/audit-gate.mjs`, `security/dependency-audit-policy.json` | Policy gate | Vulnerability policy across all scopes | Wired in test.yml:52 / validate.yml:17 |
| `scripts/license-gate.mjs`, `scripts/collect-licenses.mjs`, `security/license-policy.json`, `docs/LICENSE_POLICY.md` | Policy gate/docs | License allow/deny + exceptions | 4 expiring exceptions |
| `.github/dependabot.yml` | Update governance | npm/actions/docker/terraform coverage | Weekly, grouped, targets `develop` |
| `.github/actions/dependency-audit`, `.github/actions/secret-scan`, `.github/actions/setup-pnpm` | Composite actions | Shared CI controls | Frozen-lockfile install at setup-pnpm:52 |
| `.github/workflows/{test,validate,dependency-review,sbom,build-push,deploy-do,secret-history-scan,secret-rotation-reminder,codeql}.yml` | CI/CD | Gates, scans, attestations | All third-party `uses:` are SHA-pinned |
| `.gitleaks.toml`, `scripts/ci/verify-gitleaks-config.sh`, `scripts/ci/fixtures/` | Secret scanning | Allowlist scoping + negative fixture | gitleaks >= 8.25 config; 3 scoped allowlists |
| `scripts/scan-secrets.sh`, `scripts/scan-secrets.ps1`, `.husky/pre-commit` | Secret scanning | Local pre-commit gate | Patterns now aligned |
| `apps/api/Dockerfile`, `apps/web/Dockerfile`, `apps/worker/Dockerfile`, `docker-compose.yml`, `infra/digitalocean/docker-compose.yml` | Images | Base-image pinning, build hygiene | All FROM digests pinned; prod compose digests |
| `scripts/generate-sbom.mjs`, `scripts/validate-sbom.mjs`, `docs/SBOM_PROCESS.md` | SBOM | Commit/digest binding, validation | Lockfile + per-image SBOMs |
| `docs/SECRETS_ROTATION.md`, `.github/workflows/secret-rotation-reminder.yml` | Secrets ops | Inventory, cadence, log | 48-entry inventory; quarterly reminder |
| `SECURITY.md`, `.github/CODEOWNERS`, `.dockerignore`, `.npmrc`, `.gitignore` | Governance/config | Supply-chain posture | Registry pinned; .env excluded from builds |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log --oneline 9c0b88c..8d299b8d` | Command | What changed since the previous full run | 113 commits; supply-chain fixes `6757a478`, `7dfb8650`, `f69b5899`, `d56c755a`, `7fc3f1f6`, `2da4e9bd` |
| `grep -rn "uses:" .github/workflows .github/actions` filtered to non-40-hex | Command | Unpinned-action check | No unpinned third-party action found; 33x checkout, 12x trivy-action, etc. all SHA-pinned |
| Programmatic diff of pattern lists (`.sh` vs `.ps1` vs composite action) | Script | SC-P3-003 re-verification | Pattern sets identical (10 patterns); only file-exclusion lists and one regex spelling differ |
| `python3` parse of `pnpm-lock.yaml` `snapshots:` | Script | Duplicate/deprecated inventory | 954 snapshots; 55 names with >1 resolved version; 0 `requiresBuild` markers |
| `git branch -r | grep dependabot` | Command | SC-P2-005 re-verification | 41 dependabot branches, incl. stale `next-16.2.9` and superseding `next-16.3.8` |
| `git ls-files` filters for `.env`, keys, certs, `tfvars`, `licenses.json`, `sbom.*` | Command | Secret/artifact tracking | Only `.env.example` + non-secret baseline file tracked; generated aggregates untracked |
| `grep` for `expires` in policy JSONs vs gates | Command | New expiry finding | `expires` present in both policy files; neither gate reads dates |
| `grep -n "failure|notify|ntfy|SLACK" secret-history-scan.yml` | Command | New notification finding | No output: scheduled scan has no failure alert |
| `grep -n "pnpm licenses list" docs/ scripts/ .github/` | Command | New docs finding | docs/DEPENDENCY_POLICY.md:77 and docs/SBOM_PROCESS.md:116 still instruct the broken command |
| `grep -n "attest" SECURITY.md docs/SBOM_PROCESS.md .github/workflows/deploy-do.yml` | Command | New doc-consistency finding | SECURITY.md:48-49 contradicts SBOM_PROCESS.md:14,57-58 |
| `command -v gitleaks` | Command | Local scan capability | Not installed → `verify-gitleaks-config.sh` would skip; not run in this audit (fail-closed skip is documented) |
| `pnpm install` / `pnpm audit` / `pnpm licenses list` | Not run | Read-only + resource discipline | Advisory and license conclusions come from committed policy/config, not a fresh audit run |

## Executive Summary

The supply-chain posture at `8d299b8d` is materially hardened and the previous SC/SUPPLY/SEC verification rows are almost all confirmed fixed with current evidence: 18 of 26 findings are `verified-fixed`, including every P1/P2 fix from the last full run. Dependency advisories are gated in all scopes, images are scanned and attested before deploy, SBOMs are commit/digest-bound and validated, license policy is enforced in CI with documented exceptions, base images are digest-pinned, and secret scanning now runs locally (pre-commit), on PRs/pushes (diff) and weekly over full history (checksum-pinned gitleaks + allowlist negative fixture).

The remaining risks are governance/observability rather than missing gates: the Dependabot backlog is still large and untriaged (41 open-format branches including a stale `next-16.2.9`), the weekly secret-history scan has no failure notification, policy `expires` dates are not enforced by either gate, the PR-time secret scanner still lacks the platform's own token formats (DigitalOcean/Supabase/npm/GitLab/OpenAI/Slack-user), and three smaller follow-ups (the broken `pnpm licenses list` command in two docs, the SECURITY.md SBOM-attestation claim, and the absent unused/duplicate dependency check) will mislead operators or leave gaps. No new P0/P1 issues were found.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Root manifest | `package.json` | Workspace root, overrides, scripts | 22 overrides, `onlyBuiltDependencies: ["@sentry/cli"]`, `prepare: husky` | Low | `license: ISC` documented as intentional |
| Lockfile | `pnpm-lock.yaml` | Single resolved tree | lockfileVersion 9.0, overrides mirrored (lines 7-30) | Low | No second JS lockfile |
| Vulnerability gate | `scripts/audit-gate.mjs` | All-scope advisory policy | Blocks CRITICAL any scope, HIGH+ prod | Low | `expires` not enforced |
| License gate | `scripts/license-gate.mjs` + `security/license-policy.json` | License allow/deny | Allowlist + 4 expiring exceptions | Low | `expires` not enforced |
| Dependabot | `.github/dependabot.yml` | Update PRs | 8 entries, weekly, grouped, target `develop` | Medium | Backlog untriaged |
| Diff secret scan | `.github/actions/secret-scan/action.yml` | PR/push gate | 10-pattern grep, redacted output, tracked-env guard | Medium | Missing platform token formats |
| History scan | `.github/workflows/secret-history-scan.yml` | Weekly full-history | gitleaks 8.30.1 + SHA-256, JSON artifact | Medium | No failure notification |
| gitleaks config | `.gitleaks.toml` | Allowlist scoping | 3 allowlists, all `generic-api-key`-scoped | Low | Verifier prevents silent widening |
| Local scanner | `scripts/scan-secrets.{sh,ps1}` | Pre-commit | Patterns aligned | Low | Exclusion lists differ (minor) |
| Images | `apps/*/Dockerfile`, `infra/digitalocean/docker-compose.yml` | Runtime images | FROM digests; prod compose digests; app images SHA-tagged + verified | Low | Dependabot keeps pins fresh |
| SBOM | `scripts/generate-sbom.mjs`, `sbom.yml` | Lockfile SBOM | Commit-bound, validated, weekly | Low | Not release-attached (REL-P1-001) |
| Image SBOM/provenance | `build-push.yml`, `deploy-do.yml` | Attestations | attest-sbom + attest-build-provenance; verified at deploy | Low | Not cosign-signed (backlog) |
| License docs | `docs/LICENSE_POLICY.md` | Policy + exceptions | Current (2026-10-03) | Low | Root ISC rationale recorded |
| Rotation docs | `docs/SECRETS_ROTATION.md` | 48-secret inventory + log | Current; quarterly reminder workflow | Low | Rotation evidence is domain 38's |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 5 | Root + 6 workspace manifests; overrides + build-script allowlist | None material | Keep |
| Lockfiles | 5 | Single `pnpm-lock.yaml`; overrides mirrored; `--frozen-lockfile` in CI | None | Keep |
| Workspace dependencies | 4 | `workspace:^`/`workspace:*`; `pnpm-workspace.yaml` | No catalog/pinning policy beyond workspace protocol | Document workspace dep conventions |
| Unused/duplicate/deprecated deps | 2 | 55 multi-version names; no depcheck/dedupe gate; unused unknown read-only | No automated check | Add advisory depcheck + `pnpm dedupe --check` |
| Native/build deps | 4 | `onlyBuiltDependencies` allowlist; `--ignore-scripts` in prod install | No verification of blocked builds (no install) | Add a CI note or lockfile assertion |
| Transitive risk indicators | 4 | 22 overrides; all-scope audit gate; allowlist with reason+expiry | Expiry unenforced | Enforce `expires` |
| Dependabot/Renovate | 3 | 8 ecosystems, grouped weekly | Backlog + no SLA/security separation | Triage + SLA |
| Package scripts/postinstall | 4 | No postinstall in workspaces; pnpm 10 build allowlist; `prepare: husky` | `prepare` runs on install (expected) | Keep |
| Docker base images | 5 | All FROM digest-pinned; prod compose digests; e2e digest | Refresh is manual-by-PR | Keep Dependabot coverage |
| GitHub Actions deps | 5 | All third-party `uses:` SHA-pinned; Dependabot github-actions weekly | SHA-to-tag mapping not verifiable offline | Periodic pin audit |
| Environment examples | 4 | Placeholders only; `.env` ignored; tracked-file guard | Worker/web templates were reconciled separately | Keep |
| Secret-like strings | 4 | Scoped gitleaks allowlists + verifier; diff + weekly history scans | PR-time token-format gap; no failure alert | Extend patterns; add notifier |

## Detailed Review

### Item: Dependency vulnerability policy

- Evidence: `scripts/audit-gate.mjs:9-20,75-76,111-140`; `security/dependency-audit-policy.json`; `.github/actions/dependency-audit/action.yml:15-17`.
- What it does: audits all scopes, blocks CRITICAL anywhere and HIGH+ in prod, reports dev-tree advisories, applies a reviewed allowlist.
- Current controls: policy in JSON, gate in CI on PRs (test.yml:52) and the push deploy path (validate.yml:17); `--report` mode for advisory runs.
- Missing controls: `expires` date enforcement (new finding).
- Risks: an allowlisted advisory can outlive its review date.
- Recommended improvement: fail/warn on past `expires`.
- Suggested tests: unit test with a past-dated allowlist entry expecting failure.

### Item: Overrides and `next` scoping

- Evidence: `package.json:59-85` (22 overrides), `pnpm-lock.yaml:7-30` (mirror), line 23 for `next`.
- What it does: forces patched transitive versions, including the deliberately two-branch `next` range.
- Current controls: `--frozen-lockfile` (setup-pnpm:52) prevents lockfile drift; docs/DEPENDENCY_POLICY.md:38-57 documents governance.
- Risks: an override that never matches its target resolution (fixed for `next`); none observed now.
- Recommended improvement: none; keep the sync rule documented.

### Item: Dependabot

- Evidence: `.github/dependabot.yml` (8 entries); `git branch -r` backlog snapshot.
- Current controls: weekly grouped updates on `develop` for npm/actions/docker/terraform; `open-pull-requests-limit: 10`.
- Missing controls: triage SLA, security-update separation, stale-PR cleanup.
- Risks: patch latency and merge conflicts (see still-open SC-P2-005).

### Item: Secret scanning (diff + history + local)

- Evidence: `.github/actions/secret-scan/action.yml:14-60`; `.gitleaks.toml:9-42`; `scripts/ci/verify-gitleaks-config.sh`; `.github/workflows/secret-history-scan.yml`; `.husky/pre-commit:1`; `scripts/scan-secrets.{sh,ps1}`.
- What it does: value-pattern diff scan with redacted output and tracked-env rejection; weekly full-history gitleaks with checksum pinning and allowlist verification; pre-commit hook for local commits.
- Missing controls: platform token formats in the fast scanner; failure notification on the scheduled scan.
- Risks: up-to-7-day detection window for platform tokens; silent scan failure.

### Item: SBOM, provenance and container scanning

- Evidence: `scripts/generate-sbom.mjs:301-329,424,459`; `scripts/validate-sbom.mjs`; `.github/workflows/sbom.yml:35-57`; `build-push.yml:52-91`; `deploy-do.yml:209-248,383-556`; `docs/SBOM_PROCESS.md`.
- What it does: commit-bound lockfile SBOM (validated, weekly), digest-bound per-image SBOMs (attested on deploy), image scans with CRITICAL/HIGH exit-code gates, provenance attestations produced and verified before deploy.
- Missing controls: lockfile SBOM not attached to a release (no tags); no independent cosign signing; SECURITY.md documentation contradicts the attestation state.
- Risks: low; residual is documentation and release-process maturity.

### Item: License policy

- Evidence: `security/license-policy.json`; `scripts/license-gate.mjs`; `.github/workflows/dependency-review.yml:25-26`; `docs/LICENSE_POLICY.md`.
- What it does: PR diff denial of strong copyleft/source-available; full-tree allowlist + named expiring exceptions; stale-exception warning.
- Missing controls: exception `expires` enforcement.
- Risks: accepted license risk persists past review date.

### Item: Container base images and Dockerfiles

- Evidence: three Dockerfiles (all stages digest-pinned); `infra/digitalocean/docker-compose.yml:28,208,248,311`; `docker-compose.yml:66-67`; `.github/dependabot.yml:40-98`.
- What it does: static third-party pins, SHA-tagged app images, digest+attestation verification at deploy, digest-refresh PRs.
- Missing controls: no hadolint CI gate (lint fixes landed manually).
- Risks: low; future Dockerfile regressions unchecked.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SC-001 | Package manifests | `package.json`; workspace manifests | Overrides + build-script allowlist | None material | — | Keep |
| SC-002 | Lockfiles | `pnpm-lock.yaml`; `setup-pnpm/action.yml:52` | Single lockfile, frozen install | None | — | Keep |
| SC-003 | Workspace dependencies | `pnpm-workspace.yaml`; `workspace:^/*` | Workspace protocol | No documented conventions | P3 | Document |
| SC-004 | Unused/duplicate/deprecated | lockfile analysis; no gate | None | 55 duplicate versions; unused unknown | P3 | Add advisory depcheck/dedupe |
| SC-005 | Native/build deps | `package.json:56-58`; Dockerfile `--ignore-scripts` | Build-script allowlist | No blocked-build visibility | P3 | Add CI assertion/note |
| SC-006 | Transitive risk | `audit-gate.mjs`; 22 overrides | All-scope policy gate | `expires` unenforced | P3 | Enforce expiry |
| SC-007 | Dependabot/Renovate | `.github/dependabot.yml`; `git branch -r` | Weekly grouped updates | Backlog + no SLA | P2/P3 | Triage + SLA |
| SC-008 | Scripts/postinstall | `package.json:21,56-58` | No workspace postinstall; allowlist | None material | — | Keep |
| SC-009 | Docker base images | Dockerfiles; compose digests | Digest pins + Dependabot refresh | No hadolint gate | P3 | Add hadolint (backlog) |
| SC-010 | GitHub Actions deps | workflow `uses:` scan | All SHA-pinned | Offline tag mapping | — | Periodic pin audit |
| SC-011 | Environment examples | `.env.example` files; `.gitignore`; secret-scan guard | Placeholders only | None | — | Keep |
| SC-012 | Secret-like strings | `.gitleaks.toml`; scans; pre-commit | Diff + weekly history + local | Token formats; alerting | P2/P3 | Extend patterns; notify |

## Findings

The authoritative finding rows (severity, evidence, impact, recommendation, owner, target, confidence, status, verification note) are in `_domains/11_supply_chain_dependency_secrets.json`. Summary of all 26:

| # | Finding | Sev | Status |
|---|---|---|---|
| 1 | Critical/high advisories persist in the dev dependency tree; `next` override is mis-scoped | P1 | verified-fixed |
| 2 | No image-level container scanning; Trivy scans filesystem only | P2 | verified-fixed |
| 3 | No artifact provenance, attestation, or signing; `id-token: write` requested but unused | P2 | verified-fixed |
| 4 | License policy not enforced in CI; non-OSI and LGPL licenses present | P2 | verified-fixed |
| 5 | SBOM is generated but not bound to a commit or attached to releases/images | P2 | verified-fixed |
| 6 | Dependabot PR backlog is large and not triaged; one stale update conflicts with resolved versions | P2 | still-open |
| 7 | Root package license remains "ISC" | P3 | verified-fixed |
| 8 | e2e Docker image is not digest-pinned | P3 | verified-fixed |
| 9 | Secret-scanner pattern sets diverge between `.sh` and `.ps1` | P3 | verified-fixed |
| 10 | `licenses.json` is committed but unenforced and unverified | P2 | verified-fixed |
| 11 | Swagger UI loads an unpinned third-party script without SRI | P2 | verified-fixed |
| 12 | Unpinned container images (test/local only); production app images tag-based by design | P3 | verified-fixed |
| 13 | Dockerfile lint: missing WORKDIR in web runner stage and shell-form HEALTHCHECK | P3 | verified-fixed |
| 14 | SBOM is produced as a transient artifact, not bound to a release | P3 | verified-fixed |
| 15 | A secrets file exists on disk outside git (should never be committed) | P3 | verified-fixed |
| 16 | gitleaks generic-api-key/jwt hits are false positives (no tracked secret) | P3 | verified-fixed |
| 17 | Deploy-gate secret scan is a no-op on pushes to main | P2 | verified-fixed |
| 18 | Secret scanner misses the platform's own token formats and scans diffs only | P3 | partially-fixed |
| 19 | Dependabot has no security-update separation or triage SLA, and PR template has no enforced link to required checks | P3 | partially-fixed |
| 20 | Secret scanning is diff-scoped only; no full-history scan artifact | P2 | verified-fixed |
| 21 | Produced Terraform `prod.tfvars` is tracked despite `.gitignore` intending to exclude it | P2 | verified-fixed |
| 22 | Scheduled full-history secret scan has no failure notification | P2 | open |
| 23 | Dependency and license policy `expires` dates are not enforced by the gates | P3 | open |
| 24 | Docs instruct the broken `pnpm licenses list --json` workflow while CI uses collect-licenses.mjs | P3 | open |
| 25 | SECURITY.md says neither SBOM is signed or attested, contradicting the attested image-SBOM process | P3 | open |
| 26 | No automated unused/duplicate dependency check; lockfile carries 55 multi-version packages | P3 | open |

### Finding detail — open / partially-fixed / still-open rows

#### Scheduled full-history secret scan has no failure notification (P2, open)

- Severity: P2 · Confidence: high · Area: SC
- Evidence: `.github/workflows/secret-history-scan.yml` (no `if: failure()`/notifier); `.github/workflows/db-restore-test.yml:242-245` (ntfy pattern that already exists); db-backup/storage-backup/deploy-do also notify.
- What is happening: the weekly security scan fails silently except for GitHub's default email to the workflow's last editor.
- Why it matters: a detected credential leak or a broken scan (checksum/install/verifier failure) can go unnoticed for weeks.
- Recommended fix: add an `if: failure()` step posting to the same ntfy topic with Slack fallback and the run URL.
- Suggested validation: dispatch the workflow with a deliberately failing step in a scratch branch and confirm the alert lands.
- Owner: platform/security · Effort: S · Status: open.

#### Dependency and license policy `expires` dates are not enforced by the gates (P3, open)

- Severity: P3 · Confidence: high · Area: SC
- Evidence: `security/dependency-audit-policy.json:16`; `security/license-policy.json:66,76,84,92`; `scripts/audit-gate.mjs:75-76,93`; `scripts/license-gate.mjs:37-38,51,112-113`.
- What is happening: both policy files declare expiry dates, but neither gate compares them to the current date.
- Why it matters: accepted risk persists indefinitely while the policy claims a review deadline.
- Recommended fix: fail (or block) on past `expires`; add tests.
- Owner: supply-chain owner · Effort: S · Status: open.

#### Docs instruct the broken `pnpm licenses list --json` workflow while CI uses collect-licenses.mjs (P3, open)

- Severity: P3 · Confidence: high · Area: SC
- Evidence: `docs/DEPENDENCY_POLICY.md:77`; `docs/SBOM_PROCESS.md:116`; `scripts/collect-licenses.mjs:4-13`; `.github/actions/dependency-audit/action.yml:22-28`.
- What is happening: documented local commands produce an error document on pnpm 10.34.3 (ERR_PNPM_MISSING_PACKAGE_INDEX_FILE).
- Recommended fix: replace with `node scripts/collect-licenses.mjs --out licenses.json` in both docs.
- Owner: platform engineering (docs) · Effort: S · Status: open.

#### SECURITY.md contradicts the attested image-SBOM process (P3, open)

- Severity: P3 · Confidence: high · Area: SC
- Evidence: `SECURITY.md:45-49`; `docs/SBOM_PROCESS.md:14,57-58,153,183`; `.github/workflows/deploy-do.yml:238-241,300-303,369-372`.
- What is happening: SECURITY.md states neither SBOM is signed/attested; the deploy path attests every image SBOM to the registry.
- Recommended fix: correct SECURITY.md to distinguish the attested image SBOMs from the artifact-only lockfile SBOM.
- Owner: platform engineering (docs) · Effort: S · Status: open.

#### Secret scanner misses the platform's own token formats and scans diffs only (P3, partially-fixed)

- Severity: P3 · Confidence: high · Area: SC
- Evidence: `.github/actions/secret-scan/action.yml:14`; `docs/SECRETS_ROTATION.md:37-39,48`; `.github/workflows/secret-history-scan.yml:11,27-47`.
- What is happening: the diff-only half is fixed (weekly full-history gitleaks), but the fast scanner still lacks `dop_v1_`, `sbp_`, `npm_`, `glpat_`, `sk-proj-`/`sk-ant-`, `xoxc`/`xoxd` patterns.
- Recommended fix: run gitleaks on the PR/push diff or extend all three pattern lists.
- Owner: platform/CI owner · Effort: S/M · Status: partially-fixed.

#### Dependabot PR backlog is large and not triaged (P2, still-open)

- Severity: P2 · Confidence: medium · Area: SC
- Evidence: `git branch -r` at 8d299b8d shows 41 dependabot branches, including stale `next-16.2.9` (superseded by `next-16.3.8`); `.github/dependabot.yml:27`.
- What is happening: the queue from the previous audit persists; some families have multiple competing PRs.
- Recommended fix: triage/close stale PRs (start with `next-16.2.9`), add a triage SLA or patch auto-merge behind required checks.
- Owner: supply-chain owner · Effort: M · Status: still-open.
- Caveat: remote-ref snapshot from the audit clone; confirm against live GitHub before bulk actions.

#### Dependabot has no security-update separation or triage SLA (P3, partially-fixed)

- Severity: P3 · Confidence: medium · Area: SC
- Evidence: `.github/dependabot.yml`; `docs/DEPENDENCY_POLICY.md:61-65`; `.github/PULL_REQUEST_TEMPLATE.md:20`.
- What is happening: the PR-template half is addressed (required-checks link present); the SLA/security-separation half is not, and the repo-level security-update setting is not inspectable from the repo.
- Recommended fix: document an SLA and enable/verify Dependabot security updates with a repo-admin check.
- Owner: repo admin (owner decision) · Effort: S · Status: partially-fixed.

#### No automated unused/duplicate dependency check (P3, open)

- Severity: P3 · Confidence: medium · Area: SC
- Evidence: no depcheck/`pnpm dedupe --check` gate; lockfile analysis: 954 snapshots, 55 multi-version names.
- What is happening: duplicates and unused dependencies are not surfaced; unused/deprecated could not be assessed read-only (Unknown).
- Recommended fix: add a non-blocking advisory job and document intentional duplicates.
- Owner: supply-chain owner · Effort: M · Status: open.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Stale Dependabot PRs delay patching and conflict with overrides | P2 | High | Patch latency, merge cost | 41 branches; `next-16.2.9` vs `next-16.3.8` | Triage + SLA/auto-merge |
| Silent failure of the weekly secret-history scan | P2 | Medium | Undetected leaked credential | No notifier in `secret-history-scan.yml` | Add ntfy failure step |
| Platform token committed in a PR detected only at the next weekly scan | P3 | Medium | Up-to-7-day exposure window | `action.yml:14` pattern list | Extend patterns / PR-time gitleaks |
| Expired policy exceptions continue to pass | P3 | Medium | Stale accepted risk | `expires` fields unread by gates | Enforce expiry |
| Operators follow broken `pnpm licenses list` docs | P3 | Medium | Failed local gates, confusion | `DEPENDENCY_POLICY.md:77`; `SBOM_PROCESS.md:116` | Update docs |
| Duplicate/unused dependencies grow unchecked | P3 | Medium | Larger patched surface | 55 multi-version names; no gate | Advisory depcheck/dedupe |

## Recommendations

### Immediate / Release Blocking

- None. No P0/P1 findings; all prior P0/P1 supply-chain fixes re-verified.

### This Week

- Add the failure notifier to `secret-history-scan.yml` (copy the ntfy step from `db-restore-test.yml`).
- Triage the Dependabot backlog; close/refresh the stale `next-16.2.9` PR.

### This Month

- Enforce `expires` in `audit-gate.mjs` and `license-gate.mjs` (+ tests).
- Fix the two broken documented commands and the SECURITY.md SBOM statement.
- Extend the fast secret-scanner patterns (or run gitleaks on the diff).

### Later / Platform Evolution

- Advisory depcheck + `pnpm dedupe --check` job; document intentional duplicates.
- hadolint CI gate for Dockerfiles.
- Consider independent image signing (cosign) / SLSA Build L3; keep GitHub attestations as the baseline.
- Release attachment for the lockfile SBOM once tags/releases exist (REL-P1-001).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| ntfy failure step on the history scan | Removes silent-failure risk | `.github/workflows/secret-history-scan.yml` | Dispatch a failing run; alert lands |
| Fix two doc commands | Removes a known-broken procedure | `docs/DEPENDENCY_POLICY.md`, `docs/SBOM_PROCESS.md` | Run the new command locally |
| Correct SECURITY.md SBOM sentence | Aligns docs with the attestation gate | `SECURITY.md` | Cross-check with `deploy-do.yml` |
| Enforce `expires` | Closes a policy loophole | `scripts/audit-gate.mjs`, `scripts/license-gate.mjs` | Unit test with past-dated entry |
| Close stale Dependabot PRs | Shrinks the queue immediately | GitHub PRs | Branch list shrinks |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Extend/align secret-scanner token formats | P2 | platform/CI | S | none |
| Dependabot triage SLA + security updates | P2 | repo admin | S | GitHub settings access |
| Advisory depcheck/dedupe job | P3 | supply-chain | M | CI job budget |
| hadolint gate | P3 | infra | S | none |
| cosign/SLSA L3 evaluation | P3 | infra | L | release process |
| Lockfile SBOM release attachment | P3 | release owner | M | tags/releases (REL-P1-001) |

## Suggested Tests

- Unit: `audit-gate.mjs` with a past-dated allowlist entry → non-zero exit; `license-gate.mjs` with a past-dated exception → non-zero exit.
- CI: a scratch PR adding `DO_API_TOKEN=dop_v1_<fixture>` → diff scanner must fail (today it would not).
- CI: dispatch `secret-history-scan.yml` with a forced failure → notifier fires.
- Regression: `validate-sbom.mjs` on a truncated SBOM (<100 components) → fails; existing.
- Manual: run `node scripts/collect-licenses.mjs --out licenses.json && node scripts/license-gate.mjs licenses.json` on a fresh clone → PASS with current policy.

## Suggested Documentation Updates

- `docs/DEPENDENCY_POLICY.md` — replace the `pnpm licenses list` command; add duplicate/deprecation review guidance and (optionally) the triage SLA.
- `docs/SBOM_PROCESS.md` — replace the local command; clarify the lockfile SBOM release-attachment residual.
- `SECURITY.md` — correct the "neither SBOM is signed or attested" sentence.
- `docs/CI.md` — already current on SBOM artifact-only status; verify after the above changes.
- `docs/SECRETS_ROTATION.md` — (domain 38) rotation log still shows only the initial entry.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which Dependabot PRs are still open vs merged? | Triage scope | GitHub API/UI (no access here) |
| Is Dependabot security-update separation enabled at repo level? | Patch latency | Repo settings screen |
| Is the ntfy alert topic actually wired to on-call? | Failure notification value | `NTFY_ALERTS_*` secrets + test alert |
| Are any current dependencies deprecated? | Replacement planning | `pnpm install` + `pnpm audit`/deprecation data (not run, read-only) |
| Do the gitleaks default rules cover Supabase `sbp_` tokens? | Whether history scan catches them | gitleaks 8.30.1 rule set (not available offline) |
| Are Actions SHA pins mapping to the intended release tags? | Pin integrity | Network/API verification |

## Appendix

- Lockfile duplicate sample (static analysis at 8d299b8d): `@supabase/realtime-js` 2.106.2/2.117.2, `@types/react-dom` 18.3.7/19.3.0, `brace-expansion` 1.1.21/5.0.12, `ajv` 6.15.0/8.20.0, `debug` 2.6.9/4.4.3, `chalk` 3.0.0/4.1.2.
- Previous-run rows re-verified in this domain: SC-P1-001, SC-P2-001..005, SC-P3-001..003, SUPPLY-P2-001/002, SUPPLY-P3-001..004, SEC-P3-001, SECRET-P2-003/004, CI-P2-002, CI-P3-005, BP-P3-002. Rows left to owning domains: SECRET-P2-001/002 (rotation inventory/reminder, domain 38), CONF-P3-001 / IR-P2-004 (rotation evidence, domain 38), SBOM-P1/P2/P3 rows (domain 35), INFRA-P3-008 (duplicate of SECRET-P2-004, infra domain).
- Commit references used: `6757a478` (audit gate + image scans + attestations), `7dfb8650` (scanner alignment + rotation reminder), `f69b5899` (gitleaks allowlists + negative fixture), `d56c755a` (#135 history scan), `7fc3f1f6` (#89 e2e digest), `2da4e9bd` (#146 Dependabot docker digests), `288cde6a` (collect-licenses.mjs).

## Findings

| ID | Severity | Title |
|---|---|---|
| SC-P1-001 | P1 | Critical/high advisories persist in the dev dependency tree; `next` override is mis-scoped |
| SC-P2-001 | P2 | No image-level container scanning; Trivy scans filesystem only |
| SC-P2-002 | P2 | No artifact provenance, attestation, or signing; `id-token: write` requested but unused |
| SC-P2-003 | P2 | License policy not enforced in CI; non-OSI and LGPL licenses present |
| SC-P2-004 | P2 | SBOM is generated but not bound to a commit or attached to releases/images |
| SC-P2-005 | P2 | Dependabot PR backlog is large and not triaged; one stale update conflicts with resolved versions |
| SC-P3-001 | P3 | Root package license remains "ISC" |
| SC-P3-002 | P3 | e2e Docker image is not digest-pinned |
| SC-P3-003 | P3 | Secret-scanner pattern sets diverge between `.sh` and `.ps1` |
| SC-P2-006 | P2 | `licenses.json` is committed but unenforced and unverified |
| SC-P2-007 | P2 | Swagger UI loads an unpinned third-party script without SRI |
| SC-P3-004 | P3 | Unpinned container images (test/local only); production app images tag-based by design |
| SC-P3-005 | P3 | Dockerfile lint: missing WORKDIR in web runner stage and shell-form HEALTHCHECK |
| SC-P3-006 | P3 | SBOM is produced as a transient artifact, not bound to a release |
| SC-P3-007 | P3 | A secrets file exists on disk outside git (should never be committed) |
| SC-P3-008 | P3 | gitleaks generic-api-key/jwt hits are false positives (no tracked secret) |
| SC-P2-008 | P2 | Deploy-gate secret scan is a no-op on pushes to main |
| SC-P3-009 | P3 | Secret scanner misses the platform's own token formats and scans diffs only |
| SC-P3-010 | P3 | Dependabot has no security-update separation or triage SLA, and PR template has no enforced link to required checks |
| SC-P2-009 | P2 | Secret scanning is diff-scoped only; no full-history scan artifact |
| SC-P2-010 | P2 | Produced Terraform `prod.tfvars` is tracked despite `.gitignore` intending to exclude it |
| SC-P2-011 | P2 | Scheduled full-history secret scan has no failure notification |
| SC-P3-011 | P3 | Dependency and license policy `expires` dates are not enforced by the gates |
| SC-P3-012 | P3 | Docs instruct the broken `pnpm licenses list --json` workflow while CI uses collect-licenses.mjs |
| SC-P3-013 | P3 | SECURITY.md says neither SBOM is signed or attested, contradicting the attested image-SBOM process |
| SC-P3-014 | P3 | No automated unused/duplicate dependency check; lockfile carries 55 multi-version packages |
