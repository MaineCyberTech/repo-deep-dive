# Automation Guide — portable checks for any repo

Deterministic `grep` / `glob` / `read` starters for the audit agent and for CI.
They complement the prompts; they never replace evidence judgment. Every check
ends in either a cited finding or an explicit `Unknown` per the shared rules.

## 0. Start every repo with the inventory tool

```bash
python3 tools/repo_inventory.py <repo-root> -o /tmp/inventory.json
```

Use its `stacks`, `routes`, `migrations`, `workflows`, and `containers`
sections to fill the path map below, then run prompt `01`. When a path family
does not exist in this repo, skip its checks and record the absence as
evidence (e.g. "no `Dockerfile` in tree") — never force-fit another repo's
layout.

## 1. Path map (fill per repo, keep in the run INDEX)

| Family | This repo's paths | Prompts |
|---|---|---|
| API routes / handlers | | `08`, `06`, `24`, `45` |
| Auth / session code | | `06`, `24` |
| Migrations / schema | | `07` |
| Frontend routes / components | | `04`, `05` |
| CI workflows | | `10`, `34` |
| Dependencies / lockfiles | | `11`, `35` |
| Containers / deploy | | `36`, `12` |
| Secrets / env samples | | `38`, `11` |
| Tests | | `09` |
| Docs / runbooks | | `16` |

## 2. Portable check recipes

Conventions: `grep -ri` (case-insensitive), `glob **` (recursive), `read`
(first 100 lines suffice for a negative). Record the exact command and its
observed output under `Verification Performed`.

### Security / auth (`06`, `24`, `45`)

- `grep -ri "requireAuth\|requireOrgAccess\|authorize\|policy" <api-handlers>/` — every entity handler must reference an authz check; list files with none.
- `grep -ri "httpOnly\|secure.*cookie\|sameSite" <auth-files>` — expect all three flags.
- `grep -ri "jsonwebtoken\|jwt.verify\|getUser\|verify.*token" <auth-files>` — map the verification chain and its fallback; flag fallbacks without timeouts.
- `grep -ri "helmet\|content-security-policy\|strict-transport-security" <api-app>` — expect presence or an explicit `Unknown`.
- `grep -ri "rate.?limit\|throttle" <api-app> <api-handlers>/` — flag expensive unauthenticated endpoints with no limit (feeds `45` availability chains).
- `grep -ri "RateLimit\|limiter" <api-app>` — limits must be keyed beyond IP where accounts exist; per-IP-only on auth endpoints falls to IP rotation, so expect a per-account or per-email key (`06`).
- `grep -rn "from(['\"]<table>" <api-src>/` per table from the migration list — tables never referenced are dead schema or missing features (`07`).

### Secrets / env (`38`, `11`)

- `glob **/.env.example **/.env.sample` — every secret-like key must use an obvious placeholder (`<your-…>`, `changeme`, `placeholder`); a real-looking value is a P0.
- `grep -ri "BEGIN [A-Z ]*PRIVATE KEY\|AKIA\|ghp_\|xox[bap]" --exclude-dir=node_modules .` — any hit is path + type only, value redacted.
- `grep -rn "secrets\." .github/workflows/` — secrets must flow through `env:` blocks, never inline in `run:` commands.
- Filenames from `repo_inventory.py` `secret_adjacent_files` — confirm each is tracked intentionally, backed up, and rotation-covered, or file a finding.

### Supply chain / SBOM (`11`, `35`)

- Lockfile present and committed (`pnpm-lock.yaml` / `package-lock.json` / `poetry.lock` / `Cargo.lock` / `go.sum`)? Absence is P0-adjacent for release confidence.
- `glob **/Dockerfile*` — read each: pinned base image tag (not `latest`), non-root user, no secret `COPY`.
- Dependency bot config present (`.github/dependabot.yml`, Renovate)? Absence is P2.
- SBOM artifact per release? Absence is a `35` finding.

### CI / branch protection (`10`, `34`)

