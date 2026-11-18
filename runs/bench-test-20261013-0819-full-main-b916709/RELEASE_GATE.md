# Release Gate

- Target: `bench-test` @ `b916709` (`main`)
- Run: `bench-test-20261013-0819-full-main-b916709`
- Decision: **NO-GO**

## Basis

- P0 x6, P1 x47, P2 x138, P3 x83.

## Blocking findings

| ID | Sev | Title |
|---|---|---|
| CHAIN-P0-001 | P0 | Single shared secret is both the runner join token and the operator bearer, and it is baked into public app bundles / live ISOs -> anyone who downloads a release gets fleet-wide remote code execution (exec/shell) on every runner |
| EXEC-P0-001 | P0 | Release gate = NO-GO: 3 unresolved P0s, all about one shared operator secret baked into public artifacts |
| FINAL-P0-001 | P0 | One shared operator/join token is baked into public app bundles and the live ISO, so any release download yields fleet-wide remote code execution (merged across 10 domains) |
| FINAL-P0-002 | P0 | A write-capable GitHub PAT is baked into the publicly downloadable live ISO, and runners auto-pull code from main, turning repo write into fleet code execution (merged across 4 domains) |
| SC-P0-001 | P0 | GitHub PAT with Contents:Read/Write is baked into the publicly-downloadable live ISO |
| SEC-P0-001 | P0 | Operator token (and a repo-write GitHub PAT) baked into public release artifacts |
| ACM-P1-001 | P1 | Shared join token is the full operator credential and is baked into public releases |
| ACM-P1-002 | P1 | machine_id adoption hands out another runner's API key |
| ADMIN-P1-001 | P1 | Shared all-powerful operator token is distributed to every runner |
| ADMIN-P1-002 | P1 | Runner identity takeover via machine_id |
| AI-P1-001 | P1 | Test suite is documented as mandatory but no CI gate runs it, so an agent can land a red change on main |
| API-P1-001 | P1 | POST /api/v1/register gives away another runner's api_key via unproven machine_id adoption |
| ARCH-P1-001 | P1 | Single shared token is both the join credential and an all-powerful operator credential, and is shipped in public artifacts |
| BP-P1-001 | P1 | No test/CI workflow exists, so no required status check can gate merges to main |
| BP-P1-002 | P1 | Release workflow writes directly to main and cuts tags with no approval or documented bypass |
| CHAIN-P1-001 | P1 | Runner identity takeover via /register machine_id adoption: any authenticated runner can claim another runner's row and is handed that row's api_key (the runner_id path was fixed, the machine_id path was not) |
| CHAIN-P1-002 | P1 | A Contents:Read/Write GitHub PAT is baked into the public live ISO and every runner auto-pulls code from main at startup -> repo write access becomes code execution on the whole fleet (CI-to-production / supply-chain chain) |
| CI-P1-001 | P1 | Build workflows bake live credentials into public release artifacts |
| CI-P1-002 | P1 | No test/lint/secret-scan CI gate; nothing runs on pull_request |
| CTR-P1-001 | P1 | Control-plane and upload bearer tokens are baked into the publicly downloadable live ISO image |
| DATA-P1-001 | P1 | DELETE /api/v1/runs/<id> does not delete the run's logs; they stay orphaned in the DB and remain readable |
| DR-P1-001 | P1 | No backup of the control-plane SQLite database, which is the single system of record |
| DR-P1-002 | P1 | Restore is never exercised: no restore script, runbook, or test; the only import path cannot rebuild the DB |
| EXEC-P1-001 | P1 | Cross-domain convergence: a single shared BENCHD_TOKEN serves both the low-trust join tier and the highest-privilege operator tier |
| EXEC-P1-002 | P1 | Runner identity takeover via POST /register machine_id adoption is unfixed and gives an attacker another runner's API key |
| EXEC-P1-003 | P1 | No CI test/quality gate: main merges and auto-releases land with zero automated verification |
| EXEC-P1-004 | P1 | Disaster recovery is absent: the single SQLite system of record has no backup, no restore, and no exercise |
| FINAL-P1-001 | P1 | Control plane fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated while bound to 0.0.0.0 (reproduced across 4 domains) |
| FINAL-P1-002 | P1 | Any enrolled runner can take over another runner's identity via unproven machine_id adoption and be handed that runner's api_key (merged across 5 domains) |
| FINAL-P1-003 | P1 | No CI test/lint/secret gate, while the release workflow self-modifies main and auto-tags with no approval (merged across 5 domains) |
| FINAL-P1-004 | P1 | Data lifecycle is unmanaged: run delete leaves logs behind (reproduced), telemetry/artifacts have no retention, and there is no backup, restore, or incident plan (merged across 6 domains) |
| FINAL-P1-005 | P1 | The most destructive operation fails open on integrity checks, and third-party code is fetched and executed without verification; no SBOM or license inventory exists (merged across 4 domains) |
| FINAL-P1-006 | P1 | ~10,000 generated result files (~55 MB, with machine PII) are committed to a public repo despite a results/ ignore rule (merged across 6 domains) |
| HYGIENE-P1-001 | P1 | 9,555 generated result files (~55 MB) committed under results/ |
| INFRA-P1-001 | P1 | benchd fails open: with no BENCHD_TOKEN it serves the full operator API unauthenticated (reproduced) |
| INFRA-P1-002 | P1 | The shared operator token is baked into publicly downloadable app bundles and the live ISO, and it is the same token that grants operator control |
| INV-P1-001 | P1 | Shared control-plane token baked into public releases |
| IR-P1-001 | P1 | No incident-response documentation, severity taxonomy, roles, or postmortem process exists anywhere in the repository |
| PERF-P1-001 | P1 | Unbounded SQLite growth: telemetry/logs/events/artifacts have no retention, cap, or capacity signal |
| PERF-P1-002 | P1 | Web dashboard re-fetches 300 full run rows and an unbounded /trends scan on every refresh tick |
| PRIV-P1-001 | P1 | Unredacted hostnames and absolute home paths (usernames) committed to the public repository |
| REL-P1-001 | P1 | No CHANGELOG and no release notes are generated for version tags; release.yml only cuts a bare tag |
| RES-P1-001 | P1 | iso_fetch returns ok=True even when SHA256SUMS verification fails, so a bad ISO is accepted for a destructive write |
| SBOM-P1-001 | P1 | No SBOM is produced for either shipped artifact set (PyInstaller app bundles and the live ISO) |
| SBOM-P1-002 | P1 | Third-party binary LibreHardwareMonitor is redistributed in release bundles with no tracked license/attribution (MPL-2.0 compliance gap) |
| SC-P1-001 | P1 | Control-plane operator token is baked into public app bundles |
| SC-P1-002 | P1 | Third-party binaries are downloaded and executed without integrity verification (LibreHardwareMonitor 'latest', nvfancontrol) |
| SEARCH-P1-001 | P1 | Deleting a run does not delete its console logs; they stay retrievable by run id |
| SEC-P1-001 | P1 | Fail-open authentication when no token is configured |
| SEC-P1-002 | P1 | /api/v1/register discloses other runners' API keys |
| SECRET-P1-001 | P1 | Shared operator/join token is baked into public app release bundles |
| SECRET-P1-002 | P1 | Write-capable GitHub PAT is baked into the public live-USB ISO |
| TEST-P1-001 | P1 | No CI job runs the test suite or any compile/lint gate |

## Verification required to change the verdict

Re-run the owning domains at the remediated commit and capture artifacts; confirm zero P0/P1 remains. This run records a delta only.

