# 01_repository_inventory — Prompt 01 - Comprehensive Repository Inventory

- Run: `falcon-20261011-0416-full-f5cb7c9`
- Target: `falcon` @ `f5cb7c9` (branch `main`)
- Domain: `01_repository_inventory.md` (area INV, prompt)

## Verification Performed

## Audit Metadata

- Audit name: repo-deep-dive (falcon)
- Run: `falcon-20261011-0416-full-f5cb7c9`
- Repository: `MaineCyberTech/falcon` @ `f5cb7c96cacefb2e8b1dedc1f15e633d9072264b` (branch `main`)
- Generated at: 2026-10-11T04:45Z
- Auditor: repo-deep-dive full-pass subagent (INV)
- Area code: INV
- Output path: `docs/audits/repo-deep-dive/falcon-20261011-0416-full-f5cb7c9/01_repository_inventory.md` (intended)
- Scope limitations: repository tree only (read-only); the vendored `mct/` upstream was not consulted; no pack rebuild was attempted (repomix toolchain not exercised).

## Scope

Every tracked top-level tree was inventoried: root configs, `.github/`, `bootstrap/`, `ci/`, `closeout/`, `compose/`, `config/`, `automation/`, `mct/`, `pins/`, `docs/`, `ledgers/`, `evidence/`, `sbom/`, `review-package/`, `PACKAGE_*`, plus environment examples and generated artifacts. Application frameworks (node/python packages, migrations, routes) are absent by design (ops repository). Not reviewed: the correctness of individual evidence captures (sampled only); the `mct/` upstream; the off-repo delivery archive (not present on this host).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git ls-files` | command | tracked tree + ownership | 3,883 files; worktree clean at `f5cb7c9` |
| Top-level counts | command | composition | evidence 2,283 files / 14 MB; sbom 39 / 29 MB; docs 344 / 4.3 MB; mct 858 / 4.1 MB; automation 206; config 71 |
| `README.md`, `REPOSITORY.md`, `AGENTS.md` | docs | conventions, source-vs-generated map | regeneration commands documented |
| `ci/validate.py` (checks incl. parsers, compose pins, shell syntax, credential sourcing, gate ledger, generated drift, sbom hashes, evidence index, digest binding, publication equality) | source | the repo gate | all read-only runs |
| `automation/validation/check_generated_drift.py` | source | evidence-tree binding | `DEFAULT_MANIFESTS = ("evidence/MANIFEST.sha256",)`; docstring says review-package manifest intentionally not in the default set |
| `automation/validation/sbom_hashes.sh`, `check_evidence_index.py`, `check_digest_binding.py`, `check_publication_equality.py`, `verify_publication_chain.sh` | source | artifact binding | semantics inspected |
| `ledgers/evidence_index.csv`, `evidence/MANIFEST.sha256`, `evidence/raw/**/*.meta.json` | artifacts | evidence tree + paths | 1,134 metas; 264 legacy rows |
| `sbom/`, `PACKAGE_*.txt`, `closeout/FINAL_RESPONSE.json`, `review-package/MANIFEST.sha256` | artifacts | generated/delivery set | digest binds `3c11752`; review-package manifest tracked |
| `docs/audits/repo-deep-dive/` (6 runs) | artifacts | durable run records | structural check passes; content unbound |
| `mct/VENDORING.md`, `mct/REPO-MAP.md` | docs | vendored subtree policy | archive-only; P4 not implemented |
| `.env.example`, `config/**/*.example*`, `mct/config/examples/secrets.example.env` | config | environment samples | placeholders only |
| `docs/security/RELEASE_PACK_VERIFICATION.md` | doc | pack/delivery verification model | documents the stale-pack class (SC-P2-002) |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py --fast` | command | repo gate smoke | `validation_failures=0` (parsers, compose pins, shell syntax 322 scripts, credential sourcing, gate ledger 102) |
| `python3 automation/validation/check_generated_drift.py --root .` | command | evidence tree binding | `PASS generated_drift (2268 entries match their committed manifests)` |
| `bash automation/validation/sbom_hashes.sh verify` | command | SBOM set binding | `PASS (38 artifacts verified, manifest unsigned)` |
| `python3 automation/validation/check_evidence_index.py --root .` | command | evidence index | `PASS (1134 metas, 1134 rows, 870 host-absolute resolved, 264 legacy skipped)` |
| `python3 automation/validation/check_digest_binding.py --root .` | command | delivery binding | `PASS`; binds evidence + review-package manifest hashes; commit only checked with `git cat-file -e` (resolvability) |
| `python3 automation/validation/check_publication_equality.py --root .` | command | digest<->closeout<->manifest binding | `PASS`; enforces declared commit = HEAD/ancestor and publication-only commits after it |
| `bash automation/validation/audit_run_lifecycle.sh check` | command | run folders | 6 runs, `check_failures=0` |
| `sha256sum review-package/MANIFEST.sha256` vs `PACKAGE_DIGEST.txt` | command | declared-vs-actual | equal (`749dae85...`); 3,830 entries |
| `diff PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` | command | internal delivery consistency | 8 entries differ |
| `git show <rev>:<file> \| sha256sum` vs `PACKAGE_MANIFEST.sha256` | command | staleness attribution | PACKAGE_MANIFEST hashes equal the files at `75c3466`/abb63ab-era, not at HEAD |
| `git rev-list --count 3c11752..HEAD` | command | digest staleness | 1 (the publication commit itself; publication-only by design) |
| GitHub API `GET /actions/runs?head_sha=f5cb7c9` | command | gate status at the audited commit | `validate` run completed **success** (2026-10-11T04:04:18Z) |

