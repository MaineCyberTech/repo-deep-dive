# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

# SBOM and License Policy Audit

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (MaineCyberTech portal monorepo)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd` (2026-10-11 00:13:46 -0400, "Merge PR #168: promote develop to main")
- Generated at: 2026-10-11
- Auditor: subagent domain pass (prompt 35), read-only
- Area code: SBOM
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/35_sbom_license_policy.md`
- Scope limitations: the audit host has no `node`/`pnpm` runtime and the target is read-only (no installs), so the `.mjs` scripts were inspected statically and their lockfile-parsing assumptions were reproduced with a `python3` walk; GitHub-side state (Dependabot PR backlog, live required checks, Dependabot alerts) is not observable from the repository and is marked `Unknown`/medium confidence where relevant. Live GHCR attestations were not queried.

## Scope

Reviewed: package manifests and license fields; `pnpm-lock.yaml`; Dockerfiles and both compose files; GitHub Actions workflows and composite actions (SBOM, dependency review, build/push, deploy, validate, test, CodeQL); dependency-update config; the SBOM generator/validator and license/audit gates; the license and dependency-audit policies; the SBOM, license, dependency, CI and release documentation; release provenance/signing; the exception process.

Not reviewed here (owned by other domains): image digest pinning policy and Dockerfile lint (container runtime security), secret scanning/rotation, and the CI workflow topology itself.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `package.json`, `apps/*/package.json`, `packages/*/package.json` | manifests | license fields, versions, pnpm overrides | all declare `ISC`; root `packageManager: pnpm@10.34.3` |
| `pnpm-lock.yaml` | lockfile | resolved tree, integrity, graph source | 1,446 package entries, all with `integrity`; `snapshots:` + `importers:` present |
| `scripts/generate-sbom.mjs` (472 lines) | generator | CycloneDX 1.5 lockfile SBOM | commit/version binding, licenses, graph, serialNumber |
| `scripts/validate-sbom.mjs` | validator | CI regression guard | floor 100, unique bom-refs, no dangling refs, binding |
| `scripts/collect-licenses.mjs` | collector | replaces broken `pnpm licenses list` | reads installed tree |
| `scripts/license-gate.mjs`, `security/license-policy.json` | policy gate | allow/deny + exceptions | string-scoped matching (finding) |
| `scripts/audit-gate.mjs`, `security/dependency-audit-policy.json` | vulnerability gate | all-scope advisories + allowlist | `expires` unenforced (finding) |
| `.github/workflows/sbom.yml`, `dependency-review.yml`, `build-push.yml`, `deploy-do.yml`, `validate.yml`, `test.yml`, `codeql.yml` | CI | generation, gating, attestation, verification | see inventory |
| `.github/actions/dependency-audit/action.yml`, `setup-pnpm/action.yml` | composite actions | shared gates, frozen-lockfile install | used by test.yml:52 and validate.yml:17 |
| `.github/dependabot.yml` | update config | npm/actions/docker/terraform | weekly, grouped, limit 10 |
| `docs/SBOM_PROCESS.md`, `docs/LICENSE_POLICY.md`, `docs/DEPENDENCY_POLICY.md`, `docs/CI.md`, `docs/RELEASING.md` | docs | claims to verify against code | several drift items |
| `apps/*/Dockerfile`, `infra/digitalocean/docker-compose.yml`, `docker-compose.yml` | images | base/runtime image identity | base images and third-party runtime images digest-pinned |
| `.gitignore:59-63` | config | generated-artifact tracking policy | licenses.json/sbom.* ignored |
| pinned `actions/dependency-review-action@2031cfc` README + `src/licenses.ts` + `src/purl.ts` | upstream | semantics of deny-licenses / allow-dependencies-licenses | fetched during audit |

## Verification Performed

