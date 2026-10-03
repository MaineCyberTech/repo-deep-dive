# Supply Chain, Dependencies, and Secrets Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-master-99abf29
- Repository: `C:\temp\buddy`
- Branch: master
- Commit SHA: 99abf294dae0d9de8770dfde257bdef5fae9ae1b
- Generated at: 2026-10-03T04:18Z
- Auditor: repo-deep-dive subagent
- Area code: SUPPLY
- Output path: docs/audits/repo-deep-dive/20261003-0018-master-99abf29/11_supply_chain_dependency_secrets.md
- Scope limitations: No registry/network access, so advisories and license texts were **not queried**; version/EOL observations are from the lockfile and public release knowledge and are marked Medium confidence. Secret scan is static.

## Scope

Reviewed dependency manifests/lockfile, licensing, SBOM/advisory tooling, vendored third-party content, and secret exposure. Not reviewed: npm registry advisory database (offline), runtime transitive tree (only lock metadata sampled).

## Evidence Reviewed

- `package.json`, `package-lock.json` (lockfileVersion 3)
- resolved versions: next 14.2.35, react/react-dom 18.3.1, zod 3.25.76, zustand 4.5.7, idb 8.0.3, vitest 1.6.1, eslint 8.57.1, typescript 5.9.3, @playwright/test 1.61.1
- root file listing (no LICENSE, no NOTICE)
- `docs/prompts/...` (vendored prompt pack)
- secret-pattern grep across repo

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `package-lock.json` resolved versions | lockfile | dependency risk | sampled key packages |
| `Test-Path LICENSE*` | command | licensing | false |
| secret grep | command | secrets | no live secrets |
| `git ls-files docs` | command | vendored content | 98 md files |
| `npm audit` | command | advisories | **not run** (no network/node_modules) |

## Executive Summary

The dependency posture is **reasonable but unmanaged**. A lockfile (v3) is committed and key dependencies are current-enough patch lines, but several are on lines that are aged by 2026 standards: **Next.js 14.2.35** (a prior major; 14.x is maintenance-only), **ESLint 8** (EOL), and **@playwright/test 1.61.1** (installed but unused). There is **no LICENSE** at the repo root, which blocks any redistribution/derivative use regardless of the GitHub remote being visible. There is **no SBOM, no license policy, and no automated update/vulnerability workflow** (see CI-P2-001). No live secrets were found; pattern matches were prose only. The checked-in third-party **prompt pack** raises provenance/attribution questions (it references other projects and brand names), which is a legal/originality risk distinct from code dependencies.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Manifest | `package.json` | deps | Present | Low | ranges + lock |
| Lockfile | `package-lock.json` | pinning | Present (v3) | Low | reproducibility |
| Next.js | `next` 14.2.35 | framework | Aged | P2 | prior major in 2026 |
| React | 18.3.1 | UI | Current-ish | Low | — |
| zod | 3.25.76 | validation | Installed, unused | Medium | could validate saves |
| eslint | 8.57.1 | lint | EOL line | P2 | plan upgrade |
| Playwright | 1.61.1 | E2E | Installed, unused | Low | remove or use |
| LICENSE | (none) | legal | Absent | P1 | blocks distribution |
| SBOM | (none) | transparency | Absent | P2 | add CycloneDX |
| License policy | (none) | compliance | Absent | P2 | add allowlist |
| Update bot | (none) | maintenance | Absent | P2 | Dependabot |
| Vendored prompt pack | `docs/prompts/...` | docs | Present | P2 | provenance/IP |
| Secrets | repo-wide | secrets | None found | Low | grep clean |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Dependency pinning | 4 | lockfile v3 | — | keep |
| Dependency currency | 2 | next 14.2.x, eslint 8 | aged/EOL | upgrade plan |
| Vulnerability scanning | 0 | none | none | Dependabot + audit |
| SBOM | 0 | none | none | generate |
| License compliance | 0 | no LICENSE/policy | none | add LICENSE |
| Secret handling | 4 | no secrets found | no scan in CI | add gitleaks |
| Vendored content provenance | 1 | prompt pack | unclear | classify/prune |
| Package-manager hygiene | 3 | npm only | no engines field | add `engines` |