- `glob .github/workflows/*.yml` — each prod-deploying workflow needs an `environment:` with required reviewers; test and lint jobs must exist.
- `grep -ri "pull_request_target\|workflow_run" .github/workflows/` — each hit needs a justification review (privileged trigger).
- `grep -ri "permissions:" .github/workflows/` — expect least-privilege blocks, not job-wide `write`.

### Data / migrations (`07`, `44`)

- Migration filenames follow one pattern; gaps/renames get listed (`repo_inventory.py` `migrations`).
- Oldest vs newest schema for the same store: diff field names/types, list consumer impact.
- One consumer query/aggregation executed or read against the real mapping per major path; silent-empty results are findings.
- `grep -ri "router.patch\|\.patch(\|If-Match\|ETag\|version.*check" <api-handlers>/` — mutations need an optimistic-locking or version precondition; PATCH-style updates without one risk silent overwrites (`07`).

### API contracts (`08`, `42`)

- Route list from `repo_inventory.py` `routes` vs the documented contract vs the client/SDK usage: three-way table, every mismatch is a finding.
- Unused client methods and undocumented routes both count.

### Resilience / observability (`13`, `14`, `32`, `33`)

- `grep -ri "retry\|backoff" <src>` / `circuit.?breaker` / `AbortSignal\|timeout` — absence on external calls is P1/P2.
- `grep -ri "SIGTERM\|SIGINT" <entry-points>` — graceful shutdown expected.
- Health endpoint exists and is exercised by something outside the monitored stack.
- Last real backup-restore exercise with evidence, or `not exercised`.
- `grep -ri "catch" <ui-components>/` — bulk workflows must surface per-item ok/error states; a single success message over partially failed items is a false success (`04`).

### Webhooks (`27`)

- `grep -ri "constructEvent\|verifySignature\|webhook.*secret" <webhook-handlers>/` — every inbound endpoint verifies signatures; unsigned or timestamp-less webhooks are high risk.
- Verify the signature is computed over the raw request body; frameworks that parse before verifying break validation.

### Frontend (`04`, `05`)

- Route groups without `loading`/`error` boundaries get listed per group.
- Duplicate component stems across 3+ locations get listed as consolidation candidates.
- Pages missing titles/metadata get counted (`x/y` with evidence).

## 3. Where the retired packs' checks live now

| Retired check | New home |
|---|---|
| hardening 8-domain `automation:` grep blocks | §2 recipes above (generalized; MCT paths replaced by the §1 map) |
| hardening `merge_findings` / `reconcile` | `tools/collect_findings.py` (IDs) + prompt `22` (judgment) |
| hardening `global_risk_engine` / portal `analytics_engine` score | `tools/risk_score.py` (one formula, documented) |
| hardening/portal dashboards, badges, PR comments | `tools/render_dashboard.py` + `ci/audit.yml` |
| hardening `deep_adversarial_audit` attack trees | prompt `45` (evidence-bound chains, no hardcoded paths) |
| hardening v2 checks (per-account rate limits, webhook raw-body signatures, PATCH version checks, bulk per-item errors) | §2 recipes + prompts `06`, `27`, `07`, `04` |
| portal 7-phase engine (inventory → gate) | `tools/repo_inventory.py` (phase 1) → prompts `01`–`23` → `tools/risk_score.py` (phase 7) |
| portal operator manual / troubleshooting | `runbooks/OPERATOR_QUICKSTART*.md` + `runbooks/OPERATOR_TROUBLESHOOTING.md` |
| portal history/diff/trend engines | `runs/INDEX.md` (append-only) + `tools/diff_runs.py` |

## 4. Rules for adding a check

1. Repo-agnostic first: glob patterns and path-map variables, never a hardcoded monorepo layout.
2. Each check states its `expect:` line (what "good" looks like) and its prompt home.
3. Negative results are evidence too — record the command, the empty output, and the resulting `Unknown` or finding.
4. Never print secret values; never run destructive commands; never mutate the target repo.