| Command / action | Observed result |
|---|---|
| `git log -1 --format='%H %ci %s'` | `8d299b8d…` 2026-10-11, merge of PR #168 — target confirmed |
| `git diff --stat 9c0b88c..HEAD -- <domain files>` | empty: every SBOM/license file is byte-identical to the previous audit target; only `deploy-do.yml` changed (observability/SSH, +34/-5) |
| `cat .github/workflows/sbom.yml` | generate → validate → upload (30-day artifact); no install failure path; uses `collect-licenses.mjs` |
| `grep -n "attest\|sbom\|provenance\|id-token\|digest" deploy-do.yml` | per-image Trivy SBOM + `actions/attest-sbom` + `attest-build-provenance`; `verify-attestations` gates deploy |
| `grep -rn "uses:" .github/workflows .github/actions \| grep -v "@[0-9a-f]\{40\}"` | no unpinned action references (all 40-hex SHAs) |
| `git tag \| wc -l` | `0` — no tags; `grep -rn "softprops\|gh release\|create-release" .github scripts docs` → only prior audit reports |
| `git ls-files -- licenses.json sbom.cdx.json sbom.spdx.json` | empty (untracked); `.gitignore:60,63` ignores them; composite action fails if tracked again |
| python3 walk of `pnpm-lock.yaml` using the generator's exact regexes | 1,446 package entries, 1,446 integrity lines, 1,446 distinct name@version; floor 100 and graph checks have real input |
| `node scripts/generate-sbom.mjs` / `validate-sbom.mjs` / `license-gate.mjs` | **not reproducible** — `node: command not found` on the audit host; no install allowed. Static analysis + lockfile walk used instead |
| `grep -n "expires" scripts/license-gate.mjs scripts/audit-gate.mjs` | no match in either gate (policies carry `expires`; nothing reads it) |
| `grep -n "packages" scripts/license-gate.mjs` | only inventory iteration; `entry.packages` from the policy is never consulted |
| `webfetch` pinned `dependency-review-action` README + `src/licenses.ts` + `src/purl.ts` | `deny-licenses` deprecated; unlicensed deps never fail; `allow-dependencies-licenses` purl matching normalizes `%40` (the sharp exemption does apply on the PR gate) |
| `grep -n "image:" infra/digitalocean/docker-compose.yml` | redis/prometheus/alertmanager/caddy digest-pinned; app images `:${IMAGE_TAG}` (tag) |
| `sed -n '391,515p' deploy-do.yml`, `grep -n "pull_retry"` | digest resolved+verified at :501-514, then pulled by tag at :786-788 |
| `grep -rn "dependabot" .github/workflows` | no triage/auto-merge automation |

## Executive Summary

The domain has moved a long way from the prior full run. The lockfile SBOM is CycloneDX 1.5, commit- and version-bound, carries per-component licenses and a dependency graph, and is validated by a regression guard before upload (`sbom.yml:35-60`). Every shipped image gets a Trivy CycloneDX SBOM bound to its pushed digest and attested into the registry (`deploy-do.yml:220-243` and siblings), build provenance is attested and **verified fail-closed before deploy** (`verify-attestations`), and a real license allow/deny policy now runs on every PR and on the deploy gate over the full resolved tree (`license-gate.mjs` + `security/license-policy.json` + the `dependency-audit` composite). Generated aggregates stay untracked by policy and by guard. All GitHub Actions are SHA-pinned and Dependabot covers npm, actions, docker and terraform.

The remaining risk is not absence but **contract fidelity**. The license exceptions are matched by license string only, so the documented per-package scoping is not enforced and the `UNKNOWN` exception lets any unlicensed package pass both gates. Exception `expires` dates are decoration — neither gate reads them. On the provenance side, the deploy verifies the tag→digest attestation and then pulls the **mutable tag**, so a registry writer could substitute the artifact after verification; the SBOM predicate is never explicitly verified. Image SBOMs are attested without any completeness/binding validation, third-party runtime images (redis, caddy, prometheus, alertmanager) and the Actions dependencies have no SBOM coverage, and there is no scheduled re-scan of the resolved tree against newly published advisories. Documentation drift (broken `pnpm licenses list` command in runbooks/headers, a sharp exception that does not exist in the machine policy, a stale CI.md row) will mislead the next operator or agent.

