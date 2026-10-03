# 06 Security, AuthZ & Tenancy Audit

## Audit Metadata

- Run: 20261003-0018-main-59e12b9
- Repo: C:\temp\snowride @ main / 59e12b9
- Date: 2026-10-03
- Auditor: repo-deep-dive subagent

## Scope

Authentication (JWT/JWKS), authorization (admin/ops/player), RLS/grants, secret handling, and the launch/release trust boundary. Read-only. No production access; no secret values printed.

## Evidence Reviewed

- `apps/realtime/src/auth.ts` (`JwtVerifier`, `claimsToIdentity`), `server.ts` (`authorizedForOps`, `authorizedForAdmin`, `/runs` auth, `/metrics` auth)
- `supabase/migrations/0002_rls_and_grants.sql`, `0004`, `0008`, `0017` (`social_guard_*`), `0020`, `0021`, `0022`, `0023`, `0026`
- `.env.example`, `infra/compose/docker-compose.yml` (launch attestation block)
- `scripts/bundle-secret-gate.mjs`, `SECURITY.md`
- Tracked-file secret sweep (`git grep` for key/JWT/PEM patterns)

## Verification Performed

- Verified JWT path: `jsonwebtoken.verify` with `issuer` + `audience` against JWKS public key; `sub` required; identity frozen (auth.ts).
- Verified role source is `app_metadata.role` (server-controlled), default `user` (auth.ts lines 74–79).
- Verified admin vs ops split: `authorizedForOps` (metrics token OR admin JWT) vs `authorizedForAdmin` (admin JWT only) (server.ts 1851–1893); PII routes use admin (docs/API.md).
- Verified RLS: `ENABLE ROW LEVEL SECURITY` on exposed tables; own-row SELECT policies; explicit deny policies; default-privilege revocation (0002).
- Ran `git grep` for `sb_secret_`, `sbp_`, `ghp_`, `eyJhbGci`, `AKIA`, PEM blocks; only intentional test fixtures/placeholders found (no live secret printed).
- Attempted to run `npm audit` — `node_modules` absent in the read-only audit environment (not executed).

## Executive Summary

The authentication and authorization core is strong: server-side JWKS verification with issuer/audience/expiry, admin-vs-ops route separation, admin-only PII surfaces, per-socket/per-user rate limits, and default-deny RLS with explicit deny policies. No P0/P1 exploitable authorization defect was found in the reviewed code. The highest-severity finding is release-integrity, not runtime authz: the launch gate's `LAUNCH_OWNER_SIGNATURE` is free text with no cryptographic verification, and the checked-in production compose hardcodes an approval string — so "owner approval against the exact release identity" is a process assertion, not an enforced control. Lower findings cover the absence of HTTP origin enforcement and repository secret scanning.

## Inventory

| Control | Location | Assessment |
|---|---|---|
| JWT verify (JWKS, iss/aud/exp) | `apps/realtime/src/auth.ts` | Present, correct |
| Socket auth failure disconnect | `server.ts` (`AUTH_FAILURE_DISCONNECT_AFTER`) | Present (3 failures, per docs) |
| Admin vs ops authz split | `server.ts` 1851–1893 | Present |
| `/runs` per-user rate limit | `server.ts` 3586–3600 | Present |
| Zod validation every event | `EVENT_SCHEMAS`, `RunSubmissionSchema` | Present |
| RLS default-deny + mirrors | `0002_rls_and_grants.sql` | Present |
| SECURITY DEFINER + `search_path` | migrations 0003–0029 | Present and consistent |
| Bundle secret gate | `scripts/bundle-secret-gate.mjs` | Built artifacts only |
| Repo-tree secret scan | none | Absent |

## Findings

### Finding ID: SEC-P1-001 - Launch owner approval is unverified free text, so release identity binding is not enforced

- Severity: P1
- Confidence: Medium
- Area: SEC
- Evidence:
  - `infra/compose/docker-compose.yml` lines 103–121 — `LAUNCH_OWNER_SIGNATURE` is a plain sentence; `LAUNCH_ATTESTED_COMMIT`/`IMAGES` are literal strings
  - `apps/realtime/src/config.ts` lines 182–207 — `LAUNCH_OWNER_SIGNATURE` is `z.string().optional().default("")`; gate logic compares strings only
  - `docs/runbooks/` launch gate described as "signed owner decision" (`ext_review.md` Phase 25)
- What is happening: Any non-empty signature string satisfies the gate; there is no signature verification, and the production file already contains one.
- Why it matters: The control intended to bind an approved release to an exact commit/image is a self-attestation that the repository itself can supply.
- User / business impact: A release could be represented as owner-approved without an independent, verifiable artifact.
- Security / privacy / reliability impact: Release-integrity / governance; not a direct runtime exploit.
- Recommended fix: Verify a detached signature (e.g. SSH/GPG or asymmetric key) over a canonical release-identity document at gate evaluation, or make the signature an out-of-band artifact not committed with a default value; never ship an approval string in compose.
- Suggested validation: Gate returns not-ready when the signature is tampered; a release-identity unit test fails on a changed commit/image digest.
- Owner suggestion: Owner + release engineer
- Effort estimate: M
- Dependencies: Stale attestation (DATA-P1-001)
- Status: open

### Finding ID: SEC-P2-001 - HTTP surface enforces no Origin/CORS allowlist

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `apps/realtime/src/server.ts` line 564–570 — CORS configured on the Socket.IO server only (`origin: deps.config.allowedOrigins`)
  - `handleHttp` (server.ts ~803) sets no `Access-Control-Allow-Origin` and performs no `Origin` check
  - Anonymous HTTP endpoints: `POST /perf` (1032), `POST /client-error` (1086)
