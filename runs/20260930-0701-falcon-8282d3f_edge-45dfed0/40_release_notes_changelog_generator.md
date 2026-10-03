# Release Notes and Changelog Generator

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `20260930-0701-falcon-8282d3f_edge-45dfed0` (full-domain, synthesis pass)
- Repositories: `falcon-build` @ `8282d3f` (main, clean at run start) · `falcon-edge-build` @ `45dfed0` (main, dirty — in-flight CI work)
- Prior run: `20260930-0320-falcon-794ba31_edge-2b5bc8b` (90 findings; statuses verified by domain agents at the current commits)
- Generated at: 2026-09-30 (synthesis pass, prompt 40)
- Auditor: synthesis subagent (release-notes/changelog generator)
- Area code: `REL`
- Output path: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/40_release_notes_changelog_generator.md`
- Scope limitations: read-only; no release was cut and no ledger/gate/ledger state was changed. No changelog exists in either repo, so entries below are derived from git history, diffs versus the prior run, and the domain reports' reproduced evidence. Secret-like values are referenced by path/type only.

## Scope

Reviewed: git history of both repos since the prior run (`794ba31..8282d3f`, `2b5bc8b..45dfed0`); presence/absence of changelog, release-note, version and PR templates; release-artifact naming and digest chains in `/home/user/falcon-edge-delivery/`; central package binding; migration/rollback evidence; and the 256 current findings for release-note material. Not reviewed: GitHub-side release/tag UI state, CI run logs outside the repos, root-only backup logs, and branch protection (prompts 34/10).

## Evidence Reviewed

- `git log --oneline 794ba31..8282d3f` (falcon) and `2b5bc8b..45dfed0` (edge); `git tag` (edge: `lab-2026.09.30-lab8`; falcon: none).
- Absence checks: no `CHANGELOG*`, `VERSION*`, `RELEASE*`, `.github/PULL_REQUEST_TEMPLATE*`, or `CODEOWNERS` in either repo.
- `PACKAGE_DIGEST.txt` (falcon): binds `repository_commit=3ac6cd4…`, 2 067 review-package entries, `program_verdict=APPROVED (controlled verdict 2026-09-29)`.
- `/home/user/falcon-edge-delivery/`: versioned image/review-package filenames (lab5–lab8), `falcon-edge-release-manifest-20260930.json` + `.sha256` sidecar, secrets backups (names redacted).
- Domain reports `01`,`03`,`09`,`10`,`11`,`13`,`16`,`32`,`34`,`35`,`41`–`43` and the five lenses (findings, prior-status tables, reproduction results).

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log` both repos since prior SHAs | command | Proves which changes are real/attributable | `supported` — `93ea9c6`, `1f76aca`, `d83f421`, `6f33a06`, `824f701` etc. exist in history |
| `find`/`ls` for changelog/version/PR templates | command | Proves the generator inputs are absent | `supported` — absent in both repos; drafts in this run are the first |
| `head PACKAGE_DIGEST.txt` | command | Version/commit binding of the central package | `supported` — binds `3ac6cd4`; HEAD is `8282d3f` (publication commits only) |
| Delivery directory listing | command | Release filenames versioned vs overwritten | `supported` — image/review filenames versioned; signed manifest rewritten in place (XREPO-P1-001) |
| Edge manifest sidecar check (report 35/42) | reproduced there | Digest chain integrity | `unsupported` — `sha256sum -c` FAILs (stale `18681751…` vs actual `3fa4a49c…`) |
| `git tag` | command | Release/tag hygiene | `supported` — one edge tag (`lab-2026.09.30-lab8`); falcon none |
| Prior-run status tables in reports + lenses | report cross-check | What changed since the prior run | `supported` — 90/90 accounted: fixed 1 · partial 31 · still-open 53 · regressed 2 · not re-assessed 3 |

## Executive Summary

