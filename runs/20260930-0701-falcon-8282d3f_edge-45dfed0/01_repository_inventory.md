# Comprehensive Repository Inventory

## Audit Metadata

- Audit name: repo-deep-dive (falcon-lab) · Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repos: central `/home/user/falcon-build` @ `8282d3fd866d91df5aa3fce8ee526fd6c5d0c54c`; edge `/home/user/falcon-edge-build` @ `45dfed050fba9c25d7f8f8b5c64526887379ce84` (dirty); delivery `/home/user/falcon-edge-delivery`
- Branch `main` (both) · Generated 2026-09-30T08:10Z · Auditor: subagent, read-only (prompts 01+02)
- Area code: INV · Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/01_repository_inventory.md`
- Limits: no root/docker/WireGuard; live checks unauthenticated/read-only; edge tree dirty (in-flight CI); delivery dir outside git

## Scope

Reviewed: root configs, Compose/systemd/workspace files, applications (central, Wazuh, edge), APIs, workers/timers, shared packages, DB/migration equivalents, GitHub metadata, tests, docs, assets, generated artifacts, Docker/deploy/infra, env examples, live snapshot. Not in depth: secret contents (root-only), Docker internals, GitHub settings, sibling prompt domains (06/11/12/13/30/36/42/43).

Repo state: central `main` in sync with `origin/main`, clean except untracked `docs/audits/` (this run). Edge `main` in sync but **dirty**: modified `.github/workflows/dependabot-merge.yml`, `closeout/OWNER_ACTIONS.md`, `docs/GITHUB_CI.md`, `ledgers/risk_register.md`; untracked `.github/workflows/boot-smoke.yml`, `automation/validation/qemu_boot_smoke.sh` — an in-flight CI round (weekly drift check, QEMU boot smoke, free-plan limits) recorded, not committed.

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `AGENTS.md`, `REPOSITORY.md`, `README.md` (both repos) | Doctrine | Conventions/change flow | Central current-state text stale (INV-P1-001) |
| `PACKAGE_DIGEST.txt`, `PACKAGE_MANIFEST.sha256` (2,067), `PACK_*` notes | Generated | Publication binding | Digest matches tree; verdict binding stale (INV-P0-002) |
| `ledgers/{gate,phase9_gate,test_execution,evidence_index}`, `risk_register.md`, `contradiction_ledger.md`, `redactions.md` | Ledgers | State source of truth | 101 PASS+1 N/A; phase9 13 PASS+1 N/A |
| `pins/images.lock` (18), `ci/validate.py`, `.github/workflows/validate.yml` | Pins/CI | Supply chain | Wazuh/mct outside check (INV-P1-002) |
| `compose/{central,probe,mct}`, `automation/wazuh/multi-node` | Compose | Runtime + pinning | Wazuh stack committed 2026-09-30 |
| `docs/architecture/*`, `docs/threat-model/THREAT_MODEL.md`, `docs/runbooks/*` | Docs | Topology/trust | Port-matrix drift (report 02) |
| `docs/phase9/review/{REVIEW_REPORT,OWNER_ADOPTION,PRODUCTION_VERDICT}.md` | Review | Verdict chain | File digests match; bindings stale |
| `review-package/` (2,067), `evidence/raw/` (933 files/461 metas), `sbom/`+`sbom/vuln/` | Generated | Deliverable + scans | Hash chain verified |
| `mct/` (856) | Vendored | MCT material | Floating tags (INV-P1-002) |
| Edge `src/`, `api/`, `tests/`, `image/`, `deploy/`, `profiles/`, `closeout/`, `ci/` | Code/docs | Edge inventory | 906 tracked; 313 test rows |
| `docs/edge/EDGE_RELEASE_PIN.md` + delivery dir | Cross-repo | Pin + release manifest | Triple mismatch (INV-P0-001) |
| `live_snapshot.txt` + live probes (`systemctl`, `ss`, `df`, `curl`, `/proc`, textfile metrics) | Live | As-built | 07:01-07:20Z |

## Verification Performed

| Check | Command / method | Result |
|---|---|---|
| Central validation | `python3 ci/validate.py` | `validation_failures=0`: yaml/json, compose pins, 102 gates, 461 captures, secret scan |
| Edge validation | `bash ci/validate.sh` (dirty tree) | `ALL PASS`: 16 ops/30 schemas, models in sync, 19 decisions, 88 gates, 318 captures, 891 files clean |
| Publication chain | `bash automation/validation/verify_publication_chain.sh` | `publication_chain_failures=0`; signed archives `fc8b9007…`, `ef6e9a10…` intact |
| Digest consistency | `sha256sum PACKAGE_MANIFEST.sha256` vs digest | Match `0e591249…` (2,067); evidence manifest `2a7f4f7b…` matches |
| Verdict binding | Compare verdict/review fields to current package | MISMATCH: verdict binds `c312ab7`/`4476fc93…` (1,168)/`adacd9a1…`; current `3ac6cd4`/`0e591249…` (2,067)/`2a7f4f7b…` |
| Edge release chain | `sha256sum` manifest vs pin and sidecar | MISMATCH: pin `dffcbbb7…`, sidecar `18681751…`, actual `3fa4a49c…`; commits `35f0793` vs `155f2446` |
| Pin template claim | `grep '10.99.0.30\|edge-sensor' config/wireguard/wg0.conf.tpl` | Not present — pin claim still false (prior INTG-P0-002 partially fixed) |
| Live services | `systemctl list-units/list-timers/status` | 27 containers, 8 active timers; backup success 2026-09-30T03:34:01Z; 2 fwupd failures (unrelated) |
| Live exposure | `ss -tuln`, unauth `curl` | 9100/8008/9443/8791/1516-1518 on 0.0.0.0; CP `:9443` 404; enrollment `:2586/v1/health` 200; APIs 401/refused |
| Live code provenance | `/proc/<pid>/{cmdline,cwd}` | Edge CP runs from dirty `/home/user/falcon-edge-build` (report 02) |
| Prior-run re-check | findings.json (90) + INTG lens | P0-001 still-open; P0-002 partially-fixed; P1-001/002/003/004 still-open |

## Executive Summary

Both repositories are structurally complete and their validators pass at the audited commits. Central has closed all gates (101 PASS + 1 N/A; phase 9 13 PASS + 1 N/A) and the publication chain verifies end-to-end. Edge is honest about limits (77 PASS / 8 BLOCKED / 3 IE; production NOT_SUPPORTED; review CONDITIONAL_PASS). The main risks live in the release-binding layer: the edge manifest's sidecar and the falcon pin both name hashes that do not match the manifest on disk; the signed verdict/review bind an older 1,168-entry package (`c312ab7`) than the delivered 2,067-entry one (`3ac6cd4`); `closeout/FINAL_RESPONSE.json` hardcodes a contradicting verdict; and README/AGENTS still describe pre-closure state. Secondary: the new Wazuh stack uses tag-only images outside the pin check/lock; the vendored `mct/` tree has floating tags/foreign CI metadata; the edge risk register reuses IDs. Fix bindings first (P0), then pin coverage and docs.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Doctrine | `AGENTS.md`, `REPOSITORY.md`, `README.md` | Rules/conventions | Present; current-state text stale | Medium | INV-P1-001 |
| CI | `ci/validate.py`, `.github/workflows/validate.yml` | Static validation | Passing; scope `compose/**` only | Medium | INV-P1-002 |
| Bootstrap | `bootstrap/*.sh` (22) | Idempotent host build | Evidence-backed | Low | 95-wireguard preserves peers |
| Central stack | `compose/central` | 11 services, digest-pinned | Live | Low | Pins checked |
| Probe stack | `compose/probe` | Suricata + vector-edge | Live | Low | UDP 514/15140 buffered |
| Wazuh stack | `automation/wazuh/multi-node` | 3 indexers + master/worker/dashboard | Live (7 containers) | Medium | Tag-only images |
| MCT material | `mct/` (856) | Vendored SOC stack | IRIS + opencanary live | Medium | Floating tags |
| Edge code | `src/falcon_{agent,control,common,cli}` | Sensor/CP/CLI | Live from working tree | High | Report 02 |
| Edge contract | `api/openapi/…yaml` + 30 schemas | API contract | In sync | Low | Lint PASS |
| Edge image | `image/*`, `bake-image.yml` | Pi image | lab8 released; live lab5 | Medium | Skew |
| Edge tests | `tests/` (31 modules; 161 tests per review) | Test estate | 304 PASS / 9 historical FAIL | Low | Append-only |
| Ledgers/evidence | `ledgers/*`, `evidence/raw/**` (933) | Truth + raw capture | Indexed/hashed | Low | Redactions recorded |
| Review package | `review-package/` (2,067) | Deliverable tree | Manifest matches; committed | Low-Med | Generated tree in git |
| Delivery | `/home/user/falcon-edge-delivery` | Signed artifacts + secrets backups | Manifest mismatched vs pin/sidecar | High | INV-P0-001 |
| Live host | `falcon` | Shared runtime | 82% root, 9.9/11 GiB RAM used | High | Report 02 |

### Sensitive inventory (paths + types only)

| Path | Type | Mode | Notes |
|---|---|---|---|
| `/srv/falcon/secrets/` | Service credentials, WG keys, tokens, TLS | Root-only dir | Contents unreadable |
| `/home/user/.env` | Owner credentials (sudo + service vars) | 0600 | Used by `capture.sh --sudo` |
| `/home/user/falcon-edge-secrets/` | Edge CA, signing seed, control-plane DB | 0700 dir; DB 0644 inside | Tighten DB to 0600 |
| `falcon-edge-delivery/*credentials*`, `*ssh-key`, `*secrets-backup*` | Device credentials, keys, encrypted backups | 0600 (some root) | Review packages 0644 (no secrets intended) |
| `evidence/raw/**` redacted | OSSEC key (EX-21 accepted), WG keys, ntfy topics | In-repo | Hashes in `ledgers/redactions.md` |

### Generated / stale artifact table

| Artifact | Generator | State | Staleness |
|---|---|---|---|
| `PACKAGE_DIGEST.txt` | `publish_digests.sh` | 2026-09-30T06:57Z; matches tree | Fresh; cites stale verdict |
| `PACKAGE_MANIFEST.sha256` | `build_review_package.sh` | 2,067 entries; hash matches | Fresh |
| `evidence/MANIFEST.sha256`, `evidence_index.csv` | `automation/evidence/*` | Hash matches digest | Fresh |
| `test_execution.csv` | `build_test_ledger.py` | 461 rows (392 PASS/63 FAIL/5 FAILED_OBS/1 TOOL_FN) | Historical FAILs by design |
| `ALERT_CATALOGUE.yaml` | `build_alert_catalogue.py` | 31 rules; no `falcon_edge_*` | Coverage gap (report 02) |
| `closeout/FINAL_RESPONSE.json` | `generate_final_response.py` | Verdict hardcoded | Contradicts digest (INV-P0-002) |
| `PRODUCTION_VERDICT.md` | Template | Binds `c312ab7`/old digests | Stale (INV-P0-002) |
| Delivery manifest + `.sha256` | `build_release_manifest.py` | `3fa4a49c…` vs sidecar `18681751…` | Stale sidecar (INV-P0-001) |
| `EDGE_RELEASE_PIN.md` | Manual | `dffcbbb7…`/`35f0793`/lab6 SBOM | Stale (INV-P0-001) |

### Unknowns

| Unknown | Why it matters | Evidence needed |
|---|---|---|
| `/srv/falcon/secrets` contents/rotation age | Secret hygiene | Root read |
| Offsite backup outcome 2026-09-30 | RPO/restore confidence | Offsite logs (root) |
| Docker inspect/health (27 containers) | Runtime vs compose | Docker access |
| Effective nft ruleset | Enforcement of bound ports | `nft list` (root) |
| GitHub branch protection | CI governance claims | Admin access |
| Edge adapter/hardware state | Fleet gates | On-device checks |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Root configs | 4 | Conventions, gitleaks, validators pass | Stale README/AGENTS state | Refresh current-state docs |
| Package/workspace files | 4 | Compose pinning PASS; lock 18 images | Wazuh/mct out of scope | Extend pin check + lock |
| Applications | 4 | Central+edge code, validators pass | Live runs from trees | Pinned deploy path |
| API services | 4 | OpenAPI 16 ops/30 schemas in sync | CP on 0.0.0.0:9443 | Bind/restrict; document |
| Workers | 4 | 8 live timers; backup success | Offsite result not surfaced | Metric + alert |
| Shared packages | 3 | `falcon_common`, automation lib | No version policy | Version map |
| Database/migrations | 3 | ISM/retention docs; control DB | No schema migration discipline | Document schema/version |
| GitHub metadata | 3 | dependabot + workflows; edge 5 | No CODEOWNERS; free-plan limits | Templates + plan decision |
| Tests | 4 | Edge 161 tests; 461/313 rows | Carried FAIL rows | Triaged classification |
| Docs | 3 | 138 doc files + runbooks | Several stale | Doc refresh round |
| Assets/public files | 4 | Dashboards/schemas/profiles | Edge dashboard w/o rules | Add rules |
| Generated artifacts | 2 | Manifests mostly consistent | Pin/sidecar/verdict/FINAL_RESPONSE stale | Fix binding chain |

## Detailed Review

### Item: Central layout, root configs, compose
- Evidence: 4,165 tracked files (review-package 2,067 · evidence 934 · mct 856 · automation 101 · docs 77); `.gitleaks.toml`; `ci/validate.py`; pinned compose.
- What/how: bootstrap → compose → evidence → package → publication chain; validation enforces parsers, pins, gates, hashes, secrets.
- Missing controls: pin scan only under `compose/**`; no cross-record binding check.
- Risks / improvement / tests: stale pins pass validation; unpinned live images; extend pin scope; add binding test; document in `docs/architecture/RELEASE_BINDING.md`.

### Item: Wazuh multi-node and MCT material
- Evidence: `automation/wazuh/multi-node/docker-compose.yml` (7 services; `wazuh/*:4.14.7` tag-only; nginx digest-pinned); `mct/README.md` line 3 (CI badge for `MaineCyberTech/soc`); `mct/compose/*` (`misp-modules:latest`, greenbone `:stable`/`:latest`, `alpine:3.20`); live shows 7 Wazuh + 5 IRIS + opencanary containers.
- What/how: live SIEM and vendored SOC material; secrets excluded; configs committed 2026-09-30.
- Missing controls: digests + lock entries; provenance/not-deployed labels.
- Risks / improvement / docs: substitution drift on the SIEM path; record digests; extend lock/check; add `mct/PROVENANCE.md`.

### Item: Edge repository
- Evidence: 906 tracked files; live CP `/proc/899424`; OpenAPI 16 ops; `ci/validate.sh` ALL PASS; 77/8/3 gates; review CONDITIONAL_PASS; FINAL_RESPONSE counts match ledger.
- What/how: sensor/agent + control plane (mTLS, tokens, ed25519 signing), image/update/recovery, CI (validate/bake/publish/boot-smoke).
- Missing controls: pinned deploy path; deployed-digest record; closeout text sync; risk ID uniqueness.
- Risks / improvement / tests: unreviewed live behavior; skew (pin 61 behind; live lab5 vs lab8); deploy from release + digest metric; digest-equality test; `docs/runbooks/DEPLOYED_STATE.md`.

### Item: Generated/delivery artifact chain
- Evidence: digest/manifest/evidence/chain checks pass; stale pin/sidecar/verdict/FINAL_RESPONSE; `review-package/` committed (2,067).
- What/how: binds delivery to commits/digests for independent reproduction.
- Missing controls: no check that cited digests resolve; no re-review trigger when the package changes post-review.
- Risks / improvement: reviewers verify wrong bytes; version manifests; atomic sidecars; binding CI; re-publication checklist.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| INV-001 | Root configs | `AGENTS.md`, `.gitleaks.toml` | Doctrine + scanner | Stale current-state text | P2 | Refresh docs |
| INV-002 | Package/workspace files | `pins/images.lock`, compose | Digest pins in `compose/**` | Wazuh/mct uncovered | P1 | Extend check |
| INV-003 | Applications | `src/**`, `compose/**` | Evidence-backed deploys | Live from working tree | P1 | Pinned deploy |
| INV-004 | API services | OpenAPI; CP live | Contract drift check | CP binds all interfaces | P2 | Bind/restrict |
| INV-005 | Workers | timers; backup 03:34Z | Timers + metrics | Offsite outcome opaque | P2 | Alert plumbing |
| INV-006 | Shared packages | `falcon_common` | Unit tests | No versioning | P3 | Version map |
| INV-007 | Database/migrations | ISM docs; control DB | Snapshots/retention | No migration discipline | P2 | Schema notes |
| INV-008 | GitHub metadata | dependabot/workflows | Pinned actions, zizmor | No CODEOWNERS; plan limits | P2 | Templates/decision |
| INV-009 | Tests | edge suites; ledgers | CI + ledgers | Carried FAIL rows | P3 | Classify |
| INV-010 | Docs | 138 files | Runbooks/maps | Several stale | P2 | Refresh round |
| INV-011 | Assets/public files | dashboards/schemas | Provisioned as code | Edge dashboard w/o rules | P2 | Add rules |
| INV-012 | Generated artifacts | digests/manifests | Hash-chain verified | Pin/sidecar/verdict stale | P0 | Binding test |

## Prior-Run Findings Checked (20260930-0320)

| Prior ID | Status now | Current evidence |
|---|---|---|
| INTG-P0-001 | still-open | Pin `dffcbbb7…` + sidecar `18681751…` vs actual `3fa4a49c…`; commits `35f0793` vs `155f2446` |
| INTG-P0-002 | partially-fixed | `95-wireguard.sh` peer preserve + regression check; pin template claim still false |
| INTG-P1-001 | still-open | `falcon_edge_*` metrics exported; 0 `falcon_edge` alert rules |
| INTG-P1-002 | still-open | Live CP runs from dirty working tree (`/proc/899424`) |
| INTG-P1-003 | still-open | Edge PKI/DB backups local-only; not in falcon offsite |
| INTG-P1-004 | still-open | Pin 61 behind; manifest commit 4 behind; live lab5 vs lab8 |
| INTG-P2-005 / P3-004 | open | 9.9/11 GiB RAM + 5.2 GiB swap; CP binds `0.0.0.0:9443` |

## Findings
### Finding ID: INV-P0-001 - Edge release manifest digest chain is broken (pin + sidecar vs file)

- Severity: P0 · Confidence: High · Area: INV (prior INTG-P0-001, still-open)
- Evidence: `docs/edge/EDGE_RELEASE_PIN.md` lines 11-17; delivery manifest + `.sha256`; `sha256sum` pin `dffcbbb7…`, sidecar `18681751…`, actual `3fa4a49c…`; manifest commit `155f2446` vs pin `35f0793`.
- What is happening: the manifest was regenerated (now with lab7/lab8 artifacts) but pin and sidecar were not updated; one unversioned filename is overwritten in place.
- Why it matters: verification against the published records checks the wrong bytes; release traceability is not reproducible.
- User / business impact: reviewers/operators cannot trust "what was released".
- Security / privacy / reliability impact: substitution would go undetected by the published checks.
- Recommended fix: version manifest names; regenerate sidecar atomically; update pin; add a drift check failing on absent/mismatched cited digests.
- Suggested validation: `sha256sum -c` the sidecar; every digest cited by the pin resolves and matches.
- Owner suggestion: both maintainers · Effort: S · Dependencies: edge release freeze
- Status: still-open
### Finding ID: INV-P0-002 - Verdict artifacts bind a superseded package and contradict the digest

- Severity: P0 · Confidence: High · Area: INV (release binding/self-consistency)
- Evidence: `PRODUCTION_VERDICT.md` lines 8-18 and `REVIEW_REPORT_2026-09-29.md` (commit `c312ab7`; manifest `4476fc93…`, 1,168; evidence `adacd9a1…`, 918) vs `PACKAGE_DIGEST.txt` lines 2-12 (`3ac6cd4`; `0e591249…`, 2,067; `2a7f4f7b…`; `APPROVED`); `closeout/generate_final_response.py` lines 65-66 hardcode `INSUFFICIENT_EVIDENCE`/`NOT_SUPPORTED`, emitted in `FINAL_RESPONSE.json` beside `open_gates: []` and a 101-PASS aggregate.
- What is happening: the signed verdict binds different bytes than the delivered package; the closeout JSON states the opposite of the digest; identity fields are hand-copied from a template.
- Why it matters: §00 binding rule violated; "APPROVED" is not reproducible from current bytes; two publication artifacts disagree.
- User / business impact: owner adoption binds an older package; conflicting release status.
- Security / privacy / reliability impact: unreviewed changes self-approve by inheritance.
- Recommended fix: re-review/re-sign the current package or revert to the reviewed commit; derive verdict/production fields from the authoritative source (never literals); refresh all identity fields from `PACKAGE_DIGEST.txt`.
- Suggested validation: verdict fields == digest values == reviewed archive digest; generator test with stubbed verdict source; CI enforcement.
- Owner suggestion: owner + falcon maintainer · Effort: M · Dependencies: reviewer availability; freeze
- Status: open
### Finding ID: INV-P1-001 - README/AGENTS still describe the pre-closure open-gate state

- Severity: P1 · Confidence: High · Area: INV (docs as operator interface)
- Evidence: `README.md` lines 8-13 ("Current state (2026-09-24) … Production readiness is not supported"); `AGENTS.md` line 72 (open P8-G10/P9 gates); `ledgers/gate_ledger.csv` 101 PASS+1 N/A; `PACKAGE_DIGEST.txt` lines 9-15 (closed 2026-09-29).
- What is happening: the first files any operator/agent reads contradict the ledgers and digest.
- Why it matters: wrong expectations; agents may follow obsolete instructions.
- User / business impact: process/status confusion.
- Security / privacy / reliability impact: indirect doctrine drift.
- Recommended fix: update both from ledgers; add a CI/docs check for stale gate phrases.
- Suggested validation: gate-summary consistency test.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: none
- Status: open (prior ND-P1-002 related)
### Finding ID: INV-P1-002 - Live images and vendored stacks sit outside the pin check

- Severity: P1 · Confidence: High · Area: INV (supply chain)
- Evidence: `automation/wazuh/multi-node/docker-compose.yml` (`wazuh/*:4.14.7` tag-only); `ci/validate.py` lines 83-84 (glob `compose/**`); `pins/images.lock` (18; no wazuh); `mct/README.md` line 3; `mct/compose/*` `misp-modules:latest`/greenbone `:stable`/`:latest`/`alpine:3.20`.
- What is happening: the most sensitive live stack (SIEM) is version-pinned only, and the vendored tree mixes `latest`/`stable` tags; both escape the digest lock and validator.
- Why it matters: TB-8 claims digest enforcement "by validation script" — not for these trees.
- User / business impact: supply-chain substitution/rollback risk; ambiguous deploy status.
- Security / privacy / reliability impact: drift/substitution undetected by CI.
- Recommended fix: record digests + lock entries for the Wazuh stack; extend the check to `automation/**`/`mct/compose/**` or document exclusions; add `mct/PROVENANCE.md` and mark not-deployed services.
- Suggested validation: negative test with an unpinned image under `automation/` fails validation.
- Owner suggestion: falcon maintainer · Effort: S · Dependencies: registry access
- Status: open
### Finding ID: INV-P2-001 - Edge risk register reuses IDs R-008 and R-009

- Severity: P2 · Confidence: High · Area: INV (append-only integrity)
- Evidence: `ledgers/risk_register.md` (edge) lines 13-16 (two R-008: VLAN reachability, under-voltage; two R-009: pre-baked enrollment, A/B boot); line 18 R-011 says "R-008 resolved" without disambiguation.
- What is happening: duplicate IDs make references ambiguous in an append-only register.
- Why it matters: later resolutions can target the wrong risk; audit cross-refs unreliable.
- Security / privacy / reliability impact: record integrity only.
- Recommended fix: suffix/renumber with supersession entries; add a uniqueness check.
- Suggested validation: ledger check fails on duplicate IDs.
- Owner suggestion: edge maintainer · Effort: S · Dependencies: none
- Status: open

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Verification binds wrong bytes | P0 | High | Release trust loss | INV-P0-001/002 | Binding test + rebind |
| Unpinned live/vendored images | P1 | Medium | Supply chain | INV-P1-002 | Digests + lock |
| Unreviewed live behavior | P1 | Medium | Silent drift | report 02 | Pinned deploy |
| Stale operator docs | P2 | High | Wrong process state | INV-P1-001 | Refresh + lint |
| Duplicate ledger IDs | P2 | Low | Ambiguous refs | INV-P2-001 | Uniqueness check |

## Recommendations

### Immediate / Release Blocking
1. Regenerate the sidecar, update the pin, add digest-resolution checks (INV-P0-001).
2. Freeze or re-review the falcon package; align verdict/digest/archive bindings; fix the generator (INV-P0-002).

### This Week
3. Extend pin validation to `automation/**`/`mct/compose/**`; digest-pin the Wazuh stack (INV-P1-002).
4. Refresh README/AGENTS current state; add a gate-summary consistency check (INV-P1-001).

### This Month
5. Add `mct/PROVENANCE.md` and a floating-tag warning; fix edge risk-register IDs (INV-P1-002, INV-P2-001).
6. Add a drift check resolving every digest cited by pins/verdicts.

### Later / Platform Evolution
7. Build a release-binding subsystem (one manifest schema for both programs; auto-derived identity fields; re-review trigger on package change).

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Update sidecar + pin digests | Restores traceability | manifest `.sha256`, `EDGE_RELEASE_PIN.md` | `sha256sum`; digest resolution |
| Fix generator verdict strings | Removes contradiction | `generate_final_response.py`, `FINAL_RESPONSE.json` | Regenerate; diff vs digest |
| Refresh README/AGENTS state | Operators see truth | `README.md`, `AGENTS.md` | Counts match ledger |
| Lock Wazuh image digests | Closes pin gap | `pins/images.lock`, `ci/validate.py` | Validation run |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| Binding/drift CI check | P0 | falcon+edge | M | Manifest versioning |
| Review/rebind or revert package | P0 | owner | M | Reviewer |
| Pinned deploy path (edge CP, relay) | P1 | edge+falcon | M | Release artifact |
| Pin coverage + Wazuh digests | P1 | falcon | S | Registry access |
| Ledger ID uniqueness check | P2 | edge | S | none |
| Docs freshness check | P2 | both | S | none |

## Suggested Tests

- Unit: generator verdict fields derive from the verdict source (no literals).
- Integration: `bindings.py` over pins/sidecar/manifest/verdict; tampered fixture must fail.
- CI/security: unpinned image under `automation/`/`mct/compose/` fails validation.
- Ledger: duplicate-ID detector for risk/gate ledgers.
- Manual: rebuild package from a clean checkout; re-run `verify_publication_chain.sh`.
- Regression: no content commit between `DELIVERED_PACKAGE_COMMIT` and review bindings.

## Suggested Documentation Updates

- `README.md` + `AGENTS.md`: current state and gate status.
- `docs/architecture/RELEASE_BINDING.md`: identity fields, sources, regeneration.
- `pins/README.md`: covered vs excluded compose trees.
- `mct/PROVENANCE.md`: source repo/commit/import date; deployed vs reference.
- Edge `docs/runbooks/DEPLOYED_STATE.md`: deployed digests.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Which package is the authoritative reviewed artifact? | Determines whether APPROVED stands | Owner/reviewer statement + freeze record |
| Was a human review done, and against which archive? | Digest says human review; `REVIEW_RECORD.md` says NOT human | Signed reviewer artifact |
| Is the Wazuh stack intended to be digest-pinned? | Pin coverage decision | Owner/doctrine statement |
| Is `mct/` live or reference material? | Inventory classification | Owner statement |
| Offsite backup outcome for 2026-09-30? | RPO/restore confidence | rclone logs/operator statement |

## Appendix

- Commands: `git log/status/ls-files/diff`, `sha256sum`, `python3 ci/validate.py`, `bash ci/validate.sh`, `verify_publication_chain.sh`, `systemctl`, `ss`, `df/free/uptime`, unauth `curl`, `/proc/<pid>`, ledger parsing.
- Central tracked mix: review-package 2,067 · evidence 934 · mct 856 · automation 101 · docs 77 · config 40 · sbom 26 · bootstrap 24 · ledgers 11 · compose 6 · pins 4 · closeout 4 · ci 3 · .github 2.
- Edge tracked mix: evidence 637 · docs 61 · tests 38 · api 33 · automation 32 · src 23 · profiles 20 · image 17 · deploy 12 · ledgers 8 · closeout 6 · ci 6 · .github 5 · config 2 · bin 1.
- Live reference: `live_snapshot.txt` lines 8-15, 28-60, 72-132, 141-143. No secret values reproduced (paths/types only).
