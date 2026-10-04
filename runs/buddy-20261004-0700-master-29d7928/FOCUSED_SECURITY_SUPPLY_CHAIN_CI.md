# buddy — LLM Security / Supply-Chain / CI Deep-Dive

## Audit Metadata

- Audit name: repo-deep-dive (focused security/supply-chain/CI lens)
- Run: 20261004-0644-master-29d7928
- Repository: buddy (Next.js 14 App Router PWA virtual pet game)
- Branch: master
- Commit SHA: `29d792814255f7395ca3695026d76d85b2105c63`
- Generated at: 2026-10-04
- Auditor: subagent (LLM security/supply-chain/CI lens)
- Area codes: SEC, DEP, CI, SUPPLY, AUTH, PORT, CONF
- Scope limitations: repository is read-only and has no network-independent advisory DB;
  CVE ranges were confirmed against public advisories via web search. Branch protection,
  GitHub environment protection and tag rules are **not** stored in the repository and
  were therefore **not verifiable** from the clone. No secret values printed; secret scan
  was static. `trivy` was not available locally, so CVE-to-version matching was done
  manually against the committed lockfile.

## Scope

Reviewed: `.github/workflows/{ci,release}.yml`, `.github/{CODEOWNERS,dependabot.yml}`,
`package.json`, `package-lock.json`, `next.config.js`, `.gitignore`, `lib/storage/*`,
`lib/buddy/store.ts`, `components/hatch/HatchFlow.tsx`, `app/*`, `docs/{README.md,release-process.md,release-readiness.md}`.
Not reviewed / not present: no Dockerfile, no compose, no Kubernetes/IaC, no server API
routes, no server actions, no middleware, no auth/session/JWT code, no database, no
`.env*`, no `SECURITY.md`.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `.github/workflows/release.yml` | workflow | Release token scope, actions pinning, SBOM/provenance | write + OIDC at workflow scope |
| `.github/workflows/ci.yml` | workflow | PR gate, permissions | read-only; no scan step |
| `.github/dependabot.yml` | config | Dependency updates | npm + github-actions, weekly |
| `package.json` / `package-lock.json` | manifest | Dependency risk | locked versions confirmed |
| `lib/storage/schema.ts`, `indexeddb.ts` | source | Save input validation | zod `validateSave` present |
| `README.md`, `docs/README.md` | docs | Self-consistency | stale "not validated" claim |
| `.gitattributes` | (absent) | line-ending policy | confirmed missing |

## Verification Performed

- `git log -1` / `git status` — clean tree at `29d7928`.
- Confirmed locked versions from `package-lock.json`: `next@14.2.35` (prod),
  `nanoid@3.3.15` (transitive, dev), `postcss@8.5.15` (dev:true),
  `next/node_modules/postcss@8.4.31` (prod).
- Confirmed each flagged CVE's affected/patched ranges via public advisories
  (web search) and compared to the locked versions.
- Confirmed `.gitattributes` absent (`git ls-files`).
- Confirmed all `uses:` refs and `permissions:` blocks by grep.
- Confirmed no `environment:`, no `${{ secrets.* }}`, no `pull_request_target`.
- Confirmed no server trust boundary (no API routes / `use server` / middleware / fetch).
- Secret pattern scan across `*.ts,tsx,js,json,yml,yaml,md` — only prose matches
  (`data/personalities.ts`, vendored checklists); **no live secrets**.

## Executive Summary

`buddy` is a guest-only, client-side PWA: no server, no accounts, no tenant data, no
cookies/JWT, no database, and no committed secrets. That removes most classic
authn/authz/IDOR/SSRF/tenancy attack surface, and the save-import boundary is now
validated with zod plus a size cap (`lib/storage/schema.ts:177`,
`lib/storage/indexeddb.ts:89-106`). Guest identity uses `crypto.randomUUID`
(`HatchFlow.tsx:20`).

The material residual risk in this lens is **supply chain and CI governance**:

1. The app ships on **Next.js 14.2.35, which is End-of-Life (2025-10-26)**. Many of the
   flagged CVEs are server-side features the app does not use (Pages Router + i18n
   middleware, Server Actions, dynamic `rewrites()`, image optimization), so real
   exploitability is low — but the framework receives **no future patches on 14.x**, and
   the release artifact packages the `.next` build.