Neither repository has a changelog, a release-notes template, a version file, a PR template, or a CODEOWNERS file; releases are shipped as versioned image and review-package filenames plus a signed manifest. Since the prior run, real fixes landed: ledger-derived package digest, `set -e` backup/offsite repair (offsite succeeded 09-30 07:43Z), WireGuard peer preservation, EVE/stats rotation and disk-guard pruning, a 6 h TLS alert window, a full 31-rule alert catalogue, falcon CI + secret-scan pin fixes, edge CI (ruff/gitleaks/zizmor/3.13 matrix/weekly drift), the phase-10 consistency fix, and the P9-G04 hard-reset PASS. None of these were published as release notes, and the audit found release-binding defects that block a truthful release note today: the approval chain binds a superseded package (EVID-P0-001), the edge manifest sidecar does not match the signed manifest (FLEET-P1-001/SBOM-P2-001), the published verdict contradicts its own body and the digest at HEAD (REV-P1-002/EVID-P1-002), and credentials still ship in repo/package/delivery (API-P0-001/EVID-P1-004). Recommended next: keep these drafts as working release notes, cut notes only after the P0 binds are repaired, and add `CHANGELOG.md` + `VERSION`/tag conventions to both repos.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Central changelog / release-notes template | — (absent) | User/operator change history | Absent | Medium | This run's drafts are the first |
| PR template / CODEOWNERS | `.github/` | Review governance | Absent | Medium | BP-P2-002 |
| Version file | — (absent) | Single version read | Absent | Medium | Versions live in image filenames + tag |
| Central package digest | `PACKAGE_DIGEST.txt` | Commit/version binding | Binds `3ac6cd4`; derived verdict APPROVED | High | EVID-P0-001/INV-P0-002 |
| Central verdict | `docs/phase9/review/PRODUCTION_VERDICT.md` | Readiness statement | Contradicts itself (line 31 "NOT_SUPPORTED") | High | REV-P1-002, DOC-P2-004 |
| Edge release tag | `lab-2026.09.30-lab8` | Edge release ID | One tag only | Low | Reports 35/43 |
| Edge manifest | `falcon-edge-release-manifest-20260930.json` + sidecar | Signed artifact list | Signature valid; sidecar stale; rewritten in place | High | FLEET-P1-001, XREPO-P1-001 |
| Image/SBOM artifacts | `falcon-edge-sensor-2026.09.29-lab{5..8}*`, `*-sbom.cdx.json` | Versioned deliverables | lab5 live vs lab8 released; no release reproduces the live unit | High | FLEET-P2-003 |
| Migrations | — (none) | Schema evolution | No central migration mechanism; edge SQLite unmigrated | Medium | EVOL-P2-003, DR-P2-002 |
| Rollback notes | runbooks/commit messages | Safe revert | Partial; edge rootfs rollback absent | High | FLEET-P1-002 |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Git history | 4 | Conventional commits, evidence per change, clean linear history | No tags/changelog on falcon; `8282d3f` publication-only | Add tags + CHANGELOG |
| PR templates | 1 | `.github/` only dependabot + workflows | No PR template/CODEOWNERS | Add both; require review |
| Changelog/release notes templates | 1 | None in either repo | No release-note format | Adopt the drafts + Keep-a-Changelog |
| Version files | 2 | Edge tag + image naming; falcon digest binds commits | No `VERSION`; live vs released skew | Add VERSION + release tags |
| Package versions | 3 | lab5–lab8 filenames + per-lab SBOMs | Sidecar stale; live lab5 not reproduced | Rebuild manifest+sidecar atomically |
| Migrations | 2 | ISM retention script only | No schema migrations; edge SQLite unmigrated | Define migration policy |
| API/UI/security/bug/dependency/infra/docs changes | 2 | All changes evidence-captured | Release notes absent; docs drift | Generate notes from evidence |
| Breaking changes | 2 | None declared | Contract drift (16 vs 19 routes); no deprecation policy | Parity test + policy |
| Known issues | 3 | Risk/contradiction registers exist | Stale/unreconciled with closure | Reconcile registers |
| Operator actions | 3 | `OWNER_ACTIONS.md` in both repos | Stale items; missing secrets map | Refresh + link from notes |
| Migration steps | 1 | Only ISM retention | No index-rename/rollback drill | Write + rehearse |
| Rollback notes | 2 | Rollback notes on mutating changes | Edge OS/rootfs rollback does not exist | Add A/B per AB_STRATEGY |

## Detailed Review

### Item: Git history as release material

- Evidence: `git log 794ba31..8282d3f` (falcon), `2b5bc8b..45dfed0` (edge); commits `93ea9c6`, `1f76aca`, `d83f421`, `c5755f5`/`f1db6d8`, `6f33a06`, edge `824f701`, `f0996b8`, `45dfed0`, `96c3e08`, `4332503`/`d6147ef`.
- What it does: small, conventional-commit-labelled changes, each with evidence captures; append-only doctrine.
- Missing controls / risks: no changelog/tags on falcon; no user/admin/operator/security separation; operators learn about fixes only from the audit (EVID-P1-003).
- Recommended improvement / tests / docs: generate `CHANGELOG.md` from the commit stream in the `changelog_draft.md` categories; CI check that every non-publication commit since the last tag has an entry; release-process section in `REPOSITORY.md`.

