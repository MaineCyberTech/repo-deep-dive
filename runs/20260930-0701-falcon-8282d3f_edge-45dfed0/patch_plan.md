# Patch Plan — run `20260930-0701-falcon-8282d3f_edge-45dfed0`
Seven patch sets covering all 264 findings exactly once (256 domain/lens + 8 synthesis) (primary assignment; cross-references noted in the set narrative). Repos: `falcon-build` @ `8282d3f` (central) and `falcon-edge-build` @ `45dfed0` (edge), shared live host, delivery dir `/home/user/falcon-edge-delivery`. Owner buckets: `falcon`, `edge`, `both`, `falcon/ops`, `owner`. Effort S ≤0.5 d, M 1–3 d, L >3 d. Sequencing rule: set 1 first (release is frozen until the approval chain is honest again), then set 2 (identity substance), then sets 3–7 in parallel where files do not overlap. No finding is closed by a commit alone — it closes only when a verification pass records the artifact at the then-current commit (see Definition of Done).

| Set | Name | Findings | P0 | P1 | P2 | P3 | Primary owner | Depends on |
|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | Release blockers / approval chain | 24 | 11 | 9 | 4 | 0 | owner + falcon | freeze; reviewer availability |
| 2 | Security / isolation | 50 | 0 | 18 | 26 | 6 | edge + falcon | set 1 rotation |
| 3 | CI / supply chain | 42 | 0 | 6 | 25 | 11 | both | branch-protection admin access |
| 4 | Data / retention / backups | 47 | 0 | 16 | 27 | 4 | falcon/ops | set 2 key custody; offsite access |
| 5 | Operator experience / docs | 33 | 0 | 6 | 19 | 8 | falcon + edge | set 1 record truth |
| 6 | Observability / resilience | 40 | 0 | 16 | 17 | 7 | falcon/ops + edge | set 4 metrics exist |
| 7 | Records / verdict / evidence | 20 | 0 | 3 | 13 | 4 | falcon + owner | set 1 binding |

---

## Patch set 1 — Release blockers / approval chain

**Objective:** make the delivered artifact, its digest, its verdict, and its approval chain describe the same bytes, and restore the monitoring/backup truth needed to call the release safe.
**Findings:** `API-P0-001`, `EVID-P0-001`, `EVID-P0-002`, `INV-P0-001`, `INV-P0-002`, `LIVE-P0-001`, `LIVE-P0-002`, `RES-P0-001`, `RES-P0-002`, `REV-P0-001`, `XREPO-P0-001`, plus coupled P1/P2s: `DOC-P1-001`, `EVID-P1-001`, `EVID-P1-002`, `FEAT-P1-001`, `FEAT-P1-002`, `FLEET-P1-001`, `INV-P1-001`, `REV-P1-002`, `XREPO-P1-001`, `AI-P2-003`, `DOC-P2-004`, `HYGIENE-P2-003`, `SBOM-P2-001`.
**Concrete changes**
1. Secrets (`API-P0-001`, `EVID-P1-004` cross-ref): rotate the Wazuh cluster key and VirusTotal/Shuffle API keys; replace the literals in `automation/wazuh/multi-node/config/wazuh_cluster/etc/ossec.conf` with deploy-time lookups; append the original SHA-256 values to `ledgers/redactions.md`; rebuild `review-package/` and the delivery archive. Rewrite `automation/validation/secret_scan.py` so XML tags (`<api_key>`, `<key>`) and any 64-hex value not on a known digest line are flagged.
2. Approval chain (`EVID-P0-001`, `EVID-P0-002`, `INV-P0-002`, `REV-P0-001`, `INV-P1-001`, `FEAT-P1-002`, `DOC-P2-004`): freeze the tree; either rebuild an immutable package at the reviewed commit `c312ab7`, or re-review the exact shipped commit and re-sign. Split gate flips from publication (never one commit). Rebind `PRODUCTION_VERDICT.md`, `PACKAGE_DIGEST.txt`, `closeout/FINAL_RESPONSE.json` to one verdict source; make `generate_final_response.py` and `publish_digests.sh` read that source and fail closed on non-APPROVED content.
3. Manifest/pin lineage (`INV-P0-001`, `XREPO-P0-001`, `FLEET-P1-001`, `XREPO-P1-001`, `SBOM-P2-001`): adopt content-addressed manifest filenames; regenerate the `.sha256` sidecar atomically; delete in-place overwrite; update `docs/edge/EDGE_RELEASE_PIN.md` from the manifest; add `verify_edge_pin.sh` asserting digest/commit/SBOM/artifact names, and a falcon-side drift check that fails on any cited digest that does not resolve.
4. Package/commit consistency (`EVID-P1-001`, `FEAT-P1-001`, `DOC-P1-001`, `HYGIENE-P2-003`, `AI-P2-003`): build the package after all generation (or exclude `closeout/` and ship it separately); add a package-vs-tree diff gate; refresh `README.md`/`AGENTS.md` current-state text from the ledgers; make any summary artifact derive its verdict from `PACKAGE_DIGEST.txt`.
5. Alert path (`LIVE-P0-001`, `RES-P0-002`): make `automation/validation/heartbeat.sh` publish through the same relay path as alerts *and* to an independent instance; add a canary alert that must arrive each cycle on the independent target; add a relay-freshness rule and a watcher-age rule for `falcon_site_watcher_last_run_timestamp_seconds`; shorten the host-loss threshold with the owner; add BLIND_OPERATIONS steps.
6. Backup truth (`LIVE-P0-002`, `RES-P0-001`): emit `falcon_backup_offsite_last_success_timestamp_seconds` and a new-services last-success gauge from `bootstrap/80-offsite-backup.sh` / `backup_new_services.sh`; add 36 h stale rules; commit/rebind the 2026-09-30 offsite recovery capture; record key custody.
**Validation:** `bash automation/validation/verify_publication_chain.sh` = 0 failures; `verify_delivery.sh` binds the new archive; CI equality test verdict ↔ digest ↔ shipped packet; injected `<api_key>` fixture caught by the scanner; stop relay 15 min → independent canary arrives; force offsite failure → exactly one alert per path.
**Docs:** `docs/edge/EDGE_RELEASE_PIN.md`, `README.md`, `AGENTS.md`, `docs/runbooks/NOTIFICATION_SEPARATION_RUNBOOK.md`, `ledgers/redactions.md`, `ledgers/contradiction_ledger.md`.

