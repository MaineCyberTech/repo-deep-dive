# 01_repository_inventory — Prompt 01 - Comprehensive Repository Inventory

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `01_repository_inventory.md` (area INV, prompt)

## Verification Performed

## Metadata

- Domain: `01_repository_inventory` (area INV)
- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`); audited clone `/tmp/opencode/falcon-audit-08e20d1` (worktree clean; local branch `main` points at the live host's unpushed `6e4fccd` — see ARCH report)
- Emitted: 2026-10-09T21:52:25Z by the repo-deep-dive full-pass subagent
- Scope limitation: repository tree only (read-only); no lab artifacts were modified.

## Scope

Every tracked top-level tree was inventoried (root configs, `.github`, `bootstrap/`, `ci/`, `compose/`, `config/`, `automation/`, `mct/`, `pins/`, `docs/`, `ledgers/`, `evidence/`, `sbom/`, `closeout/`, `PACKAGE_*`), plus environment examples and generated artifacts. Application frameworks (node/python packages, migrations, routes) are absent by design (ops repository). Not reviewed: content correctness of individual evidence captures (sampled), the `mct/` upstream (vendored, no upstream access).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `tools/repo_inventory.py` output | generated inventory | file/line counts, stacks, tests, secret-adjacent names | 3,866 files / 944,166 lines; stacks: github-actions only; no lockfiles/migrations/routes |
| `git ls-files` | command | tracked tree + ownership | 3,865 tracked files; worktree clean at `08e20d1` |
| `README.md`, `REPOSITORY.md`, `AGENTS.md`, `docs/README.md` | docs | conventions, source-vs-generated map, evidence rules | regeneration commands documented |
| `ci/validate.py` (checks 1-19) | source | the repo gate | generated-drift, evidence-index, sbom-hashes, digest-binding, publication-equality |
| `automation/validation/check_generated_drift.py`, `sbom_hashes.sh`, `check_evidence_index.py`, `check_digest_binding.py`, `check_publication_equality.py` | source | artifact binding | all ran read-only |
| `ledgers/evidence_index.csv`, `evidence/MANIFEST.sha256`, `evidence/raw/**/*.meta.json` | artifacts | evidence tree + paths | 1,127 metas; 264 legacy rows |
| `sbom/`, `PACKAGE_*.txt`, `closeout/FINAL_RESPONSE.json` | artifacts | generated/delivery set | 39 SBOM/vuln files; digest binds `69b3c80` |
| `docs/audits/repo-deep-dive/` (6 runs) | artifacts | durable run records | structural check passes |
| `mct/VENDORING.md`, `mct/REPO-MAP.md` | docs | vendored subtree policy | archive-only; P4 not implemented |
| `.env.example`, `config/**/*.example*` | config | environment samples | placeholders only; no real values |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `python3 ci/validate.py --fast` | command | repo gate smoke | `validation_failures=0` (parsers, compose pins, shell syntax 321 scripts, credential sourcing, gate ledger 102) |
| `python3 automation/validation/check_generated_drift.py --root .` | command | evidence tree binding | `PASS generated_drift (2268 entries match)` |
| `bash automation/validation/sbom_hashes.sh verify` | command | SBOM set binding | `PASS (38 artifacts verified, manifest unsigned)` |
| `python3 automation/validation/check_evidence_index.py --root .` | command | evidence index | `PASS (1127 metas, 1127 rows, 863 host-absolute resolved, 264 legacy skipped)` |
| `python3 automation/validation/check_digest_binding.py --root .` | command | delivery binding | `PASS` (review-package absent -> skip) |
| `python3 automation/validation/check_publication_equality.py --root .` | command | digest<->closeout binding | `PASS` |
| `bash automation/validation/audit_run_lifecycle.sh check` | command | run folders | 6 runs, `check_failures=0` |
| `sha256sum evidence/MANIFEST.sha256` vs `PACKAGE_DIGEST.txt` | command | declared-vs-actual | equal (`958f92f7...`) |
| `git rev-list --count 69b3c80..HEAD` | command | digest staleness | 11 commits |

## Executive Summary

Falcon is a single ops repository (no package manifests, lockfiles, app routes or migrations); most bytes are generated evidence and SBOM payloads (60% of files, 78% of bytes). The prior INV-P2-001 gap has been substantially closed: `ci/validate.py` now binds the evidence tree (2,268 entries) and the SBOM set (38 artifacts) to committed manifests, checks the evidence index, and verifies the delivery digest/closeout equality — all passing at `08e20d1`. Residuals: the committed audit-run folders and the vendored `mct/` subtree have no content/import binding, the legacy evidence paths (264 index rows; 1,127 absolute meta paths) still need the resolver, two pack-fidelity entries ship as "unexpected; investigate", and the delivery digest binds an 11-commit-old tree while the gate's "stale digest fails" claim only checks commit resolvability.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Root conventions | `README.md`, `AGENTS.md`, `REPOSITORY.md` | doctrine, layout, evidence rules | current | low | source |
| Root configs | `.gitattributes`, `.gitignore`, `.gitleaks.toml`, `.env.example` | line endings, ignores, secret scan, env sample | current | low | placeholders only |
| CI metadata | `.github/` (3 workflows, CODEOWNERS, dependabot) | validate/smoke/dependabot | active | low | workflows pinned by SHA |
| Host bootstrap | `bootstrap/` (30 scripts) | host prep, firewall, secrets, deploy, timers | active | medium (runtime-mutating) | idempotent per docs |
| Static gate | `ci/` (validate.py, license_check.py, requirements) | 19 checks | active, passing fast set | low | full set includes live-dependent checks |
| Compose | `compose/central`, `compose/probe`, `compose/mct` (7 files) | deployment sources | active | low | digest-pinned via `pins/images.lock` |
| Config templates | `config/` (69 files) | nftables, docker, prometheus, grafana, suricata, vector, traefik, systemd, ntfy, wireguard, rsyslog | active | medium | rendered with secrets on deploy |
| Automation | `automation/` (205 files) | evidence capture, validation (104 scripts), alerting, vpn, wazuh | active | medium | 51 offline suites run in CI |
| Vendored MCT | `mct/` (858 files) | imported SOC stack snapshot | archive-only (policy) | medium | no upstream commit; P4 drift check unimplemented |
| Docs | `docs/` (344 files) | phases, runbooks, audits, architecture, security | mixed source/generated | low | audits are generated records |
| Ledgers | `ledgers/` (11 files) | gates, tests, evidence index, risk/exceptions/decisions | append-only, checked | low | 102+14 gates |
| Evidence | `evidence/` (2,269 files, 14 MB) | raw captures + manifest | drift-bound (PASS) | low | 264 legacy paths |
| SBOM | `sbom/` (39 files, 29 MB) | SBOM + vuln JSON | hash-bound (PASS, unsigned) | medium | large committed payloads (HYGIENE-P2-001) |
| Pins | `pins/` (5 files) | 24-image lock + waivers + scripts | active | medium | blanket `mct/compose` waiver |
| Closeout | `closeout/` (4 files) | final response records | digest-bound | low | binds `69b3c80` |
| Delivery digests | `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256`, `PACK_*.txt` | publication binding | verify PASS; binds `69b3c80` (11 commits behind HEAD) | medium | see INV-P3-003 |
| Audit records | `docs/audits/repo-deep-dive/` (6 runs, 205 files) | durable audit records | structural check PASS | medium | no content binding; 20261005 record divergence (ORCH-P2-001) |

### Sensitive inventory

| Item | Type | State | Notes |
|---|---|---|---|
| `.env.example` | env sample | placeholders only | never contains real values |
| `/home/user/.env` (host, outside repo) | owner credentials | not in repo | referenced by name only |
| `/srv/falcon/secrets/*` (host) | service secrets | not in repo | root-only per doctrine |
| `mct/config/examples/secrets.example.env` | env sample | tracked, placeholder | excluded from the repomix pack (see INV-P3-002) |
| `*.pem|*.key|*.crt|*.p12|*.pfx|*.age|*.gpg` | patterns | gitignored | no such files tracked |

### Generated / stale artifact table

| Artifact | Regenerated by | Binding at `08e20d1` | Staleness |
|---|---|---|---|
| `evidence/MANIFEST.sha256` | `automation/evidence/manifest.sh create` | `generated-drift` PASS (2,268 entries) | current |
| `sbom/SBOM_MANIFEST.sha256` | `automation/validation/sbom_hashes.sh create` | `sbom-hashes` PASS (38 artifacts, unsigned) | current |
| `ledgers/evidence_index.csv` | `automation/evidence/index.sh` | `evidence-index` PASS | current |
| `docs/phase9/ALERT_CATALOGUE.yaml` | `automation/validation/build_alert_catalogue.py` (live) | none | drifts from live (79 vs 77; FEAT-P2-002) |
| `config/dashboards/*.json` | `bootstrap/91-dashboards.sh` (live export) | none | regenerated on live runs |
| `PACKAGE_DIGEST.txt` / `PACKAGE_MANIFEST.sha256` / `closeout/FINAL_RESPONSE.json` | `automation/validation/publish_digests.sh` + `closeout/generate_final_response.py` | digest-binding + publication-equality PASS | binds `69b3c80`; 11 commits behind HEAD |
| `docs/audits/repo-deep-dive/*` | audit runs | structural check only | no content binding |
| `review-package/` | `automation/validation/build_review_package.sh` | absent (gitignored, HYG-P1-001) | generated on demand |
| `mct/` | manual import | none | no import manifest (P4 proposed) |

## Findings

### INV-P2-001 - Repository is majority generated/derived content with no in-repo regeneration or drift check (partially fixed)

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `git ls-files` -> 3,865 files; `evidence/` 2,269 files + `sbom/` 39 files = ~60% of files; 14 MB + 29 MB of 55 MB = ~78% of bytes
  - `automation/validation/check_generated_drift.py:37` — default manifests bind only `evidence/MANIFEST.sha256`
  - `python3 automation/validation/check_generated_drift.py --root .` -> `PASS (2268 entries)`
  - `bash automation/validation/sbom_hashes.sh verify` -> `PASS (38 artifacts)`
  - `ci/validate.py:512-531` (sbom-hashes), `ci/validate.py:489-509` (digest-binding), `ci/validate.py:471-486` (publication-equality)
  - `REPOSITORY.md:35-59` — source-vs-generated table and regeneration commands
  - Residual unbound trees: `docs/audits/` (validated structurally only, `automation/validation/audit_run_lifecycle.sh:99-147`) and `mct/` (`mct/VENDORING.md:67-73`, P4 proposed, not implemented)
- What is happening: the repository is still majority generated bytes, but the two largest generated trees (evidence, SBOM) are now bound to committed manifests and verified every gate run; the review-package rebind was superseded by untracking it (HYG-P1-001). The remaining generated records (`docs/audits/`, `mct/`) have no regeneration/drift binding.
- Why it matters: the original risk (a stale or hand-edited generated artifact silently contradicting its source) is largely closed for the big trees; the audit records themselves remain unbound.
- User / business impact: reviewer trust in generated records depends on manual checks.
- Security / privacy / reliability impact: low; integrity risk in audit records.
- Recommended fix: add a lightweight binding for committed run folders (e.g., record the canonical run hash in the pack index) and implement the `mct/` import manifest (P4).
- Suggested validation: `ci/validate.py` fails when a committed run folder or `mct/` file is edited without rebinding.
- Owner suggestion: repo maintainer.
- Effort estimate: M.
- Dependencies: none.
- Status: partially-fixed.

### INV-P3-001 - Legacy host-absolute evidence paths require the resolver to resolve in a clone (partially fixed)

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `ledgers/evidence_index.csv` — 264 rows still `../monitoring-build/evidence/...`; 1,127 rows repo-relative
  - `evidence/raw/**/*.meta.json` — 1,127/1,127 `raw_artifact` fields record `/home/user/falcon-build/...` absolute paths
  - `python3 automation/validation/resolve_evidence_path.py '../monitoring-build/evidence/raw/P2-G01/20260922T073429Z_auditd-rules-fix.out' --root .` -> resolved, exit 0; same for an absolute `/home/user/falcon-build/...` sample
  - `automation/validation/tests/resolve_evidence_path_test.sh` exists
  - `REPOSITORY.md:61-74` — mapping documented (R-14 / DOC-P2-002 / INV-P3-001)
- What is happening: recorded paths still do not resolve by themselves in a fresh clone; the resolver maps both forms to `evidence/raw/...` and verifies existence, but every consumer must know to run it.
- Why it matters: off-host review requires an extra step; a script that opens recorded paths directly fails.
- User / business impact: friction for reviewers.
- Security / privacy / reliability impact: none directly.
- Recommended fix: keep the legacy rows (history) but teach the evidence tooling to resolve recorded paths centrally, or emit resolved paths in new meta records.
- Suggested validation: extend `resolve_evidence_path_test.sh` with a random sample of legacy rows; make `check_evidence_index.py` resolve-then-check.
- Owner suggestion: repo maintainer.
- Effort estimate: S.
- Dependencies: none.
- Status: partially-fixed.

### INV-P3-002 - Delivery pack fidelity artifact ships two unresolved "unexpected; investigate" entries

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `PACK_NOT_INCLUDED.txt:4-5` — `evidence/raw/REVIEW-FIX/20261001T202630Z_sec-p3-001-gitleaks-tree.out` and `mct/config/examples/secrets.example.env` marked `not-in-pack (unexpected; investigate)`
  - `automation/validation/pack_fidelity.py:81` — that disposition is written when a manifest entry is absent from the repomix pack
  - `automation/validation/make-repomix.sh:21` — the ignore list names neither path
  - both files exist in the repository tree
- What is happening: the published `PACK_NOT_INCLUDED.txt` (a delivery artifact) advertises two unexplained absences from the review pack and no disposition was ever recorded.
- Why it matters: a reviewer cannot tell whether the omissions are benign tool behavior or missing content; the artifact says "investigate" indefinitely.
- User / business impact: review friction; possible hidden content gap in the delivered pack.
- Security / privacy / reliability impact: low; integrity/trust.
- Recommended fix: reproduce the pack build, determine the cause (likely repomix built-in secret-file heuristics — verify, do not assume), then record the reason in the artifact or adjust the fidelity classification; regenerate `PACK_NOT_INCLUDED.txt`.
- Suggested validation: rebuild the pack and confirm every `not-in-pack` row has a stated reason.
- Owner suggestion: release owner.
- Effort estimate: S.
- Dependencies: repomix toolchain.
- Status: open.

### INV-P3-003 - Gate claim "a stale digest fails" is not implemented; the digest binds an 11-commit-old tree

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `PACKAGE_DIGEST.txt:2-4` — `repository_commit=69b3c80d764f0fe70f962bb11074fe7fb3bb4978`; `generated_utc=2026-10-04T21:36:48Z`
  - `git rev-list --count 69b3c80..HEAD` -> 11
  - `ci/validate.py:494-497` — docstring: "A stale digest therefore fails here instead of being mistaken for current"
  - `automation/validation/check_digest_binding.py:83-88` — only `git cat-file -e <commit>^{commit}` (resolvability), never HEAD equality; check passes at `08e20d1`
  - `AGENTS.md` standard flow step 5 — "rebind the delivery when the tree changed"
- What is happening: the delivery digest/closeout pair still binds the 2026-10-04 commit while the tree has moved 11 commits (including merged remediation and CI changes); the check passes because it only requires the old commit to exist.
- Why it matters: the "stale digest fails closed" property is claimed but not enforced; only a publication discipline keeps the digest current, and there is no signal when it goes stale.
- User / business impact: a reviewer could believe the delivered package corresponds to the current tree.
- Security / privacy / reliability impact: release-integrity signaling gap.
- Recommended fix: either implement a staleness policy (e.g., fail when `repository_commit != HEAD` on main, or record an explicit "superseded by" field), or correct the docstring to state that resolvability, not freshness, is checked.
- Suggested validation: `check_digest_binding.py` test with a digest bound to an ancestor commit asserts the documented behavior.
- Owner suggestion: release owner.
- Effort estimate: S.
- Dependencies: publication flow.
- Status: open.

## Prior-Run Comparison

| Prior finding | Status now | Evidence |
|---|---|---|
| INV-P2-001 | partially-fixed | evidence + SBOM drift checks PASS; `docs/audits/` and `mct/` remain unbound |
| INV-P3-001 | partially-fixed | resolver + docs + test exist; 264 legacy rows and 1,127 absolute meta paths remain |

New this run: INV-P3-002 (pack fidelity), INV-P3-003 (digest staleness claim).

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Audit records diverge from canonical runs | P2 | Medium | High | ORCH-P2-001 | bind committed runs |
| Vendored `mct/` silently edited | P2 | Low | Medium | `mct/VENDORING.md` P4 | import manifest |
| Stale delivery digest read as current | P3 | Medium | Medium | digest binds `69b3c80` | staleness policy |
| Legacy paths break tooling | P3 | Medium | Low | 264 rows | resolver adoption |

## Recommendations

### Immediate / Release Blocking
- None.

### This Week
- Record a disposition for the two `not-in-pack (unexpected)` entries (INV-P3-002).

### This Month
- Decide and implement the digest staleness policy (INV-P3-003); bind committed audit-run folders.

### Later / Platform Evolution
- Implement `mct/` import manifest + vendor-drift check (P4).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Resolve-then-check in the evidence index tool | removes the manual resolver step | `check_evidence_index.py` | all rows resolve |
| Fix the digest-binding docstring or add the HEAD check | removes a false claim | `ci/validate.py`, `check_digest_binding.py` | test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Committed-run content binding | P2 | maintainer | M | run registry |
| `mct/` import manifest | P2 | maintainer | M | upstream pin |
| Pack-fidelity disposition automation | P3 | release | S | repomix |

## Suggested Tests

- Unit: `check_digest_binding` behavior for ancestor-commit digests.
- CI: a synthetic stale run folder fails the lifecycle/content binding.
- Manual: rebuild the repomix pack and reconcile `PACK_NOT_INCLUDED.txt`.

## Suggested Documentation Updates

- `REPOSITORY.md`: state the digest staleness policy explicitly.
- `docs/security/RELEASE_PACK_VERIFICATION.md`: record the pack-fidelity disposition rules.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is the digest meant to track HEAD or only publication windows? | determines the right staleness rule | owner statement |
| Why does repomix omit the two files? | closes INV-P3-002 | reproduced pack build |

## Limitations

- No pack rebuild was run (would require the repomix toolchain); the omission cause is stated as unverified.
- Evidence capture contents were sampled, not exhaustively reviewed.

## Findings

| ID | Severity | Title |
|---|---|---|
| INV-P2-001 | P2 | Repository is majority generated/derived content with no in-repo regeneration or drift check |
| INV-P3-001 | P3 | Legacy host-absolute evidence paths require manual rewrite to resolve in a clone |
| INV-P3-002 | P3 | Delivery pack fidelity artifact ships two unresolved 'unexpected; investigate' entries |
| INV-P3-003 | P3 | Gate claim 'a stale digest fails' is not implemented; the delivery digest binds an 11-commit-old tree |
