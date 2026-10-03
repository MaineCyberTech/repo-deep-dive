# Repository Hygiene and Maintainability

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20261003-0018-main-7bac320
- Repository: C:\temp\repo-deep-dive
- Branch: main
- Commit SHA: 6cada03 (worktree)
- Generated at: 2026-10-03
- Auditor: audit subagent
- Area code: HYG
- Output path: docs/audits/repo-deep-dive/20261003-0018-main-7bac320/21_repo_hygiene_maintainability.md
- Scope limitations: static read; lint/self-test not executed.

## Scope

Standards files, generated-artifact integrity, stale files, duplication, and insensitive artifact handling.

## Evidence Reviewed

- Root listing, `git ls-files`, `PACK_DIGEST.txt`, `inventory.json`
- `tools/deterministic_checks.py` (`check_portability`, `check_hygiene`)
- `runs/*/live_snapshot.txt`, archived findings

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| root listing | command | standards files | no LICENSE/.gitignore/.gitattributes |
| `PACK_DIGEST.txt` header | artifact | integrity | 196 files |
| `inventory.json.totals.files` | artifact | compare | 195 |
| git ls-files secret sweep | command | sensitive commits | `live_snapshot.txt` archived |

## Executive Summary

Hygiene is a weak area: no LICENSE, `.gitignore`, or `.gitattributes`; the digest is not a complete manifest of the tracked tree; and archived runs commit environment snapshots that the shared rules classify as sensitive. Duplication across runner/manifest/profile was covered in ARCH. These are mostly P3 with one P2 for the missing cross-platform hygiene files.

## Inventory

| Item | Present | Notes |
|---|---|---|
| `LICENSE` | No | also SUPPLY-P3-004 |
| `.gitignore` | No | `opencode.json`, OS junk |
| `.gitattributes` | No | CRLF policy absent |
| `PACK_DIGEST.txt` | Yes | 196 entries, skips tracked `opencode.json` |
| `SECURITY.md` | No | also SEC-P3-004 |
| Sensitive archives | Yes | `runs/.../live_snapshot.txt`, findings |

## Findings

### Finding ID: HYG-P2-001 - Missing `.gitignore` and `.gitattributes` create cross-platform and config-sprawl risk

- Severity: P2
- Confidence: High
- Area: HYG
- Evidence:
  - root listing — no `.gitignore`, no `.gitattributes`
  - `tools/deterministic_checks.py` lines 84-93 — would emit `PORT-P3` for missing/loose LF policy
  - `opencode.json` — tracked environment pin, excluded from digest
- What is happening: There is no line-ending policy and no ignore file, so OS/editor junk and machine-local config can enter or drift.
- Why it matters: CRLF checkouts break the bash tools/digest on Linux; committed local pins confuse consumers.
- User / business impact: Windows contributors risk breaking Linux CI.
- Security / privacy / reliability impact: Medium low.
- Recommended fix: Add `.gitattributes` (`* text=auto eol=lf`, `*.sh text eol=lf`) and a `.gitignore` (OS/editor junk, local model pins).
- Suggested validation: `git ls-files --eol` shows only `lf` for scripts; junk is ignored.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: none
- Status: open

### Finding ID: HYG-P3-002 - The integrity digest omits a tracked file and disagrees with the inventory count

- Severity: P3
- Confidence: High
- Area: HYG
- Evidence:
  - `PACK_DIGEST.txt` header — `# files: 196`
  - `tools/pack_digest.sh` — skips `opencode.json` (tracked)
  - `inventory.json` — `totals.files = 195` (different commit, see INV-P1-001)
  - `tools/lint_pack.sh` §8 — digest freshness check also skips `opencode.json`
- What is happening: A tracked file is excluded from the integrity manifest, and the digest file-count is not comparable to the run inventory.
- Why it matters: The digest cannot be used as a complete "what shipped" manifest.
- User / business impact: Minor.
- Security / privacy / reliability impact: Integrity completeness.
- Recommended fix: Untrack `opencode.json` and ignore it, or include it in the digest.
- Suggested validation: `comm` between `git ls-files` and digest paths is empty.
- Owner suggestion: pack maintainer
- Effort estimate: S
- Dependencies: INV-P3-003
- Status: open

### Finding ID: HYG-P3-003 - Archived runs commit sensitive environment snapshots

- Severity: P3
- Confidence: High
- Area: HYG
- Evidence:
  - `runs/20260930-0701-falcon-8282d3f_edge-45dfed0/live_snapshot.txt` — host state capture (systemd, sockets, journal)
  - `runs/20260930-0701-falcon-8282d3f_edge-45dfed0/findings.json` and 40+ reports — sensitive exports
  - shared rules: "Treat repository exports, logs, `.env` files, test artifacts, and generated outputs as sensitive."
- What is happening: Live-host and audit exports are committed in the archive.
- Why it matters: The pack's own safety rule says such exports are sensitive; committing them may leak host topology.
- User / business impact: Potential information disclosure if the repo is shared.
- Security / privacy / reliability impact: Reconnaissance value from sockets/units.
- Recommended fix: Document the archive as sensitive, redact host-identifying fields, or store snapshots outside the repo.
- Suggested validation: `live_snapshot.txt` contains no hostnames/paths deemed sensitive.
- Owner suggestion: pack maintainer
- Effort estimate: M
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| CRLF breaks Linux tools | P2 | Medium | Medium | HYG-P2-001 | `.gitattributes` |
| Sensitive host export committed | P3 | Medium | Medium | HYG-P3-003 | redact/relocate |
| Incomplete digest | P3 | High | Low | HYG-P3-002 | reconcile |

## Recommendations

### This Week
- Add `.gitattributes`/`.gitignore`.

### This Month
- Decide handling for committed snapshots and `opencode.json`.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| `.gitattributes` | stable EOL | root | `git ls-files --eol` |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Sensitive-artifact policy for runs | P3 | maintainer | M | none |

## Suggested Tests

- Portability check passes (no CRLF in index; scripts executable).

## Suggested Documentation Updates

- CONTRIBUTING: hygiene files and sensitive-archive handling.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `runs/` intended for public distribution? | sensitivity decision | maintainer intent |

## Appendix

Not applicable.
