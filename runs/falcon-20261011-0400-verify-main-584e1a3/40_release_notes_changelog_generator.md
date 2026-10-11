# 40_release_notes_changelog_generator — Prompt 40 - Release Notes and Changelog Generator

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `40_release_notes_changelog_generator.md` (area REL, prompt)

## Verification Performed

# Release Notes and Changelog Generator — falcon @ 08e20d1

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` @ `08e20d1a77900dcc0c0a8a3fd16ae8d203d9d65d` (branch `main`)
- Generated at: 2026-10-09 · Auditor: subagent, read-only
- Area code: REL
- Output path: `docs/audits/repo-deep-dive/falcon-20261009-2117-full-08e20d1/40_release_notes_changelog_generator.md`
- Scope limitations: git history available (866 commits, no tags); the live deployment worktree was inspected read-only; companion drafts below are drafts for owner edit and invent nothing beyond commits/ledgers.

## Scope

Reviewed: git history (69b3c80..HEAD and the full log), PR template, changelog/release-note artifacts, version files, package versions (`pins/images.lock`), migrations (OpenSearch index rename, Docker volume migration), breaking changes, known issues, operator actions, rollback notes, test evidence, and audit outputs. Companion artifacts required by the prompt (release notes draft, changelog draft, GitHub release body, upgrade/rollback notes) are embedded below because this run writes one machine file per domain.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log` (866 commits; no tags) | git history | What shipped | Commit messages use `area: summary` |
| `.github/pull_request_template.md` | PR template | Release inputs | Evidence/rollback/security/gate sections |
| `mct/RELEASE-NOTES.md` | release notes | Existing notes | Vendored upstream stack, v1.2.0 (2026-08-22) |
| `docs/audits/repo-deep-dive/{20260930,20261002}/changelog_draft.md`, `release_notes_draft.md` | drafts | Prior generator output | Not regenerated since |
| `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json` | binding artifacts | Version/commit identity | Bound to 69b3c80 (2026-10-04) |
| `pins/images.lock` (24 images) | package versions | Shipped image set | generated 2026-09-20; verify in CI |
| `ledgers/test_execution.csv` (1,127 rows) | test evidence | Confidence | PASS/FAIL records |
| `docs/RELEASE_GATE.md`, `docs/phase9/review/PRODUCTION_VERDICT.md` | known issues/verdict | Operator-facing | Verdict 2026-09-29; gate page stale |
| `docs/security/BRANCH_PROTECTION.md` | process | Release/rollback process | Tags claim vs zero tags |

## Verification Performed

| Check | Command / read | Result |
|---|---|---|
| Commit/version binding | `PACKAGE_DIGEST.txt` fields + `verify_publication_chain.sh` | 0 failures; digest bound to 69b3c80; HEAD is 08e20d1 (11 commits later) |
| Manifest resolves | compare `PACKAGE_MANIFEST.sha256` (3,783 entries) to worktree | 3,780 present; 3 missing are declared package-generated files (`PACK_*_NOT_INCLUDED.txt`) |
| Tags/version | `git tag -l`; `find -iname 'VERSION*'` | none (finding REL-P3) |
| Breaking changes | `git log 69b3c80..HEAD`; PR template | none declared; no breaking-change record exists |
| Migrations | `automation/validation/index_rename_migration.sh`, `docs/runbooks/DOCKER_VOLUME_MIGRATION.md` | documented with rollback drills; no DB schema migrations in repo |
| Live deployment | `git -C /home/user/falcon-build` + docker inspect | divergent worktree; uncommitted runtime config (finding REL-P2) |
| Test evidence | `wc -l ledgers/test_execution.csv` | 1,127 rows; current through 2026-10-01/02 waves |
| Operator actions | `docs/runbooks/OPERATOR_START_HERE.md`, `docs/RELEASE_GATE.md` | present; release-gate pointer stale (cross-ref HYGIENE P2) |

## Executive Summary