2. The Release workflow runs `npm ci` (lifecycle scripts) and **unpinned third-party
   actions** under a workflow-scoped token with `contents: write` + `id-token: write`;
   a compromised dependency or action tag inherits that token.
3. There is **no dependency-vulnerability, license, or secret-scanning gate** in CI —
   `npm audit`/`npm sbom` scripts exist but are never invoked by a workflow.
4. Release governance (environment approval, protected tags, branch protection) is
   **not represented in the repository** and could not be verified.

No P0 was found. Strengths: least-privilege `contents: read` CI token, `npm ci` with a
committed lockfile, default-deny CSP + HSTS + frame-ancestors in `next.config.js`,
build-provenance attestation, and a clean secret scan.

## Domain Scorecard

| Category | Score | Evidence | Gap |
|---|---:|---|---|
| Secrets | 4 | repo-wide scan clean; `.env*` gitignored | no secret scan in CI; no rotation runbook |
| Dependency risk | 2 | `package-lock.json` versions | EOL Next.js 14; vulnerable postcss/nanoid |
| Supply chain / actions | 2 | `release.yml:88,93`, `ci.yml:24,27` | refs not SHA-pinned; stale majors |
| CI/CD governance | 3 | `ci.yml`, `release.yml` | no vuln/license/secret gate; no env protection |
| Container runtime | N/A | no Dockerfile/compose | not applicable |
| Authn/Authz/Tenancy | 5 | no server, no accounts, no tenant data | revisit before cloud/account mode |
| Branch protection | 0 | not in repo | unverifiable; must be set in GitHub settings |
| SBOM / provenance | 3 | `release.yml:62-90` | SBOM includes dev deps; no license policy |

## Findings

### Finding ID: buddy-DEP-001 — Next.js 14.2.35 is EOL and ships unpatched known CVEs

- Severity: P1
- Confidence: High
- Area: DEP
- Evidence:
  - `package.json:24` — `"next": "^14.2.0",`
  - `package-lock.json:6185-6187` — `node_modules/next` `"version": "14.2.35"` (production; no `dev` flag)
  - `package.json:5-6` — `"engines": { "node": ">=20" }` (no framework-version guard)
  - `.github/workflows/release.yml:85` — `tar -czf "buddy-${GITHUB_REF_NAME}.tar.gz" .next public ...` (ships the framework build)
  - Deterministic ref: `DET-P1-001` (14 P1), `DET-P2-002` (13 P2), `DET-P3-003` (2 P3)
- What is happening: the committed lockfile resolves Next.js to 14.2.35, the final
  14.2.x patch. Next.js 14 left Maintenance LTS on 2025-10-26 and now receives no
  security fixes. The advisories in the deterministic set (e.g. CVE-2026-44573
  middleware/i18n bypass, CVE-2026-64641 Server Action DoS, CVE-2026-64645 SSRF in
  `rewrites()`) all affect 14.x and are fixed only in 15.5.x/16.3.x.
- Why it matters: an EOL framework silently accumulates unpatched CVEs; there is no
  14.x fix path, so every future advisory is permanently exposed.
- User / business impact: a future framework RCE/SSRF/DoS would block a security
  response; release artifacts would carry the vuln.
- Security / privacy / reliability impact: **Low-to-moderate in practice.** `buddy`
  uses the App Router with no `middleware.ts`, no `i18n`, no API routes/`use server`,
  no dynamic `rewrites()`/`redirects()`, and `images.unoptimized = true`. Several CVEs
  therefore require features the app does not use. The risk is the unpatched EOL line,
  not a confirmed reachable exploit.
- Recommended fix: upgrade to a supported line (15.5.26+ or 16.3.6+) on a branch;
  if the migration is deferred, record a dated risk acceptance and re-check monthly.
- Suggested validation: `npm ls next`; add a CI step that fails if `next` major <
  supported; run the existing quality gate on the upgraded branch.
- Owner suggestion: frontend/platform maintainer
- Effort estimate: L (major upgrade)
- Dependencies: React 18→19 peer changes if moving to 16.x
- Status: open
- Attack path: none identified (features required by the CVEs are absent), but EOL
  guarantees no future patch.

### Finding ID: buddy-DEP-002 — Vulnerable transitive copies: nanoid 3.3.15 and nested postcss 8.4.31