Verdict: the pipeline is **functionally strong (score ~4/5) but not yet trustworthy as an audit artifact** until exception scoping/expiry, digest-pinned deployment, image-SBOM validation and the scheduled advisory scan are fixed. No P0/P1 issues were found at this commit; the previously filed P1s are verified fixed except the release-identity residual (partially fixed).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Lockfile SBOM | `scripts/generate-sbom.mjs`, `sbom.yml` | CycloneDX 1.5 npm SBOM | implemented, validated | low | commit+version bound; 30-day artifact; not release-attached |
| Image SBOM | `deploy-do.yml:220-243` etc., `build-push.yml:64-90` | per-image OS+npm SBOM | implemented, attested on deploy path | medium | unvalidated; third-party images uncovered |
| Provenance | `actions/attest-build-provenance` | SLSA-style build provenance | implemented + verified | medium | verified against tag→digest, deploy pulls tag |
| SBOM attestation | `actions/attest-sbom` (`push-to-registry`) | durable digest-bound SBOM | implemented | medium | predicate not verified at deploy |
| License policy | `security/license-policy.json`, `scripts/license-gate.mjs` | allow/deny + exceptions | implemented in CI | medium | string-scoped; expiry ignored |
| PR license gate | `dependency-review.yml` | diff-level deny list | implemented | medium | deprecated option; unlicensed never fails |
| Vulnerability gate | `scripts/audit-gate.mjs`, `security/dependency-audit-policy.json` | all-scope advisories | implemented on PR/deploy | medium | no schedule; expiry ignored |
| License inventory | `scripts/collect-licenses.mjs` | licenses.json from installed tree | implemented | low | docs still name the broken pnpm command |
| Dependency updates | `.github/dependabot.yml` | npm/actions/docker/terraform | configured | medium | no triage automation |
| Generated artifacts | `.gitignore:59-63`, composite guard | untracked aggregates | enforced | low | `git ls-files` empty |
| Release identity | `VERSION`, git tags, releases | product version / release | partial | medium | no tags/releases (documented decision) |
| Docs | `docs/SBOM_PROCESS.md`, `LICENSE_POLICY.md`, `DEPENDENCY_POLICY.md`, `CI.md` | operator guidance | mostly accurate | low | several stale commands/rows |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Package manifests | 4 | all workspace `package.json` declare `ISC`; rationale documented (`docs/LICENSE_POLICY.md:66-71`) | no per-package license CI check (lockfile only) | add a manifest license lint to the docs/guard set |
| Lockfiles | 4 | `pnpm-lock.yaml` committed; `setup-pnpm` installs `--frozen-lockfile` (action.yml:52) | lockfile freshness only via Dependabot | keep |
| Docker images | 4 | base images digest-pinned (`apps/*/Dockerfile:1`); prod compose third-party images digest-pinned | app images pulled by tag after verification | digest-pinned deploy (new finding) |
| GitHub Actions | 4 | every `uses:` is a 40-hex SHA; Dependabot `github-actions` weekly | no inventory/SBOM of Actions deps | generate an actions inventory (new finding) |
| Dependency updates | 3 | comprehensive `dependabot.yml`; PRs re-run both gates | no triage automation; no scheduled re-scan | scheduled audit + triage SLA |
| License fields | 4 | per-component `licenses` in the lockfile SBOM; root/workspace ISC | license data depends on licenses.json presence | keep |
| Third-party/transitive deps | 4 | full resolved tree gated in CI; graph emitted | exception scoping/UNKNOWN fail-open | scope exceptions by package |
| SBOM workflows | 4 | generate→validate→upload; parser-regression floor | not part of the deploy gate (documented artifact-only) | optionally run generate+validate in validate.yml |
| Container SBOM | 4 | digest-bound image SBOMs, attested on deploy path | unvalidated; third-party runtime images uncovered | validate image SBOMs; cover redis/caddy/etc. |
| Dependency review | 3 | `fail-on-severity: high` + deny list + purl exemptions | deprecated `deny-licenses`; unlicensed never fails | migrate to `allow-licenses`; no-license failure |
| Vulnerability alerts | 3 | audit-gate on every PR and deploy; CodeQL weekly | no scheduled dependency re-scan | weekly `audit-gate` job or documented Dependabot reliance |
| Release provenance | 3 | provenance attested + verified; SBOMs digest-bound | tag-TOCTOU; no tags/releases | digest-pinned deploy; tag/release decision |

## Detailed Review

### Item: Lockfile SBOM generation and binding

- Evidence: `scripts/generate-sbom.mjs:258-269,300-315,325-328,365-406,424-465`; `sbom.yml:35-60`; `scripts/validate-sbom.mjs:47-67`.
- What it does: parses `pnpm-lock.yaml` (packages/snapshots/importers) into a CycloneDX 1.5 document with purls, hex integrity hashes, per-component licenses, a dependency graph, a deterministic serialNumber, and `metadata.component.version = "<VERSION>+<sha>"` plus `mct:productVersion`/`mct:commit`.
- Current controls: validation before upload (format, unique refs, dangling refs, floor 100, binding); CI regenerates it on push/PR/weekly.
- Missing controls: no durable storage for the lockfile SBOM (30-day artifact); no release attachment.
- Risks: a per-commit npm BOM is unavailable after the artifact window.

### Item: Image SBOMs and attestation

- Evidence: `deploy-do.yml:220-243,286-304,355-373`; `build-push.yml:64-90,135-160,216-241`; `docs/SBOM_PROCESS.md:36-63`.
- What it does: Trivy scans the pushed digest (`format: cyclonedx`) and (on the deploy path) `actions/attest-sbom` binds the document to the digest as an OCI referrer.
- Current controls: digest binding; durable attestation.
- Missing controls: no validation of the image SBOM; no SBOM for redis/caddy/prometheus/alertmanager.

### Item: Deploy attestation verification

- Evidence: `deploy-do.yml:391-515` (verify), `:786-788` (pull), `infra/digitalocean/docker-compose.yml:69,131,187`.
- What it does: resolves each tag to a digest, runs `gh attestation verify` with `--signer-workflow`/`--source-digest`, fail-closed; rollback path uses an explicit allow-list.
- Missing controls: the resolved digest is not passed to the deploy; the pull is by tag; no `--predicate-type` for provenance or SBOM.
- Risks: post-verification substitution; SBOM predicate could be absent while verification still passes.

### Item: License policy and exception process

