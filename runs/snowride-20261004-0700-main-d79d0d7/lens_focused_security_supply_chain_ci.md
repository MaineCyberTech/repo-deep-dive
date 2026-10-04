# Focused security / supply-chain / CI deep-dive - snowride

## Findings

| ID | Severity | Title | Report |
|---|---|---|---|
| SUPPLY-P1-001 | P1 | Vulnerable runtime transitive dependency @grpc/grpc-js 1.14.4 with a non-blocking audit gate | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P2-001 | P2 | GitHub Action upload-artifact@v4 not pinned to a commit SHA | lens_focused_security_supply_chain_ci.md |
| SUPPLY-P2-002 | P2 | Container base and CI service images not pinned by digest | lens_focused_security_supply_chain_ci.md |
| CI-P2-001 | P2 | Supply-chain license/vulnerability workflow is not a required branch-protection check | lens_focused_security_supply_chain_ci.md |
| PORT-P3-001 | P3 | Six tracked shell scripts lack the executable bit | lens_focused_security_supply_chain_ci.md |
| SEC-P3-001 | P3 | Secret scan allowlists whole files, masking future real secrets | lens_focused_security_supply_chain_ci.md |
| SEC-P3-002 | P3 | Metrics token compared non-constant-time and has no rotation path | lens_focused_security_supply_chain_ci.md |
| SECRET-P3-001 | P3 | Empty service-role key silently disables persistence; no committed rotation evidence | lens_focused_security_supply_chain_ci.md |
| CI-P3-001 | P3 | CODEOWNERS is a personal account; release/hotfix branch rules absent | lens_focused_security_supply_chain_ci.md |
| CONF-P3-001 | P3 | Residual CRLF files and hadolint DL3025 HEALTHCHECK warnings | lens_focused_security_supply_chain_ci.md |

---

# snowride — LLM Security / Supply-Chain / CI Deep-Dive

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261004-snowride-d79d0d7
- Repository: `C:\temp\snowride`
- Branch: `main`
- Commit SHA: `d79d0d777497dd940794ea58328c77e2a245c748`
- Generated at: 2026-10-04
- Auditor: LLM subagent (security / supply-chain / CI focus)
- Scope: security & authz, CI/CD governance, supply chain & secrets, SBOM/license, container runtime, env/secret rotation, branch protection.
- Read-only: no files in the repo were modified.

## Scope

Reviewed: `.github/` (workflows, branch-protection policy, CODEOWNERS, dependabot), Dockerfiles + compose + `.dockerignore`, realtime auth/config/server/rate-limit, service-role client, Supabase RLS
migrations/tests, secret-scan tooling (`.gitleaks.toml`, `scripts/repo-secret-scan.sh`, `scripts/bundle-secret-gate.mjs`, `.githooks/pre-commit`), `package.json`/`package-lock.json`, and secret/rotation docs.

Not reviewed in depth: full application logic of every feature, live/GitHub server-side settings, the host `.env`, and the ~816 `evidence/**` artifacts beyond the deterministic gitleaks hits.

## Deterministic Findings — Validation

| DET ID | Verdict | Evidence | Note |
|---|---|---|---|
| DET-P1-001 | **REAL** | `package-lock.json:1003` `@grpc/grpc-js` `1.14.4`; pulled at runtime via `apps/realtime/package.json:22` `@opentelemetry/sdk-node` | CVE-2026-101916 / GHSA-m9gg-hp2v-232j (high). Runtime transitive (not dev). **Fixed in 1.14.5 / 1.13.6**. |
| DET-P3-002 | **REAL** | same package `1.14.4` | CVE-2026-101915 / GHSA-f596-whhp-79r4 (low). Fixed in 1.14.5 / 1.13.6. |
| DET-P2-003 | **PARTIAL** → P3 | `git ls-files -s` mode `100644` for the 6 scripts; all invocations are `bash scripts/...` (`ci-foundation.yml:30,112,116,120`; `verify-all.sh:5` uses the executable `preflight-disk.sh`) | Exec bit never needed by any documented invocation. Portability nit only. |
| DET-P2-004 | **FALSE-POSITIVE** (largely fixed) → P3 | `git ls-files --eol` at `d79d0d7`: only 2 `i/crlf` (`docs/archive/reviewer.md`, `evidence/phase2/.../g16_finding_disposition_ledger.csv`); `.gitattributes` has `* text=auto eol=lf` | The claimed "21 files" is not reproducible at current HEAD. Residual is docs/evidence only. |
| DET-P2-005 | **FALSE-POSITIVE** | `.gitleaks.toml:15-21` allowlists every hit path; `full_actor_operation_matrix.sql:123` is a literal test string `'anon-key-1'`; `recovery_ledger_r71.jsonl` hits are hex `idempotencyKey` hashes; `bundle-secret-gate.mjs:82` is the `sb_secret_FixTuRe...` fixture | No live credential. See SEC-001 for the residual allowlist-design risk. |
| DET-P2-006 | **REAL** | `ci-foundation.yml:55` `uses: actions/upload-artifact@v4` (tag), while `:84` pins `upload-artifact@ea165f8d...` | Inconsistent; tag can be repointed upstream. |
| DET-P3-007 | **FALSE-POSITIVE** (as stated) | `docker-compose.yml:7,69` `snowride-web:certified` / `snowride-realtime:certified` both have local `build:` sections | Locally-built images have no registry digest to pin. The real analog is unpinned **base** images → SUPPLY-003. |
| DET-P3-008 | **PARTIAL** → P3 | `apps/web/Dockerfile:50`, `apps/realtime/Dockerfile:49`, `Dockerfile.p2runtime:11` | DL3025 flags the **HEALTHCHECK** shell-form `CMD`; the actual `CMD` lines are already JSON (`apps/web/Dockerfile:52`). Cosmetic. |