## Detailed Review

### Item: Dependency versions
- Evidence: `package-lock.json` resolved versions (sampled above).
- Note: `package.json` uses caret ranges, so fresh installs follow the lockfile; without Dependabot the lockfile silently ages.
- Confidence on EOL status: Medium (offline; based on public release lines known at audit time).

### Item: Licensing
- Evidence: no `LICENSE`/`NOTICE` at root; `git remote` is a public-looking GitHub URL.
- Risk: "all rights reserved" by default; downstream use undefined.

### Item: Vendored prompt pack
- Evidence: `docs/prompts/buddy_virtual_pet_v2_complete_prompt_pack/**`; README line 17 warns against copying Tamaweb/Tamagotchi/other projects.
- Risk: unclear license/provenance of the pack text; potential third-party marks.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| SUPPLY-001 | Licensing | no LICENSE | none | undefined rights | P1 | add LICENSE |
| SUPPLY-002 | Dependency currency | lockfile | pinned | aged/EOL | P2 | upgrade + update bot |
| SUPPLY-003 | SBOM/audit | none | none | no visibility | P2 | generate + CI |
| SUPPLY-004 | Vendored content | prompt pack | none | provenance | P2 | classify/prune |
| SUPPLY-005 | Secrets in CI | no CI | none | no scan | P3 | gitleaks |

## Findings

### Finding ID: SUPPLY-P1-001 - No LICENSE file; distribution/derivative rights are undefined

- Severity: P1
- Confidence: High
- Area: SUPPLY
- Evidence:
  - `Test-Path LICENSE*` → false; root `*.md` listing empty
  - `git remote -v` → `https://github.com/MaineCyberTech/buddy.git`
- What is happening: The repository has no license, so by default it is "all rights reserved" and others cannot legally use, modify, or redistribute it.
- Why it matters: Blocks open-source distribution, community contribution, and some company/CI usage; ambiguous for the vendored prompt pack too.
- User / business impact: Legal exposure; limits adoption and contribution.
- Security / privacy / reliability impact: None technical.
- Recommended fix: Add an explicit `LICENSE` (e.g., MIT/Apache-2.0) matching intent, plus `NOTICE`/attribution if the prompt pack is third-party. Confirm the prompt pack's own license.
- Suggested validation: `LICENSE` present and referenced from `README.md`; GitHub license detection.
- Owner suggestion: maintainer/legal
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: SUPPLY-P2-001 - Dependencies are pinned but unmanaged and include aged/EOL lines

- Severity: P2
- Confidence: Medium
- Area: SUPPLY
- Evidence:
  - `package-lock.json` — next 14.2.35, eslint 8.57.1, @playwright/test 1.61.1, react 18.3.1, vitest 1.6.1
  - `package.json` — caret ranges, no `engines`
  - no `.github/dependabot.yml` or Renovate config
- What is happening: The lockfile is committed (good) but nothing updates it; sampled versions are on maintenance/EOL lines as of 2026.
- Why it matters: Unpatched frameworks/tooling accumulate known vulnerabilities and incompatibilities; original advisory status could not be queried offline.
- User / business impact: Security/reliability risk grows silently.
- Security / privacy / reliability impact: Supply-chain risk (advisories unverified here).
- Recommended fix: Enable Dependabot (npm + GitHub Actions), schedule grouped upgrades, and add an `engines` field (e.g., `node >= 20`). Re-verify advisories against the npm advisory DB when online.
- Suggested validation: Dependabot PRs open; `npm audit --production` clean or triaged in CI.
- Owner suggestion: maintainer
- Effort estimate: M
- Dependencies: CI-P1-001
- Status: open

### Finding ID: SUPPLY-P2-002 - No SBOM, license policy, or dependency-vulnerability scanning

