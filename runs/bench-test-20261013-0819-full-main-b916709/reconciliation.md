# Reconciliation — bench-test full-domain run

This run is bound to `bench-test` @ `b9167095` (VERSION 1.11.3). It was executed on
2026-10-13 while the target was actively moving (see `verification_log.md`). This file
records (a) adjudications of findings whose headline claim did not reproduce, and
(b) the upstream drift observed since the pin.

## Adjudications (headline claims that did not reproduce)

| Finding | Claim | Verdict | Evidence |
|---|---|---|---|
| INV-P3-002 | "multi-MB result screenshots **and a signing key**" | **partially-not-reproducible** — there is no private signing key | `live/keys/omarchy.gpg` is a **PGP public key block** (645 bytes; `file` reports "PGP public key block"; no `PRIVATE KEY` marker). It is the Omarchy/Arch package verification key, public by design. The screenshots half is accurate: the largest tracked example PNGs are ~3.2–3.9 MB under `examples/`. Keep P3, reword to drop "signing key". |
| ORCH-P3-001 | "Deterministic finding DET-P3-002 is dropped from the aggregate with no exclusion record" | **not-reproducible** | `findings.json` contains all five deterministic findings, including `DET-P3-002` (`[DEP] trivy not installed`). Nothing was excluded. |

## Upstream drift since the pin (informational)

The target advanced well past `b9167095` while the audit and remediation ran
(`1.11.3` → `1.12.x`). At the time of writing, these run findings are **fixed
upstream** and should be re-checked before remediation:

- `ARCH-P3-002` / `DATA-P2-001` / `PERF-P1-001` / `PRIV-P2-004` / `SEARCH-P2-001` —
  upstream now has a retention policy (`RETENTION_DAYS` + `retain_old_data`).
- `SEC-P3-001` — the static handler now uses a real containment check (upstream test
  `static file serving uses a real containment check`).

All other findings remain open at the current commit unless addressed by the
remediation PR stack referenced from `docs/KNOWN_ISSUES.md` in the target.

*Recorded by the audit operator; no finding was rewritten — this is an append-only
reconciliation note.*