- Evidence: `security/license-policy.json`; `scripts/license-gate.mjs:35-146`; `dependency-review.yml:17,25-30`; `docs/LICENSE_POLICY.md:6-98`.
- What it does: full-tree allow/deny gate on every PR and deploy; diff-level deny list on PRs; exceptions carry a reason, package list and expiry.
- Missing controls: package scope and `expires` are not enforced; the docs/JSON disagree for sharp; `deny-licenses` is deprecated; unlicensed deps never fail.
- Risks: a new copyleft/unlicensed dependency can pass unreviewed.

### Item: Dependency updates and vulnerability alerts

- Evidence: `.github/dependabot.yml`; `.github/actions/dependency-audit/action.yml:12-17`; `test.yml:52`; `validate.yml:17`; `codeql.yml:8-9`.
- What it does: weekly grouped updates; audit gate on PRs and deploys; CodeQL weekly.
- Missing controls: no scheduled dependency audit; no triage automation.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SBOM-001 | Package manifests | `package.json:4` + workspace manifests | ISC declared everywhere; rationale documented | no manifest lint | P3 | add a manifest license check |
| SBOM-002 | Lockfiles | `pnpm-lock.yaml`; `setup-pnpm/action.yml:52` | frozen-lockfile installs; integrity in SBOM | — | — | keep |
| SBOM-003 | Docker images | `apps/*/Dockerfile:1`; compose files | digest-pinned base/third-party images | app images pulled by tag | P2 | digest-pinned deploy |
| SBOM-004 | GitHub Actions | all `uses:` SHA-pinned; `dependabot.yml` | pinning + weekly updates | no actions SBOM | P3 | generate an actions inventory |
| SBOM-005 | Dependency updates | `dependabot.yml:1-87` | grouped weekly PRs | no triage automation | P2 | triage SLA / automation |
| SBOM-006 | License fields | `generate-sbom.mjs:356-358` | per-component licenses in SBOM | depends on licenses.json | — | keep |
| SBOM-007 | Third-party/transitive deps | `license-gate.mjs`; lockfile SBOM graph | full-tree gate + graph | exception scoping/UNKNOWN | P2 | scope by package; fail UNKNOWN |
| SBOM-008 | SBOM workflows | `sbom.yml:35-60` | generate/validate/upload | artifact-only (documented) | P3 | consider a deploy-gate run |
| SBOM-009 | Container SBOM | `deploy-do.yml:220-243` | digest-bound, attested | unvalidated; third-party images | P2/P3 | validate; extend coverage |
| SBOM-010 | Dependency review | `dependency-review.yml:17,25-30` | severity + deny list | deprecated option; unlicensed | P3 | migrate to allow-licenses |
| SBOM-011 | Vulnerability alerts | `audit-gate.mjs` via composite | PR + deploy gating | no schedule | P2 | weekly audit job |
| SBOM-012 | Release provenance | `verify-attestations`; `generate-sbom.mjs` | provenance verified; commit/digest binding | tag-TOCTOU; no tags/releases | P2 | digest-pinned deploy; release decision |

## Findings

Verification rows reuse the previous register's titles (aggregator assigns IDs); new findings are listed after them. Full evidence is in `35_sbom_license_policy.json`.

### Verification of previous findings (17 rows)

| Title | Sev | Status | Key evidence at 8d299b8d |
|---|---|---|---|
| SBOM Is Lockfile-Only, Not an Image SBOM or Attestation | P1 | verified-fixed | `deploy-do.yml:220-243` attest-sbom per image |
| Unsigned Images With No Provenance/Attestation | P1 | verified-fixed | `build-push.yml:85-90`; `deploy-do.yml:391-515` verify fail-closed |
| No version identity: no tags, no product version, no commit binding in generated artifacts | P1 | partially-fixed | `generate-sbom.mjs:441-465` binds version+commit; `git tag` = 0 |
| No license allow/deny policy in dependency review or any CI gate | P1 | verified-fixed | `license-policy.json`; `license-gate.mjs`; composite in test/validate |
| SBOM carries no license data and no dependency graph | P1 | verified-fixed | `generate-sbom.mjs:258-269,365-406`; `validate-sbom.mjs:47-54` |
| SBOM is artifact-only: not release-bound, not commit-bound, not attested | P2 | partially-fixed | image path fixed; lockfile SBOM still 30-day artifact (`SBOM_PROCESS.md:179-186`) |
| No container/image SBOM; base-image OS packages untracked | P2 | verified-fixed | Trivy `format: cyclonedx` per digest |
| `docs/CI.md` documents the SBOM workflow as "Blocking" but it gates nothing | P2 | verified-fixed | `docs/CI.md:29` now "Artifact-only (not a gate)" |
| No artifact provenance, attestation, or signing; `id-token: write` unused | P2 | verified-fixed | permissions used; provenance attested + verified |
| License policy not enforced in CI; non-OSI and LGPL licenses present | P2 | verified-fixed | gate runs in CI; exceptions documented |
| SBOM is generated but not bound to a commit or attached to releases/images | P2 | verified-fixed | commit-bound; digest-bound+attested; releases N/A |
| Dependabot PR backlog is large and not triaged | P2 | open | repo-side: config only, no triage automation; backlog not repo-visible |
| Root license is ISC with no documented rationale | P3 | verified-fixed | `docs/LICENSE_POLICY.md:66-71` documents rationale |
| SBOM format/count not validated before upload; no regression guard | P3 | verified-fixed | `validate-sbom.mjs` + `sbom.yml:52-53` |
| Root package license remains "ISC" | P3 | still-open | `package.json:4` ISC; now declared intentional (owner decision) |
| `licenses.json` is committed but unenforced and unverified | P2 | verified-fixed | `.gitignore:60,63`; untracked guard; `git ls-files` empty |
| SBOM is produced as a transient artifact, not bound to a release | P3 | verified-fixed | registry-side SBOM attestations on the deploy path |

