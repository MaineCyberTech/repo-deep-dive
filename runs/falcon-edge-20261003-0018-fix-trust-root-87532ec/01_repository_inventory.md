# Comprehensive Repository Inventory

## Audit Metadata

- Audit name: repo-deep-dive (Full Hardening, base profile)
- Run: 20261003-0018-fix-trust-root-87532ec
- Repository: `C:\temp\falcon-edge` (MaineCyberTech/falcon-edge)
- Branch: fix/trust-root
- Commit SHA: 87532ec (87532ec973a2aa5fb7d6133f73b8305d6b4f51dc)
- Generated at: 2026-10-03T00:18Z
- Auditor: repo-deep-dive subagent
- Area code: INV
- Output path: docs/audits/repo-deep-dive/20261003-0018-fix-trust-root-87532ec/01_repository_inventory.md
- Scope limitations: repository read-only; no live lab host, Pi, or GitHub API access. `evidence/raw` treated as sensitive raw captures; contents sampled, not exhaustively read.

## Scope

Reviewed: repository tree, `inventory.json`, root configs (`README.md`, `REPOSITORY.md`, `AGENTS.md`, `.gitignore`, `.gitleaks.toml`), `src/` (5 packages), `api/` (OpenAPI + schemas + generated models), `ci/`, `.github/`, `automation/`, `image/`, `profiles/`, `deploy/`, `config/`, `ledgers/`, `docs/`, `closeout/`, and `evidence/` (metadata and counts). Not reviewed: individual raw evidence payloads beyond the sampled files named in the reports.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `inventory.json` | Generated inventory | Wave-0 input | 1,288 files / 38,359 lines; 900 under `evidence/` |
| `git ls-files` | Repo manifest | Source vs generated split | 5 workflows, 101 `.py`, 49 `.sh`, 153 `.md` |
| `README.md`, `REPOSITORY.md`, `AGENTS.md` | Docs | Doctrine, branch policy, environment facts | Lab-only program |
| `src/**` (23 files) | Source | Agent/control-plane/CLI/common | 4,303 LOC in `src/` |
| `api/openapi/falcon-edge-v1.yaml` | Contract | 19 documented operations | See 08 |
| `ledgers/gate_ledger.csv` | Ledger | 88 gates, 86 PASS / 2 BLOCKED | Machine artifact |
| `evidence/` | Raw captures | 900 committed files | Generated, sensitive |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log -1` / `git status` | Command | Bind run to commit | HEAD `87532ec`, clean tree |
| `git ls-files` counts | Command | Aggregate reconciliation | 49 test files; 900 evidence files; 4,303 `src` LOC |
| gate ledger parse | Command | Aggregate check | 88 rows: PASS 86, BLOCKED 2 |
| `inventory.json` cross-check | Diff | Self-consistency | Reports 0 routes / 0 migrations / 0 entry points (see INV-P2-002) |

## Executive Summary

Falcon Edge is a small, unusually well-documented lab program: stdlib-only Python agent/control-plane/CLI, an authoritative OpenAPI 3.1 contract, five GitHub Actions workflows, an image pipeline, ledgers, and 900 raw evidence captures. Source is cleanly separated from generated artifacts in most directories, and CI enforces model/contract drift, license, secret, and evidence checks. The dominant inventory risks are (a) 900 committed raw evidence files with no retention policy and no size budget, (b) the Wave-0 inventory tooling failing to see the real HTTP route table, SQLite schema, or entry points, and (c) committed generated artifacts (audit mirrors, `closeout/FINAL_RESPONSE.json`, generated models/schemas) that will silently go stale.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Control plane | `src/falcon_control/` | mTLS service, PKI, tokens, SQLite | Implemented | Med | 19 routes in `service.ROUTES` |
| Agent | `src/falcon_agent/` | Lifecycle, queue, updates, directives | Implemented | Med | stdlib only |
| CLI | `src/falcon_cli/__main__.py` | Operator interface | Implemented | Low | destructive cmds gated by `--confirm` |
| Contract | `api/openapi/falcon-edge-v1.yaml` | OpenAPI 3.1 | Implemented | Med | pagination drift (API-P2-001) |
| Generated models | `src/falcon_common/models_generated.py` | Pydantic-free validators | Generated + drift-checked | Low | `api/generate_models.py --check` |
| Evidence | `evidence/raw/` | Raw captures + SHA-256 | 900 files committed | High | No retention (INV-P2-001) |
| Ledgers | `ledgers/*.csv|*.md` | Gates/evidence/risk/decisions | Append-only | Low | 86/88 PASS |
| Docs | `docs/**` | Phase design, runbooks | Extensive (153 md) | Low | some drift (HYG-P2-001) |
| Closeout | `closeout/FINAL_RESPONSE.json` | Generated final response | Committed | Med | regenerable artifact |
| CI | `.github/workflows/*` | Build/validate/release | 5 workflows | Med | see 10 |
| Deploy | `deploy/*.service` | systemd units | Hardened | Low | working-tree exec (ARCH-P2-001) |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Root configs | 4 | `README`, `AGENTS.md`, `.gitleaks.toml` | no LICENSE | add license/proprietary notice |
| Package/workspace files | 4 | stdlib-only, no lockfile | no requirements pinning | document/pin CI tools |
| Applications | 4 | `src/falcon_agent`, `src/falcon_control`, `src/falcon_cli` | no packaging metadata | add `pyproject.toml` |
| API services | 4 | `src/falcon_control/http_server.py` | no rate limiting/headers | see SEC-P2-001 |
| Workers | 4 | `falcon-agent.service` | none material | — |
| Shared packages | 4 | `src/falcon_common/` | none material | — |
| Database/migrations | 2 | `src/falcon_control/store.py` | no migrations/FK | see DATA |
| GitHub metadata | 3 | `.github/*` | branch protection plan-blocked | see CI-P2-001 |
| Tests | 3 | `tests/phase0..10` | coverage not gated | see TEST |
| Docs | 4 | `docs/**` | stale counts | see HYG-P2-001 |
| Assets/public files | 3 | `config/`, `profiles/` | none | — |
| Generated artifacts | 2 | `evidence/`, `closeout/`, models | no retention | INV-P2-001 |

## Detailed Review

### Item: Source tree (`src/`)

- Evidence: `src/falcon_control/service.py`, `src/falcon_agent/runner.py`, `src/falcon_cli/__main__.py`
- What it does: control plane, device agent, operator CLI; Python 3.11+ stdlib only.
- How it appears to work: request → `ControlPlaneService.handle` route table → certificate-resolved identity → handler → SQLite `Store`.
- Dependencies: `openssl` CLI for PKI; `sqlite3` stdlib.
- Current controls: mTLS, Ed25519-signed directives, idempotency keys, path sensor-id checks.
- Missing controls: rate limiting, schema migrations.
- Risks: see 06/07.
- Recommended improvement: none structural.
- Suggested tests: contract tests against `ROUTES` (already in `tests/phase1/test_contract_routes.py`).
- Suggested docs: keep README layout table current.

### Item: Evidence tree (`evidence/`)

- Evidence: 900 files, 447 `.out`, 493 `.json`; `automation/evidence/index.sh`, `manifest.sh`
- What it does: raw captures + SHA-256 metadata backing every PASS claim.
- How it appears to work: `capture.sh` writes `meta.json` + raw `.out`; `index.sh` rebuilds `ledgers/evidence_index.csv`; `manifest.sh` maintains `evidence/MANIFEST.sha256`.
- Dependencies: `ci/check_evidence.py`.
- Current controls: append-only, hash-checked by `ci/validate.sh`.
- Missing controls: retention/size policy; no pruning of superseded captures.
- Risks: repo bloat and unbounded growth (INV-P2-001).

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INV-001 | Root configs | `README.md`, `AGENTS.md` | doctrine + rules | no LICENSE | P3 | add license notice |
| INV-002 | Package/workspace files | stdlib-only | none | no pinning metadata | P3 | add `pyproject.toml` |
| INV-003 | Applications | `src/**` | reviewed | none material | — | — |
| INV-004 | API services | `service.ROUTES` | mTLS + validation | rate limiting | P2 | see SEC |
| INV-005 | Workers | systemd units | hardened | none material | — | — |
| INV-006 | Shared packages | `falcon_common/` | reviewed | none material | — | — |
| INV-007 | Database/migrations | `store.SCHEMA` | CREATE IF NOT EXISTS | no migrations | P2 | see DATA |
| INV-008 | GitHub metadata | `.github/` | CODEOWNERS, dependabot | unpinned enforcement | P2 | see CI |
| INV-009 | Tests | `tests/**` | 49 files, unittest | coverage not gated | P3 | see TEST |
| INV-010 | Docs | `docs/**` | extensive | stale counts | P2 | see HYG |
| INV-011 | Assets/public files | `config/`, `profiles/` | reviewed | none material | — | — |
| INV-012 | Generated artifacts | `evidence/`, `closeout/` | hash/regeneration | no retention | P2 | INV-P2-001 |

## Findings

### Finding ID: INV-P2-001 - 900 raw evidence files committed with no retention or size policy

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `evidence/raw/` — 900 tracked files (447 `.out`, 493 `.json`)
  - `inventory.json` — `largest_dirs[0] = {evidence: 900}`
  - `automation/evidence/index.sh`, `automation/evidence/manifest.sh`
  - `ci/check_evidence.py` — hash integrity only
- What is happening: every lab capture since the program start is committed and hash-indexed; there is no retention window, size budget, or archival step.
- Why it matters: the evidence tree is ~70% of all tracked files; clone time, secret-scan time, and review surface grow without bound.
- User / business impact: slower CI/review; harder to find current evidence among superseded captures.
- Security / privacy / reliability impact: more captured host/network detail retained than necessary; larger blast radius if the repo is exposed.
- Recommended fix: define a retention/archive policy (e.g. keep N most recent per gate, move older to external storage) and a size check in `ci/validate.sh`.
- Suggested validation: add a CI step that fails when `evidence/` exceeds the budget; document the archive path.
- Owner suggestion: build-agent + owner
- Effort estimate: M
- Dependencies: external evidence archive
- Status: open

### Finding ID: INV-P2-002 - Wave-0 inventory tooling is blind to the route table, schema, and entry points

- Severity: P2
- Confidence: High
- Area: INV
- Evidence:
  - `inventory.json` — `"routes": []`, `"migrations": []`, `"entry_points": []`, `"containers": []`
  - `src/falcon_control/service.py` — `ControlPlaneService.ROUTES` (19 routes)
  - `src/falcon_control/store.py` — `SCHEMA` (10 tables)
  - `src/falcon_agent/__main__.py`, `src/falcon_control/__main__.py`, `src/falcon_cli/__main__.py`
- What is happening: the generated inventory reports no routes, migrations, or entry points even though the repo has a regex route table, a SQLite schema, and CLI/module entry points.
- Why it matters: downstream audit waves that trust `inventory.json` will miss the entire API and data surface; this run had to read the source directly to recover it.
- User / business impact: incomplete automated inventories → missed findings.
- Security / privacy / reliability impact: false confidence that nothing exists.
- Recommended fix: teach `tools/repo_inventory.py` to parse regex route tables, `CREATE TABLE` schemas, and `__main__`/`console_scripts` entry points, or document that the repo is "not a web stack" so the empty fields are expected.
- Suggested validation: re-run inventory and assert `routes`/`migrations` are non-empty.
- Owner suggestion: audit-tooling owner
- Effort estimate: M
- Dependencies: `repo-deep-dive/tools/repo_inventory.py`
- Status: open

### Finding ID: INV-P3-001 - Generated models, schemas, dashboard JSON, and audit mirrors are committed and can go stale

- Severity: P3
- Confidence: High
- Area: INV
- Evidence:
  - `src/falcon_common/models_generated.py` — generated from OpenAPI (`api/generate_models.py`)
  - `api/schemas/*.json` — 30 exported schemas (`api/generate_schemas.py`)
  - `config/grafana/edge-fleet-dashboard.json`
  - `docs/audits/repo-deep-dive/20261002-0630-edge-f6f1610/**`, `closeout/FINAL_RESPONSE.json`
- What is happening: multiple generated/derived artifacts are committed. Models and schemas are guarded by `--check` in `ci/validate.sh`; the dashboard, audit mirror, and `FINAL_RESPONSE.json` are not guarded by a regeneration check.
- Why it matters: unguarded generated artifacts diverge from their source of truth and mislead readers.
- User / business impact: stale audit claims and dashboards.
- Security / privacy / reliability impact: low.
- Recommended fix: add regeneration/`--check` guards for the dashboard and closeout response, or mark them as point-in-time snapshots in-file.
- Suggested validation: mutate the source and assert `ci/validate.sh` fails.
- Owner suggestion: build-agent
- Effort estimate: S
- Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Unbounded evidence growth | P2 | High | Repo/CI slowdown | `inventory.json` | retention policy |
| Inventory blind spots | P2 | High | Missed findings | `inventory.json` empty fields | fix tooling |
| Stale generated artifacts | P3 | Medium | Misleading docs | committed mirrors | regen guards |

## Recommendations

### Immediate / Release Blocking
None.

### This Week
Add an `evidence/` size/retention check and regenerate/guard the closeout/dashboard artifacts.

### This Month
Fix Wave-0 inventory extraction (routes/schema/entry points).

### Later / Platform Evolution
Externalize raw evidence; keep the repo a thin index.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add LICENSE/notice | clear ownership | repo root | present in tree |
| Document empty inventory fields | prevents false confidence | `tools/repo_inventory.py` docs | re-run |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Evidence retention/size gate | P2 | build-agent | M | archive |
| Inventory parser fix | P2 | tooling | M | none |
| Generated-artifact guards | P3 | build-agent | S | none |

## Suggested Tests

- CI: assert `evidence/` byte budget.
- CI: assert `closeout/FINAL_RESPONSE.json` regenerates identically.
- Tooling: unit test that `repo_inventory` finds the 19 routes and 10 tables.

## Suggested Documentation Updates

- `README.md`: add a size/retention note for `evidence/`.
- `docs/README.md`: mark audit mirrors as frozen snapshots.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is there an external evidence archive already? | determines retention fix | owner answer |
| Which generated artifacts must be byte-reproducible? | scope of guards | owner decision |

## Appendix

Counts: 1,288 files / 38,359 lines; 101 `.py`; 153 `.md`; 49 test files; 900 evidence files; `src` 4,303 LOC. Gate ledger: 88 rows (86 PASS / 2 BLOCKED).
