# Risk Register — falcon-lab run `20260930-0320-falcon-794ba31_edge-2b5bc8b`

Aggregated from the four lens reports (90 findings). Impact is a short phrase; full narrative is in the lens reports and `source_reports/`. Status: `open` = as at audit time; post-audit remediation is tracked in `follow_up_register.md`.

## P0 — Critical

| ID | Sev | Area | Title | Impact | Evidence (source) | Recommendation | Owner | Effort |
|---|---|---|---|---|---|---|---|---|
| INTG-P0-001 | P0 | INTG | Pin ↔ delivery digest mismatch; manifest overwritten in place | Release verification irreproducible | 05 §INT-C1 | Version manifest names; re-pin to a stable release; add drift check | both | M |
| INTG-P0-002 | P0 | INTG | Edge WG peer persistence claim wrong; bootstrap re-run drops the tunnel | Sensor tunnel loss (R-30 class) | 05 §INT-C2 | Make peer persistence real; non-destructive re-render; regression check | falcon | S/M |
| LIVE-P0-001 | P0 | LIVE | Offsite backup failed silently; cold tier stale; no alert | Offsite protection degraded | 06 §5.3 | Fix `.env`; re-run; add success/freshness alert | falcon/ops | S |
| LIVE-P0-002 | P0 | LIVE | New-services backup failing/unverified; archival state unproven | Recovery set incomplete | 06 §5.3 | Confirm archive contents; fix verification; alert | falcon | S/M |
| LIVE-P0-003 | P0 | LIVE | Data-LV growth ~10 GB/day; first signal only at 5 GiB guard | Disk exhaustion → writer wedge/data loss | 06 §5.1 | EVE housekeeping; retention/offload decision; <15 GiB warning | falcon | M |
| LIVE-P0-004 | P0 | LIVE | TLS-silence rule flaps hourly; 56% of alerts are noise | Operator fatigue; missed real alerts | 06 §3.5/§6 | Widen window / re-anchor rule; rename | falcon | S |

## P1 — High

| ID | Sev | Area | Title | Impact | Evidence (source) | Recommendation | Owner | Effort |
|---|---|---|---|---|---|---|---|---|
| ND-P1-001 | P1 | ND | "Authoritative" digest contradicts ledgers and verdict | False status propagation | 01 §F-01 | Generate from ledgers; verifier cross-check | falcon | S |
| ND-P1-002 | P1 | ND | `AGENTS.md` directs work at closed gates | Wasted/wrong agent work | 01 §F-02 | Generated current-state block | falcon | S |
| ND-P1-003 | P1 | ND | Dangerous scripts linked without warnings | Firewall open / ingestion down | 01 §F-03 | Warning headers; fix checklist; reclassify tests | falcon | S |
| ND-P1-004 | P1 | ND | README quick start cannot deploy the stack | Onboarding failure | 01 §F-04 | Complete `run-all.sh` or rewrite README | falcon | S/M |
| ND-P1-005 | P1 | ND | Edge status docs say hardware absent; it is live | Trust erosion; wrong planning | 03 §F-01 | Update three status lines | edge | S |
| REV-P1-001 | P1 | REV | Publication artifacts contradict the APPROVED verdict (hard-coded) | Verdict credibility | 02 §HIGH-1 | Generate from ledgers + verdict; verifier check | falcon | S |
| REV-P1-002 | P1 | REV | Independence/adoption unverifiable; appears self-closed | Production verdict unverifiable | 02 §HIGH-2 | Produce reviewer artifact; disambiguate JPB; record authorization | owner | M |
| REV-P1-003 | P1 | REV | Published verdict contradicts itself | Record integrity | 02 §HIGH-3 | Correct lines; re-verify document | falcon/reviewer | S |
| REV-P1-004 | P1 | REV | Enrollment can escalate to operator access | Fleet authority compromise | 04 §F-01 | Server-side subjects; unforgeable operator auth; reopen gates | edge | M |
| REV-P1-005 | P1 | REV | Update-apply trusts agent-writable request | Root code execution | 04 §F-02 | Root-side verification; safe extraction; negative tests | edge | M |
| REV-P1-006 | P1 | REV | `FINAL_RESPONSE.json` stale; HEAD fails phase-10 test | Machine status wrong | 04 §F-03 | Regenerate from ledger; re-run tests; amend C-101/C-106 | edge | S |
| INTG-P1-001 | P1 | INTG | No alert covers the edge path | Silent edge outages | 05 §INT-H1 | Deploy edge rules / falcon-side probes | both | M |
| INTG-P1-002 | P1 | INTG | Live code is the edge working tree | Unreviewed live behavior | 05 §INT-H2 | Pinned deployed copy + digest | edge | M |
| INTG-P1-003 | P1 | INTG | Edge PKI/DB backup local-only; outside offsite | Fleet trust loss on host loss | 05 §INT-H3 | Offsite the edge secrets (encrypted) or accept | both | S/M |
| INTG-P1-004 | P1 | INTG | Version skew across four moving references | "What is deployed?" unanswerable | 05 §INT-H4 | Freeze, rebuild, re-pin, push, record deployed digest | both | M |
| LIVE-P1-001 | P1 | LIVE | Root LV 82% unguarded; Docker growth unowned | Platform outage risk | 06 §7 P1-5 | Cleanup; move volumes; growth signal | falcon | M |
| LIVE-P1-002 | P1 | LIVE | Monitoring-of-the-monitoring gaps | Silent blindness | 06 §5.5 | Freshness metrics + staleness alerts; swap; guard; alert-eval dead-man | falcon | M |
| LIVE-P1-003 | P1 | LIVE | Never-handshaked peers invisible | Silent connectivity gaps | 06 §3.1/§5.4 | Export metric for all peers; document `.20` | falcon | S |
| LIVE-P1-004 | P1 | LIVE | Alert hygiene: benign families, Zen flood, catalogue drift | Noise; untracked rules | 06 §7 P1-8 | Exclusions; rate alert; catalogue update | falcon | S |
| LIVE-P1-005 | P1 | LIVE | Duplicate snapshots; undocumented recovery window; narrow rehearsal | Surprise data loss; restore uncertainty | 06 §3.3/§5.3 | One snapshot/day; document RPO/RTO; extend rehearsal | falcon | M |
| LIVE-P1-006 | P1 | LIVE | Runbook drift; no non-root health view | Incident response fails | 06 §4/§5 | Update four runbooks; add read-only view | falcon | M |
| LIVE-P1-007 | P1 | LIVE | Power outage had no real-time external notification | Outage detection by humans only | 06 §5.2/§5.4 | Document/tighten external watcher; dead-man | falcon/owner | M |

