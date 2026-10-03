# Patch Plan — falcon-lab run `20260930-0320-falcon-794ba31_edge-2b5bc8b`

Patch sets group the 90 findings into safe, reviewable changes. Each set should be applied through the normal repo flow (branch → change → tests → docs → evidence → ledger), not by the audit.

## Patch Set 1 - Release blockers

| Finding | Change |
|---|---|
| INTG-P0-001 | Version manifest filenames; re-pin (digest + commit + SBOM + signature); add a cross-repo drift check that fails when the pinned digest is absent |
| INTG-P0-002 | Make edge peer persistence real (template/config-managed or dedicated non-destructive step); keep runtime peers through re-renders; regression check |
| LIVE-P0-001 | Quote `.env` values; re-run offsite; add offsite success/freshness metric + alert |
| LIVE-P0-002 | Confirm new-services archive contents; fix the verification logic; add success/freshness alert |
| LIVE-P0-003 | Automate EVE housekeeping; decide retention vs R2 cold-offload; add <15 GiB warning alert |
| LIVE-P0-004 | Re-anchor/widen the TLS-silence rule; rename to what it watches |

## Patch Set 2 - Security and isolation

| Finding | Change |
|---|---|
| REV-P1-004 | Server-generated sensor subjects; unforgeable operator authentication (separate CA/EKU); reopen P2-G02/P2-G03 |
| REV-P1-005 | Root-side verification of updates; constrain request paths; `extractall(filter="data")`; negative tests |
| REV-P2-007 | Enable control-plane hostname/SAN verification; separate server/client issuance |
| ND-P1-003 | Warning headers on dangerous scripts; checklist points at read-only battery |
| LIVE-P2-005 / REV-P3-010 / REV-P3-011 / INTG-P2-003 | Secret handling: rotate exposed credentials; permissions review; move secrets backups out of the release surface; capture wrapper passes only needed vars |
| INTG-P3-004 | Restrict control-plane binding to the tunnel or nft rules |

## Patch Set 3 - CI/CD and supply chain

| Finding | Change |
|---|---|
| ND-P2-001 / ND-P2-003 / ND-P2-017 | Publication flow runs pack rebuild, history scan, and artifact-coherence checks |
| ND-P2-002 / ND-P2-013 / REV-P1-001 / REV-P1-006 | Generated closeout artifacts derive from ledgers; commit bound at generation; phase-10 consistency test green |
| REV-P2-001 / REV-P2-002 / REV-P3-009 | Unambiguous delivery naming; archive-runnable verification; publish signing public key |
| ND-P3-006 / ND-P3-011 | Minimal CI (validate + tests + route parity) and/or hooks |
| INTG-P1-004 | Freeze release commit; rebuild artifacts; re-pin; push both repos |

## Patch Set 4 - Data, retention and backups

| Finding | Change |
|---|---|
| LIVE-P0-003 | EVE rotation/compression; retention or offload decision; warning band |
| LIVE-P1-005 | One snapshot/day; document RPO/RTO + post-deletion window; extend clean-host rehearsal (R2/Wazuh/IRIS/edge) |
| LIVE-P2-002 / LIVE-P2-003 | Index cleanup; ISM for auditlog/top_queries/ISM history; mapping repair (`event_type`, `host.keyword`) |
| ND-P2-014 | Queue cutoff fix + mixed-queue regression test |
| ND-P2-015 / REV-P3-008 | Directive expiry filter / acknowledgement path |

## Patch Set 5 - Operator experience and onboarding

| Finding | Change |
|---|---|
| ND-P1-001 / ND-P1-002 / ND-P2-002 | Generated current-state block (digest, AGENTS, README, REPOSITORY) sourced from ledgers |
| ND-P1-004 / ND-P2-001 / ND-P2-006 | README quick start fixed; pack rebuilt; probe path matches as-built |
| ND-P2-004 / ND-P2-005 / ND-P2-007 / ND-P2-008 / ND-P2-009 / ND-P2-010 / ND-P2-011 | Port matrix refresh; tunnel test port; runbook superseded notes; contradiction resolutions; Cloudflare reproducibility; live-services inventory; evidence-index paths |
| ND-P1-005 / ND-P2-012 / ND-P2-016 / ND-P2-018 | Edge status lines; OpenAPI completion + parity; maintenance units in repo; templated Vector profile |
| ND-P3-001…ND-P3-010 / REV-P3-002 | Documentation/hygiene batch (references, banners, counts, register status summary, secrets layout) |

## Patch Set 6 - Observability and resilience

| Finding | Change |
|---|---|
| LIVE-P0-004 / LIVE-P1-004 | Alert noise reduction; catalogue regeneration from live rules |
| LIVE-P1-002 / LIVE-P2-001 / LIVE-P2-004 | Freshness metrics + staleness alerts (exporter, probe); swap alert; guard-metric alert; alert-eval dead-man; NIC panel repair |
| LIVE-P1-001 / INTG-P2-005 | Root LV cleanup + growth signal; joint resource ownership |
| LIVE-P1-003 | Metric for never-handshaked peers; document/retire `.20` |
| LIVE-P1-006 / LIVE-P1-007 | Runbook refresh; non-root health view; external watcher documented and tightened |
| INTG-P1-001 / INTG-P2-004 | Edge alert rules deployed (additively) or falcon-side probes; catalogue/runbook updates |
| INTG-P1-002 / INTG-P1-003 | Pinned deployed copy + digest; offsite the edge PKI/DB (encrypted) or accept |
| REV-P2-003 | Capture the missing gate scenarios or annotate claims |

## Patch Set 7 - Records, verdict and documentation integrity

| Finding | Change |
|---|---|
| REV-P1-002 / REV-P1-003 / REV-P2-005 / REV-P2-006 | Reviewer artifact produced; JPB disambiguation; owner authorization recorded; verdict lines corrected; gate citations fixed |
| REV-P3-001 / REV-P3-004 / REV-P3-005 / REV-P3-006 / REV-P3-007 / REV-P3-012 | Evidence index/metadata backfill; citation/annotation refreshes; minor code cleanup |
| ND-P2-013 / ND-P3-004 / ND-P3-005 | Closeout/ledger note refreshes; exception status summary |
| INTG-P2-001 / INTG-P2-002 / INTG-P3-001 / INTG-P3-002 / INTG-P3-003 | Dashboard ownership declared; joint WG procedure; pin coupling fix; unit naming; cosmetic drift |
| REV-P3-010 / INTG-P2-003 | Secrets-in-delivery decision recorded (encrypt or owner-accept) |

## Validation Plan

1. Per set: the repo's normal validators (`ci/validate.sh`, test suites) plus set-specific checks (negative tests for Set 2; phase-10 consistency for Set 3; free-space trend for Set 4; runbook walk-throughs for Set 5; alert-fires-when-simulated for Set 6; claim-vs-evidence re-sampling for Set 7).
2. Evidence captured per doctrine (capture tooling, hashes, ledger rows) — no claim without an artifact.
3. After Sets 1–3: re-run the affected lens checks; after all sets: a **verification-only pass** over every fixed finding.
4. Refresh `22`/`23`/`40` equivalents (risk register, gate, changelog) at the next synthesis.

## Definition of Done

- Every P0 finding: fixed, evidenced, and marked `verified-fixed` in a verification pass (or explicitly owner-accepted with a recorded rationale).
- Every P1 finding: fixed or scheduled with an owner and date.
- No finding closed without an artifact that supports the closure.
- Decision log updated; risk register and follow-up register reconciled.
- The next full domain run starts from a clean, consistent tree.