Deterministic totals: **3 REAL, 3 FALSE-POSITIVE, 2 PARTIAL.**

## Findings

### Finding ID: snowride-SUPPLY-001 - Vulnerable runtime transitive dependency `@grpc/grpc-js` with a non-blocking audit gate

- Severity: **P1**
- Confidence: High
- Area: SUPPLY/DEP
- Evidence:
  - `package-lock.json:1003-1005` — `"node_modules/@grpc/grpc-js": { "version": "1.14.4", "resolved": ".../grpc-js-1.14.4.tgz" }`
  - `apps/realtime/package.json:22` — `"@opentelemetry/sdk-node": "0.222.0"` (production dep) pulls the gRPC exporters.
  - `.github/workflows/ci-foundation.yml:38-39` — `continue-on-error: true` / `npm audit --omit=dev --audit-level=high`
  - `.github/workflows/supply-chain.yml:54-55` — same advisory posture.
- What is happening: A high-severity advisory (CVE-2026-101916, `getAuthContext` can treat unauthorized certificates as authorized) and a low-severity advisory (CVE-2026-101915) affect the installed `@grpc/grpc-js@1.14.4`. Both are fixed in `1.14.5` (and `1.13.6`). The dependency ships in the runtime image and no CI job blocks on it.
- Why it matters: the fix is a one-line lockfile bump, but the vulnerability can ship because the only audit step is advisory.
- Impact: runtime gRPC/TLS trust confusion in the collector exporter path; supply-chain exposure.
- Recommendation: bump `@grpc/grpc-js` to `1.14.5` via `overrides` (or refresh the lockfile), then flip the CI audit steps to blocking for high severity.
- Suggested validation: `npm ls @grpc/grpc-js`; `npm audit --omit=dev --audit-level=high` exits 0.
- Owner suggestion: platform/infra. Effort: S. Status: open.
- Deterministic ref: DET-P1-001, DET-P3-002

### Finding ID: snowride-SUPPLY-002 - GitHub Action not pinned to a commit SHA

- Severity: **P2**
- Confidence: High
- Area: SUPPLY/CI
- Evidence:
  - `.github/workflows/ci-foundation.yml:55` — `uses: actions/upload-artifact@v4`
  - `.github/workflows/ci-foundation.yml:84` — `uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2` (the sibling call is pinned).
- What is happening: One `uses:` reference uses a mutable major tag while every other action in both workflows is SHA-pinned.
- Why it matters: a moved/compromised tag can execute arbitrary code in CI with repository read token.
- Recommendation: pin line 55 to the same `ea165f8d...` SHA and add a CI check (or rely on Dependabot github-actions) to prevent tag refs.
- Deterministic ref: DET-P2-006

### Finding ID: snowride-SUPPLY-003 - Container base images not pinned by digest

- Severity: **P2**
- Confidence: High
- Area: SUPPLY/CTR
- Evidence:
  - `apps/web/Dockerfile:4,38`, `apps/realtime/Dockerfile:4,21,38`, `Dockerfile.p2runtime:1` — `FROM node:24.20.0-bookworm-slim` (tag, no `@sha256:`)
  - `.github/workflows/ci-foundation.yml:96` — `image: postgres:17-alpine` (mutable tag, no digest)
  - Contrast: compose already digest-pins `busybox@sha256`, `otel/...@sha256`, `nginx@sha256`, `certbot@sha256` (`docker-compose.yml:191,216,247,305`).