## P2 — Medium

| ID | Sev | Area | Title | Impact | Evidence (source) | Recommendation | Owner | Effort |
|---|---|---|---|---|---|---|---|---|
| ND-P2-001 | P2 | ND | Stale repomix pack; packed-only verification fails | Reviewer path broken | 01 §F-05 | Rebuild pack in publication flow | falcon | S |
| ND-P2-002 | P2 | ND | `FINAL_RESPONSE.json` stale, mis-bound, hardcoded | Misleading closeout | 01 §F-06 | Generate from ledger; bind commit | falcon | S |
| ND-P2-003 | P2 | ND | History secret scan mismatch (20 findings) | "Scans pass" claim false | 01 §F-07 | Scan in publication flow; update records | falcon | S |
| ND-P2-004 | P2 | ND | `PORT_PROTOCOL_MATRIX.md` materially stale | Wrong ports in diagnostics | 01 §F-08 | Refresh or mark historical | falcon | S/M |
| ND-P2-005 | P2 | ND | Tunnel test wrong port; companion opens firewall | Onboarding step fails; exposure | 01 §F-09 | Parameterize port; fix checklist | falcon | S |
| ND-P2-006 | P2 | ND | Retired synthetic probe path still targeted | False pipeline confidence | 01 §F-10 | Update bootstrap/test to ens19; canary assertions | falcon | M |
| ND-P2-007 | P2 | ND | Runbooks carry stale current state | Wrong incident actions | 01 §F-11 | Superseded notes; decision-log pointers | falcon | S |
| ND-P2-008 | P2 | ND | Contradiction ledger shows resolved items OPEN | Reconciliation confusion | 01 §F-12 | Append resolution rows | falcon | S |
| ND-P2-009 | P2 | ND | Cloudflare config not reproducible | Rebuild/change risk | 01 §F-13 | Document token/scopes; wire script | falcon | S/M |
| ND-P2-010 | P2 | ND | Live services with off-repo sources | Incomplete stack picture | 01 §F-14 | Live-services inventory | falcon | M |
| ND-P2-011 | P2 | ND | Evidence index paths unresolvable in package | Dead reviewer references | 01 §F-15 | Package-relative regeneration | falcon | S |
| ND-P2-012 | P2 | ND | OpenAPI contract missing 3 live endpoints | Incomplete contract/models | 03 §F-02 | Add paths; route-parity CI | edge | S/M |
| ND-P2-013 | P2 | ND | Summary artifacts contradict ledgers (edge) | Wrong status quoted | 03 §F-03 | Regenerate; append corrections | edge | S |
| ND-P2-014 | P2 | ND | `purge_expired()` deletes non-expired items | Latent queue data loss | 03 §F-04 | Shared cutoff; regression test | edge | S |
| ND-P2-015 | P2 | ND | `pending_directives` never decrements | Phantom dashboard state | 03 §F-05 | Expiry filter / ack path | edge | S |
| ND-P2-016 | P2 | ND | Maintenance units host-only | Non-reproducible host | 03 §F-06 | Units into `deploy/maintenance/` | edge | S |
| ND-P2-017 | P2 | ND | Release/delivery set not coherent | Wrong artifact delivered | 03 §F-07 | Freeze, rebuild, re-verify | edge | M |
| ND-P2-018 | P2 | ND | Vector profile hardcodes sensor identity/URL | Multi-sensor friction | 03 §F-08 | Template at deploy time | edge | S |
| REV-P2-001 | P2 | REV | Delivery binding drift; reviewed archive not at cited path | Ambiguous canonical delivery | 02 §MED-1 | Re-bind; unambiguous names | falcon | S |
| REV-P2-002 | P2 | REV | Reproduction claims not reproducible as written | Reviewer friction | 02 §MED-2 | Fix commands; archive-runnable checks | falcon | S |
| REV-P2-003 | P2 | REV | Evidence gaps for specific gate claims | Unsupported gate claims | 02 §MED-3 | Capture scenarios or annotate | falcon | M |
| REV-P2-004 | P2 | REV | Review package incomplete/stale (edge) | Reviewer cannot reproduce image gates | 04 §F-04 | Extend staging; rebuild | edge | S |
| REV-P2-005 | P2 | REV | P4-G02 claim unsupported by cited evidence | Unearned PASS citation | 04 §F-05 | Fix citations; attest owner flash | edge | S |
| REV-P2-006 | P2 | REV | P9-G04 flipped without owner approval | Gate integrity | 04 §F-06 | Record approval or return gate | edge/owner | S |
| REV-P2-007 | P2 | REV | No hostname verification; single CA | Impersonation risk (on-path) | 04 §F-07 | SAN verification; EKU separation | edge | M |
| INTG-P2-001 | P2 | INTG | Dashboard boundary breach; ownership ambiguous | Rollback could delete adopted file | 05 §INT-M1 | Declare owner; fix rollback note | both | S |
| INTG-P2-002 | P2 | INTG | WG peer administration inverted | Coordinated changes silently break path | 05 §INT-M2 | Document joint procedure; single owner | both | S |
| INTG-P2-003 | P2 | INTG | Secrets backup inside release surface | Secrets in release artifacts | 05 §INT-M3 | Move out; exclusion rules | edge | S |
| INTG-P2-004 | P2 | INTG | Falcon record/alert drift (catalogue, runbook, pin claim) | Untracked rule; wrong docs | 05 §INT-M4 | Update catalogue/runbook/records | falcon | S |
| INTG-P2-005 | P2 | INTG | Shared-host resource risk unowned | Joint outage exposure | 05 §INT-M5 | Joint ownership + quotas | both | M |
| LIVE-P2-001 | P2 | LIVE | Broken Network throughput panel; host NIC unmonitored | Blind spot in dashboards | 06 §3.6 | Host-netns exporter or fix panel | falcon | S |
| LIVE-P2-002 | P2 | LIVE | Leftover test indices; no retention on auditlog/top_queries/ISM history | Clutter; unbounded growth | 06 §3.3 | Cleanup + ISM policies | falcon | S |
| LIVE-P2-003 | P2 | LIVE | Mapping drift (`event_type`, `host`) | Silent empty aggregations | 06 §3.3 | Document/repair; `host.keyword` | falcon | S/M |
| LIVE-P2-004 | P2 | LIVE | Daily Suricata restart invisible | Hidden restart pattern | 06 §3.4 | Reload or uptime alert | falcon | S |
| LIVE-P2-005 | P2 | LIVE | `.env` cleartext secrets; recent terminal exposure | Credential compromise risk | 06 §7 P2-15 | Permissions review; split files; rotate | falcon/owner | M |