## Executive Summary

Falcon remains a single ops repository with no package manifests, lockfiles, app routes or migrations; the majority of files and bytes are generated evidence and SBOM payloads (evidence 2,283 files / 14 MB + sbom 39 / 29 MB = ~60% of files, ~77% of bytes). The two largest generated trees are bound to committed manifests and verified every gate run, and the publication chain (digest ↔ closeout ↔ review-package manifest ↔ evidence manifest) now passes and is CI-green at the audited commit. Two delivery-integrity regressions appeared since the prior full run, both in the publication artifacts: (1) `PACKAGE_MANIFEST.sha256` — the published copy of the package manifest — is two publication cycles stale (last refreshed at `75c3466`) and now disagrees with the shipped `review-package/MANIFEST.sha256` on 8 entries, and no check binds it; (2) the repository's documented HYG-P1-001 doctrine ("review-package is generated, gitignored, must not be committed") is contradicted by the tracked `review-package/MANIFEST.sha256` that the last three publication cycles commit. Residual prior gaps: the `docs/audits/` records and `mct/` have no content/drift binding, 264 legacy evidence-index rows still need the resolver, and two pack-fidelity entries still ship as "unexpected; investigate". The prior INV-P3-003 concern ("a stale digest fails" not implemented; digest 11 commits old) is resolved in substance: the digest binds its own declared commit, and `check_publication_equality.py` fails a digest with non-publication commits after it (proven by the CI-P2-004 red→rebind cycle); only the digest-binding docstring still mis-describes its own scope.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Root conventions | `README.md`, `AGENTS.md`, `REPOSITORY.md` | doctrine, layout, evidence rules | current | low | source |
| Root configs | `.gitattributes`, `.gitignore`, `.gitleaks.toml`, `.env.example` | line endings, ignores, secret scan, env sample | current | low | placeholders only |
| CI metadata | `.github/` (3 workflows, CODEOWNERS, dependabot) | validate/smoke/dependabot | active | low | workflows pinned by SHA |
| Host bootstrap | `bootstrap/` (30 scripts) | host prep, firewall, secrets, deploy, timers | active | medium (runtime-mutating) | idempotent per docs |
| Static gate | `ci/` (validate.py, license_check.py, requirements) | repo gate | active, fast set passing | low | full set includes live-dependent checks |
| Compose | `compose/central`, `compose/probe`, `compose/mct` (7 files) | deployment sources | active | low | digest-pinned via `pins/images.lock` |
| Config templates | `config/` (71 files) | nftables, docker, prometheus, grafana, suricata, vector, traefik, systemd, ntfy, wireguard, rsyslog | active | medium | rendered with secrets on deploy |
| Automation | `automation/` (206 files) | evidence capture, validation, alerting, vpn, wazuh | active | medium | offline suites run in CI |
| Vendored MCT | `mct/` (858 files) | imported SOC stack snapshot | archive-only (policy) | medium | no upstream commit; P4 drift check unimplemented |
| Docs | `docs/` (344 files) | phases, runbooks, audits, architecture, security | mixed source/generated | low | audits are generated records |
| Ledgers | `ledgers/` (11 files) | gates, tests, evidence index, risk/exceptions/decisions | append-only, checked | low | 102+14 gates |
| Evidence | `evidence/` (2,283 files, 14 MB) | raw captures + manifest | drift-bound (PASS) | low | 264 legacy paths |
| SBOM | `sbom/` (39 files, 29 MB) | SBOM + vuln JSON | hash-bound (PASS, unsigned) | medium | large committed payloads (HYGIENE-P2-001) |
| Pins | `pins/` (5 files) | 24-image lock + waivers + scripts | active | medium | blanket `mct/compose` waiver |
| Closeout | `closeout/` (4 files) | final response records | digest-bound to `3c11752` | low | publication-only commit after it |
| Delivery artifacts | `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `PACK_*.txt` | publication binding | digest+equality PASS; `PACKAGE_MANIFEST` stale (8 entries) | medium | INV-P3-004 |
| Review-package manifest | `review-package/MANIFEST.sha256` (tracked, 3,830 entries) | shipped package manifest | bound by digest/closeout | medium | doctrine contradiction (INV-P3-005) |
| Audit records | `docs/audits/repo-deep-dive/` (6 runs, 205 files) | durable audit records | structural check PASS | medium | no content binding; 20261005 record divergence (ORCH-P2-001) |

### Sensitive inventory

| Item | Type | State | Notes |
|---|---|---|---|
| `.env.example` | env sample | placeholders only | never contains real values |
| `/home/user/.env` (host, outside repo) | owner credentials | not in repo | referenced by name only |
| `/srv/falcon/secrets/*` (host) | service secrets | not in repo | root-only per doctrine |
| `mct/config/examples/secrets.example.env` | env sample | tracked, placeholder | still excluded from the repomix pack (INV-P3-002) |
| `*.pem|*.key|*.crt|*.p12|*.pfx|*.age|*.gpg` | patterns | gitignored | no such files tracked |

### Generated / stale artifact table

| Artifact | Regenerated by | Binding at `f5cb7c9` | Staleness |
|---|---|---|---|
| `evidence/MANIFEST.sha256` | `automation/evidence/manifest.sh create` | `generated-drift` PASS (2,268 entries) | current |
| `sbom/SBOM_MANIFEST.sha256` | `automation/validation/sbom_hashes.sh create` | `sbom-hashes` PASS (38 artifacts, unsigned) | current |
| `ledgers/evidence_index.csv` | `automation/evidence/index.sh` | `evidence-index` PASS (1,134/1,134) | current |
| `review-package/MANIFEST.sha256` | `build_review_package.sh` (committed by the publication flow) | digest + publication-equality PASS | current vs tree; doctrine contradiction |
| `PACKAGE_MANIFEST.sha256` | `verify_delivery.sh` (copy of the review-package manifest) | **none** | stale: last refreshed at `75c3466`; 8 entries differ |
| `PACKAGE_DIGEST.txt` / `closeout/FINAL_RESPONSE*.json` | `publish_digests.sh` + `generate_final_response.py` | digest-binding + publication-equality PASS | binds `3c11752`; publication commit `f5cb7c9` is publication-only |
| `PACK_VERIFICATION_NOTES.txt` / `PACK_NOT_INCLUDED.txt` | `pack_fidelity.py` (pack rebuild) | none | last rebuilt at `df934e5`; 2 unresolved entries |
| `docs/audits/repo-deep-dive/*` | audit runs | structural check only | no content binding |
| `mct/` | manual import | none | no import manifest (P4 proposed) |

## Findings

### INV-P2-001 - Repository is majority generated/derived content; the largest trees are now bound but audit records and `mct/` remain unbound (partially fixed)

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `git ls-files` -> 3,883 files; `evidence/` 2,283 files / 14 MB + `sbom/` 39 files / 29 MB = ~60% of files, ~77% of the ~56 MB tree
  - `python3 automation/validation/check_generated_drift.py --root .` -> `PASS (2268 entries)`; `bash automation/validation/sbom_hashes.sh verify` -> `PASS (38 artifacts)`
  - `automation/validation/check_generated_drift.py:37` — `DEFAULT_MANIFESTS = ("evidence/MANIFEST.sha256",)`; docstring: the review-package manifest is intentionally not in the default set
  - Residual unbound trees: `docs/audits/` (structural validation only, `automation/validation/audit_run_lifecycle.sh`) and `mct/` (`mct/VENDORING.md`, P4 proposed, not implemented)
  - `review-package/MANIFEST.sha256` is now committed (3,830 entries) but is not drift-bound by any check
- What is happening: the original risk (a stale or hand-edited generated artifact silently contradicting its source) is closed for evidence and SBOM, and the delivered package manifest is bound by the digest; the committed audit records, the `mct/` subtree, and the published `PACKAGE_MANIFEST.sha256` copy remain unbound.
- Why it matters: reviewer trust in generated records still depends on manual checks; the unbound copy produced INV-P3-004.
- User / business impact: review friction; possible hidden content drift.
- Security / privacy / reliability impact: low; integrity risk in generated records.
- Recommended fix: add a lightweight binding for committed run folders and the `mct/` import (P4), and bind `PACKAGE_MANIFEST.sha256` to the review-package manifest (INV-P3-004).
- Suggested validation: `ci/validate.py` fails when a committed run folder, `mct/` file, or `PACKAGE_MANIFEST.sha256` is edited without rebinding.
- Owner suggestion: repo maintainer.
- Effort estimate: M.
- Dependencies: none.
- Status: partially-fixed.

### INV-P3-001 - Legacy host-absolute evidence paths require the resolver to resolve in a clone (partially fixed)

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `python3 automation/validation/check_evidence_index.py --root .` -> `PASS (1134 metas, 1134 rows, 870 host-absolute resolved, 264 legacy skipped)`
  - `ledgers/evidence_index.csv` — 264 rows still `../monitoring-build/evidence/...`; 1,134 rows repo-relative
  - `evidence/raw/**/*.meta.json` — 870 `raw_artifact` fields record `/home/user/falcon-build/...` absolute paths
  - `automation/validation/resolve_evidence_path.py` + `automation/validation/tests/resolve_evidence_path_test.sh` exist
  - `REPOSITORY.md` documents the mapping
- What is happening: recorded paths still do not resolve by themselves in a fresh clone; the resolver maps both forms and verifies existence, but every consumer must know to run it (the index check skips legacy rows rather than resolving them).
- Why it matters: off-host review requires an extra step; a script that opens recorded paths directly fails.
- User / business impact: friction for reviewers.
- Security / privacy / reliability impact: none directly.
- Recommended fix: keep the legacy rows (history) but teach the evidence tooling to resolve recorded paths centrally, or emit resolved paths in new meta records.
- Suggested validation: extend `resolve_evidence_path_test.sh` with a random sample of legacy rows; make `check_evidence_index.py` resolve-then-check.
- Owner suggestion: repo maintainer.
- Effort estimate: S.
- Dependencies: none.
- Status: partially-fixed (unchanged).
- Endpoint / data path: `ledgers/evidence_index.csv` -> reviewer tooling.
- Attack path: none identified.

### INV-P3-002 - Delivery pack fidelity artifact ships two unresolved "unexpected; investigate" entries

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `PACK_NOT_INCLUDED.txt:4-5` — `evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out` and `mct/config/examples/secrets.example.env` marked `not-in-pack (unexpected; investigate)`
  - both files exist in the tracked tree (`ls -la` -> 196 B and 724 B)
  - `automation/validation/pack_fidelity.py` writes that disposition when a manifest entry is absent from the repomix pack
  - `PACK_NOT_INCLUDED.txt` last changed at `df934e5`; no newer disposition anywhere (`grep -rn "unexpected; investigate"` -> only this file)
- What is happening: the published `PACK_NOT_INCLUDED.txt` advertises two unexplained absences from the review pack and no disposition was ever recorded.
- Why it matters: a reviewer cannot tell whether the omissions are benign tool behavior or missing content; the artifact says "investigate" indefinitely.
- User / business impact: review friction; possible hidden content gap in the delivered pack.
- Security / privacy / reliability impact: low; integrity/trust.
- Recommended fix: reproduce the pack build, determine the cause (likely repomix built-in secret-file heuristics — verify, do not assume), then record the reason or adjust the fidelity classification; regenerate `PACK_NOT_INCLUDED.txt`.
- Suggested validation: rebuild the pack and confirm every `not-in-pack` row has a stated reason.
- Owner suggestion: release owner.
- Effort estimate: S.
- Dependencies: repomix toolchain.
- Status: still-open.
- Endpoint / data path: pack build -> `PACK_NOT_INCLUDED.txt` -> reviewer.
- Attack path: none identified.

### INV-P3-003 - "A stale digest fails" is enforced by publication equality, not by the digest-binding check whose docstring claims it (residual)

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `ci/validate.py:489-497` — digest-binding docstring: "A stale digest therefore fails here instead of being mistaken for current"
  - `automation/validation/check_digest_binding.py:80-88` — only manifest-hash equality and `git cat-file -e <commit>^{commit}` (resolvability); no freshness/HEAD rule
  - `automation/validation/check_publication_equality.py:168-193` — declared commit must be HEAD or an ancestor; every commit after it must touch only `PUB_ARTIFACTS` (`^PACKAGE_DIGEST\.txt|PACKAGE_MANIFEST\.sha256|PACK_VERIFICATION_NOTES\.txt|PACK_NOT_INCLUDED\.txt|closeout/FINAL_RESPONSE.*\.json|ci/validate\.py|...tests/.*$`)
  - `PACKAGE_DIGEST.txt:2` — `repository_commit=3c11752`; `git rev-list --count 3c11752..HEAD` -> 1 (the publication commit `f5cb7c9`, which touches only digest/closeout files)
  - CI `validate` run at `f5cb7c9` -> success; the gate went red for exactly this reason after PRs #51/#52 (CI-P2-004) and was rebound
- What is happening: the substance of the prior finding is fixed — the digest binds its own declared commit, and a genuinely stale digest (non-publication commits after the declared commit) fails the composite gate. What remains is a local accuracy defect: the digest-binding docstring claims that check itself fails stale digests, which it does not (freshness lives in publication equality).
- Why it matters: a maintainer reading the digest-binding docstring could believe freshness is checked there and weaken/skip the publication-equality step.
- User / business impact: low; reviewer/maintainer confusion.
- Security / privacy / reliability impact: release-integrity signaling wording.
- Recommended fix: correct the `ci/validate.py` and `check_digest_binding.py` wording to say resolvability + manifest equality, and point freshness at `check_publication_equality.py`.
- Suggested validation: doc/comment review; a test asserting publication equality fails on a synthetic post-publication code commit.
- Owner suggestion: release owner.
- Effort estimate: S.
- Dependencies: none.
- Status: partially-fixed (primary defect fixed; docstring residual).
- Endpoint / data path: `PACKAGE_DIGEST.txt` -> gate -> reviewer.
- Attack path: none identified.

### INV-P3-004 - Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-package manifest; no check binds it

- Severity: P3
- Confidence: High (hash-level attribution against git revisions)
- Area: INV
- Evidence:
  - `diff PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` -> 8 differing entries: `automation/validation/export_monitor_metrics.sh`, `automation/validation/phase6_backup_restore.sh`, `bootstrap/80-offsite-backup.sh`, `bootstrap/90-alerting.sh`, `bootstrap/96-public-access.sh`, `bootstrap/97-cloudflare-api-config.sh`, `closeout/FINAL_RESPONSE.json`, `closeout/FINAL_RESPONSE_SUPERSEDING_2026-09-23.json`
  - `PACKAGE_MANIFEST.sha256` hashes for those files equal the content at `75c3466` (the bind at `abb63ab`), e.g. `bootstrap/90-alerting.sh` = `1783655...` = hash at `75c3466`, while the tree and review-package manifest carry `8408b3f8...`
  - `git log --oneline -- PACKAGE_MANIFEST.sha256` -> last change `75c3466`; the later publication binds `184f605` and `f5cb7c9` changed only `PACKAGE_DIGEST.txt` + closeout JSONs (`git show --name-only`)
  - `automation/validation/verify_delivery.sh:38` — `cp -f review-package/MANIFEST.sha256 PACKAGE_MANIFEST.sha256` (the copy step that was skipped)
  - `PACKAGE_DIGEST.txt:5` — the publication relationship names `PACKAGE_MANIFEST.sha256` as an artifact the publishing commit adds
  - No check binds it: `check_digest_binding.py` binds `evidence/MANIFEST.sha256` + `review-package/MANIFEST.sha256`; `check_publication_equality.py` compares digest/closeout against the shipped review-package manifest only
- What is happening: the published package manifest (used for packed-only verification) was not refreshed in the last two publication cycles, so it now contradicts the shipped review-package manifest on 8 files and would make a pack verification against it report mismatches.
- Why it matters: a reviewer verifying the delivered pack against `PACKAGE_MANIFEST.sha256` gets false mismatches for files the remediation actually changed; the delivery's own verification is INCOMPLETE for those entries (the SC-P2-002 class).
- User / business impact: release verification friction; possible false "tampered" signals.
- Security / privacy / reliability impact: release-integrity signaling gap.
- Recommended fix: refresh `PACKAGE_MANIFEST.sha256` from `review-package/MANIFEST.sha256` in every publication cycle (the documented `verify_delivery.sh` step), and add a gate assertion that the two are byte-identical (and/or bind `PACKAGE_MANIFEST.sha256` in `PACKAGE_DIGEST.txt`).
- Suggested validation: `cmp PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256`; a CI check failing on mismatch.
- Owner suggestion: release owner.
- Effort estimate: S.
- Dependencies: publication flow.
- Status: open.
- Endpoint / data path: `verify_delivery.sh` -> `PACKAGE_MANIFEST.sha256` -> pack verification.
- Attack path: none identified.

### INV-P3-005 - HYG-P1-001 doctrine ("review-package is generated, gitignored, must not be committed") contradicts the tracked review-package/MANIFEST.sha256

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `.gitignore:26` — `review-package/` (comment: "no longer committed (HYG-P1-001)")
  - `AGENTS.md:44` — "generated artifact; gitignored, do NOT commit (HYG-P1-001)"; `REPOSITORY.md:33,47,51-52`; `docs/architecture/EVOLUTION_GUIDE.md:89` — "gitignored — do not commit"
  - `automation/validation/build_review_package.sh:9-11` — "the output directory review-package/ is generated and gitignored; it is built on demand and must not be committed"
  - `automation/validation/check_digest_binding.py:7,60,70` and `check_publication_equality.py:16,187-190` — comments assume the review package is not committed
  - `git ls-files -s review-package/MANIFEST.sha256` -> tracked (`100644 5fda0c9...`); `git log -- review-package/MANIFEST.sha256` -> re-added at `abb63ab` and modified at `b09a50f`, `3c11752` ("review-package: rebuild at <sha> (declared manifest)")
  - `git ls-tree 08e20d1 review-package/` -> empty (it was untracked at the prior audit)
- What is happening: since `abb63ab` the publication flow commits `review-package/MANIFEST.sha256` (so the digest can bind a committed manifest), while every doctrine page and script comment still says the directory is gitignored and must not be committed; `build_review_package.sh` even `rm -rf`s the directory, which would recreate the tracked file as a working-tree modification.
- Why it matters: an operator following the documented flow could untrack the manifest (breaking the digest/publication equality checks) or treat the recurring `git status` change as unexpected; the fallback branches/comments in the checks are dead code and mislead.
- User / business impact: release-process confusion; risk of breaking the binding.
- Security / privacy / reliability impact: release-integrity process risk.
- Recommended fix: decide the policy explicitly — either keep the manifest tracked (and update `.gitignore`/AGENTS/REPOSITORY/EVOLUTION_GUIDE/script comments + drop the dead fallback branches) or untrack it and bind the digest to a build-time artifact (the a2dded8 design); do not leave doctrine and practice contradicting.
- Suggested validation: `ci/validate.py` passes with the chosen policy; a doc-lint test asserts the doctrine text matches the tracked state.
- Owner suggestion: release owner.
- Effort estimate: S.
- Dependencies: INV-P3-004 (same publication flow).
- Status: open.
- Endpoint / data path: publication flow -> `review-package/MANIFEST.sha256` -> digest binding.
- Attack path: none identified.

## Prior-Run Comparison

| Prior finding | Status now | Evidence |
|---|---|---|
| INV-P2-001 | partially-fixed | evidence + SBOM drift PASS; `docs/audits/` and `mct/` remain unbound; review-package manifest committed but not drift-bound |
| INV-P3-001 | still-open | 264 legacy rows, 870 absolute meta paths; resolver exists but the index check skips legacy rows |
| INV-P3-002 | still-open | `PACK_NOT_INCLUDED.txt` unchanged (last `df934e5`); both files exist |
| INV-P3-003 | partially-fixed | digest binds `3c11752`; staleness enforced by `check_publication_equality.py` (CI-P2-004 red→rebind; CI green at `f5cb7c9`); digest-binding docstring residual |
| — (new) | INV-P3-004 | PACKAGE_MANIFEST stale by 8 entries; unbound |
| — (new) | INV-P3-005 | HYG-P1-001 doctrine contradicts the tracked review-package manifest |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Reviewer verifies the pack against a stale manifest | P3 | Medium | Medium | 8 differing entries | refresh + gate `cmp` (INV-P3-004) |
| Doctrine-driven untracking breaks the digest binding | P3 | Medium | Medium | `.gitignore` vs tracked file | decide policy; update docs (INV-P3-005) |
| Vendored `mct/` silently edited | P2 | Low | Medium | `mct/VENDORING.md` P4 | import manifest |
| Legacy paths break tooling | P3 | Medium | Low | 264 rows | resolver adoption |
| Unresolved pack omissions hide content | P3 | Low | Medium | `PACK_NOT_INCLUDED.txt:4-5` | record disposition |

## Recommendations

### Immediate / Release Blocking
- None (the publication chain itself is PASS and CI-green at the audited commit).

### This Week
- Refresh `PACKAGE_MANIFEST.sha256` and add the equality check (INV-P3-004).
- Record a disposition for the two `not-in-pack (unexpected)` entries (INV-P3-002).
- Decide and document the review-package tracking policy (INV-P3-005).

### This Month
- Correct the digest-binding wording (INV-P3-003); bind committed audit-run folders; resolve-then-check the evidence index (INV-P3-001).

### Later / Platform Evolution
- Implement the `mct/` import manifest + vendor-drift check (P4).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `cp review-package/MANIFEST.sha256 PACKAGE_MANIFEST.sha256` in the bind step | removes the stale manifest | publication flow, `PACKAGE_MANIFEST.sha256` | `cmp` passes |
| Fix the digest-binding docstring | removes a false claim | `ci/validate.py`, `check_digest_binding.py` | review |
| Resolve-then-check in the evidence index tool | removes the manual resolver step | `check_evidence_index.py` | all rows resolve |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Delivery-manifest equality gate | P3 | release | S | publication flow |
| Review-package tracking policy + doc sweep | P3 | release | S | owner decision |
| Committed-run content binding | P2 | maintainer | M | run registry |
| `mct/` import manifest | P2 | maintainer | M | upstream pin |
| Pack-fidelity disposition automation | P3 | release | S | repomix |

## Suggested Tests

- CI: `cmp PACKAGE_MANIFEST.sha256 review-package/MANIFEST.sha256` (or an equivalent hash equality) fails on drift.
- CI: a synthetic stale run folder fails the lifecycle/content binding.
- Unit: `check_digest_binding` behavior for ancestor-commit digests (documented scope).
- Manual: rebuild the repomix pack and reconcile `PACK_NOT_INCLUDED.txt`.

## Suggested Documentation Updates

- `REPOSITORY.md` / `AGENTS.md` / `docs/architecture/EVOLUTION_GUIDE.md`: state the review-package tracking policy as implemented.
- `ci/validate.py` + `automation/validation/check_digest_binding.py`: correct the staleness wording.
- `docs/security/RELEASE_PACK_VERIFICATION.md`: record the current `PACKAGE_MANIFEST.sha256`/review-package relationship and the entry count.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the tracked review-package manifest the intended design? | determines whether INV-P3-005 is a doc fix or a rollback | owner/publication-flow statement |
| Why does repomix omit the two files? | closes INV-P3-002 | reproduced pack build |
| Should `PACKAGE_MANIFEST.sha256` remain a separate copy at all? | simpler alternative: bind the digest to the single review-package manifest | owner decision |

## Limitations

- No pack rebuild was run (would require the repomix toolchain); the omission cause is stated as unverified.
- Evidence capture contents were sampled, not exhaustively reviewed.
- The off-repo delivery archive was not available; delivery-impact statements are based on the in-tree artifacts.

## Appendix

- Gate outputs at `f5cb7c9`: `validation_failures=0`; `generated_drift PASS (2268)`; `sbom_hashes PASS (38)`; `evidence_index PASS (1134/1134, 870 resolved, 264 legacy)`; `digest binding PASS`; `publication equality PASS`; `audit_run_lifecycle check_failures=0`.
- Manifest comparison: `PACKAGE_MANIFEST.sha256` 3,830 entries, `review-package/MANIFEST.sha256` 3,830 entries, 8 differing hashes.
- Publication lineage: `75c3466` (last `PACKAGE_MANIFEST` refresh) -> `184f605` (digest+closeout only) -> `3c11752` (review-package rebuild) -> `f5cb7c9` (digest+closeout only).

## Findings

| ID | Severity | Title |
|---|---|---|
| INV-P2-001 | P2 | Repository is majority generated/derived content; largest trees bound, audit records and mct/ remain unbound |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require the resolver to resolve in a clone |
| INV-P3-002 | P3 | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries |
| INV-P3-003 | P3 | 'A stale digest fails' is enforced by publication equality, not by the digest-binding check whose docstring claims it |
| INV-P3-004 | P3 | Published PACKAGE_MANIFEST.sha256 is two publication cycles stale and disagrees with the shipped review-package manifest; no check binds it |
| INV-P3-005 | P3 | HYG-P1-001 doctrine ('review-package is generated, gitignored, must not be committed') contradicts the tracked review-package/MANIFEST.sha256 |