### New findings (9 rows)

#### SBOM-P2 (new) — License exceptions are matched by license string only; documented package scope and UNKNOWN fail open

- Severity: P2 · Confidence: high · Status: open
- Evidence: `scripts/license-gate.mjs:37-39,50-53` (exceptions keyed by license; `entry.packages` never read); `security/license-policy.json:87-92` (`UNKNOWN` exception for browser-assert → blanket pass for every unlicensed package); `docs/LICENSE_POLICY.md:44-45` claims per-package scoping that the code does not implement; pinned `dependency-review-action` `src/licenses.ts` reports unlicensed deps without failing.
- What is happening: any new dependency whose license string equals an exception key passes without review, and any package with no license field passes both gates.
- Why it matters: the compliance control does not implement its documented contract; a future MPL-2.0 / LGPL-3.0-or-later / FSL / unlicensed dependency merges unreviewed.
- Recommended fix: match on (license, package name); fail UNKNOWN unless the package is explicitly listed; update JSON comment and docs; add unit fixtures.
- Owner/effort: supply-chain owner · S–M

#### SBOM-P2 (new) — Exception `expires` dates are documentation-only

- Severity: P2 · Confidence: high · Status: open
- Evidence: `security/license-policy.json:66,76,84,92`; `security/dependency-audit-policy.json:16`; neither `scripts/license-gate.mjs` nor `scripts/audit-gate.mjs` references `expires` (grep); `docs/DEPENDENCY_POLICY.md:30` promises an expiry.
- Why it matters: accepted risks outlive their review with no failing signal (the only removal hint is when the license string vanishes — never for UNKNOWN).
- Recommended fix: parse ISO dates and fail/warn when past due; add a past-date fixture test.
- Owner/effort: supply-chain owner · S

#### SBOM-P2 (new) — Deploy verifies the tag's attestation but pulls by mutable tag; SBOM predicate never verified

- Severity: P2 · Confidence: high · Status: open
- Evidence: `deploy-do.yml:501-514` (tag→digest + `gh attestation verify`, no `--predicate-type`), `:786-788` (pull by `:${IMAGE_TAG}`), `docker-compose.yml:69,131,187`; `docs/SBOM_PROCESS.md:120-135` documents a stronger manual check than CI runs; `:159-174` claims deploy-time verification.
- Why it matters: post-signing substitution (re-pointing the commit tag) defeats the stated guarantee; the SBOM predicate could be absent while verification still passes. Direct hit on the "no post-signing additions" extended check.
- Recommended fix: pass resolved digests from `verify-attestations` to the deploy and pull/run by digest (or re-verify on the droplet); add `--predicate-type` checks for provenance and SBOM.
- Owner/effort: platform/infrastructure · M

#### SBOM-P2 (new) — No scheduled dependency vulnerability re-scan

- Severity: P2 · Confidence: medium · Status: open
- Evidence: `dependency-audit` composite (`action.yml:12-17`) is only invoked from `test.yml:52` (PR) and `validate.yml:17` (deploy gate); `sbom.yml:8-9` is weekly but never runs the audit; `codeql.yml:8-9` is code scanning.
- Why it matters: advisories published while the tree is unchanged stay invisible to CI; Dependabot alerts may cover it but are not repo-verifiable.
- Recommended fix: weekly scheduled `audit-gate.mjs` (or report + dedup issue), or document Dependabot alerts as the compensating control with a triage date.
- Owner/effort: supply-chain owner · S

#### SBOM-P3 (new) — Image SBOMs are attested but never validated

- Severity: P3 · Confidence: high · Status: open
- Evidence: `validate-sbom.mjs:56-61` + `SBOM_PROCESS.md:95-100` (lockfile only); `deploy-do.yml:220-243` attests with no validation step; `build-push.yml:64-83` uploads unvalidated.
- Why it matters: an empty/partial image SBOM would be attested and retained as the durable record for that digest.
- Recommended fix: small validator (component floor, expected classes, digest in `metadata.component.purl`) run before attest/upload.
- Owner/effort: platform/infrastructure · S