- What is happening: The images that actually build/run the app are tag-pinned; only the ancillary compose images are digest-pinned.
- Why it matters: mutable base/service tags break reproducibility and are a tag-repointing supply-chain vector.
- Recommendation: pin each `node:...` and `postgres:...` reference by digest, or document a periodic digest-refresh step.
- Deterministic ref: DET-P3-007 (derived)

### Finding ID: snowride-CI-001 - Supply-chain license/vulnerability workflow is not a required branch-protection check

- Severity: **P2**
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/supply-chain.yml:1-7` — "merge-gating supply-chain checks … a disallowed license or a high-severity advisory could reach `main`".
  - `.github/branch-protection.json:5` — `"contexts": ["foundation", "migrations", "e2e"]` (no `license-and-vulnerability`).
  - `scripts/verify-branch-protection.mjs:21` — `WORKFLOW_PATH = .../ci-foundation.yml` (the validator never inspects `supply-chain.yml`).
- What is happening: The license allow-list gate and audit run on the PR event, but the `main` ruleset only requires the three ci-foundation jobs. A red/detached `supply-chain` run is not merge-blocking, and the policy validator cannot detect the drift.
- Why it matters: license/vulnerability policy enforcement is advisory in practice, contradicting the workflow's own rationale.
- Recommendation: add `license-and-vulnerability` to `requiredStatusChecks.contexts` and extend `verify-branch-protection.mjs` to enumerate all workflow files.
- Suggested validation: open a PR with a prohibited license and confirm the merge button stays blocked.

### Finding ID: snowride-PORT-001 - Six shell scripts lack the executable bit

- Severity: **P3**
- Confidence: High
- Area: PORT
- Evidence: `git ls-files -s` shows mode `100644` for `scripts/ci-db-tests.sh`, `scripts/ci-migrations-dryrun.sh`, `scripts/install-clean.sh`, `scripts/migrations-manifest.sh`, `scripts/repo-secret-scan.sh`, `scripts/verify-all.sh`. All documented invocations use `bash scripts/...` (`ci-foundation.yml:30,112,116,120`; `AGENTS.md:49`; `README.md:43`).
- What is happening: Scripts are not executable in the index, but are always invoked via an explicit interpreter.
- Why it matters: Low — `./script.sh` would fail on Linux/macOS, but no documented path uses that form.
- Recommendation: `git update-index --chmod=+x` for the six files (and `install-clean.sh` if it is ever documented as `./`).
- Deterministic ref: DET-P2-003

### Finding ID: snowride-SEC-001 - Secret scan allowlists whole files, masking future real secrets

- Severity: **P3**
- Confidence: Medium
- Area: SEC
- Evidence: `.gitleaks.toml:15-21` allowlists by file path, including the append-only `evidence/recovery/recovery_ledger_r71\.jsonl$` and `scripts/bundle-secret-gate\.mjs$`.
- What is happening: The 16 generic-api-key hits are all benign fixtures (validated: SQL `'anon-key-1'`, hex `idempotencyKey` values, the bundle-gate's `sb_secret_FixTuRe...` fixture). However, path-level allowlisting means any real credential later appended to those files bypasses CI detection.
- Why it matters: The append-only evidence ledger is a plausible place for a future accidental real secret to land undetected.
- Recommendation: replace whole-file allowlists with rule/entropy-scoped allowlists or line/regex fingerprints; periodically re-scan allowlisted files.
- Deterministic ref: DET-P2-005

### Finding ID: snowride-SEC-002 - Metrics token compared non-constant-time; no rotation path

- Severity: **P3**
- Confidence: Medium
- Area: SEC/SECRET
- Evidence:
  - `apps/realtime/src/server.ts:2011` — `if (configured && token === configured) return true;`
  - `apps/realtime/src/server.ts:1286` — `if (token !== configured) { ... }`
  - `apps/realtime/src/config.ts:231` — `METRICS_TOKEN` is a static shared secret; `.env.example:80` documents it.
- What is happening: The shared `METRICS_TOKEN`/`x-metrics-token` is compared with `===` and has no documented rotation/expiry.
- Why it matters: Timing side-channel is low-risk over a network, but a static, never-rotated ops token is a durable credential if leaked.
- Recommendation: use `crypto.timingSafeEqual` on equal-length buffers; document token rotation in the secret rotation runbook.
- Deterministic ref: none identified

### Finding ID: snowride-SECRET-001 - Empty service-role key silently disables persistence; rotation evidence gap

- Severity: **P3**
- Confidence: Medium
- Area: SECRET/AUTH
- Evidence:
  - `apps/realtime/src/config.ts:43` — `RM_SUPABASE_SERVICE_ROLE_KEY: z.string().optional().default("")`
  - `apps/realtime/src/services/supabase.ts:39-44` — `if (!key) { ... return null; }` (trusted run persistence disabled).
  - `docs/archive/agent_final_response.json:695` — `"R-021 OPEN_PENDING_ROTATION: owner-side .env plaintext credentials - rotation is an owner action"`.
- What is happening: Missing/incorrect service-role key degrades to "no persistence" rather than failing boot closed, and host-side plaintext credentials have no committed rotation evidence (only an audit-generated runbook under `docs/audits/.../secret_rotation_runbook.md`).
- Why it matters: A misconfigured deploy can silently run without trusted persistence/scoring, and rotation is unverifiable from the repo.
- Recommendation: fail boot (or emit a loud readiness failure) when `NODE_ENV=production` and the key is empty; commit a rotation runbook with dated evidence.
- Deterministic ref: none identified

### Finding ID: snowride-CONF-001 - Residual CRLF/hadolint hygiene in committed files

- Severity: **P3**
- Confidence: High
- Area: CONF
- Evidence:
  - `git ls-files --eol` at `d79d0d7`: `i/crlf` for `docs/archive/reviewer.md` and `evidence/phase2/20260908T2110Z-p2/G16-supply-chain/g16_finding_disposition_ledger.csv` only.
  - hadolint DL3025 on `apps/web/Dockerfile:50`, `apps/realtime/Dockerfile:49`, `Dockerfile.p2runtime:11` (HEALTHCHECK shell-form CMD).
- What is happening: The deterministic run's "21 CRLF files" is stale/false at HEAD; two docs/evidence files remain CRLF. hadolint only flags HEALTHCHECK shell form.
- Why it matters: Cosmetic reproducibility noise; no functional or security impact.
- Recommendation: `git add --renormalize` the two files; optionally convert HEALTHCHECK to JSON array form.
- Deterministic ref: DET-P2-004, DET-P3-008

### Finding ID: snowride-CI-002 - CODEOWNERS is a personal account; release/hotfix branch rules absent

- Severity: **P3**
- Confidence: Medium
- Area: CI/AUTH
- Evidence:
  - `.github/CODEOWNERS:5` — `* @MaineCyberTech` with a comment "personal account, not an org team".
  - `.github/branch-protection.json` — only protects `main`; no `release/*`/`hotfix/*` rules.
  - `docs/runbooks/BRANCH_PROTECTION.md:20-22` — claims `tests/branch-protection.test.ts` guards drift.
- What is happening: Required CODEOWNERS review resolves to one personal account; policy cannot be verified server-side from the repo; release/hotfix branches are unprotected by the declared policy.
- Why it matters: Governance bus-factor and potential merge-authority ambiguity.
- Recommendation: replace with an org team handle; add a release/hotfix ruleset to the declared policy.

## Strengths Observed

- Both workflows set top-level `permissions: contents: read` and checkouts use `persist-credentials: false`; no `pull_request_target`/`workflow_run`.
- JWT verification uses JWKS + issuer/audience and `jsonwebtoken@9.0.3`, which infers allowed algorithms from the key type (no algorithm-confusion gap).
- Admin surfaces require `role === "admin"` from a verified JWT; PII endpoints use `authorizedForAdmin`, ops-only endpoints use the metrics token.
- Server-side Zod env validation; fail-closed `COMPETITIVE_CONTACT_MODE`/`AVALANCHE_MODE="ranked"` refinements.
- RLS enabled across tables with deny-by-default grants and CI-run SQL negative suites (`ci-db-tests.sh`, `migrations` job).
- SBOM generated per commit with a pinned `npx --no-install` tool and uploaded as a 90-day artifact.
- Pinned gitleaks binary with SHA-256 verification; build-output secret gate with self-test.
- Container hardening: non-root `USER 1001`, `read_only`, `cap_drop: ALL`, `no-new-privileges`, `pids_limit`, resource caps, JSON log rotation.

## Open Questions

- The cited CVEs are internally consistent with live advisories, but the deterministic scanner's CVE→advisory mapping was not reproducible offline; confirm with `npm audit`/`trivy` in the pinned lab.
- Whether `main` branch protection is actually applied server-side (`verify-branch-protection.mjs` needs `GITHUB_TOKEN`; not run here).
- Whether `RM_SUPABASE_SERVICE_ROLE_KEY` is set on the certified host (host `.env` not readable in this audit).