- Severity: P2
- Confidence: High
- Area: DEP
- Evidence:
  - `package-lock.json:6144-6146` — `node_modules/nanoid` `"version": "3.3.15"`
  - `package-lock.json:6235-6236` — `node_modules/next/node_modules/postcss` `"version": "8.4.31"`
  - `package-lock.json:6772-6774` — `node_modules/postcss` `"version": "8.5.15"` (`"dev": true`)
  - Deterministic ref: `DET-P1-001`, `DET-P2-002`
- What is happening:
  - `nanoid@3.3.15` is < the patched `3.3.18`/`3.3.16` for CVE-2026-67213 / CVE-2026-67214
    (infinite-loop DoS when a `size` of 0 / negative is passed). It is pulled in as a
    transitive build dependency of the dev-only top-level `postcss` (`^3.3.12`).
  - The top-level `postcss@8.5.15` is **patched** for CVE-2026-45623 (fixed 8.5.12) and
    CVE-2026-41305 (fixed 8.5.10), but still **vulnerable** to CVE-2026-73646 (fixed
    8.5.18) and CVE-2026-69153 (fixed 8.5.19).
  - The production copy `next/node_modules/postcss@8.4.31` is vulnerable to **all** of
    the above plus CVE-2026-45623 (path traversal / arbitrary file read via
    `sourceMappingURL`, patched 8.5.12).
- Why it matters: trivy is not wrong on these three package identities; the nuance is
  that the postcss CVEs are split between a dev copy and a Next.js-pinned production
  copy, and nanoid is dev-only.
- User / business impact: low today (build-time, mostly untrusted-CSS paths not taken);
  becomes relevant if CSS/images are ever processed from untrusted input.
- Security / privacy / reliability impact: arbitrary file read (postcss) and DoS
  (nanoid) primitives — build-time, not reached by the shipped client in normal use.
- Recommended fix: upgrade the direct `postcss` dev dep to `>=8.5.19`; grandfather the
  Next.js-pinned copy until the framework upgrade in `buddy-DEP-001`; update `nanoid`
  via a non-breaking resolution or once postcss is bumped. Do not rely on dev/prod
  scoping alone — the nested postcss is production.
- Suggested validation: `npm ls postcss nanoid`; `npm audit --omit=dev`; assert fixed
  versions in CI (see `buddy-CI-001`).
- Owner suggestion: dependency owner
- Effort estimate: S–M
- Dependencies: `buddy-DEP-001` for the nested copy
- Status: open
- Attack path: build pipeline processing attacker-controlled CSS (not currently reachable).

### Finding ID: buddy-SUPPLY-001 — Release workflow runs install scripts and unpinned actions with a write token

- Severity: P1
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `.github/workflows/release.yml:13-16` — `permissions:` `contents: write`, `id-token: write`, `attestations: write`
  - `.github/workflows/release.yml:38-39` — step `Install dependencies` / `run: npm ci`
  - `.github/workflows/release.yml:88` — `uses: actions/attest-build-provenance@v1`
  - `.github/workflows/release.yml:93` — `uses: softprops/action-gh-release@v2`
  - `.github/workflows/release.yml:28,33` — `actions/checkout@v4`, `actions/setup-node@v4`
  - `.github/workflows/ci.yml:24,27` — `actions/checkout@v4`, `actions/setup-node@v4`
  - Deterministic ref: `DET-P2-005` (6 refs not pinned to a SHA)
- What is happening: all six `uses:` refs are moving major tags, not 40-hex SHAs. The
  whole `release` job — including `npm ci`, which executes dependency lifecycle
  (postinstall) scripts — runs with a workflow-scoped token that can write releases
  (`contents: write`) and mint OIDC tokens (`id-token: write`). A compromised
  dependency or a hijacked third-party action tag (`softprops/action-gh-release@v2`,
  `attest-build-provenance@v1`) inherits that capability.
- Why it matters: this is the classic CI supply-chain escalation: untrusted install-time
  code plus a write-capable identity equals the ability to publish or tamper with
  releases/attestations.
- User / business impact: a single compromised transitive dependency could publish a
  malicious release under the project's name.
- Security / privacy / reliability impact: high if chained; requires an upstream
  compromise or a moved tag.