- Severity: P2
- Confidence: High
- Area: SUPPLY
- Evidence:
  - no SBOM artifact; no `license-checker`/`cyclonedx` config
  - no `.github/workflows` (no audit/CodeQL)
- What is happening: The project cannot produce a dependency inventory or enforce license allowlists.
- Why it matters: Compliance and incident response (e.g., log4shell-style) require knowing the dependency tree quickly.
- User / business impact: Slow response to supply-chain incidents; audit friction.
- Security / privacy / reliability impact: Supply-chain transparency.
- Recommended fix: Generate a CycloneDX SBOM in CI and publish per release; add a license allowlist check.
- Suggested validation: CI produces an SBOM artifact attached to the release.
- Owner suggestion: DevSecOps
- Effort estimate: M
- Dependencies: CI-P1-001
- Status: open

### Finding ID: SUPPLY-P2-003 - Vendored prompt-pack content has unclear provenance and third-party references

- Severity: P2
- Confidence: Medium
- Area: SUPPLY
- Evidence:
  - `docs/prompts/buddy_virtual_pet_v2_complete_prompt_pack/**` — 98 markdown files
  - pack `README.md` line 17 — explicit warning about Tamaweb/Tamagotchi/other copyrighted projects
  - no LICENSE/NOTICE covering the pack
- What is happening: A large text pack of uncertain licensing is committed with the product.
- Why it matters: Potential copyright/trademark/originality risk and repo bloat; unclear whether pack text may be redistributed.
- User / business impact: Legal/reputational risk.
- Security / privacy / reliability impact: None technical.
- Recommended fix: Confirm the pack's license/ownership, add attribution or remove it, and classify it in docs. Keep product code free of third-party brand references.
- Suggested validation: Legal review sign-off recorded; `docs/README.md` classifies pack provenance.
- Owner suggestion: legal/maintainer
- Effort estimate: S
- Dependencies: SUPPLY-P1-001
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| No license | P1 | High | High | SUPPLY-P1-001 | add LICENSE |
| Aged deps | P2 | High | Medium | SUPPLY-P2-001 | Dependabot + upgrade |
| No SBOM/audit | P2 | Medium | Medium | SUPPLY-P2-002 | CI SBOM/audit |
| Vendored IP ambiguity | P2 | Medium | High | SUPPLY-P2-003 | classify/attribute |

## Recommendations

### Immediate / Release Blocking
- Add a LICENSE before any public/non-RC release.

### This Week
- Enable Dependabot; add `engines`; run `npm audit`.
- Classify the prompt pack.

### This Month
- Add SBOM + audit to CI; plan Next/ESLint upgrades.

### Later / Platform Evolution
- Subscription-based security updates for long-lived dependencies.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add LICENSE | legal clarity | `LICENSE` | GitHub detection |
| Dependabot config | maintenance | `.github/dependabot.yml` | PRs |
| `engines` field | reproducibility | `package.json` | install warning |
| Use zod for saves | turns dep into control | `lib/storage/*` | tests |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| LICENSE + attribution | P1 | legal | S | none |
| Dependency update program | P2 | maintainer | M | CI |
| SBOM + license policy | P2 | DevSecOps | M | CI |
| Prompt-pack provenance | P2 | legal | S | none |

## Suggested Tests

- `npm audit --production` gate in CI.
- SBOM generation test; license allowlist test.
- `gitleaks` secret scan job.

## Suggested Documentation Updates

- `LICENSE`, `NOTICE`, `SECURITY.md`, `docs/third-party.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Was the prompt pack authored in-house? | licensing | authorship record |
| Target license? | legal | maintainer decision |
| Advisory status of next 14.2.35? | vuln triage | online advisory DB |

## Appendix

Resolved versions sampled from `package-lock.json`:
`next 14.2.35`, `react 18.3.1`, `react-dom 18.3.1`, `zod 3.25.76`, `zustand 4.5.7`, `idb 8.0.3`, `vitest 1.6.1`, `eslint 8.57.1`, `typescript 5.9.3`, `@playwright/test 1.61.1`. Advisory status **not queried** (offline) → marked unverified.
