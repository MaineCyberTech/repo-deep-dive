# Roadmap (20261003-0018-fix-trust-root-87532ec)

Seqencing: fix the P1 first, then the controls that protect the release, then
hardening. Effort scale S/M/L = ≤0.5d / 1–3d / >3d.

## 7-day plan (this week)

| Item | Finding(s) | Owner | Effort |
|---|---|---|---|
| Enrollment revocation guard + regression test | SEC-P1-001, TEST-P2-002 | security/build-agent | S |
| Dependabot merge head binding | CI-P2-002 | build-agent | S |
| Pin/hash CI deps + tool checksums; git-history secret scan | SC-P2-001/002/003 | build-agent/security | S |
| Fix documented test counts and Dependabot cadence | TEST-P2-001, HYG-P2-001, CI-P3-001 | build-agent | S |
| Idempotency TTL prune | DATA-P2-001 | build-agent | S |

## 30-day plan

| Item | Finding(s) | Owner | Effort |
|---|---|---|---|
| Alert delivery path (critical receiver + self-test) | OBS-P2-001 | owner | M |
| Schema migrations + FK enforcement + retention | DATA-P2-002/003 | build-agent | M |
| Inventory DB permissions; pin SSH host keys | SEC-P2-002/003 | build-agent | S |
| Derived-artifact regeneration guards | HYG-P2-002, INV-P3-001 | build-agent | S |
| Cursor pagination (or contract removal) | API-P2-001 | build-agent | M |
| Populate/remove `queueDepth` | FEAT-P2-001, API-P2-002 | build-agent | S |
| Transport rate limits + security headers | SEC-P2-001, ARCH-P3-001 | build-agent | M |
| Fix or remove stale `pending_directives` metric | OBS-P3-001 | build-agent | S |

## 60-day plan

| Item | Finding(s) | Owner | Effort |
|---|---|---|---|
| Pin the deployed control-plane tree; operational dirty-tree alarm | ARCH-P2-001 | build-agent | M |
| Evidence retention/size gate + archive | INV-P2-001 | build-agent | M |
| Per-sensor inventory metric export | OBS-P2-002 | build-agent | M |
| CI coverage floor; stabilize time-relative fixtures | TEST-P3-001/002 | build-agent | S |
| Inventory tooling fix (routes/schema/entry points) | INV-P2-002 | tooling | M |

## 90-day plan / platform evolution

| Item | Finding(s) | Owner | Effort |
|---|---|---|---|
| Dedicated edge control-plane host (remove shared-host SPOF) | ARCH-P2-002 | owner | L |
| Multi-site tenant/isolation model | ARCH (tenant) | owner | L |
| Artifact attestation (cosign/SLSA) + encrypted credential side-files | SC-P2-004, SC SBOM | build-agent | M |
| Complete P10 owner gates for production readiness | EXEC-P2-001 | owner | L |

## Definition of Done

- 0 P0; P1 merged with a test that fails before and passes after.
- `ci/validate.sh` ALL PASS at the fix commit, captured as evidence.
- Docs/status derived from CI artifacts, not hand-maintained constants.
- Production claim remains unasserted until P10-G02/G04/G06 complete.