---

## Patch set 2 — Security / isolation

**Objective:** remove the enrollment→operator→root ladder, the shared-key blast radius, and the plaintext trust material in the delivery surface.
**Findings:** `ACM-P1-001`, `ACM-P1-002`, `ADV-P1-001`, `ADV-P1-002`, `API-P1-001`, `ARCH-P1-003`, `CTR-P1-001`, `CTR-P1-002`, `EVID-P1-004`, `PRIV-P1-001`, `PRIV-P1-002`, `SC-P1-001`, `SEC-P1-001`, `SEC-P1-002`, `SECRET-P1-001`, `SECRET-P1-002`, `SECRET-P1-003`, `XREPO-P1-003`, `ACM-P2-001`–`ACM-P2-004`, `ADV-P2-001`–`ADV-P2-003`, `AI-P2-004`, `API-P2-005`, `ARCH-P2-001`, `ARCH-P2-002`, `CTR-P2-004`, `FLEET-P2-005`, `FLEET-P2-006`, `NOTIF-P2-001`, `PRIV-P2-001`, `SC-P2-001`, `SEC-P2-001`–`SEC-P2-005`, `SECRET-P2-004`–`SECRET-P2-007`, `ACM-P3-001`, `ACM-P3-002`, `ADV-P3-001`, `SECRET-P3-008`, `SECRET-P3-010`, `XREPO-P3-001`.
**Concrete changes**
1. Identity (`SEC-P1-001`, `API-P1-001`, `ACM-P1-001`, `ADV-P1-001`): in `src/falcon_control/pki.py`/`service.py` reject or rewrite CSR subjects at enrollment and renewal (allow only `CN=device-<uuid8>`); resolve operator role from an explicit registry/credential, not `peer_cn`; add negative tests for a `CN=operator` CSR and a renewed unmapped certificate.
2. Root trust boundary (`SEC-P1-002`, `CTR-P1-002`, `CTR-P1-001`): make `falcon-apply-update.sh` verify a control-plane signature over the request and bundle before any write; reject symlink/device members and absolute targets; run services from a pinned copy/versioned artifact instead of the user-writable tree; add symlink/forged-request negatives to `tests/phase7`.
3. Lifecycle (`ACM-P1-002`, `SEC-P2-003`, `FLEET-P2-005`, `ACM-P2-001`): enforce REVOKED/RETIRED at ingest and renewal; implement `destroyKeys` or remove it; prune expired tokens/directives; document DB-only revocation and add a CRL or fingerprint allow-list check.
4. Host/network (`ARCH-P1-003`, `ARCH-P2-001`, `XREPO-P3-001`, `ADV-P2-001`, `NOTIF-P2-001`): scope `iifname wg0 accept` in `config/nftables/falcon.nft`; bind the edge control plane to the wg0 address; require auth on the alert webhook and close the fail-open branch; align `PORT_PROTOCOL_MATRIX.md` with live binds.
5. Credential custody (`SECRET-P1-001/002/003`, `ADV-P1-002`, `PRIV-P1-002`, `PRIV-P2-001`, `SC-P2-001`, `XREPO-P1-003`, `SECRET-P2-004`–`SECRET-P2-007`): encrypt edge secrets backups and move them out of the delivery/release surface; split `/home/user/.env` by class, restrict modes, stop baking host/Wi-Fi credentials into sensor images; pass only needed variables in `automation/evidence/capture.sh` and deploy wrappers; add an owner-env inventory/validator.
6. Detection/abuse (`ADV-P2-002`, `ADV-P2-003`, `ADV-P3-001`, `API-P2-005`, `FLEET-P2-006`, `PRIV-P1-001`): authenticate sensor identity at ingest (registry check, not payload `sensor_id`); rate-limit and version the client-VPN enrollment service; redact support bundles before write; record the real-telemetry privacy position and the privacy authority decision.
**Validation:** sandbox reproductions from the security lens re-run as tests (token→operator blocked; forged apply rejected; symlink tar rejected; spoofed sensor rejected); `nft list ruleset` shows no blanket wg0 accept; secret-scan negatives pass; edge secrets backup restore works from the encrypted archive.
**Docs:** `access_control_matrix.md`, edge `docs/` identity/runbook updates, `ledgers/exception_register.md` entries where residual risk is accepted.