#### SBOM-P3 (new) — Runbooks and script headers still document the broken `pnpm licenses list --json`; docs/CI.md row stale

- Severity: P3 · Confidence: high · Status: open
- Evidence: `docs/SBOM_PROCESS.md:116,26`; `docs/DEPENDENCY_POLICY.md:77`; `scripts/license-gate.mjs:16,30`; `scripts/generate-sbom.mjs:11,258`; the failure mode is documented at `sbom.yml:36-47` and `collect-licenses.mjs:5-19` (pinned pnpm 10.34.3 writes an error document); `docs/CI.md:29` still credits build-push.yml only for image SBOMs.
- Why it matters: the documented local procedure fails as written and can produce an error-document licenses.json.
- Recommended fix: point every doc/header at `node scripts/collect-licenses.mjs --out licenses.json`; refresh the CI.md row.
- Owner/effort: supply-chain owner · S

#### SBOM-P3 (new) — Documented sharp license exception does not match the machine policy

- Severity: P3 · Confidence: medium · Status: open
- Evidence: `docs/LICENSE_POLICY.md:50` (`Apache-2.0 AND LGPL-3.0-or-later`, `@img/sharp-win32-x64`) vs `security/license-policy.json:79-81` (key `LGPL-3.0-or-later`, `@img/sharp-libvips-linux-x64`) vs `dependency-review.yml:28` (Windows purl comment); `license-gate.mjs:54-63` denies an expression whose LGPL leaf is denied and whose full string is not an exception key.
- Why it matters: the documented exception does not protect the documented case on a non-Linux run; the table of record disagrees with the machine policy.
- Recommended fix: align the exception key/package with reality, implement package scoping, and regenerate the docs table (or add a parity check).
- Owner/effort: supply-chain owner · S

#### SBOM-P3 (new) — Shipped third-party images and GitHub Actions deps have no SBOM coverage

- Severity: P3 · Confidence: high · Status: open
- Evidence: `infra/digitalocean/docker-compose.yml:28,208,248,311` (redis/prometheus/alertmanager/caddy, digest-pinned); image SBOMs only for mct-api/worker/web (`deploy-do.yml:220,286,355`); acknowledged at `SBOM_PROCESS.md:89-91,170-171`; no actions inventory.
- Why it matters: OS advisories in the runtime sidecars cannot be mapped from the produced SBOMs; Actions inventory is implicit in workflow files.
- Recommended fix: emit/retain SBOMs for the third-party images by digest; add a generated actions inventory.
- Owner/effort: platform/infrastructure · M

#### SBOM-P3 (new) — PR license gate depends on the deprecated `deny-licenses` and cannot fail on unknown licenses

- Severity: P3 · Confidence: high · Status: open
- Evidence: `dependency-review.yml:25-26`; pinned action README (deprecation warning; "if we can't detect the license … the action won't fail"); pinned `src/licenses.ts` (unlicensed/NOASSERTION never `forbidden`).
- Why it matters: the diff layer silently stops enforcing when the option is removed and never blocks unlicensed additions.
- Recommended fix: migrate to `allow-licenses` and/or rely on the full-tree gate; add the no-license failure to `license-gate.mjs`.
- Owner/effort: supply-chain owner · S

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unreviewed copyleft/unlicensed dependency enters the tree | P2 | Medium | Legal/compliance exposure | license-gate string scoping; UNKNOWN exception | package-scoped exceptions; fail UNKNOWN |
| Post-verification image substitution at deploy | P2 | Low | Runs an unverified artifact in prod | tag pull after digest verification | digest-pinned pull/re-verify |
| Durable SBOM attestation records an empty image SBOM | P3 | Low | Incident triage relies on bad data | no image-SBOM validation | validate before attest |
| Advisory published between deploys is missed | P2 | Medium | Slow remediation | no scheduled audit | weekly audit job / Dependabot reliance documented |
| Expired exception silently persists | P2 | Medium | Accepted risk outlives review | `expires` unread | enforce expiry in gates |
| Operator runbook fails locally | P3 | Medium | Wasted time / missing licenses locally | broken pnpm command in docs | point to collect-licenses.mjs |
| Release identity absent (no tags/releases) | P3 | High | SBOM not release-attachable | `git tag` = 0 | owner decision (REL-P1-001) |

## Recommendations

### Immediate / Release Blocking

None. No P0/P1 findings are open at this commit.

### This Week

1. Scope license exceptions by package and fail `UNKNOWN` by default (`license-gate.mjs` + policy JSON + docs + fixtures).
2. Enforce `expires` in `license-gate.mjs` and `audit-gate.mjs`.
3. Digest-pin the deploy: pass resolved digests from `verify-attestations` and pull/run by `@sha256:…`; add `--predicate-type` checks.

### This Month

