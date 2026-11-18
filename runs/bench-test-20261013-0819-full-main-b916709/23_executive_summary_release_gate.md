# 23_executive_summary_release_gate — Prompt 23 - Executive Summary and Release Gate

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `23_executive_summary_release_gate.md` (area EXEC, prompt)

## Verification Performed

# Executive Summary and Release Gate

## Audit Metadata

- Audit name: `repo-deep-dive`
- Run: `bench-test-20261013-0819-full-main-b916709`
- Repository: `C:\temp\bench-test` (`https://github.com/MaineCyberTech/bench-test`)
- Branch: `main`
- Commit SHA: `b9167095b08c2f45a814e88e09d88decbd0ea885` (run pin, VERSION 1.11.3) — observed working tree `60ab90eb69db1daaeed080a157b8fd8208f2a413` (VERSION 1.11.5, 5 commits ahead)
- Generated at: 2026-10-13
- Auditor: domain subagent `23_executive_summary_release_gate` (synthesis over emitted per-domain findings)
- Area code: EXEC
- Output path: `docs/audits/repo-deep-dive/bench-test-20261013-0819-full-main-b916709/23_executive_summary_release_gate.md`
- Scope limitations: This report is a **synthesis** over the 40 per-domain findings JSONs under `runs/bench-test-20261013-0819-full-main-b916709/_domains/`. I did not re-run every domain probe; I aggregated severities, de-duplicated the P0/P1 mass, and independently re-verified the two load-bearing gate facts (baked credentials, no test CI) against the current tree.

## Scope

Reviewed: every emitted per-domain findings file (40 JSONs, 245 findings), aggregated by severity and theme. Re-verified at the current tree: public-release credential baking (`.github/workflows/build-app.yml`, `.github/workflows/build-iso.yml`, `README.md`, `server/benchd.py`), the absence of any test/lint step in CI, and the commit binding of the run vs the working tree. Reconciled against the repository's pre-existing published gate at `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/RELEASE_GATE.md`.