---

## Patch set 3 — CI / supply chain

**Objective:** make "what is deployed" verifiable and prevent the drift classes that produced the P0s.
**Findings:** `ARCH-P1-002`, `BP-P1-001`, `INTG-P1-002`, `INV-P1-002`, `SBOM-P1-001`, `XREPO-P1-004`, `AI-P2-005`, `AI-P2-006`, `API-P2-001`–`API-P2-004`, `BP-P2-001`–`BP-P2-003`, `CI-P2-001`, `CI-P2-002`, `CI-P2-004`, `CTR-P2-003`, `CTR-P2-005`, `EVOL-P2-004`, `FLEET-P2-003`, `HYGIENE-P2-001`, `SBOM-P2-002`–`SBOM-P2-004`, `SC-P2-004`, `TEST-P2-001`, `TEST-P2-002`, `TEST-P2-004`, `XREPO-P2-003`, `API-P3-001`, `API-P3-002`, `BP-P3-001`, `BP-P3-002`, `CI-P3-001`, `CI-P3-002`, `CTR-P3-006`, `CTR-P3-007`, `SBOM-P3-001`, `SC-P3-001`, `SEC-P3-001`.
**Concrete changes**
1. Branch protection (`BP-P1-001`, `BP-P2-001`–`003`, `BP-P3-001/002`): protect `main` in both repos with required checks, no force-push, review required for credential-bearing paths (bake/release), CODEOWNERS + PR template, and documented break-glass; stop bot self-merge.
2. Pipeline truth (`CI-P2-001/002/004`, `HYGIENE-P2-001`, `TEST-P2-001/002/004`, `SEC-P3-001`, `SC-P2-004`, `SC-P3-001`): make `ci/validate.py` pass with audit run folders present (exclude/whitelist with a documented lifecycle); run tests and secret scan in CI, fail closed on scanner invocation; checksum-pin downloaded CI tooling; add route-vs-contract parity test (`API-P2-001`–`004`, `API-P3-001/002`) and contract schema tests.
3. Pinning (`INV-P1-002`, `CTR-P2-003/005`, `EVOL-P2-004`, `FLEET-P2-003`, `CTR-P3-006/007`): record Wazuh/MCT image digests in `pins/images.lock`; extend the pin check to `automation/**` and `mct/compose/**` or document exclusions; reconcile live images with SBOM/pins; refresh vulnerability dispositions.
4. SBOM/license (`SBOM-P1-001`, `SBOM-P2-002`–`004`, `SBOM-P3-001`, `XREPO-P1-004`, `XREPO-P2-003`, `INTG-P1-002`): add license fields + a license gate (or encode the license-free amendment), complete SBOM coverage, make CI enforce SBOM/vuln thresholds, publish the edge signing key, add the joint release gate/upgrade-order check.
5. Hygiene (`ARCH-P1-002`, `AI-P2-005/006`): install live services from versioned artifacts; add CI human-approval enforcement for the documented gates; refresh edge CI docs.
**Validation:** protected branch rejects a direct push; a PR without required checks cannot merge; removing a documented contract path fails CI; adding an unpinned image under `automation/` fails `ci/validate.py`; `verify_edge_pin.sh` runs in CI.

