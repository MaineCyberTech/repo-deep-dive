# Release notes draft — snowride @ `38b34a9`

Companion artifact for `40_release_notes_changelog_generator.md`. Draft only;
not an attested release.

## Audit run `snowride-20261005-full-main-38b34a9`

Full-domain deep dive at `38b34a9` (main): 43 domains, 42 findings
(P0 x0, P1 x1, P2 x7, P3 x34). Verdict: **GO WITH CONDITIONS** — bounded runtime
use, not an attested release.

### Blocking condition

- `FINAL-P1-001` — the committed launch attestation covers commit `9125913`
  while HEAD is `38b34a9`; the runtime gate correctly fails closed
  (`commit_mismatch`). Re-attest at the released HEAD and migration head
  `0057`, including built image digests.

### Highlights since the 2026-10-03 run

- Branch protection / required checks proven policy-consistent
  (`foundation`, `migrations`, `e2e`, `license-and-vulnerability`).
- Signature-verified owner approval replaces free text (`SEC-P1-001`).
- SBOM generated and uploaded commit-bound; licence allow-list merge-gating.
- Assurance schedule version-controlled (`OBS-P1-001`).
- `@grpc/grpc-js` bumped to 1.14.5; production advisory gate now blocking.

### Notable residual risks

- `SC-P2-001` stale `docs/SUPPLY_CHAIN.md`.
- `SECRET-P2-001` empty service-role key silently disables persistence.
- `SEC-P3-001` non-constant-time, non-rotatable `METRICS_TOKEN`.
- `ADMIN-P3-001` admin mutations have no rate limit/step-up.