4. Add a weekly scheduled dependency audit (enforcing or report + dedup issue).
5. Validate image SBOMs before attest/upload.
6. Fix the runbook/header drift (`collect-licenses.mjs`) and the sharp exception/docs mismatch.
7. Decide and record: release tags/attachment (REL-P1-001) and lockfile-SBOM durability (SBOM-P2-001).

### Later / Platform Evolution

8. Cover third-party runtime images with SBOMs; add an Actions inventory.
9. Migrate the PR gate off `deny-licenses` to `allow-licenses`.
10. Optionally run `generate-sbom.mjs` + `validate-sbom.mjs` in `validate.yml` so a parser regression blocks deploys (dependency-free, cheap).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fail on expired exceptions | closes a silent drift | `license-gate.mjs`, `audit-gate.mjs` | fixture with past date fails |
| Package-scope exceptions | restores the documented contract | `license-gate.mjs`, `license-policy.json` | fixture: same license, different package fails |
| Replace the pnpm command in docs/headers | runbook works as written | `SBOM_PROCESS.md`, `DEPENDENCY_POLICY.md`, `license-gate.mjs`, `generate-sbom.mjs` | literal walk on a dev box |
| Add `--predicate-type` to `gh attestation verify` | requires the predicate that is claimed | `deploy-do.yml` | dry-run dispatch, job summary shows both checks |
| Refresh `docs/CI.md:29` image-SBOM producer | docs match pipeline | `docs/CI.md` | review |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Digest-pinned deploy + post-pull re-verification | P2 | platform/infrastructure | M | verify-attestations outputs |
| Weekly dependency audit job | P2 | supply-chain owner | S | none |
| Image-SBOM validator | P3 | platform/infrastructure | S | none |
| Third-party image SBOM coverage | P3 | platform/infrastructure | M | SBOM job design |
| Actions dependency inventory | P3 | supply-chain owner | S | none |
| Release tags + SBOM attachment decision | P3 | release owner | S–M | owner decision |
| Exception parity check (docs ↔ JSON) | P3 | supply-chain owner | S | package scoping |

## Suggested Tests

- Unit: `license-gate.mjs` fixtures — allowed license passes; denied fails; exception for package A does not cover package B; `UNKNOWN` for a listed package passes, for a new package fails; expired exception fails/warns.
- Unit: `audit-gate.mjs` — expired allowlist entry fails/warns.
- Unit: image-SBOM validator — empty components, missing digest in `metadata.component.purl`, and a valid Trivy document.
- CI: assert `docs/LICENSE_POLICY.md` exception table equals `security/license-policy.json` (license, package pairs).
- CI: assert `git ls-files licenses.json sbom.cdx.json sbom.spdx.json` empty (exists; keep).
- Security/regression: an integration job that re-points a test tag after verification and asserts the deploy would refuse a digest mismatch (or a unit test of the digest-passing logic).
- Manual: follow `docs/SBOM_PROCESS.md` "Retrieve and verify" literally on a workstation; record any failing command.

## Suggested Documentation Updates

- `docs/SBOM_PROCESS.md`: replace the local `pnpm licenses list --json` steps; state that image SBOMs are also emitted by `deploy-do.yml`; document the image-SBOM validation once added.
- `docs/LICENSE_POLICY.md`: fix the sharp row; describe exception scoping as implemented; document expiry enforcement.
- `docs/DEPENDENCY_POLICY.md`: replace the broken command; state the scheduled-audit trigger and the triage SLA.
- `docs/CI.md`: correct the SBOM row's image-SBOM producer and note the new scheduled audit job.
- `docs/RELEASING.md`: keep the commit-as-identity model explicit; if tags are adopted, describe SBOM attachment.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Are GitHub Dependabot security alerts enabled and triaged? | determines whether the no-scheduled-scan gap is compensated | repo settings (not in repo) / alert triage log |
| Which license string does `@img/sharp-win32-x64` actually report on a Windows install? | fixes the docs/JSON mismatch precisely | `pnpm install` on Windows + `collect-licenses.mjs` |
| Is the lockfile SBOM required as a durable compliance artifact, or is the registry-attested image SBOM sufficient? | decides SBOM-P2-001 remediation | owner/legal decision |
| Will annotated tags/GitHub Releases be adopted? | REL-P1-001; SBOM release attachment | owner/release decision |
| Is `redis/caddy/prometheus/alertmanager` SBOM coverage in scope for compliance? | scope of the third-party SBOM gap | owner decision |

## Appendix

### Dependency source inventory

- npm workspace tree: `pnpm-lock.yaml` (1,446 resolved package entries), installed frozen-lockfile in CI (`setup-pnpm/action.yml:52`); licenses collected from the installed tree by `scripts/collect-licenses.mjs`.
- Container images: `node:20-alpine@sha256:fb4cd…` (base, `apps/*/Dockerfile`); prod runtime `redis:7-alpine`, `prom/prometheus:v3.5.1`, `prom/alertmanager:v0.28.1`, `caddy:2-alpine` (all digest-pinned, `infra/digitalocean/docker-compose.yml`); app images `mct-api|worker|web:<sha>` built by `deploy-do.yml`/`build-push.yml`.
- GitHub Actions: all `uses:` pinned to 40-hex SHAs; updated weekly by `.github/dependabot.yml`; no generated inventory.
- Terraform providers: covered by Dependabot (`/infra/terraform/digitalocean`); out of this domain's gates.