---

## Patch set 4 — Data / retention / backups

**Objective:** make retention, snapshots, and backup recovery claims true and observable, and fix the latent data-loss bugs.
**Findings:** `DATA-P1-001`–`DATA-P1-003`, `DQ-P1-001`, `DR-P1-001`–`DR-P1-005`, `LIVE-P1-001`, `OBS-P1-002`, `PERF-P1-001`, `PERF-P1-002`, `RES-P1-004`–`RES-P1-006`, `DATA-P2-004`–`DATA-P2-006`, `DQ-P2-002`–`DQ-P2-008`, `DR-P2-001`, `DR-P2-002`, `EVOL-P2-003`, `FEAT-P2-001`, `FLEET-P2-007`, `INFRA-P2-003`, `INTG-P2-002`, `PERF-P2-001`, `PERF-P2-002`, `PERF-P2-004`, `PRIV-P2-002`, `RES-P2-002`, `SEARCH-P2-001`–`SEARCH-P2-004`, `TEST-P2-003`, `DATA-P3-007`, `DQ-P3-009`, `SEARCH-P3-005`, `SEARCH-P3-006`.
**Concrete changes**
1. Retention/schema (`DATA-P1-001`, `DATA-P2-004`–`006`, `DQ-P2-002/005/008`, `SEARCH-P2-001`–`004`, `PRIV-P2-002`, `DATA-P3-007`, `SEARCH-P3-005/006`): deploy the ISM/template policies currently only validated by scripts; pin every queried field (`severity`, `transport`, `host.keyword`, `event_type`); add delete/rotate counters; schedule search/audit-log retention; remove fixture indices; define cold-copy deletion scope.
2. Latent bugs (`DATA-P1-003`, `RES-P2-002`, `TEST-P2-003`, `DQ-P1-001`, `DQ-P2-003/004/006/007`): fix `purge_expired()` cutoff and directive decrement; count sink/write failures in DLQ; add canary assertions and per-feed rate bands; convert device time to UTC with per-feed skew metrics; emit spool rotation counters.
3. Backups (`DATA-P1-002`, `DR-P1-001`–`005`, `RES-P1-004`, `OBS-P1-002`, `FEAT-P2-001`, `INFRA-P2-003`, `INTG-P2-002`, `FLEET-P2-007`, `DR-P2-001/002`, `DQ-P3-009`): schedule Wazuh indexer snapshots + offsite copy (or record accepted gap); offsite/new-services metrics and 36 h rules; retained-union remote retention; config tar digests; include edge PKI/DB in offsite (encrypted); publish the dataset→backup→window→owner matrix; add index-rename rollback drill; add SD wear monitoring; join the edge restore path to central recovery.
4. Capacity (`LIVE-P1-001`, `PERF-P1-001/002`, `PERF-P2-001/002/004`, `RES-P1-005/006`): root reclaim plan + ≥90 % critical page; <15–20 GiB data warning with projection; swap alert; guard reclaim drill; incremental offsite copy; export all WireGuard peers (including never-handshaked).
**Validation:** forced ISM expiry emits metrics; `limit`/rebuild restore from offsite in scratch; `purge_expired()` mixed input test; 7-day free-space stable; guard drill frees space and pages; restore drill restores WG keys, Wazuh registry, IRIS, enrollment.

---

## Patch set 5 — Operator experience / docs