Not reviewed: no live lab, no external systems, no secret values. I did not independently reproduce the RCE / identity-takeover exploits (marked below as reported by source domains, `High` confidence, with `file:line`).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `_domains/*.json` (40 files) | Generated artifacts | Source of all aggregated counts | 245 findings; 4 domains correctly returned empty |
| `.github/workflows/build-app.yml:63` | CI config | Bakes `BENCH_AGENT_CONF` into public app bundles | Verified current tree |
| `.github/workflows/build-iso.yml:66,77` | CI config | Bakes `BENCH_UPLOAD_CONF` + `BENCH_AGENT_CONF` into public ISO | Verified current tree |
| `server/benchd.py:26` | Source | One `BENCHD_TOKEN` = join token + operator bearer | Verified current tree |
| `README.md:162` | Docs | Declares the baked token world-readable on public releases | Verified current tree |
| `.github/workflows/*` | CI config | Only 3 workflows; none runs tests (`git grep ... -- .github` → no matches) | Verified current tree |
| `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/RELEASE_GATE.md` | Prior published gate | Reconcile, never revoke | Prior verdict: GO WITH CONDITIONS, P0×0 P1×1 |
| `runs/.../audit_manifest.json:17` | Manifest | Commit binding of the run | Pin b916709 vs observed HEAD 60ab90eb |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git -C C:\temp\bench-test rev-parse HEAD` | Command | Confirm observed tree | `60ab90eb…` (VERSION 1.11.5) |
| `git rev-list --count b9167095..HEAD` | Command | Measure pin drift | `5` commits |
| `git grep -nE 'BENCH_AGENT_CONF|BENCH_UPLOAD_CONF|BENCH_BAKE_AGENT_CONF' -- .github` | Command | Reproduce baked-credential P0 | Match at `build-app.yml:63`, `build-iso.yml:64,66,70,75,77,81` |
| `git grep -nE 'join/registration token|operator API bearer' -- server/benchd.py` | Command | Reproduce single-secret claim | Match at `:26`, `:1423` |
| `git grep -nE 'world-readable' -- README.md AGENTS.md` | Command | Reproduce public exposure claim | `README.md:162,362`, `AGENTS.md:179` |
| `git grep -nE 'run_all|pytest|py_compile|unittest|tests/' -- .github` | Command | Prove no test CI gate | No matches (exit 1) |
| Read all 40 `_domains/*.json` | Aggregate | Compute P0/P1 counts | P0=3, P1=36, P2=126, P3=80 |

## Executive Summary

`bench-test` is a workstation benchmark/stress toolkit with a stdlib control plane (`server/benchd.py`), a live-USB build (`live/`), packaging (`packaging/`) and three GitHub workflows. It is real and cohesive code — roughly 245 findings across 40 domains, with four SaaS/privacy domains (multi-tenant, webhooks, billing, Supabase RLS) correctly assessed as **not applicable**. The engineering depth is genuine; the problem is where the risk concentrates.

**Strengths.** A working control plane and reporting pipeline with a stdlib test suite; per-runner API keys already exist as a concept; a recent security commit (`a3dc49b8`) closed the explicit-`runner_id` identity-takeover path and added a regression test; the deterministic lens is clean apart from CRLF and unpinned Action refs. Portability spans Windows PowerShell and an Arch live-USB.

**Biggest risk (the single root cause).** One shared `BENCHD_TOKEN` is simultaneously the low-trust runner **join** secret and the all-powerful **operator** bearer, and CI bakes it into publicly downloadable app bundles and the live ISO. Independent domains converged on this from four directions — architecture, authz, access-control and the exploit-chain lens — and I re-verified the raw facts at the current tree (`build-app.yml:63`, `build-iso.yml:66,77`, `benchd.py:26`, `README.md:162`). A downloader of any public release reads the operator token and can issue `exec`/`shell` (root on the live USB), `reboot`/`shutdown` and raw `iso_write` to every registered runner. The README's documented mitigation ("use a limited, rotatable one") is not implementable: no limited token tier exists in the code.

**Second-order themes.** (1) A separate, still-open identity flaw lets any enrolled runner seize another runner's row and API key via `machine_id` adoption — the un-fixed half of the recent security patch. (2) No CI runs the "mandatory" test suite, so `main` merges and auto-tags public releases unverified. (3) No backup/restore exists for the single SQLite system of record. (4) ~9.5k generated run files are committed to the public repo with usernames/absolute paths/hostnames.

**Release gate decision: NO-GO.** Under the pack rule (any unresolved P0 ⇒ NO-GO), the **3 unresolved P0s** — all facets of the baked public credential — block release. This **does not revoke** the prior published gate (GO WITH CONDITIONS at `4ecee97`); it records a material regression: what the earlier run rated P1 has now reproduced as P0 in three domains.

**Investment recommendation: Conditional — fix security plumbing before more features.** The toolkit's core is worth continuing, but its differentiators (remote control, live-USB fleet ops) are exactly where the trust boundary is broken. Spend the next sprint on the credential split, the identity fix and a CI gate before adding benchmarks.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Control plane | `server/benchd.py` | Fleet API + web/SSE | Functional | Single shared token = operator bearer | `:26`, `:572-580` |
| Public app bundles | `.github/workflows/build-app.yml`, `packaging/build_app.py` | Ship GUI/TUI/agent | Bakes `BENCH_AGENT_CONF` | Public artifact carries operator token | `build-app.yml:63` |
| Public live ISO | `.github/workflows/build-iso.yml`, `live/Build-LiveUSB.sh` | Bootable fleet stick | Bakes agent + upload conf | Carries operator token + repo-write PAT | `build-iso.yml:66,77` |
| Runner registration | `server/benchd.py` `_register` | Enrol/re-enrol runners | `runner_id` guarded, `machine_id` not | Another runner's key can be stolen | `:1190-1218` |
| Test suite | `tests/run_all.py` | Validation | Exists, never run in CI | Regressions ship | `git grep … .github` → none |
| Release automation | `.github/workflows/release.yml` | Tag + publish | Pushes to main with `contents:write` | Unverified auto-release | `:22-23`, `:81-107` |
| System of record | `server/data/benchd.sqlite` | All run data + keys | Single file, ignored by git | No backup/restore | `server/benchd.py:50` |
| Generated output | `results/` | Run artifacts | 9,555 files tracked | Public PII + repo bloat | `.gitignore:2` vs index |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Current state | 3 | Working stdlib control plane, tests, ISO/app builds | Security plumbing broken at the trust boundary | Split credentials, add CI, then ship |
| Strengths | 4 | Per-runner keys exist; `a3dc49b8` fixed runner_id takeover with a test | Strength not extended to machine_id path | Finish the identity model |
| Biggest risks | 1 | 3 P0 from 06/11/45 all = baked shared credential | Public artifact ⇒ fleet RCE | Rotate + split + stop baking |
| Release blockers | 1 | 3 unresolved P0 | No release gate met | NO-GO until P0s closed |
| Business/security/ops/UX impact | 2 | Remote root exec, no audit trail, no DR, no alerting | No least privilege, no attribution, no recovery | Roadmap below |
| Investment recommendation | 3 | Differentiated toolkit, real engineering | Trust boundary undermines the differentiator | Fix plumbing first |
| Next actions | 3 | Clear P0/P1 backlog across domains | No enforced release process | Add CI gate, then single-source-of-truth fixes |
| Risk counts/themes | 4 | 245 findings cleanly themed, 4 domains N/A | Evidence split across commits | Re-pin run to one commit |

## Detailed Review

### Item: Public release credential exposure (P0 cluster)

- Evidence: `build-app.yml:63`; `build-iso.yml:66,77`; `server/benchd.py:26,572-580,1220-1232`; `README.md:162`.
- What it does: CI writes a single shared token into every published app bundle and the public ISO; that same token is the operator bearer.
- How it appears to work: Runners register with it and operators authenticate with it — one secret, two privilege tiers.
- Dependencies: `packaging/build_app.py:66-84`; `live/Build-LiveUSB.sh:127-139`.
- Current controls: A README warning to rotate; nothing in code.
- Missing controls: No registration-only token, no read-only role, no startup fail-closed on missing token (`12_infra`/`06_security` P1).
- Risks: Remote root command execution on the whole fleet from a public download.
- Recommended improvement: Registration-only enrollment token, never bake an operator/PAT credential, rotate all shipped tokens.
- Suggested tests: Assert `/commands` rejects an enrollment-token bearer (403) and that no shipped file matches the operator/GitHub-token pattern.
- Suggested docs: `docs/CONTROL_PLANE.md` role matrix.

### Item: Runner identity adoption by `machine_id`

- Evidence: `server/benchd.py:1190-1218`; `tests/test_control_plane.py:46-68`.
- What it does: Re-registering with a peer's `machine_id` returns that row's `api_key`.
- Current controls: The `runner_id` path is guarded; the `machine_id` path is not.
- Risks: Impersonation, command-queue theft, data corruption.
- Recommended improvement: Require proof of ownership on the `machine_id` branch; add the mirrored regression test.

### Item: Release/CI governance

- Evidence: only 3 workflows; `release.yml:22-23,81-107`; `AGENTS.md:164-174`; `git grep` shows no test step.
- Risks: Unverified, auto-published releases from `main`.
- Recommended improvement: Required `ci.yml` (tests + compile + `bash -n` + secret scan, actions SHA-pinned) gating the release workflows.

### Item: Disaster recovery

- Evidence: `server/benchd.py:50`; `.gitignore:27`; no backup/restore artifact anywhere.
- Recommended improvement: Scheduled online-API backup + restore runbook + a backup/restore test.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| EXEC-001 | Current state | 245 findings / 40 domains | Working toolkit | Security plumbing broken | P1 | Fix plumbing first |
| EXEC-002 | Strengths | `tests/run_all.py`, commit `a3dc49b8` | Keys exist, one takeover path fixed | Not extended | P2 | Finish identity model |
| EXEC-003 | Biggest risks | Baked shared token (06/11/45) | README warning only | Public artifact ⇒ RCE | P0 | Split + rotate |
| EXEC-004 | Release blockers | 3 P0 unresolved | None | Gate not met | P0 | NO-GO |
| EXEC-005 | Business/security/ops/UX impact | No audit trail, no DR, no alerting | Ad hoc | No least privilege/attribution | P1 | Roadmap below |
| EXEC-006 | Investment recommendation | Strong core, broken trust boundary | — | — | P2 | Conditional GO on fixes |
| EXEC-007 | Next actions | P0/P1 backlog | Manual | Not enforced | P1 | CI gate + credential split |
| EXEC-008 | Risk counts/themes | P0=3 P1=36 P2=126 P3=80 | Aggregated | Commit drift | P2 | Re-pin run to one commit |

## Findings

Seven EXEC findings are recorded in the machine-readable companion (`23_executive_summary_release_gate.json`), most severe first: one P0 (gate = NO-GO), four P1 (shared-credential convergence; `machine_id` takeover; no CI gate; no DR), two P2 (commit-binding drift; generated-artifact/privacy hygiene). Each cites `file:line` or an exact command.

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Public release ⇒ fleet operator credential | P0 | High (by design) | Remote root RCE fleet-wide | `build-app.yml:63`, `build-iso.yml:66,77`, `benchd.py:26` | Split tokens; rotate; stop baking |
| Runner identity takeover via `machine_id` | P1 | Medium | Impersonation, data corruption | `benchd.py:1190-1218` | Ownership proof + test |
| Unverified auto-release from `main` | P1 | High | Regression ships publicly | `release.yml:22-23`, no test CI | Required `ci.yml` |
| Total loss of the system of record | P1 | Low/Med | All history + keys gone | `benchd.py:50`, `.gitignore:27` | Online backup + restore drill |
| Public repo leaks user/machine identifiers | P2 | High (already committed) | Permanent PII exposure | `examples/omarchy-20261009/runs-index.jsonl:1` | Untrack results; scrub |

## Recommendations

### Immediate / Release Blocking
1. Split the credential: registration-only token (cannot act as operator) vs operator credential never shipped in artifacts (remediates the 3 P0s).
2. Rotate every currently-baked token (`BENCHD_TOKEN`, `BENCH_UPLOAD_CONF` PAT); assume compromise.
3. Close the `machine_id` adoption path with an ownership proof.

### This Week
4. Add a required `ci.yml` (tests, `py_compile`, `bash -n`, gitleaks, actionlint; SHA-pinned) and make `release.yml`/`build-*` depend on it.
5. Fail closed when `BENCHD_TOKEN` is unset/placeholder; stop binding `0.0.0.0` by default.

### This Month
6. Scheduled online-API backup + `docs/DR_RUNBOOK.md` + a backup/restore test.
7. Fix run deletion to purge `logs` (and add FKs / `ON DELETE CASCADE`).
8. Add DB retention/size thresholds and surface them on `/health`.

### Later / Platform Evolution
9. Per-user operator accounts with roles and audit attribution; read-only viewer role.
10. Untrack `results/`, publish run output as CI artifacts, scrub committed examples.
11. Add SBOM/license policy for distributed bundles and the vendored LHM tree.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Add `logs` to run delete | Honors documented "+data" contract | `server/benchd.py:665-672` | Delete run → `GET /runs/<id>/logs` = 404 |
| Fail closed on missing token | Removes an open control plane | `server/benchd.py:1413-1441` | Server refuses to start without a token |
| Pin Action refs to SHAs | Removes mutable-CI supply risk | `.github/workflows/*` | `grep` shows no bare `@vN` tags |
| Add a `ci.yml` skeleton | Creates the missing gate | `.github/workflows/ci.yml` | PR runs `tests/run_all.py` |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Credential split + rotation | P0 | Control-plane owner | M | None |
| machine_id ownership proof | P1 | Control-plane owner | S | None |
| Required CI workflow | P1 | CI owner | S | Repo settings |
| Backup/restore + DR runbook | P1 | Ops owner | M | None |
| Delete-cascade fix (logs/FKs) | P1 | Data owner | S | None |
| Untrack `results/` + scrub | P2 | Repo owner | M | CI artifact publishing |

## Suggested Tests

- **Security/regression:** enrollment token is rejected on `/commands` (403); `machine_id` adoption without proof is rejected; server refuses to start with no token.
- **Unit:** delete run purges every run-scoped table; `iso_fetch` returns `ok:False` on sha256 mismatch.
- **Integration/CI:** `ci.yml` runs `tests/run_all.py` on ubuntu + windows; a red suite blocks `release.yml`.
- **DR:** backup → delete → restore → assert row counts and an artifact sha256.
- **Manual:** unsquash a built ISO and assert no `/etc/*.conf` contains `GITHUB_TOKEN`/operator token.

## Suggested Documentation Updates

- `docs/CONTROL_PLANE.md` — role/credential matrix; token scopes; fail-closed startup.
- `docs/DR_RUNBOOK.md` (new) — backup + restore procedure with RTO.
- `docs/INCIDENT_RESPONSE.md` (new) — severity, roles, comms, postmortem.
- `README.md` — replace the "use a limited, rotatable token" note once the split exists; fix stale version (v1.1.0 vs VERSION).
- `AGENTS.md` — correct "a few runs tracked" vs the ~9.5k tracked files.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which commit is authoritative — `b916709` pin or observed `60ab90eb`? | Binds the gate decision to a shippable revision | A single-commit re-run or explicit declaration |
| Are the baked secrets still live in currently-published releases? | Determines whether rotation is urgent-and-real | Release asset inspection (out of audit scope) |
| Does branch protection exist on `main`? | Determines whether required checks can be enforced | GitHub repo settings (not in repo) |

## Appendix

**Severity aggregation (this run, 40 domains, 245 findings):** P0 = 3, P1 = 36, P2 = 126, P3 = 80.

**Not-applicable domains (correctly empty):** `25_multi_tenant_isolation_attack_simulation`, `27_webhook_delivery_replay_idempotency_audit`, `29_billing_payments_reconciliation_audit`, `37_supabase_rls_policy_deep_dive` — this toolkit has no tenant/RLS, webhook-delivery, or billing surface.

**P0 sources:** `06_security_authz_tenancy_audit`, `11_supply_chain_dependency_secrets`, `45_exploit_chain_attack_path_audit`.

**Prior gate reconciliation:** `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/RELEASE_GATE.md` = GO WITH CONDITIONS (P0×0, P1×1) at `4ecee97`. Current run: 3 P0 at `b916709`/`60ab90eb`. Delta = regression; prior verdict neither granted nor revoked.

**Gate rule applied:** unresolved P0 ⇒ **NO-GO**.

## Findings

| ID | Severity | Title |
|---|---|---|
| EXEC-P0-001 | P0 | Release gate = NO-GO: 3 unresolved P0s, all about one shared operator secret baked into public artifacts |
| EXEC-P1-001 | P1 | Cross-domain convergence: a single shared BENCHD_TOKEN serves both the low-trust join tier and the highest-privilege operator tier |
| EXEC-P1-002 | P1 | Runner identity takeover via POST /register machine_id adoption is unfixed and gives an attacker another runner's API key |
| EXEC-P1-003 | P1 | No CI test/quality gate: main merges and auto-releases land with zero automated verification |
| EXEC-P1-004 | P1 | Disaster recovery is absent: the single SQLite system of record has no backup, no restore, and no exercise |
| EXEC-P2-001 | P2 | Evidence binding gap: the run is pinned to b916709 but the working tree advanced 5 commits and findings reproduce at 60ab90eb/72c18734 |
| EXEC-P2-002 | P2 | Published-artifact and privacy hygiene: ~9.5k generated files are tracked on a public repo with host/user identifiers |
