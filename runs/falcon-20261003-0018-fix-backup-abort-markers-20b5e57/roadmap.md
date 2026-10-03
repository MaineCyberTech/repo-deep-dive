# Roadmap

Run `20261003-0018-fix-backup-abort-markers-20b5e57` — `falcon` @ `20b5e57`.
Grouped by remediation window; IDs map to the domain reports and `risk_register.md`.

## Immediate (release-blocking, same day)

| Item | Findings | Owner | Effort |
|---|---|---|---|
| Rebuild/rebind the delivery chain; add digest↔closeout↔manifest↔HEAD CI test | FINAL-P0-001, HYG-P0-001, HYG-P0-002 | owner | M |
| Fix the abort-marker contract (clear on clean completion; marker on failure exits) | ARCH-P1-002 | ops/resilience | S |
| Make monitoring-death detection independent of the textfile exporter | OBS-P0-001 | observability | M |

## This week

| Item | Findings | Owner | Effort |
|---|---|---|---|
| Extend the abort trap to offsite/cold-copy/indexer/restore | ARCH-P2-005 | ops/resilience | S |
| Add offsite retry/backoff + dead-letter + alert | FEAT-P2-002 | ops/resilience | M |
| Per-path relay delivery metrics | OBS-P1-003 | observability | M |
| Set Wazuh/IRIS retention | DATA-P1-001 | data owner | M |
| Narrow wg0 accept; fence OpenCanary ports; reconcile inbound state | SEC-P1-001, SEC-P1-002, SEC-P1-003 | ops+owner | M |
| Close digest-gate scope hole; gate vulnerabilities | SUPPLY-P1-001, SUPPLY-P1-002 | supply-chain | M |
| Make the pairing contract verifiable from a clone | API-P1-001 | release owner | M |
| Enrollment token expiry | API-P2-001 | release owner | S |

## This month

| Item | Findings | Owner | Effort |
|---|---|---|---|
| Origin auth (or testable acceptance) on public routers | SEC-P2-001 | ops+owner | M |
| Move Cloudflare token off argv | SEC-P2-002 | ops+owner | S |
| Redeploy declared container hardening | ARCH-P2-001 | container/ops | S |
| Bring Wazuh/MCT images into pin/SBOM scope | ARCH-P2-002 | supply-chain | M |
| Narrow gitleaks allowlists; lock-age gate | SUPPLY-P2-001, SUPPLY-P2-002 | supply-chain | S |
| Rule linter + de-duplication; expression style | OBS-P1-001, OBS-P1-002 | observability | M |
| Package drift check; move SBOM output to CI artifacts | HYG-P1-001, HYG-P2-001 | owner | M |
| Environment-gated auto-merge | CI-P2-002 | owner | S |
| Repo-relative test-ledger provenance; `--fast` gate | TEST-P1-001, TEST-P1-002 | build/QA | M |
| Stubbed backup/offsite/restore e2e test | TEST-P2-001 | build/QA | M |
| Single-source schema for `event_time` | DATA-P2-001 | data owner | M |
| Generated-artifact regeneration/drift policy | INV-P2-001 | release owner | M |
| MCT adopt-or-archive enforcement | FEAT-P2-001 | maintainer | M |
| mTLS/signing + idempotency for ingest | ARCH-P2-003, API-P2-002 | release owner | M |

## This quarter / platform evolution

| Item | Findings | Owner | Effort |
|---|---|---|---|
| Warm standby / shorter dead-man window | ARCH-P1-001 | owner/ops | L |
| Rate-limit hardening (trusted client IP) | SEC-P2-003 (context) | ops | M |
| DOCKER-USER assertions in CI | SEC-P3-001 | ops | S |
| verify-digests full RepoDigests set | SUPPLY-P3-001 | supply-chain | S |
| Relative evidence paths | INV-P3-001 | release owner | S |
| Policy-as-code for branch protection | CI-P1-002 | owner | M |

## Sequencing note

C0 (release integrity) is independent and can proceed in parallel with C1–C6. Within resilience, fix the marker contract (ARCH-P1-002) before extending the trap (ARCH-P2-005) and adding retry (FEAT-P2-002), because the retry logic should write the same marker.