**Objective:** one truthful current-state layer; runbooks a non-root on-call can execute; onboarding that does not mutate the evidence record.
**Findings:** `AI-P1-001`, `DOC-P1-002`, `DOC-P1-003`, `INFRA-P1-001`, `LIVE-P1-002`, `ND-P1-001`, `DOC-P2-001`–`003`, `EVOL-P2-001`, `FEAT-P2-002`, `FLEET-P2-004`, `INFRA-P2-001/002`, `INTG-P2-003`, `IR-P2-001`, `LIVE-P2-001/002/004`, `ND-P2-001`–`005`, `RES-P2-003`, `FEAT-P3-001`, `FLEET-P3-008`, `HYGIENE-P3-002`, `INFRA-P3-001/002`, `ND-P3-001`, `NOTIF-P3-002`, `RES-P3-001`.
**Concrete changes**
1. Orientation (`ND-P1-001`, `ND-P2-003/004`, `ND-P3-001`, `DOC-P2-002`, `HYGIENE-P3-002`): add a generated "current state" block (from ledgers) at the top of `README.md`/`AGENTS.md`; label historical drafts; fix broken references and counts; clean dead files/duplicate register rows.
2. Onboarding (`DOC-P1-003`, `ND-P2-001/002/005`, `INFRA-P3-001`, `EVOL-P2-001`): complete or rewrite the quick start so it works in a fresh checkout; move the root-mutating script out of the "health" list and label danger; make examples append-only safe; add module template/roadmap for evolution.
3. Runbooks (`INFRA-P1-001`, `LIVE-P1-002`, `DOC-P2-001`, `RES-P2-003`, `INFRA-P2-001/002`, `INTG-P2-003`, `LIVE-P2-*`): walk each runbook read-only as non-root; annotate every step with required role; add a non-root health view; refresh topology (no VPN/SPAN/offsite claims that are false); add blind-ops and escalation contacts; fix VPN port/test drift.
4. Edge docs (`DOC-P1-002`, `FLEET-P2-004`, `FLEET-P3-008`, `FEAT-P2-002`, `FEAT-P3-001`, `NOTIF-P3-002`): correct "hardware absent" statements; provide fleet inventory verification and edge quick start/secrets map; mark the MCT imported docs as partially deployed; document notification preferences/opt-out.
**Validation:** run the literal walk of every runbook as non-root; CI lint for stale phrases and broken refs; docs tests resolve every cited evidence path.

---

## Patch set 6 — Observability / resilience

**Objective:** every silent-failure class has a detector; every detector has a firing proof; the edge fleet pages.
**Findings:** `ARCH-P1-001`, `FLEET-P1-002`, `INTG-P1-001`, `IR-P1-001/002`, `LIVE-P1-003`, `NOTIF-P1-001/002`, `OBS-P1-001`, `OBS-P1-003`–`005`, `RES-P1-001`–`003`, `XREPO-P1-002`, `EVOL-P2-002`, `INTG-P2-001`, `IR-P2-002`–`005`, `LIVE-P2-003`, `NOTIF-P2-002/003`, `OBS-P2-001`–`003`, `PERF-P2-003`, `RES-P2-001`, `XREPO-P2-001/002/004`, `EVOL-P3-001/002`, `IR-P3-001`, `NOTIF-P3-001`, `PERF-P3-001/002`, `TEST-P3-001`.
**Concrete changes**
1. Alert integrity (`NOTIF-P1-002`, `OBS-P1-001/003`, `RES-P1-001/002`): relay queue/retry with failure metric; real-time external host-loss notification; freshness rules for every timer/exporter/guard and the alert-evaluation plane; hourly heartbeat with an owner-decided threshold; alert-feed rate/absence rules.
2. Edge alerting (`OBS-P1-004`, `RES-P1-003`, `INTG-P1-001`, `XREPO-P1-002`, `LIVE-P1-003`): deploy the scoped edge rules through the operator flow (exclude RETIRED/REVOKED residue) or add central probes; fire-test `EdgeSensorSilence`.
3. Resilience (`FLEET-P1-002`, `ARCH-P1-001`, `RES-P2-001`, `IR-P2-002`, `INTG-P2-001`, `XREPO-P2-001/002/003`, `EVOL-P2-002`, `EVOL-P3-001/002`): crash-safe update swap + boot recovery; reboot-failure re-exercise; cgroup OOM protection / documented single-host acceptance; cross-repo contract versioning and upgrade/rollback tests.
4. Alert quality (`NOTIF-P2-002`, `OBS-P2-001/002/003`, `NOTIF-P2-003`, `LIVE-P2-003`, `PERF-P2-003/004`, `NOTIF-P3-001`, `TEST-P3-001`): noise filters + 7-day re-measure; Suricata rotation visibility; firing-proof backlog; throughput budget tracking; retire the external ntfy test path; reconcile quality claims.
5. Incident readiness (`IR-P1-001/002`, `IR-P2-003/004/005`, `IR-P3-001`, `EVOL-P3-001`): add total-alert-loss and CI/CD incident scenarios; complete the exercise catalogue; fix postmortem follow-through; stage release process.
**Validation:** each detector has a firing proof captured; stop each timer → one statement alert; kill Grafana → external path fires; edge silence fires for ACTIVE sensors only; QEMU kill during apply recovers on boot.

---

## Patch set 7 — Records / verdict / evidence