The repository has excellent provenance hygiene for what it *does* record (append-only ledgers, a derived digest bound to a commit, a publication-chain verifier that passes, a resolved manifest) and a real PR/rollback process. What it lacks is a release-notes layer for falcon itself: no root CHANGELOG, no generator, no drafts since the 2026-10-02 audit run, no tags and no VERSION file, and no artifact that binds the live deployment to a commit — while the live host runs a divergent worktree with uncommitted runtime configuration. For the Oct 4–9 window that means the P0/P1 fixes and the CI posture changes are documented only in commit messages and ledgers. Three findings: REL-P3-001 (prior, still open), REL-P2 (deploy binding), REL-P3 (release versioning).

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Git history | 866 commits, no tags | Change record | Conventional prefixes; append-only | Low | No release markers |
| PR template | `.github/pull_request_template.md` | Change intake | Current | Low | Rollback section required for runtime changes |
| Changelog | — | Release notes | Absent at root | Medium | REL-P3-001 |
| Upstream notes | `mct/RELEASE-NOTES.md` | Vendored stack | v1.2.0 (2026-08-22) | Low | Not falcon |
| Version file | — | Version identity | Absent | Medium | REL-P3 |
| Package versions | `pins/images.lock` | Image set | 24 entries; CI verify | Low | generated 2026-09-20 |
| Migrations | index rename; docker volumes | Data/host moves | Documented + rollback drills | Low | No DB schema migrations |
| Binding artifacts | `PACKAGE_DIGEST.txt` etc. | Delivery identity | Bound to 69b3c80 | Medium | HEAD 11 commits later |
| Known issues | `docs/RELEASE_GATE.md`, registers | Operator view | Stale pointer | Medium | Cross-ref HYGIENE P2 |
| Test evidence | `ledgers/test_execution.csv` | Confidence | 1,127 rows | Low | Through 2026-10-01/02 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Git history | 4 | 866 commits, disciplined messages | No tags | Tag releases |
| PR templates | 4 | Template with evidence/rollback | No provenance field | Optional |
| Changelog/release notes templates | 2 | Only old audit drafts; mct notes upstream | No falcon generator | REL-P3-001 |
| Version files | 1 | None | No VERSION | REL-P3 |
| Package versions | 4 | `pins/images.lock` + CI verify + SBOM | Lock generated 2026-09-20 | Refresh cadence |
| Migrations | 3 | Index rename + volume migration docs/drills | No schema migrations (N/A) | Keep drills |
| API/UI/security/bug/dependency/infra/docs changes | 3 | Commit categories; ledgers | No consolidated notes | Generator |
| Breaking changes | 2 | None declared | No breaking-change record | Template field |
| Known issues | 3 | Registers + release gate | Gate page stale | Refresh pointer |
| Operator actions | 3 | Runbooks; deploy records | Oct 9 ops only in live worktree | Bind deploy |
| Migration steps | 3 | Runbooks + rehearsal scripts | — | Keep |
| Rollback notes | 3 | PR template; commit-level reverts; runbooks | Not per release | Include in notes |

## Detailed Review

### Item: Release identity and binding

- Evidence: `PACKAGE_DIGEST.txt` (commit 69b3c80, verdict fields), `closeout/FINAL_RESPONSE.json` (same commit), `PACKAGE_MANIFEST.sha256` (3,783 entries, hash matches digest).
- Verification: `verify_publication_chain.sh` → 0 failures; 3 manifest entries missing from the worktree are the declared package-generated files; signed 2026-09-29 archives intact.
- Gap: the binding is to the last delivered package, not to HEAD or the live deployment; nothing states the deployed commit (REL-P2).

### Item: Release notes/changelog generation

- Evidence: no root CHANGELOG; drafts only in 20260930/20261002 runs; mct notes upstream-only.
- Gap: the Oct 4–9 changes (P0/P1 fixes, hygiene fix, CI posture changes) have no user/operator/security notes (REL-P3-001).

### Item: Versioning

- Evidence: zero tags; no VERSION; `BRANCH_PROTECTION.md:59` says releases are tags.
- Gap: release identity depends on external date-named archives; overwrite-in-place digest filenames (REL-P3).

### Item: Live deployment traceability

- Evidence: live worktree at 6e4fccd (2 ahead/22 behind origin/main), 40 dirty files incl. mounted `config/prometheus/edge-alerts.yaml` (+112/-7).
- Gap: no deploy manifest; release notes cannot say what is live (REL-P2).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| REL-001 | Git history | 866 commits | Disciplined messages | No tags | P3 | Tag |
| REL-002 | PR templates | template | Evidence/rollback fields | Provenance | P3 | Optional |
| REL-003 | Changelog/release notes | old drafts only | None for falcon | No generator | P3 | REL-P3-001 |
| REL-004 | Version files | none | Commit SHA only | No VERSION | P3 | Add |
| REL-005 | Package versions | images.lock | CI verify | Refresh cadence | P3 | Keep |
| REL-006 | Migrations | index/volume docs | Drills | — | — | Keep |
| REL-007 | Change categories | commits/ledgers | Per-commit | No consolidated notes | P3 | Generator |
| REL-008 | Breaking changes | none declared | — | No record | P3 | Template field |
| REL-009 | Known issues | registers/gate | Append-only | Gate stale | P2 | Refresh (HYGIENE) |
| REL-010 | Operator actions | runbooks | Documented | Live deploy unbound | P2 | REL-P2 |
| REL-011 | Migration steps | runbooks | Documented | — | — | Keep |
| REL-012 | Rollback notes | template/commits | Per change | Not per release | P3 | Include in notes |