### Item: Release binding and artifact set

- Evidence: `PACKAGE_DIGEST.txt` binds `3ac6cd4`; `FINAL_RESPONSE.json` contradicts it (EVID-P1-002); edge sidecar `18681751…` vs manifest `3fa4a49c…` (report 35); review package `0b83acc` precedes release `155f244` (report 11).
- Current controls / gaps: signed edge manifest and central digest exist, but there is no atomic manifest+sidecar rebuild, no single verdict source, and no published public key.
- Risks / improvement / tests / docs: unverifiable release claims and an approval that does not cover the shipped tree (EVID-P0-001, XREPO-P0-001); one `release bind` script regenerating manifest, sidecar, verdict, digest and archive in one commit; `sha256sum -c` and digest↔verdict↔archive equality tests; release runbook (partly in `AGENTS.md`).

### Item: Versioning, migrations, known issues and operator actions

- Evidence: no `VERSION`; versions only in image filenames/tag; edge SQLite has no migration mechanism (EVOL-P2-003); retention is ISM-only; no index-rename rollback drill (DR-P2-002); risk/contradiction registers stale (HYGIENE-P2-003, EVID-P2-003); owner decisions D1–D8 open.
- Missing controls / risks: no migration/rollback template; fleet upgrades without a rollback story (FLEET-P1-002); operators repeat stale steps (INFRA-P1-001).
- Recommended improvement / tests / docs: `VERSION` + release tags; migrations index with rollback notes; release-time known-issues block and a publish checklist that blocks on open P0 binds; rollback rehearsal per release; `docs/RELEASING.md`, `docs/MIGRATIONS.md`, `docs/CURRENT_STATE.md` (DOC-P1-001/002).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| REL-001 | Git history | commit stream | Conventional commits + evidence | No changelog/tags | P2 | Generate changelog from history |
| REL-002 | PR templates | `.github/` | None | No template/CODEOWNERS | P2 | Add both (BP-P2-002) |
| REL-003 | Changelog/release-notes template | this run's drafts | None | No format | P2 | Adopt drafts |
| REL-004 | Version files | tag/digest | Edge tag + digest commits | No `VERSION` | P2 | Add VERSION |
| REL-005 | Package versions | delivery listing | Versioned filenames + SBOM | Live≠released; sidecar stale | P1 | Atomic rebind |
| REL-006 | Migrations | ISM only | ISM retention | No migration mechanism | P2 | Migration policy |
| REL-007 | API/UI/security/bug/dependency/infra/docs changes | reports 06–16, 30–44 | Evidence-captured | Notes absent | P2 | Publish notes |
| REL-008 | Breaking changes | contract 16 vs 19 routes | None declared | Contract drift | P2 | Parity test + policy |
| REL-009 | Known issues | registers | Risk/contradiction registers | Stale | P2 | Reconcile at release |
| REL-010 | Operator actions | OWNER_ACTIONS | Checklist exists | Stale/missing secrets map | P1 | Refresh + link |
| REL-011 | Migration steps | runbooks | Retention script | No step template | P2 | Add template |
| REL-012 | Rollback notes | AB_STRATEGY | Notes on mutating changes | No edge rootfs rollback | P1 | Implement/accept |

## Findings

**No new `REL`-prefixed findings are registered by this synthesis pass.** The release-notes/changelog capability gaps are already carried by registered findings, and the machine-readable aggregate must stay single-source. The existing findings that constitute REL-domain evidence are:

| Symptom | Registered finding(s) |
|---|---|
| Approval/digest bind the wrong package | EVID-P0-001, INV-P0-002, REV-P0-001, XREPO-P0-001 |
| Manifest sidecar/rewrite-in-place; verdict contradictions | FLEET-P1-001, XREPO-P1-001, SBOM-P2-001, EVID-P1-002, DOC-P2-004, FEAT-P1-002, REV-P1-002 |
| No changelog/version/PR process; status docs drift | BP-P2-002, BP-P3-001/002, CI-P3-001, HYGIENE-P2-003, EVID-P1-003, DOC-P1-001/002/003, FEAT-P1-001, HYGIENE-P2-004 |
| No migration/rollback path | EVOL-P2-003, DR-P2-002, FLEET-P1-002, XREPO-P2-003 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Public release notes overclaim | High | High | Trust loss | EVID-P0-001, REV-P0-001 | Publish only after rebind; template blocks |
| Operators miss safety-critical changes | Medium | High | Recurrence | HYGIENE-P2-003 | Changelog + known-issues block |
| Upgrade without rollback / version skew | High | Medium | Fleet outage, broken pairing | FLEET-P1-002, XREPO-P1-004 | A/B rollback; pin verify + skew alert |
| Secret in release archive | High | Certain | Compromise | API-P0-001, SECRET-P1-003 | Rotate, remove, rescan |