**Objective:** one source of truth for status; append-only registers that reconcile; reviewer independence artifacts that exist.
**Findings:** `AI-P1-002`, `EVID-P1-003`, `REV-P1-001`, `EVID-P2-001`–`003`, `HYGIENE-P2-002/004`, `INV-P2-001`, `PRIV-P2-003`, `REV-P2-001`–`003`, `SC-P2-002/003`, `TEST-P2-005`, `EVID-P3-001`, `HYGIENE-P3-001`, `PRIV-P3-001/002`.
**Concrete changes**
1. Verdict source (`REV-P1-001`, `REV-P2-001/002`, `PRIV-P2-003`): a single controlled verdict file feeds `PACKAGE_DIGEST.txt` and `FINAL_RESPONSE.json`; include NOT_APPLICABLE in aggregates (`EVID-P2-001`); contradiction ledger entries for every known conflict; reviewer-produced signed disposition and provenance test (author ≠ implementer).
2. Registers (`EVID-P2-002/003`, `HYGIENE-P2-002/004`, `INV-P2-001`, `SC-P2-002/003`): reconcile exception and contradiction registers with closures; fix `PACKAGE_MANIFEST.sha256` semantics; de-duplicate edge risk IDs; refresh progress/ledger status; record history-scan state.
3. Evidence portability (`TEST-P2-005`, `HYGIENE-P3-001`, `EVID-P1-003`, `EVID-P3-001`, `AI-P1-002`, `PRIV-P3-001/002`): rebind legacy symlinked captures; commit/stage the in-place evidence edit; add decision-log ordering column; update doctrine docs to the closed-gate state; publish identifier inventory and signing key.
**Validation:** generated-artifact equality test; aggregate sums to 14; evidence manifest verifies at HEAD; provenance test for the review record; docs test that no cited path is broken.

---

## Validation Plan
Run in order; record captures under `automation/evidence/capture.sh` and refresh derived artifacts (`automation/evidence/index.sh`, `automation/evidence/manifest.sh create`, `python3 automation/validation/build_test_ledger.py`).
1. **Repo gates:** `python3 ci/validate.py` (falcon) and edge `ci/validate.sh` — must pass at HEAD, including with the audit run folder present (patch set 3 fixes the current failure, `CI-P2-001`/`HYGIENE-P2-001`).
2. **Release chain:** `bash automation/validation/verify_publication_chain.sh` (0 failures), `verify_delivery.sh`, `sha256sum -c` on the manifest sidecar, `verify_edge_pin.sh` (new) — every cited digest resolves and matches.
3. **Secrets:** secret scan over repo, `review-package/`, delivery archives, and history; injected XML-tag and 64-hex fixtures are caught; `grep` shows the rotated literals gone; `ledgers/redactions.md` entries present.
4. **Security tests:** enrollment `CN=operator` rejection; renew-then-operator blocked; forged `apply-request.json` and symlink tar rejected; revoked cert ingest rejected; sensor spoof rejected.
5. **Alert path drills:** stop relay 15 min → independent canary + relay-freshness alert; stop heartbeat → external alert within the documented threshold; stop each timer/exporter → one staleness alert; stop Grafana → external path fires.
6. **Backup drills:** break the Spaces probe → one alert per path; scratch restore from offsite (WG keys, Wazuh registry, IRIS, enrollment, edge PKI); retention deletion test in a scratch bucket; guard reclaim drill.
7. **Data quality:** forced ISM expiry and spool rotation emit counters; rate-drop and parse-error injections alert; mixed-input `purge_expired()` test; timestamp skew metric appears for a shifted sender.
8. **Runbooks:** read-only non-root walk of SENSOR_SILENCE, DISK_PRESSURE, RESTORE, VPN, blind-ops; every step works or states its required role.
9. **CI governance:** protected-branch negative test; unpinned-image negative test; route-parity failure test; license-gate negative test.
10. **Synthesis re-run:** `tools/check_run.sh` + `tools/collect_findings.py --write --update-manifest`, then a verification-only pass recording `verified-fixed` only where an artifact at the then-current commit proves it.