## Findings

### Finding: REL-P3-001 — No root CHANGELOG/release-notes generator; the 2026-10-04..09 window is undocumented (see JSON)

### Finding: REL-P2 (new) — Deployment state is not bound to any release (see JSON)

### Finding: REL-P3 (new) — Releases are not versioned: no tags, no VERSION; binding artifacts overwrite in place (see JSON)

## Release Notes Draft (for owner edit)

> Draft generated from `git log 69b3c80..08e20d1` (the window since the last delivered package) and the ledgers. No claims beyond commits/evidence. Not a substitute for the program's own closeout.

### falcon — 2026-10-04 .. 2026-10-09 (unreleased; main @ 08e20d1)

**Security / reliability (fixes)**
- OBS-P0-001: Prometheus now has per-file textfile-collector freshness rules + validation, de-concentrating the monitoring dead-man path (#46, 483f878).
- API-P1-001: the edge pairing contract verifies offline from a clean clone (#47, f7522d0).
- FINAL-P1-001: end-to-end restore assertion + dead-man contract added to the release gate (#48, 27ed413).
- HYGIENE-P1-001: the generated `review-package/` is no longer committed; it is gitignored and built on demand (#43, a2dded8).

**CI / operations**
- CI runs on self-hosted lab runners (GitHub-hosted jobs are billing-blocked) — validate/external-smoke/dependabot-merge (#70292a0).
- external-smoke: the lab-runner vantage accepts the owner-IP Access bypass (origin reachability is the lab check; Access posture is verified externally) (#08e20d1). **Audit note: this removes the only automated Access-posture assertion — see CHAIN finding.**

**Records**
- Audit runs published/renamed to the `YYYYMMDD-HHMM-` lifecycle ids (#44, #45).

### Operator actions
- No new migration steps in this window.
- Re-run `bash automation/validation/verify_publication_chain.sh` before any delivery.
- The live host is not at this commit (see REL-P2): verify the deployed commit before claiming these fixes live.

### Upgrade / rollback notes
- Upgrade: `git pull` on the lab worktree, then run the standard flow in `AGENTS.md` §Standard change flow; re-run `python3 ci/validate.py`.
- Rollback: `git revert <commit>` per change; runtime changes follow the PR-template rollback note. The SEC-P1-002 firewall narrowing is not yet applied live (CHAIN finding) — applying it is a runtime change with the documented rollback (restore previous `/etc/nftables.conf`).

## Changelog Draft (for `CHANGELOG.md`)

```markdown
## [unreleased] — 2026-10-04..09 hardening (main @ 08e20d1)

### Fixed
- Observability: per-file textfile-collector freshness rules and validation (OBS-P0-001, #46).
- API: offline edge-pin pairing verification from a clean clone (API-P1-001, #47).
- Release gate: end-to-end restore assertion + dead-man contract (FINAL-P1-001, #48).
- Hygiene: generated review-package/ untracked and gitignored (HYG-P1-001, #43).

### Changed
- CI: workflows run on self-hosted lab runners (billing-blocked hosted runners retired).
- CI: external-smoke accepts the owner-IP Access bypass from the lab vantage (audit note: detection gap, see CHAIN).

### Added
- Audit run folders published under lifecycle-valid ids (#44, #45).

### Security
- (Pending deploy) firewall narrowing for WireGuard peers (SEC-P1-002) remains committed-but-not-live; apply before the next release claim.
```

## GitHub Release Body (draft)

```
falcon lab — hardening window 2026-10-04..09 (commit 08e20d1)

Highlights
- OBS-P0-001 fix: monitoring freshness is no longer textfile-collector-only (#46)
- API-P1-001: pairing verifies offline from a clean clone (#47)
- FINAL-P1-001: restore assertion in the release gate (#48)
- HYG-P1-001: review-package is no longer committed (#43)

Notes
- CI now runs on the lab runners; the external smoke no longer asserts Cloudflare Access posture from an external vantage (audit CHAIN finding).
- The live host is not bound to this commit; deployment traceability is an open audit finding.
- No git tags exist; this release is identified by commit 08e20d1.
```

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Fixes claimed but not deployed live | P2 | High | Medium | live worktree 6e4fccd; nft drift | REL-P2 + deploy manifest |
| No release notes for security changes | P3 | High | Low | no drafts since 20261002 | REL-P3-001 |
| Release identity ambiguity | P3 | Medium | Low | no tags/VERSION | REL-P3 |

## Recommendations

### Immediate / Release Blocking
- None (no P0/P1 in this domain).

### This Week
- Record the deployed commit/config in a deploy manifest; state it in release notes (REL-P2).
- Publish a changelog/release-notes draft for 69b3c80..HEAD (REL-P3-001).

### This Month
- Add tags/VERSION and a generator; refresh the images.lock cadence.

### Later / Platform Evolution
- Automate release-note generation from ledgers + git in the publication flow.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `CHANGELOG.md` from the draft above | Visible release history | root | file present |
| Tag `main` at releases | Identity | git tags | `git tag -l` non-empty |
| Deploy-manifest line in `PACKAGE_DIGEST.txt` | Live binding | digest generator | field present |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Release-notes generator from git+ledgers | P3 | maintainer | M | none |
| Deploy manifest per deploy | P2 | ops | S/M | deploy flow |
| Tag/version release policy | P3 | owner | S | owner decision |

## Suggested Tests

- CI: `PACKAGE_DIGEST.txt` commit == the commit named in `FINAL_RESPONSE.json` (exists) and a deploy manifest names the live commit (new).
- Test: release-note generator produces a draft with no invented items (diff against `git log`).
- Regression: manifest entries resolve to present artifacts (exists via `check_digest_binding.py`).

## Suggested Documentation Updates

- Root `CHANGELOG.md` + `release_notes_draft.md` per run.
- `docs/security/BRANCH_PROTECTION.md` §release process — align the tag claim with reality.
- `docs/RELEASE_GATE.md` — current audit opinion (cross-ref HYGIENE).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which commit/config is the live host supposed to run? | Release traceability | Owner/ops answer; deploy manifest |
| Are tags intended, or is commit-SHA identity the accepted policy? | Versioning approach | Owner decision |

## Prior-Run Comparison

- `REL-P3-001` (no root CHANGELOG/generator): prior status open → still open; the undocumented window has grown from the audit window to 11 commits including P0/P1 fixes.
- No other REL findings existed in the prior full run.

## Limitations

- Companion drafts are generated from commits/ledgers only; the owner edits them before merge.
- No tags exist, so no tag-diff was possible; the window since the delivered package was used instead.
- Live worktree inspection was read-only; intent behind the local commits is inferred from the pack's post-audit notes (PR #49 line), not from the commit itself.

## Appendix — window since the delivered package

| Commit | Date | Subject |
|---|---|---|
| 08e20d1 | 2026-10-09 | ci: accept the owner-IP Access bypass in the lab-runner smoke |
| 70292a0 | 2026-10-09 | ci: run on the self-hosted lab runners |
| 27ed413 | 2026-10-04 | final: offline end-to-end restore assertion + dead-man contract (#48) |
| f7522d0 | 2026-10-04 | api: verify the edge pairing contract offline (#47) |
| 483f878 | 2026-10-04 | obs(OBS-P0-001): per-file textfile-collector freshness rules (#46) |
| 427298b | 2026-10-04 | fix(audit): rename published runs to valid ids (#45) |
| a2dded8 | 2026-10-04 | hygiene: stop tracking generated review-package/ (#43) |
| dba374d | 2026-10-04 | docs(audit): publish run 20261005-full-main-e267ce1 (#44) |
| e267ce1 | 2026-10-04 | docs(audit): publish run 20261004-fast-main-f9cb67d (#42) |
| f9cb67d | 2026-10-04 | publication: pack-verified package manifest |
| b8d490c | 2026-10-04 | publication: bind (closeout + digest at the declared commit) |

## Findings

| ID | Severity | Title |
|---|---|---|
| REL-P3-001 | P3 | No root CHANGELOG/release-notes generator; the 2026-10-04..09 window is undocumented |
| REL-P2-001 | P2 | Deployment state is not bound to any release: the live host runs a divergent worktree with uncommitted runtime config |
| REL-P3-002 | P3 | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place |