- Recommended fix: (1) pin every `uses:` to a full commit SHA (Dependabot supports this);
  (2) scope `permissions` to the job/step that needs writes and keep `npm ci` under
  `contents: read`; (3) prefer `npm ci --ignore-scripts` where the build permits, or run
  install in a read-only job and pass the build via artifacts; (4) bump stale majors
  (`checkout`/`setup-node` v4 → v7, `attest-build-provenance` v1 → v4,
  `action-gh-release` v2 → v3, per Dependabot PRs in the clone).
- Suggested validation: `zizmor`/`actionlint` in CI; assert every `uses:` matches
  `@[0-9a-f]{40}`.
- Owner suggestion: release/CI owner
- Effort estimate: S
- Dependencies: none
- Status: open
- Attack path: compromised dependency/action → token with `contents: write` +
  `id-token: write` → forge a release/attestation.

### Finding ID: buddy-CI-001 — No dependency-vulnerability, license, or secret-scanning gate in CI

- Severity: P2
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/ci.yml:32-48` — steps: install, lint, typecheck, test, coverage, build (no scan step)
  - `package.json:17` — `"audit": "npm audit --omit=dev"` (defined but never invoked by a workflow)
  - `package.json:18` — `"sbom": "npm sbom --sbom-format cyclonedx --omit=dev"` (not invoked by CI)
  - `package.json:19` — `"test:coverage": "vitest run --coverage"` invoked at `ci.yml:45`
- What is happening: the CI gate proves correctness (lint/type/unit/build) but does not
  detect vulnerable dependencies, license obligations, or secret leakage. The scripts to
  do dependency audit/SBOM exist in `package.json` but are never wired into a workflow.
  Dependabot (`dependabot.yml`) opens version PRs but does not block a vulnerable merge.
- Why it matters: the `DET-P1/2/3` vulnerable dependencies reached `master` because
  nothing fails the build on advisories. This is the enforcement half of prompts 11/35.
- User / business impact: vulnerable/EOL dependencies stay in shipped artifacts.
- Security / privacy / reliability impact: medium — detection (not cure) gap.
- Recommended fix: add a CI job running `npm audit --audit-level=high --omit=dev`
  (non-blocking for dev-only), `actions/dependency-review-action` on PRs, a
  `gitleaks`/secret scan, and (once a policy exists) a license allow/deny check.
- Suggested validation: a PR that downgrades `postcss` should fail the new gate.
- Owner suggestion: CI owner
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: buddy-CI-002 — Release is not gated by environment protection or protected tags

- Severity: P2
- Confidence: Medium
- Area: CI
- Evidence:
  - `.github/workflows/release.yml:7-10` — `on: push: tags: ["v*"]` (no `environment:`)
  - `.github/workflows/release.yml:13-16` — workflow-scoped write permissions, no
    `needs:`/approval gate
  - `.github/CODEOWNERS:3` — `* @JulianB-MCT` (does not itself enforce review)
  - `docs/release-readiness.md:42` — condition requires "protection enabled" but no
    repository artifact records branch protection
  - `git ls-files` shows no ruleset/branch-protection file (those live in GitHub
    settings and were **not verifiable** from the clone)
- What is happening: publishing a `v*` tag immediately runs the release and publishes a
  GitHub Release with `contents: write`; there is no GitHub Environment with required
  reviewers, no protected-tag rule, and no in-repo evidence of required status checks /
  branch protection. The workflow does run its own lint/type/test/build, which limits
  the blast radius, but a maintainer (or a stolen write token) can tag an unmerged commit.
- Why it matters: release gating and required checks are the governance layer the audit
  pack (prompts 10/34) asks to confirm; it cannot be confirmed from the repository.
- User / business impact: an unvetted commit could be published as a release.
- Security / privacy / reliability impact: medium — release integrity/authorization.
- Recommended fix: create a `release` GitHub Environment with required reviewers, apply
  a `v*` tag protection rule, and enable branch protection on `master` requiring the
  `CI` check and CODEOWNERS review. Document the settings in `docs/release-process.md`.
- Suggested validation: attempt a tag push from a non-maintainer account — it must not
  publish until approved.
- Owner suggestion: repo admin / release owner
- Effort estimate: S
- Dependencies: `buddy-SUPPLY-001` (SHA pinning) recommended first
- Status: open

### Finding ID: buddy-CI-003 — Release SBOM includes dev dependencies, inconsistent with the npm script

- Severity: P3
- Confidence: High
- Area: CI
- Evidence:
  - `.github/workflows/release.yml:63` — `npm sbom --sbom-format cyclonedx > sbom.cdx.json` (no `--omit=dev`)
  - `package.json:18` — `"sbom": "npm sbom --sbom-format cyclonedx --omit=dev"`
  - `.github/workflows/release.yml:85,99` — SBOM packed and published with the release
- What is happening: the released SBOM describes the full tree including dev
  dependencies, while the documented script describes production only. The two
  definitions of "the SBOM" disagree.
- Why it matters: SBOM consumers cannot tell which dependency set is authoritative, and
  the released SBOM over-reports (and mis-attributes dev-only CVEs such as nanoid).
- Recommended fix: use one definition; if the release ships production code, generate
  `npm sbom ... --omit=dev` and note exclusions per the aggregate rule.
- Suggested validation: diff the workflow SBOM against `npm run sbom` output.
- Owner suggestion: release owner
- Effort estimate: S
- Status: open

### Finding ID: buddy-PORT-001 — `.gitattributes` missing (no line-ending policy)

- Severity: P3
- Confidence: High
- Area: PORT
- Evidence:
  - `.gitattributes` is absent at the repo root (`git ls-files` returns no `.gitattributes`)
  - Platform mix: Windows dev environment (`C:\`) with Linux CI (`.github/workflows/ci.yml:21` — `runs-on: ubuntu-latest`)
  - Deterministic ref: `DET-P3-004`
- What is happening: without a normalization policy, checkouts differ between Windows
  (CRLF) and Linux (LF), and files can churn or break shell-sensitive tooling.
- Recommended fix: add `.gitattributes` with `* text=auto eol=lf` and mark binary
  asset types as `binary`.
- Suggested validation: `git add --renormalize .`; confirm no unexpected diffs.
- Owner suggestion: maintainer
- Effort estimate: S
- Status: open

### Finding ID: buddy-CONF-001 — Product docs still claim saves are not runtime-validated

- Severity: P3
- Confidence: High
- Area: CONF
- Evidence:
  - `README.md:20-21` — "loaded/imported saves are not runtime-validated"
  - `docs/README.md:61` — `Save validation | Not reported | DATA-P1-002 / SEC-P2-001 no runtime save validation | open (tracked)`
  - `lib/storage/schema.ts:177` — `export function validateSave(input: unknown): SaveValidationResult`
  - `lib/storage/indexeddb.ts:3,50,96` — imports and calls `validateSave` on load and import
- What is happening: the code now validates and migrates saves (zod schemas, bounded
  numbers, size cap `MAX_IMPORT_LENGTH = 1_000_000`), but the README and the reconciled
  audit matrix still mark the gap as open. Generated/status artifacts contradict the
  source of truth.
- Why it matters: reviewers and AI agents reading the docs will implement or "fix" a
  control that already exists, or mis-state release risk.
- Recommended fix: update `README.md:19-22` and the `docs/README.md` status matrix to
  `verified-fixed` with the commit/evidence, per the finding-status vocabulary.
- Suggested validation: docs test (`docs/inventory-release-docs.test.ts`) should assert
  the corrected status.
- Owner suggestion: docs owner
- Effort estimate: S
- Status: open

### Finding ID: buddy-SUPPLY-002 — License is explicitly pending and vendored prompt-pack provenance is unconfirmed

- Severity: P3
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `LICENSE:1` — `LICENSE - PENDING`
  - `README.md:118-121` — "No license has been chosen yet. Absent an explicit license grant, all rights are reserved"
  - `docs/README.md:28-35` — vendored prompt pack "Authorship / ownership: not recorded in-repo and therefore unconfirmed", "Licensing: unconfirmed"
- What is happening: the repository is all-rights-reserved by default and a large
  vendored prompt pack has unconfirmed authorship/licensing.
- Why it matters: distribution/derivative rights are undefined; the pack is an
  unvetted third-party-content supply-chain item (provenance/license gate).
- Recommended fix: choose a license (or keep proprietary + internal-only) and record
  the prompt-pack provenance/ownership decision in `NOTICE`; add a license-policy gate
  if the project opens up.
- Suggested validation: `docs/README.md` provenance row updated with owner + date.
- Owner suggestion: maintainer / legal
- Effort estimate: M (legal decision)
- Status: open

## Deterministic Validation Summary

| Deterministic ID | Verdict | Evidence at 29d7928 | Notes |
|---|---|---|---|
| `DET-P1-001` (14 P1) | **REAL** | `package-lock.json:6186` next 14.2.35; `:6145` nanoid 3.3.15; `:6236` nested postcss 8.4.31 | postcss CVEs split dev 8.5.15 vs prod 8.4.31; nanoid dev-only; next EOL (no 14.x fix) |
| `DET-P2-002` (13 P2) | **REAL** | same packages | CVE-2026-41305 / CVE-2026-69153 etc. confirmed by range |
| `DET-P3-003` (2 P3) | **REAL** | `package.json:24` / `package-lock.json:6186` | next CVE-2026-44572 / 44582 |
| `DET-P3-004` (.gitattributes) | **REAL** | absent from `git ls-files` | add `* text=auto eol=lf` |
| `DET-P2-005` (6 unpinned actions) | **REAL** | `ci.yml:24,27`; `release.yml:28,33,88,93` | also stale majors; combined with write token → `buddy-SUPPLY-001` |

Fixed-version availability: nanoid → `3.3.18`/`3.3.16` (available, easy); postcss →
`8.5.19` (available for the dev copy; nested Next.js-pinned copy requires the framework
upgrade); next → only `15.5.26`/`16.3.6` (major upgrade; **no 14.x fix**).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| EOL Next.js fixed only by major upgrade | P1 | High | High | `package-lock.json:6186` | Upgrade plan + monthly advisory check |
| Compromised dep/action inherits release write token | P1 | Low | High | `release.yml:13-16,38-39,88,93` | SHA pin; least-privilege permissions |
| Vulnerable deps undetected in CI | P2 | High | Medium | `ci.yml:32-48` | Add audit/dependency-review/secret scan gates |
| Release not environment-gated | P2 | Medium | Medium | `release.yml:7-10` | GitHub Environment + protected tags + branch protection |

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `.gitattributes` | Cross-platform stability | new `.gitattributes` | `git add --renormalize .` |
| Pin 6 actions to SHAs | Supply-chain hardening | `ci.yml`, `release.yml` | `actionlint`/regex check |
| Add `npm audit --omit=dev` CI step | Detect `DET-*` deps | `ci.yml` | failing PR on vulnerable dep |
| Fix SBOM flag | Consistent SBOM | `release.yml:63` | diff vs `npm run sbom` |
| Update save-validation status docs | Self-consistency | `README.md`, `docs/README.md` | docs tests |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Upgrade Next.js to supported LTS | P1 | frontend | L | react peer |
| Least-privilege release permissions + SHA pins | P1 | CI | S | — |
| Dependency/license/secret CI gates | P2 | CI | S | license policy |
| GitHub Environment + tag/branch rules | P2 | admin | S | — |
| Bump postcss/nanoid | P2 | deps | S–M | next upgrade for nested |
| Choose license + pack provenance | P3 | legal | M | decision |

## Suggested Tests

- CI: fail if any `uses:` ref is not a 40-hex SHA; fail if `next` major is unsupported.
- CI: `npm audit --omit=dev --audit-level=high` on PRs.
- Docs: assert `README.md` / `docs/README.md` no longer claim saves are unvalidated.
- (Security) import fuzz: oversize payload, negative `size`, prototype-pollution keys —
  relies on existing `lib/storage/schema.test.ts` patterns.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is branch protection / tag protection enabled on `master`? | Required-check enforcement | GitHub settings screenshot/API output |
| Is there a `release` Environment with required reviewers? | Release approval | GitHub settings |
| Any secrets in Actions/environments (none referenced in-repo)? | Rotation scope | `gh secret list` (authorized) |
| Prompt-pack ownership/license? | Distribution rights | legal confirmation |

## Appendix

- No container artifacts exist (no `Dockerfile`/compose) → container-runtime lens is N/A.
- No `.env*`, no `.env.example`, no `${{ secrets.* }}` in workflows; secret scan clean.
- Guest identity: `components/hatch/HatchFlow.tsx:19-22` uses `crypto.randomUUID()` with
  a non-secure fallback only when `randomUUID` is unavailable.
- CSP/headers: `next.config.js:28-57` (default-src 'self', object-src 'none',
  frame-ancestors 'none', HSTS).