## Definition of Done
A patch set is done when all of the following hold:
1. Every listed finding has either a merged fix with a captured validation artifact at the then-current commit, or an explicit `owner-accepted` entry with rationale, expiry, and register rows (finding + exception/contradiction).
2. `ci/validate.py` / `ci/validate.sh` pass at HEAD in both repos with no audit-folder or secret-scan exceptions; no new `NO_FINDINGS`-style blind spots.
3. Release artifacts are self-consistent: verdict ↔ digest ↔ shipped archive ↔ reviewed commit are equal, and the sidecar verifies the signed manifest.
4. All new alerts have a captured firing proof; all new backup/retention paths have a captured exercise; no detector uses `noDataState: OK` to mask a missing series.
5. No credential values remain in repo, package, delivery, or image; redaction entries and rotation records exist.
6. Findings move to `verified-fixed` only with the artifact; `partially-fixed` rows state exactly which residual part is open; the register and `follow_up_register.md` reconcile to the same counts.
7. A contradiction-ledger entry exists for each previously contradictory artifact; gate flips and approvals are separate commits.
8. The synthesis reports (`22`, `23`, `40`) are re-run and the run manifest `verification` block records the pass.

## Appendix — Set Membership (primary assignment, all 264 findings)

**Set 1 — Release blockers / approval chain (24):** `AI-P2-003`, `API-P0-001`, `DOC-P1-001`, `DOC-P2-004`, `EVID-P0-001`, `EVID-P0-002`, `EVID-P1-001`, `EVID-P1-002`, `FEAT-P1-001`, `FEAT-P1-002`, `FLEET-P1-001`, `HYGIENE-P2-003`, `INV-P0-001`, `INV-P0-002`, `INV-P1-001`, `LIVE-P0-001`, `LIVE-P0-002`, `RES-P0-001`, `RES-P0-002`, `REV-P0-001`, `REV-P1-002`, `SBOM-P2-001`, `XREPO-P0-001`, `XREPO-P1-001`

**Set 2 — Security / isolation (50):** `ACM-P1-001`, `ACM-P1-002`, `ACM-P2-001`, `ACM-P2-002`, `ACM-P2-003`, `ACM-P2-004`, `ACM-P3-001`, `ACM-P3-002`, `ADV-P1-001`, `ADV-P1-002`, `ADV-P2-001`, `ADV-P2-002`, `ADV-P2-003`, `ADV-P3-001`, `AI-P2-004`, `API-P1-001`, `API-P2-005`, `ARCH-P1-003`, `ARCH-P2-001`, `ARCH-P2-002`, `CTR-P1-001`, `CTR-P1-002`, `CTR-P2-004`, `EVID-P1-004`, `FLEET-P2-005`, `FLEET-P2-006`, `NOTIF-P2-001`, `PRIV-P1-001`, `PRIV-P1-002`, `PRIV-P2-001`, `SC-P1-001`, `SC-P2-001`, `SEC-P1-001`, `SEC-P1-002`, `SEC-P2-001`, `SEC-P2-002`, `SEC-P2-003`, `SEC-P2-004`, `SEC-P2-005`, `SECRET-P1-001`, `SECRET-P1-002`, `SECRET-P1-003`, `SECRET-P2-004`, `SECRET-P2-005`, `SECRET-P2-006`, `SECRET-P2-007`, `SECRET-P3-008`, `SECRET-P3-010`, `XREPO-P1-003`, `XREPO-P3-001`

**Set 3 — CI / supply chain (42):** `AI-P2-005`, `AI-P2-006`, `API-P2-001`, `API-P2-002`, `API-P2-003`, `API-P2-004`, `API-P3-001`, `API-P3-002`, `ARCH-P1-002`, `BP-P1-001`, `BP-P2-001`, `BP-P2-002`, `BP-P2-003`, `BP-P3-001`, `BP-P3-002`, `CI-P2-001`, `CI-P2-002`, `CI-P2-004`, `CI-P3-001`, `CI-P3-002`, `CTR-P2-003`, `CTR-P2-005`, `CTR-P3-006`, `CTR-P3-007`, `EVOL-P2-004`, `FLEET-P2-003`, `HYGIENE-P2-001`, `INTG-P1-002`, `INV-P1-002`, `SBOM-P1-001`, `SBOM-P2-002`, `SBOM-P2-003`, `SBOM-P2-004`, `SBOM-P3-001`, `SC-P2-004`, `SC-P3-001`, `SEC-P3-001`, `TEST-P2-001`, `TEST-P2-002`, `TEST-P2-004`, `XREPO-P1-004`, `XREPO-P2-003`