- What is happening: Plain HTTP endpoints rely purely on Bearer tokens; the configured `ALLOWED_ORIGINS` does not apply to them.
- Why it matters: Cross-origin pages can drive anonymous/ingest endpoints; OWASP recommends explicit origin allowlisting for browser-facing services.
- User / business impact: Ingest/spam potential; limited because state-changing player routes require a token.
- Security / privacy / reliability impact: Abuse/monitoring poisoning; no cookie-based CSRF surface identified.
- Recommended fix: Validate `Origin` on browser-facing HTTP endpoints against `ALLOWED_ORIGINS` (reject/allow), or set explicit CORS headers with the allowlist.
- Suggested validation: Integration test with a disallowed Origin is rejected on `/perf` and `/client-error`.
- Owner suggestion: Realtime engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SEC-P2-002 - No repository-tree secret scanning in CI or pre-commit

- Severity: P2
- Confidence: High
- Area: SEC
- Evidence:
  - `.github/workflows/ci-foundation.yml` — steps are typecheck/lint/format/test/build/compose/`bundle-secret-gate` (built bundles only)
  - `scripts/bundle-secret-gate.mjs` — scans only the directories passed (`.next/static`, `dist`)
  - 849-file `evidence/` tree with 94 tracked `.log` files
- What is happening: Only build output is scanned; the git tree/history is not scanned by any automated secret detector.
- Why it matters: Historical logs/snapshots are a plausible place for accidental credential material to persist undetected.
- User / business impact: Slow detection if a secret is ever committed.
- Security / privacy / reliability impact: Secret-leak exposure window.
- Recommended fix: Add a pinned gitleaks/trufflehog-style scan (tree + history) to CI and a pre-commit hook.
- Suggested validation: Injected dummy secret in a test branch is caught by CI.
- Owner suggestion: CI/security engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SEC-P3-001 - Claim-less SQL callers are treated as trusted by `social_guard_*`

- Severity: P3
- Confidence: Medium
- Area: SEC
- Evidence:
  - `supabase/migrations/0017_social_party_moderation.sql` lines 391–455 — `social_guard_self`/`social_guard_moderator` return trusted when `request.jwt.claims` is empty
  - Grants: functions are granted to `service_role, authenticated` only (lines 1616–1698), not `anon`
- What is happening: The guards infer trust from missing JWT claims (a psql/db-admin convention).
- Why it matters: The safety of the convention depends entirely on `anon` never holding EXECUTE, which is currently true.
- User / business impact: None today.
- Security / privacy / reliability impact: Defense-in-depth residual risk; a future grant to `anon` would become a privilege-escalation vector.
- Recommended fix: Prefer an explicit `current_user = 'service_role'` check in the claim-less branch rather than absence of claims.
- Suggested validation: Negative SQL test: an `anon`-role call to each self-service RPC is denied.
- Owner suggestion: DB engineer
- Effort estimate: S
- Dependencies: None
- Status: open

### Finding ID: SEC-P3-002 - Service-role key delivered via environment rather than a Docker secret

- Severity: P3
- Confidence: High
- Area: SEC
- Evidence:
  - `infra/compose/docker-compose.yml` lines 73–75 — `RM_SUPABASE_SERVICE_ROLE_KEY: ${RM_SUPABASE_SERVICE_ROLE_KEY}` (plus `env_file` `.env`)
  - `.env.example` line 66 documents it as server-only
- What is happening: The privileged key is interpolated into the container environment.
- Why it matters: Environment variables are readable by processes with container access and appear in `docker inspect`.
- User / business impact: Low on a single certified host.
- Security / privacy / reliability impact: Reduced secret isolation.
- Recommended fix: Use Docker/Compose secrets mounted as files and read at boot, or a runtime secret store.
- Suggested validation: `docker inspect` does not expose the key.
- Owner suggestion: Operator
- Effort estimate: M
- Dependencies: None
- Status: open

## Risks

- R-SEC-1: Release trust is self-asserted (SEC-P1-001).
- R-SEC-2: Anonymous ingest abuse without origin checks (SEC-P2-001).
- R-SEC-3: Undetected secret persistence in evidence (SEC-P2-002).

## Recommendations

1. Enforce cryptographic release attestation (SEC-P1-001).
2. Add Origin enforcement + repo secret scanning (SEC-P2-001/002).
3. Tighten SQL trust inference and move secrets to files (SEC-P3-001/002).

## Quick Wins

- Add origin check (S). Add gitleaks CI step (S). Remove committed approval string (S).

## Hardening Backlog

- Dry-run an `anon`-role negative suite over every self-service RPC.

## Suggested Tests

- Origin rejection tests; signature-tamper gate test; secret-scan self-test in CI.

## Suggested Documentation Updates

- `SECURITY.md`/release runbook: clarify that the current signature is an assertion, not a cryptographic approval.

## Open Questions

- Is the release identity signed out of band (e.g. owner key) in any evidence artifact? (`Unknown`.)

## Appendix

- Redaction note: the secret sweep encountered only fixtures/placeholders; no live credential was printed.
- Tracked secret-shaped matches were limited to `scripts/bundle-secret-gate.mjs`, `scripts/check-web-bundle.mjs` and `repomix-output*.xml` fixtures (test data).