## P3 — Low

| ID | Sev | Area | Title | Impact | Evidence (source) | Recommendation | Owner | Effort |
|---|---|---|---|---|---|---|---|---|
| ND-P3-001 | P3 | ND | Non-existent evidence dir references | Dead references | 01 §F-16 | Fix two references | falcon | S |
| ND-P3-002 | P3 | ND | Broken repo references | Minor confusion | 01 §F-17 | Batch fix; counts from repo | falcon | S |
| ND-P3-003 | P3 | ND | Phase-0 drafts presented as current | Wrong mental model | 01 §F-18 | Historical banners / regenerate | falcon | S |
| ND-P3-004 | P3 | ND | Gate ledger historical counts | Quote errors | 01 §F-19 | Refresh notes at publication | falcon | S |
| ND-P3-005 | P3 | ND | Exception register duplicates | Reconciliation friction | 01 §F-20 | Generated status summary | falcon | S |
| ND-P3-006 | P3 | ND | No validate-before-commit enforcement | Drift enters unnoticed | 01 §F-21 | Minimal CI + hook | falcon | S/M |
| ND-P3-007 | P3 | ND | Edge repo invisible at root (Info) | Discovery friction | 01 §F-22 | Related-repos section | falcon | S |
| ND-P3-008 | P3 | ND | Dead first-boot script; README drift | Wrong script patched | 03 §F-09 | Delete/deprecate; fix text | edge | S |
| ND-P3-009 | P3 | ND | Small doc/hygiene inaccuracies (edge) | Time loss | 03 §F-10 | Batch refresh | edge | S |
| ND-P3-010 | P3 | ND | Secrets-dir hygiene (stray `control.db`, tokens) | Wrong DB opened; residue | 03 §F-11 | Remove; prune helper; document | edge | S |
| ND-P3-011 | P3 | ND | CI skips tests/route parity | Contract drift | 03 §F-12 | Parity test; document both commands | edge | S |
| REV-P3-001 | P3 | REV | Uncatalogued raw evidence (10 files) | Index gaps | 02 §LOW-1 | Backfill metadata/index | falcon | S |
| REV-P3-002 | P3 | REV | Stale supporting docs (owner inputs, progress, R-29) | Wrong status quoted | 02 §LOW-2 | Append-only refreshes | falcon | S |
| REV-P3-003 | P3 | REV | Minor integrity/format nits | Review friction | 02 §LOW-3 | Note-level corrections | falcon | S |
| REV-P3-004 | P3 | REV | P1-G06 cites failing capture | Citation defect | 04 §F-08 | Append green-run reference | edge | S |
| REV-P3-005 | P3 | REV | Truncated 45/45 evidence | Weaker citation | 04 §F-09 | Full output next build | edge | S |
| REV-P3-006 | P3 | REV | Unexplained traceback in P5-G04 negatives | Unclear evidence | 04 §F-10 | Interpretation note | edge | S |
| REV-P3-007 | P3 | REV | Stale notes/citations (rules, tests, image) | Quote errors | 04 §F-11 | Append-only refresh | edge | S |
| REV-P3-008 | P3 | REV | Expired directives counted (dup of ND-P2-015) | Phantom state | 04 §F-12 | Expiry filter | edge | S |
| REV-P3-009 | P3 | REV | Release verification not self-contained | Independent check impossible | 04 §F-13 | Publish public key; re-sign set | edge | S |
| REV-P3-010 | P3 | REV | Secrets backups in delivery dir | Secret exposure surface | 04 §F-14 | Encrypt or move; accept/decide | edge | S/M |
| REV-P3-011 | P3 | REV | Capture wrapper exports credential env | Imprecise redaction claim | 04 §F-15 | Pass only needed vars | edge | S |
| REV-P3-012 | P3 | REV | Minor code/hygiene (Info) | Small defects | 04 §F-16 | Batch cleanup | edge | S |
| INTG-P3-001 | P3 | INTG | Pin misidentifies 15140/15141 coupling | Wrong dependency model | 05 §INT-L1 | Correct pin | falcon | S |
| INTG-P3-002 | P3 | INTG | `falcon-` prefix on edge units | Ownership confusion | 05 §INT-L2 | Rename or document | edge | S |
| INTG-P3-003 | P3 | INTG | Cosmetic drift (comments, `control.db`, tokens) | Hygiene | 05 §INT-L3 | Cleanup; prune | both | S |
| INTG-P3-004 | P3 | INTG | Control plane on `0.0.0.0:9443` | Every VPN peer can reach | 05 §INT-L4 | Bind/restrict; document trust | edge | S |

## Notes

- 90 findings: P0 ×6, P1 ×22, P2 ×35, P3 ×27.
- Severity mapping and conversion notes: see `INDEX.md` and `audit_manifest.json`.
- Post-audit remediation status: `follow_up_register.md`.