**Set 4 — Data / retention / backups (47):** `DATA-P1-001`, `DATA-P1-002`, `DATA-P1-003`, `DATA-P2-004`, `DATA-P2-005`, `DATA-P2-006`, `DATA-P3-007`, `DQ-P1-001`, `DQ-P2-002`, `DQ-P2-003`, `DQ-P2-004`, `DQ-P2-005`, `DQ-P2-006`, `DQ-P2-007`, `DQ-P2-008`, `DQ-P3-009`, `DR-P1-001`, `DR-P1-002`, `DR-P1-003`, `DR-P1-004`, `DR-P1-005`, `DR-P2-001`, `DR-P2-002`, `EVOL-P2-003`, `FEAT-P2-001`, `FLEET-P2-007`, `INFRA-P2-003`, `INTG-P2-002`, `LIVE-P1-001`, `OBS-P1-002`, `PERF-P1-001`, `PERF-P1-002`, `PERF-P2-001`, `PERF-P2-002`, `PERF-P2-004`, `PRIV-P2-002`, `RES-P1-004`, `RES-P1-005`, `RES-P1-006`, `RES-P2-002`, `SEARCH-P2-001`, `SEARCH-P2-002`, `SEARCH-P2-003`, `SEARCH-P2-004`, `SEARCH-P3-005`, `SEARCH-P3-006`, `TEST-P2-003`

**Set 5 — Operator experience / docs (33):** `AI-P1-001`, `DOC-P1-002`, `DOC-P1-003`, `DOC-P2-001`, `DOC-P2-002`, `DOC-P2-003`, `EVOL-P2-001`, `FEAT-P2-002`, `FEAT-P3-001`, `FLEET-P2-004`, `FLEET-P3-008`, `HYGIENE-P3-002`, `INFRA-P1-001`, `INFRA-P2-001`, `INFRA-P2-002`, `INFRA-P3-001`, `INFRA-P3-002`, `INTG-P2-003`, `IR-P2-001`, `LIVE-P1-002`, `LIVE-P2-001`, `LIVE-P2-002`, `LIVE-P2-004`, `ND-P1-001`, `ND-P2-001`, `ND-P2-002`, `ND-P2-003`, `ND-P2-004`, `ND-P2-005`, `ND-P3-001`, `NOTIF-P3-002`, `RES-P2-003`, `RES-P3-001`

**Set 6 — Observability / resilience (40):** `ARCH-P1-001`, `EVOL-P2-002`, `EVOL-P3-001`, `EVOL-P3-002`, `FLEET-P1-002`, `INTG-P1-001`, `INTG-P2-001`, `IR-P1-001`, `IR-P1-002`, `IR-P2-002`, `IR-P2-003`, `IR-P2-004`, `IR-P2-005`, `IR-P3-001`, `LIVE-P1-003`, `LIVE-P2-003`, `NOTIF-P1-001`, `NOTIF-P1-002`, `NOTIF-P2-002`, `NOTIF-P2-003`, `NOTIF-P3-001`, `OBS-P1-001`, `OBS-P1-003`, `OBS-P1-004`, `OBS-P1-005`, `OBS-P2-001`, `OBS-P2-002`, `OBS-P2-003`, `PERF-P2-003`, `PERF-P3-001`, `PERF-P3-002`, `RES-P1-001`, `RES-P1-002`, `RES-P1-003`, `RES-P2-001`, `TEST-P3-001`, `XREPO-P1-002`, `XREPO-P2-001`, `XREPO-P2-002`, `XREPO-P2-004`

**Set 7 — Records / verdict / evidence (20):** `AI-P1-002`, `EVID-P1-003`, `EVID-P2-001`, `EVID-P2-002`, `EVID-P2-003`, `EVID-P3-001`, `HYGIENE-P2-002`, `HYGIENE-P2-004`, `HYGIENE-P3-001`, `INV-P2-001`, `PRIV-P2-003`, `PRIV-P3-001`, `PRIV-P3-002`, `REV-P1-001`, `REV-P2-001`, `REV-P2-002`, `REV-P2-003`, `SC-P2-002`, `SC-P2-003`, `TEST-P2-005`

Total: 264 findings across 7 sets (256 domain/lens + 8 synthesis), each finding assigned exactly once.

## Synthesis findings (filed by prompts 22/23)

| ID | Set | Note |
|---|---|---|
| FINAL-P0-001 | 1 | Release cannot be approved/delivered on current evidence |
| FINAL-P0-002 | 6 | Live protection cannot detect its own failure |
| FINAL-P1-001 | 3 | findings.json lacks classification fields |
| FINAL-P1-002 | 7 | Stale-but-open statuses persist |
| FINAL-P1-003 | 3 | Run artifacts fail ci/validate.py |
| FINAL-P1-004 | 1 | No verification pass has run |
| EXEC-P1-001 | 1 | Prior-run P0s not verified-fixed |
| EXEC-P1-002 | 7 | Owner decisions pending | Cross-references between sets are noted in the set narratives.