### License risk review (current tree, by policy artifact)

- Permissive allowlist (MIT/ISC/Apache-2.0/BSD/0BSD/BlueOak/Unlicense/CC0/CC-BY/Python-2.0/Artistic-2.0/WTFPL/Zlib/BSL-1.0/PostgreSQL/OpenSSL/X11/NCSA/MS-PL/UPL-1.0) — `security/license-policy.json:3-30`.
- Denied (GPL/AGPL all forms, SSPL-1.0, BUSL-1.1, CC-BY-NC, EUPL, OSL-3.0, RPL-1.5) — `:32-56`.
- Reviewed exceptions with expiry: MPL-2.0 (axe-core tooling), FSL-1.1-MIT (@sentry/cli tooling), LGPL-3.0-or-later (@img/sharp-libvips-linux-x64, dev/build-only via @storybook/nextjs; no workspace package declares sharp — grep of `apps/*/package.json`, `packages/*/package.json`), UNKNOWN (browser-assert, dev-only) — `:58-94`; caveats: scope/expiry not enforced, sharp docs mismatch.
- Root product license: ISC for every workspace (`package.json` + `apps/*` + `packages/*`), rationale documented.

### Evidence-gathering notes

- The domain files are unchanged between `9c0b88c` (previous audit target) and `8d299b8d`; every verification row therefore re-verified the same artifacts at the new commit, and the `deploy-do.yml` diff since `9c0b88c` (observability/SSH only) does not touch the attestation or SBOM steps.
- Scripts could not be executed (no node runtime; read-only target, no installs). Parser assumptions were reproduced with python3 against the real lockfile; upstream action semantics were verified against the pinned SHA.

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P1-001 | P1 | SBOM Is Lockfile-Only, Not an Image SBOM or Attestation |
| SBOM-P1-002 | P1 | Unsigned Images With No Provenance/Attestation |
| SBOM-P1-003 | P1 | No version identity: no tags, no product version, no commit binding in generated artifacts |
| SBOM-P1-004 | P1 | No license allow/deny policy in dependency review or any CI gate |
| SBOM-P1-005 | P1 | SBOM carries no license data and no dependency graph, limiting triage and license review |
| SBOM-P2-001 | P2 | SBOM is artifact-only: not release-bound, not commit-bound, not attested |
| SBOM-P2-002 | P2 | No container/image SBOM; base-image OS packages untracked |
| SBOM-P2-003 | P2 | `docs/CI.md` documents the SBOM workflow as "Blocking" but it gates nothing |
| SBOM-P3-001 | P3 | Root license is ISC with no documented rationale |
| SBOM-P3-002 | P3 | SBOM format/count not validated before upload; no regression guard |
| SBOM-P2-004 | P2 | No artifact provenance, attestation, or signing; `id-token: write` requested but unused |
| SBOM-P2-005 | P2 | License policy not enforced in CI; non-OSI and LGPL licenses present |
| SBOM-P2-006 | P2 | SBOM is generated but not bound to a commit or attached to releases/images |
| SBOM-P2-007 | P2 | Dependabot PR backlog is large and not triaged; one stale update conflicts with resolved versions |
| SBOM-P3-003 | P3 | Root package license remains "ISC" |
| SBOM-P2-008 | P2 | `licenses.json` is committed but unenforced and unverified |
| SBOM-P3-004 | P3 | SBOM is produced as a transient artifact, not bound to a release |
| SBOM-P2-009 | P2 | License exceptions are matched by license string only — documented package scope and UNKNOWN fail open |
| SBOM-P2-010 | P2 | Exception `expires` dates are documentation-only and never enforced by the gates |
| SBOM-P2-011 | P2 | Deploy verifies the tag's attestation but pulls by mutable tag; the SBOM predicate is never verified |
| SBOM-P2-012 | P2 | No scheduled dependency vulnerability re-scan — advisories are only evaluated on PRs and deploys |
| SBOM-P3-005 | P3 | Image SBOMs are attested but never validated (no floor or binding check) |
| SBOM-P3-006 | P3 | Runbooks and script headers still document the broken `pnpm licenses list --json` command; docs/CI.md SBOM row is stale |
| SBOM-P3-007 | P3 | Documented sharp license exception does not match the machine policy |
| SBOM-P3-008 | P3 | Shipped third-party images and GitHub Actions dependencies have no SBOM coverage |
| SBOM-P3-009 | P3 | PR license gate depends on the deprecated `deny-licenses` option and cannot fail on unknown licenses |