## Recommendations

### Immediate / Release Blocking

- Do not publish notes claiming verification until EVID-P0-001/INV-P0-002 are rebound and the FLEET-P1-001 sidecar is rebuilt.
- Rotate/remove the committed Wazuh credential set and rescan (API-P0-001/EVID-P1-004); freeze release artifacts.

### This Week

- Publish this draft internally; keep the known-issues block.
- Add `CHANGELOG.md` + `VERSION` + release tags; CI check tag↔digest-bind commit.
- Refresh `OWNER_ACTIONS.md` and link operator actions from the notes.

### This Month

- Release process doc with user/admin/operator/security sections, upgrade/rollback and migration steps.
- Reconcile risk/contradiction registers; generate the known-issues block automatically.
- Implement/accept edge OS rollback and rehearse once.

**Later / Platform Evolution:** versioned shared tooling package (EVOL-P2-002); provenance attestations (SBOM-P2-004); single verdict source (REV-P1-002).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `CHANGELOG.md` with this run's entries | First real change history | `CHANGELOG.md` (both repos) | Renders; entries match commits |
| Add `VERSION` + tag on falcon | Version lookup | `VERSION`, git tag | Tag resolves; digest binds tag commit |
| Publish known-issues block + link OWNER_ACTIONS | Honest release, no lost actions | notes, `OWNER_ACTIONS.md` | Matches findings.json; links resolve |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Atomic release-rebind script (manifest+sidecar+digest+verdict) | P0 | falcon/edge maintainers | M | EVID-P0-001 |
| CHANGELOG/VERSION/tag conventions + CI check | P2 | both maintainers | S/M | none |
| Release process + migration/rollback templates; doc-drift check | P2 | both maintainers | M | FLEET-P1-002, HYGIENE-P2-003 |
| Public key publication in delivery | P1 | edge maintainer | S | SBOM-P2-004 |

## Suggested Tests

- CI: every non-publication commit since the last tag is represented in `CHANGELOG.md`; tag↔`PACKAGE_DIGEST.txt` commit equality; manifest sidecar `sha256sum -c` PASS on the shipped set.
- Release E2E: dry-run that builds notes from `findings.json` + commit log and blocks on any open P0 bind; secret scan over release archives incl. XML-tag credential forms.
- Manual/regression: rollback rehearsal of one edge release per cycle; ISM delete/restore drill.

## Suggested Documentation Updates

- New: `CHANGELOG.md`, `VERSION`, `docs/RELEASING.md`, `docs/MIGRATIONS.md`, `docs/CURRENT_STATE.md` (both repos).
- Update: `REPOSITORY.md` (release process), `AGENTS.md` (release sequence), `README.md` (version), edge `docs/GITHUB_CI.md` (cadence), `closeout/OWNER_ACTIONS.md`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Who owns release cutting, rebind, and is the falcon package semver-versioned or commit-bound? | Notes need an accountable publisher and a meaningful `VERSION` | Owner/maintainer decision record |
| Should notes be generated in CI and published to GitHub Releases; is the lab5→lab8 skew acceptable? | Automation scope and supported version statement | Owner/maintainer decision; FLEET-P2-003 resolution |

## Appendix

### Suggested release-note structure (adopted by `release_notes_draft.md`)

Header (audit ID, commits, date) → audit outcome counts → verified fixes since the prior run (commit-cited) → new findings by severity (P0 highlighted) → **separate** user / admin-operator / security notes → upgrade, rollback and migration steps → known issues + owner decisions (D1–D8) → verification performed and artifact binding → redaction statement.

### Prior-run delta used in the drafts

- Statuses: verified-fixed 1 · partially-fixed 31 · still-open 53 · regressed 2 · not re-assessed 3 (of 90); fixes cited in `changelog_draft.md` with SHAs.
- Redactions: no secret values printed; `.env`/delivery/secret-store references are path/type only.
