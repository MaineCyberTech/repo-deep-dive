# Executive Summary — falcon-lab audit run `20260930-0320-falcon-794ba31_edge-2b5bc8b`

## What this is

A **lens-focused audit run** of the falcon monitoring lab (central `falcon-build` + edge `falcon-edge-build` + the shared live host), executed 2026-09-30 ~03:20–03:45 UTC as six independent read-only audits and converted into this run folder. Findings: **90 total — 6 × P0, 22 × P1, 35 × P2, 27 × P3** across the `ND` (new developer), `REV` (independent reviewer), `INTG` (integration), and `LIVE` (live operations) lenses.

Method: read-only throughout; evidence cited per finding; reproductions confined to `/tmp` and clean clones; secrets referenced by path/type only. Full narratives: `source_reports/`.

## Headline results by audit

| Audit | Verdict |
|---|---|
| falcon-build, new developer (01) | Mechanically strong (validators, manifests, chain all green); **current-state drift misleads a newcomer**: the "authoritative" digest, `AGENTS.md`, README, and closeout artifacts describe a pre-closure world; dangerous scripts are linked as health checks; the README quick start cannot deploy |
| falcon-build, independent reviewer (02) | Internal integrity reproduced (2,043 + 930 manifests, chain 0 failures from a clone, 26 sampled captures supported); **the Phase 9 APPROVED verdict is not supported at the level claimed**: machine artifacts contradict it (hard-coded), the independence/adoption chain is attestation-based and appears self-closed, and the verdict document contradicts itself |
| falcon-edge, new developer (03) | Program real and disciplined (161 tests OK, validators pass, manifest/signature/SBOM verify, 45/45 image verification); **status docs are a generation stale** (hardware claimed absent — it is live and enrolled); contract/closeout artifacts contradict ledgers; a latent queue bug was reproduced |
| falcon-edge, independent reviewer (04) | Evidence integrity HOLDS (296/296 captures hash-verified; no fabrication); **two significant security weaknesses** (enrollment→operator privilege escalation; update-apply root trust); current HEAD fails its own phase-10 consistency test; specific gate citations (P4-G02, P9-G04, P1-G06) not supported as written. Overall: **CONDITIONAL_PASS for lab review gates; production readiness remains INSUFFICIENT_EVIDENCE** |
| Integration (05) | The joint system works live, but the pairing contract is untrustworthy: **pin digest no longer exists** (manifest overwritten); the WG peer persistence claim is false and a bootstrap re-run silently drops the tunnel; no alert covers the edge path; live edge code runs from the working tree; edge PKI backups are local-only; four-way version skew |
| Live operations (06) | Core pipeline healthy and fast (lag sub-second–1.6 s, 0 drops, probes up); **two silent backup regressions caught live** (offsite + new-services); disk is the dominant near-term risk (~10 GB/day data LV; 5 GiB guard is the first signal); 56% of alerts are one flapping rule; the Sep 28 outage produced no real-time external notification; runbooks drift from reality |

## Top risks (P0)

1. **INTG-P0-001** — pinned edge manifest digest exists nowhere; release verification irreproducible.
2. **INTG-P0-002** — a WireGuard bootstrap re-run silently drops the edge sensor tunnel (R-30 class).
3. **LIVE-P0-001** — offsite backup failed silently; cold tier one day stale; no alert.
4. **LIVE-P0-002** — new-services backup failing and unverified; recovery set unproven.
5. **LIVE-P0-003** — data LV losing ~10 GB/day with the guard as the first signal.
6. **LIVE-P0-004** — alert noise (56% one rule) masks real alerts.

## Strengths worth protecting

- Evidence discipline is sincere and unusual: manifests verify, failures are retained, contradictions are logged, no fabricated output found.
- The review/adoption/verdict separation is the right model — it needs artifacts, not replacement.
- Live monitoring works: feeds flowing, retention/snapshots succeeding locally, dual-path alert delivery reliable, dashboards mostly accurate.
- Both repos are small, coherent, and mechanically validated; the fixes above are scoped, not structural.

## Conditions to proceed (summary — full text in `RELEASE_GATE.md`)

1. Close the P0 set (6 items) with evidence.
2. Reconcile the delivery artifacts with the verdict and resolve the independence/adoption gap (`REV-P1-001..003`) — remediate or record explicit owner acceptance.
3. Fix the two edge security weaknesses (`REV-P1-004/005`) and re-verify the release (`INTG-P0-001`, `REV-P1-006`).
4. Re-pin, freeze, and push the edge release; record the deployed digest (`INTG-P1-004`).
5. Run a verification-only pass over every fixed finding; refresh the register/gate/changelog.

## Next steps

1. Apply `patch_plan.md` sets 1–2 first; record each change per doctrine.
2. Owner decisions needed: JPB disambiguation and reviewer-artifact production; P9-G04 disposition; edge alert-rules deployment; retention vs cold-offload; secrets-backup encryption/acceptance.
3. Schedule the first **full domain run** after P0/P1 closure — the lens view is covered; the domains (41–43 included) are not yet audited as domains.
4. This run folder is staged for repo wiring: copy to `falcon-build/docs/audits/repo-deep-dive/{run}/` and mirror the edge-scoped artifacts to the edge repo when the tree settles.

## Scope limitations (all audits)

No root/docker/wg for the audit account; container-internal state, live firewall/VPN internals, offsite contents, and host-side PVE protections were not independently verifiable and are marked as such throughout. The edge repo HEAD moved during the audit (`cfaf09d` → `ced99b3` → `2b5bc8b`); falcon HEAD was `794ba31` at observation.
