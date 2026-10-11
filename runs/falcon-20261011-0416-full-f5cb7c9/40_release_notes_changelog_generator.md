# 40_release_notes_changelog_generator — Prompt 40 - Release Notes and Changelog Generator

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `40_release_notes_changelog_generator.md` (area REL, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `falcon` @ `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (branch `main`), read-only worktree `/tmp/opencode/falcon-audit-f5cb7c9`
- Generated at: 2026-10-11 (UTC) - Auditor: subagent, read-only
- Area code: REL
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/40_release_notes_changelog_generator.md`
- Scope limitations: git history available (0 tags); the live deployment worktree and GitHub main were checked read-only; companion drafts below are drafts for owner edit and invent nothing beyond commits/ledgers.

## Scope

Reviewed: git history (08e20d1..f5cb7c9 and the full log), PR template, changelog/release-note artifacts, version files, package versions (`pins/images.lock`), migrations (OpenSearch index rename, Docker volume migration), breaking changes, known issues, operator actions, rollback notes, test evidence, audit outputs, and the publication/binding chain. Companion artifacts required by the prompt (release notes draft, changelog draft, GitHub release body, upgrade/rollback notes) are embedded below because this run writes one machine file per domain.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log 08e20d1..f5cb7c9` (16 commits) | git history | What shipped since the prior audit | No tags anywhere (0) |
| `.github/pull_request_template.md` | PR template | Release inputs | Evidence/rollback/security/gate sections; no provenance |
| `mct/RELEASE-NOTES.md` | release notes | Existing notes | Vendored upstream stack, v1.2.0 (2026-08-22) - not falcon |
| `docs/audits/repo-deep-dive/{20260930,20261002}/changelog_draft.md`, `release_notes_draft.md` | drafts | Prior generator output | Not regenerated since 2026-10-02 |
| `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json` | binding artifacts | Version/commit identity | Bound to `3c11752` (parent of the publication commit f5cb7c9); chain 0 failures |
| `PACKAGE_MANIFEST.sha256` vs `review-package/MANIFEST.sha256` | binding artifacts | Shipped manifest set | 8 files differ (REL-P2-002) |
| `pins/images.lock` | package versions | Shipped image set | CI-verified |
| `ledgers/test_execution.csv` | test evidence | Confidence | 1,127+ rows |
| `docs/RELEASE_GATE.md`, `docs/CURRENT_STATE.md` | known issues/verdict | Operator-facing | Gate page stale (cross-ref HYGIENE-P2-002) |
| `docs/security/BRANCH_PROTECTION.md:56-61` | process | Release/rollback process | "releases are tags on main" vs zero tags |
| live `/home/user/falcon-build`; GitHub API `commits/main` | deployment | What is live | Clean tree, HEAD f5cb7c9 == remote main |
| `/home/user/falcon-review-delivery-*.tar.gz` | delivery archives | Shipped artifact set | Newest 2026-10-04; no archive for the 2026-10-10/11 rebinds |

## Verification Performed

| Check | Command / read | Result |
|---|---|---|
| Commit/version binding | `PACKAGE_DIGEST.txt` + `verify_publication_chain.sh` | 0 failures; digest bound to 3c11752 (one commit before the publication commit, by design) |
| Publication equality | `check_publication_equality.py` | PASS on the working tree; the declared-commit checks pass because the manifest is tracked |
| Published vs declared manifest | `sha256sum PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` | differ: 4ea4a08f vs 749dae85; 8 files differ (REL-P2-002) |
| Packaged closeout binding | `git show <commit>:closeout/FINAL_RESPONSE.json` + manifest hashes | declared manifest hashes the closeout naming `b09a50f`, not the declared `3c11752` (REL-P3-003) |
| Tags/version | `git tag -l`; tracked `VERSION`/`CHANGELOG` | 0 tags; none tracked |
| Breaking changes | `git log 08e20d1..f5cb7c9` | none declared; no breaking-change record exists |
| Migrations | `automation/validation/index_rename_migration.sh`, `docs/runbooks/DOCKER_VOLUME_MIGRATION.md` | documented with rollback drills; no DB schema migrations in repo |
| Live deployment | `git -C /home/user/falcon-build status --porcelain`; `rev-parse HEAD`; GitHub API | clean (0 entries); HEAD f5cb7c9; remote main f5cb7c9 - prior divergence **fixed** |
| Test evidence | `wc -l ledgers/test_execution.csv` | 1,127+ rows |
| Operator actions | `docs/runbooks/OPERATOR_START_HERE.md`, `docs/RELEASE_GATE.md` | present; gate pointer stale (cross-ref HYGIENE-P2-002) |

## Executive Summary

The publication chain is materially healthier than at the prior full run: the digest is now bound to `3c11752` (the immediate parent of the publication commit, not 11 commits behind), `verify_publication_chain.sh` reports 0 failures, `check_publication_equality.py` passes, and the live deployment tree is clean at `f5cb7c9` == GitHub main (the prior divergent worktree with uncommitted runtime config is resolved). Two binding inconsistencies remain in the published artifact set: the top-level `PACKAGE_MANIFEST.sha256` is stale (it still carries the abb63ab-cycle hashes; 8 files differ from the declared manifest, including the security-relevant bootstrap scripts changed by PRs #51/#53/#54), and the packaged `closeout/FINAL_RESPONSE.json` names the previous publication commit (`b09a50f`) while the digest declares `3c11752` - the equality gate reads the working tree only, so both pass. Release hygiene for falcon itself is still absent: no root CHANGELOG/release-notes generator (the 2026-10-04..11 window, including the Oct 9 remediation and Oct 10/11 fixes, is undocumented), no tags, no VERSION file, and no deploy manifest binding the deployment to a release (deployment identity is the mutable main HEAD). Four of five findings are P2/P3; none are release-blocking.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Git history | 16 commits since 08e20d1; 0 tags | Change record | Disciplined messages | Low | No release markers |
| PR template | `.github/pull_request_template.md` | Change intake | Current | Low | Rollback required for runtime changes |
| Changelog | - | Release notes | Absent at root | Medium | REL-P3-001 |
| Version file | - | Version identity | Absent | Medium | REL-P3-002 |
| Binding artifacts | `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `review-package/MANIFEST.sha256` | Delivery identity | Digest current; published manifest stale | Medium | REL-P2-002 |
| Package closeout | `closeout/FINAL_RESPONSE.json` | Delivery record | Working tree names 3c11752; packaged copy names b09a50f | Low/Medium | REL-P3-003 |
| Delivery archives | `/home/user/falcon-review-delivery-*.tar.gz` | Shipped bytes | Newest 2026-10-04; no archive for the Oct 10/11 rebinds | Medium | REL-P2-002 context |
| Deployed state | `/home/user/falcon-build` | What is live | Clean; f5cb7c9 == remote main | Low | REL-P2-001 residual |
| Known issues | `docs/RELEASE_GATE.md`, registers | Operator view | Gate pointer stale | Medium | cross-ref HYGIENE-P2-002 |
| Test evidence | `ledgers/test_execution.csv` | Confidence | 1,127+ rows | Low | - |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Git history | 4 | 16-commit window, disciplined messages | No tags | Tag releases |
| PR templates | 4 | Evidence/rollback sections | No provenance field | AI-P3-002 |
| Changelog/release notes templates | 2 | Only 20260930/20261002 drafts | No falcon generator | REL-P3-001 |
| Version files | 1 | None | No VERSION | REL-P3-002 |
| Package versions | 4 | `pins/images.lock` + CI verify + SBOM | Refresh cadence | Keep |
| Migrations | 3 | Index rename + volume migration docs/drills | No schema migrations (N/A) | Keep drills |
| API/UI/security/bug/dependency/infra/docs changes | 3 | Commit categories; ledgers | No consolidated notes | Generator |
| Breaking changes | 2 | None declared | No breaking-change record | Template field |
| Known issues | 3 | Registers + release gate | Gate page stale | HYGIENE-P2-002 |
| Operator actions | 3 | Runbooks; live tree now clean at HEAD | No deploy manifest | REL-P2-001 |
| Migration steps | 3 | Runbooks + rehearsal scripts | - | Keep |
| Rollback notes | 3 | PR template; commit-level reverts; runbooks | Not per release | Include in notes |

## Detailed Review

### Item: Release identity and binding

- Evidence: `PACKAGE_DIGEST.txt` (repository_commit=CLOSEOUT_SOURCE_COMMIT=DELIVERED_PACKAGE_COMMIT=3c11752; review_package_manifest_sha256=749dae85; entries=3830), `closeout/FINAL_RESPONSE.json` (commit 3c11752), `verify_publication_chain.sh` -> 0 failures, `check_publication_equality.py` -> PASS.
- Verification: `PACKAGE_MANIFEST.sha256` (4ea4a08f) != `review-package/MANIFEST.sha256` (749dae85); same 3,830 paths, 8 differing hashes: `automation/validation/export_monitor_metrics.sh`, `automation/validation/phase6_backup_restore.sh`, `bootstrap/80-offsite-backup.sh`, `bootstrap/90-alerting.sh`, `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh`, `closeout/FINAL_RESPONSE.json`, `closeout/FINAL_RESPONSE_SUPERSEDING_2026-09-23.json`.
- Gap: PACKAGE_MANIFEST.sha256 is refreshed only by `verify_delivery.sh:38`; the last two rebinds did not run it (no archive after 2026-10-04; PACK_VERIFICATION_NOTES.txt/PACK_NOT_INCLUDED.txt last touched df934e5, 2026-10-01), and no gate compares the two manifests.

### Item: Release notes/changelog generation

- Evidence: no root CHANGELOG; drafts only in the 20260930/20261002 runs; mct notes upstream-only (v1.2.0).
- Gap: the 2026-10-04..11 window (16 commits incl. the Oct 9 remediation #49 and fixes #50-#54) has no user/operator/security notes (REL-P3-001).

### Item: Versioning and deployment traceability

- Evidence: `git tag -l` = 0; no VERSION; `BRANCH_PROTECTION.md:59` "releases are tags on main"; live tree clean at f5cb7c9 == remote main (GitHub API); no deploy manifest anywhere (`grep 'deploy manifest|deployed commit' docs/` -> none).
- Gap: deployment identity is a mutable branch HEAD with no release/manifest artifact; the prior divergence/uncommitted-config problem is fixed.

### Item: Packaged closeout lag (REL-P3-003)

- Evidence: declared manifest (3c11752) hashes `closeout/FINAL_RESPONSE.json` = 09b2c0d0..., which is the closeout at 584e1a3/3c11752 naming `b09a50f`; the live built package contains the same 09b2c0d0 file; the working-tree closeout at f5cb7c9 (02733f8b) names `3c11752`. `check_publication_equality.py` reads the working-tree closeout only.
- Root cause: the documented order (`AGENTS.md` standard flow step 5) builds the review package before `generate_final_response.py`, so the packaged closeout always lags one publication cycle.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| REL-001 | Git history | 16-commit window | Disciplined messages | No tags | P3 | Tag |
| REL-002 | PR templates | template | Evidence/rollback fields | Provenance | P3 | AI-P3-002 |
| REL-003 | Changelog/release notes | old drafts only | None for falcon | No generator | P3 | REL-P3-001 |
| REL-004 | Version files | none | Commit SHA only | No VERSION | P3 | REL-P3-002 |
| REL-005 | Package versions | images.lock | CI verify | Refresh cadence | P3 | Keep |
| REL-006 | Migrations | index/volume docs | Drills | - | - | Keep |
| REL-007 | Change categories | commits/ledgers | Per-commit | No consolidated notes | P3 | Generator |
| REL-008 | Breaking changes | none declared | - | No record | P3 | Template field |
| REL-009 | Known issues | registers/gate | Append-only | Gate stale | P2 | HYGIENE-P2-002 |
| REL-010 | Operator actions | runbooks; clean live tree | Documented | No deploy manifest | P2 | REL-P2-001 |
| REL-011 | Migration steps | runbooks | Documented | - | - | Keep |
| REL-012 | Rollback notes | template/commits | Per change | Not per release | P3 | Include in notes |

## Findings

### REL-P2-001 - Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now clean at main HEAD

- Severity: P2
- Confidence: High
- Evidence:
  - `/home/user/falcon-build`: `git status --porcelain` -> 0 entries; `rev-parse HEAD` -> f5cb7c96... (prior divergence/uncommitted-config leg **fixed**)
  - GitHub API `repos/MaineCyberTech/falcon/commits/main` -> f5cb7c96... (same)
  - `git tag -l` -> 0; no `VERSION` tracked; `docs/security/BRANCH_PROTECTION.md:59` "releases are tags on main"
  - no deploy manifest: `grep -rn 'deploy manifest|deployed commit' docs/*.md docs/runbooks/*.md` -> none
- What is happening: the live host now matches main HEAD exactly and the tree is clean, but nothing records "the deployment is release X" - there are no releases and no deploy manifest; deployment identity remains a mutable branch HEAD, and the publication digest binds the delivered package (3c11752), not the deployment.
- Why it matters: release notes/operator docs cannot cite a release identity; a future HEAD move silently changes "what is live".
- Recommended fix: record the deployed commit in a deploy manifest/decision-log entry per deploy (or tag releases per REL-P3-002) and state it in release notes.
- Suggested validation: CI/ops check that a deploy record exists for the live commit; release notes name the deployed commit.
- Owner suggestion: ops
- Effort estimate: S/M
- Status: open

### REL-P2-002 - Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files and no gate compares them

- Severity: P2
- Confidence: High
- Evidence:
  - `sha256sum PACKAGE_MANIFEST.sha256` -> 4ea4a08f... (last changed at 75c3466, the abb63ab cycle, 2026-10-10); `review-package/MANIFEST.sha256` -> 749dae85... (declared by PACKAGE_DIGEST.txt at 3c11752)
  - same 3,830 paths; 8 differing hashes (export_monitor_metrics.sh, phase6_backup_restore.sh, 80-offsite-backup.sh, 90-alerting.sh, 96-public-access.sh, 97-cloudflare-api-config.sh, both closeout files)
  - examples: `bootstrap/80-offsite-backup.sh` PACKAGE_MANIFEST=108de2c7... (pre-#51) vs declared/actual=47fa22b6...; `bootstrap/97-cloudflare-api-config.sh` PACKAGE_MANIFEST=688f454d... (pre-#54) vs declared/actual=26e52e6b...
  - `automation/validation/verify_delivery.sh:38` is the only refresher (cp from review-package/MANIFEST.sha256); no archive after 2026-10-04 and PACK_VERIFICATION_NOTES.txt/PACK_NOT_INCLUDED.txt last touched df934e5 (2026-10-01)
  - no gate compares the two manifests (check_digest_binding.py binds evidence + review-package only; verify_publication_chain.sh binds review-package only)
- What is happening: the last two rebinds (b09a50f, 3c11752) skipped the full delivery step, so the published packed-only manifest still carries the previous cycle's hashes for the files changed by PRs #51/#53/#54.
- Why it matters: a packed-only reviewer verifying against PACKAGE_MANIFEST.sha256 sees 8 false mismatches on security-relevant scripts; the published artifact set contradicts itself.
- Recommended fix: refresh PACKAGE_MANIFEST.sha256 in the bind flow (or retire it as redundant) and add a publication-gate equality check between the published and declared manifests.
- Suggested validation: CI diff of PACKAGE_MANIFEST.sha256 vs review-package/MANIFEST.sha256 must be empty after a bind.
- Owner suggestion: maintainer/publication session
- Effort estimate: S
- Status: open

### REL-P3-001 - No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented

- Severity: P3
- Confidence: High
- Evidence:
  - no root CHANGELOG (`git ls-files | grep -iE '(^|/)(CHANGELOG|VERSION)'` -> none)
  - drafts exist only under `docs/audits/repo-deep-dive/20260930-.../` and `20261002-.../`
  - `git log --oneline 08e20d1..f5cb7c9` -> 16 commits (Oct 9 remediation #49, reconcile #50, offsite fix #51, exec bit #52, listener alert #53, tunnel v13 #54, publication rebinds)
  - `git log --oneline e267ce1..HEAD | wc -l` -> 24 commits since the newest published full run
- What is happening: no falcon-level release notes/changelog exist for the window; changes are documented only in commit messages, decision-log entries (through 2026-10-10T02:55Z) and audit runs outside the repo.
- Why it matters: operators/auditors cannot read a consolidated user/admin/security change list.
- Recommended fix: publish a CHANGELOG + release-notes draft for the window (drafts embedded below) and wire generation from git+ledgers.
- Owner suggestion: maintainer
- Effort estimate: S (draft) / M (generator)
- Status: still-open

### REL-P3-002 - Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place

- Severity: P3
- Confidence: High
- Evidence:
  - `git tag -l` -> 0
  - no tracked `VERSION`/`CHANGELOG`
  - `docs/security/BRANCH_PROTECTION.md:59` "releases are tags on main"
  - `automation/validation/publish_digests.sh` rewrites PACKAGE_DIGEST.txt in place each bind; delivery archives are date-named (`falcon-review-delivery-YYYY-MM-DD.tar.gz`, no overwrite; newest 2026-10-04)
- What is happening: release identity is a commit SHA; the documented tag policy is not implemented; the digest file is overwritten in place (git history preserves).
- Why it matters: release identity ambiguity; the documented release process does not match reality.
- Recommended fix: adopt tags/VERSION or explicitly record the commit-SHA identity policy; align BRANCH_PROTECTION.md.
- Owner suggestion: owner
- Effort estimate: S
- Status: open

### REL-P3-003 - The delivered package embeds a closeout bound to the previous publication cycle (b09a50f) while the digest declares 3c11752; the equality gate reads the working tree only

- Severity: P3
- Confidence: High
- Evidence:
  - declared manifest at 3c11752: `closeout/FINAL_RESPONSE.json` hash 09b2c0d0...; that file at 584e1a3/3c11752 names commit `b09a50f3a8ae718902b6ea5bf388c07ea46c0838`
  - live built package `/home/user/falcon-build/review-package/closeout/FINAL_RESPONSE.json` -> 09b2c0d0... (same)
  - working tree at f5cb7c9 -> 02733f8b..., names `3c11752...`; `PACKAGE_DIGEST.txt` declares DELIVERED_PACKAGE_COMMIT=3c11752
  - `check_publication_equality.py` compares the working-tree closeout (passes); `AGENTS.md` standard flow builds the package before `generate_final_response.py`
- What is happening: the package is built before the closeout is regenerated, so the packaged closeout always names the previous publication commit; the gate cannot see it.
- Why it matters: a reviewer unpacking the package sees a closeout bound to a different commit than the digest declares.
- Recommended fix: regenerate the closeout before building the package (or rebuild the manifest after), and assert in verify_delivery.sh that the packaged closeout commit == the declared commit.
- Suggested validation: `cd review-package && grep -q "$(sed -n 's/^DELIVERED_PACKAGE_COMMIT=//p' ../PACKAGE_DIGEST.txt)" closeout/FINAL_RESPONSE.json`.
- Owner suggestion: maintainer/publication session
- Effort estimate: S
- Status: open

## Release Notes Draft (for owner edit)

> Draft generated from `git log 08e20d1..f5cb7c9` and the ledgers. No claims beyond commits/evidence. Supersedes the 20261002 draft; not a substitute for the program's own closeout.

### falcon - 2026-10-09 .. 2026-10-11 (unreleased; main @ f5cb7c9)

**Security / reliability (fixes)**
- The committed wg0 firewall narrowing (SEC-P1-002) is now applied live: per-port tunnel allows only (9443; 15140/15141; 514/1514/1515; udp 514/2055); peer SSH over the tunnel blocked; `/etc/nftables.conf` byte-identical to `config/nftables/falcon.nft` and re-applied at boot (#49, dc8ec12).
- Capacity close-out: 7 migrated Wazuh volumes retired; OpenSearch snapshot repo relocated off the data LV; disk guard watches both LVs; nightly snapshots keep the newest 3; backup retries 3x with immediate failure alert (#49).
- Pipeline: central Vector aggregator 512 MiB -> 1 GiB (OOM crash-loop ended); drop counters + two Grafana rules make silent source-side loss visible; feeds real-time (#49).
- ntfy: lab instance internal-only; the only public instance is the independent DO ntfy; DO watcher reads the heartbeat locally (#49).
- Offsite backup fix: uploader points at the real snapshot repo path (the symlink broke find-based enumeration; 2026-10-10 failure) (#51, 0246b08).
- Exec bit restored on `automation/validation/lab_stress_test.sh` (DET-P2-002) (#52, e9cdbf7).
- New alert on the Wazuh VPN proxy listeners after the 2026-10-11 reboot found them dead (#53, d70b121).
- Cloudflare tunnel ingress set to falcon/iris/enroll (live v13); remote-managed source of truth documented (#54, 584e1a3).

**Records / publication**
- Live-tree reconciliation: edge alert rules and opencanary evidence committed (#50, 95c89f4).
- Publication rebound to the current tree (declared manifest + digest; chain 0 failures) (#49-#54 sequence; 3c11752/f5cb7c9).

### Operator actions
- Re-run `bash automation/validation/verify_publication_chain.sh` before any delivery; refresh `PACKAGE_MANIFEST.sha256` in the bind flow (REL-P2-002).
- The live host now runs main @ f5cb7c9 (clean, == remote main). Record the deployed commit per deploy until releases are tagged (REL-P2-001).
- No new migration steps in this window.

### Upgrade / rollback notes
- Upgrade: `git pull` on the lab worktree, then the standard flow in `AGENTS.md` section Standard change flow; re-run `python3 ci/validate.py`.
- Rollback: `git revert <commit>` per change; runtime changes follow the PR-template rollback note. The wg0 narrowing rollback is the documented one (restore the previous `/etc/nftables.conf` and re-apply).

## Changelog Draft (for `CHANGELOG.md`)

```markdown
## [unreleased] - 2026-10-09..11 remediation + verification pass (main @ f5cb7c9)

### Fixed
- Security: wg0 narrowing applied live (per-port tunnel set; peer SSH blocked) (#49).
- Capacity: volume retirement, snapshot-repo relocation, dual-LV disk guard, keep-3 retention, backup retry+alert (#49).
- Pipeline: aggregator 1 GiB; source-drop metrics + rules (#49).
- Offsite: real snapshot-repo path for the uploader (#51).
- Port: exec bit restored on lab_stress_test.sh (DET-P2-002) (#52).
- Ops: tunnel ingress v13 restores enroll; Wazuh proxy listener alert (#53, #54).

### Changed
- Notification: lab ntfy internal-only; public ntfy is the independent DO instance (#49).
- Records: live-tree reconciliation (edge alert rules, opencanary evidence) (#50).

### Security
- WireGuard peer trust narrowed to sensor/Wazuh/syslog paths only (applied live, boot-persistent).
```

## GitHub Release Body (draft)

```
falcon lab - remediation + verification window 2026-10-09..11 (commit f5cb7c9)

Highlights
- SEC-P1-002 applied live: wg0 per-port narrowing; peer SSH blocked.
- Capacity close-out: volumes retired, snapshot repo off the data LV, dual-LV guard, keep-3 retention.
- Pipeline: 1 GiB aggregator + drop visibility; ntfy internal-only.
- Offsite uploader fix; exec bit fix; Wazuh proxy listener alert; tunnel ingress v13.

Notes
- The live host runs this commit (clean tree, == remote main). No git tags exist; identified by commit f5cb7c9.
- Known publication gaps: stale published PACKAGE_MANIFEST.sha256 and a packaged closeout bound to the previous cycle (audit REL-P2-002/REL-P3-003).
```

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Reviewer verifies against a stale published manifest | P2 | Medium | Medium | PACKAGE_MANIFEST.sha256 vs declared (8 files) | REL-P2-002 |
| Deployment identity drifts silently (mutable HEAD) | P2 | Medium | Medium | no tags/deploy manifest | REL-P2-001 + REL-P3-002 |
| Packaged closeout names the wrong commit | P3 | Medium | Low | 09b2c0d0 vs 02733f8b | REL-P3-003 |
| No consolidated notes for security changes | P3 | High | Low | no CHANGELOG | REL-P3-001 |

## Recommendations

### Immediate / Release Blocking
- None (no P0/P1 in this domain).

### This Week
- Refresh PACKAGE_MANIFEST.sha256 in the bind flow + add the manifest equality check (REL-P2-002).
- Regenerate the closeout before the package build and assert the packaged closeout commit (REL-P3-003).
- Publish the changelog/release-notes draft for 08e20d1..f5cb7c9 (REL-P3-001).

### This Month
- Record the deployed commit per deploy (REL-P2-001); adopt tags/VERSION or record the SHA policy (REL-P3-002).

### Later / Platform Evolution
- Automate release-note generation from ledgers + git in the publication flow.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `CHANGELOG.md` from the draft above | Visible release history | root | file present |
| Copy the declared manifest at each bind | Published manifest matches declared | `automation/validation/publish_digests.sh`/`verify_delivery.sh` | two manifests equal |
| Tag `main` at releases | Identity | git tags | `git tag -l` non-empty |
| Deploy-record line per deploy | Live binding | decision log / deploy manifest | record names f5cb7c9 |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Release-notes generator from git+ledgers | P3 | maintainer | M | none |
| Deploy manifest per deploy | P2 | ops | S/M | deploy flow |
| Tag/version release policy | P3 | owner | S | owner decision |
| Manifest equality + packaged-closeout checks in the gate | P2/P3 | maintainer | S | publication flow |

## Suggested Tests

- CI: `PACKAGE_MANIFEST.sha256` == `review-package/MANIFEST.sha256` after a bind (new).
- CI: packaged `closeout/FINAL_RESPONSE.json` commit == `DELIVERED_PACKAGE_COMMIT` (new).
- Regression: manifest entries resolve to present artifacts (exists via `check_digest_binding.py`/`verify_publication_chain.sh`).
- Test: release-note generator output diffed against `git log` (no invented items).

## Suggested Documentation Updates

- Root `CHANGELOG.md` + `release_notes_draft.md` per run.
- `docs/security/BRANCH_PROTECTION.md` section release process - align the tag claim with reality.
- `docs/RELEASE_GATE.md` - current audit opinion (cross-ref HYGIENE-P2-002).
- `AGENTS.md` standard flow - add the manifest-refresh + closeout-order steps (cross-ref HYGIENE-P2-003).

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is PACKAGE_MANIFEST.sha256 still needed, or is the declared manifest enough? | Determines fix (refresh vs retire) | Owner/maintainer answer |
| Are tags intended, or is commit-SHA identity the accepted policy? | Versioning approach | Owner decision |
| Was verify_delivery intentionally skipped for the 2026-10-10/11 rebinds? | Whether archives should exist per bind | Publication-session answer |

## Prior-Run Comparison

- `REL-P2-001` (deployment not bound to a release): prior open -> **open**; the divergence/uncommitted-config leg is **verified-fixed** (live tree clean at f5cb7c9 == remote main, 2026-10-11); the residual is release identity (no tags/deploy manifest).
- `REL-P3-001` (no CHANGELOG/generator): prior still-open -> **still-open**; the undocumented window has grown (16 commits in 08e20d1..f5cb7c9; 24 since the newest in-repo full run).
- `REL-P3-002` (no tags/VERSION): prior open -> **open** (0 tags; no VERSION).
- New this run: REL-P2-002 (stale published manifest) and REL-P3-003 (packaged closeout lag).
- Strengths vs prior: digest rebound to 3c11752 (was 69b3c80, 11 commits behind), chain/equality PASS, live deployment matches HEAD.

## Limitations

- Companion drafts are generated from commits/ledgers only; the owner edits them before merge.
- No tags exist, so no tag-diff was possible; the window since the prior audit was used instead.
- GitHub main was verified via the read-only API (the live host has no GitHub credentials); the audit clone's origin ref was stale but the API confirmed f5cb7c9.

## Findings

| ID | Severity | Title |
|---|---|---|
| REL-P2-001 | P2 | Deployment state is not bound to any release: no tags/VERSION and no deploy manifest; the live tree is now clean at main HEAD |
| REL-P2-002 | P2 | Published PACKAGE_MANIFEST.sha256 is stale: it disagrees with the declared review-package manifest on 8 files and no gate compares them |
| REL-P3-001 | P3 | No root CHANGELOG/release-notes generator; the 2026-10-04..11 window is undocumented |
| REL-P3-002 | P3 | Releases are not versioned: no tags, no VERSION file; binding artifacts overwrite in place |
| REL-P3-003 | P3 | The delivered package embeds a closeout bound to the previous publication cycle (b09a50f) while the digest declares 3c11752; the equality gate reads the working tree only |
