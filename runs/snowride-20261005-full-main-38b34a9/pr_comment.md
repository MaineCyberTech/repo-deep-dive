## Full-domain deep dive — `snowride-20261005-full-main-38b34a9`

Read-only audit of `snowride @ 38b34a9` (`main`), 43 domains.

**Verdict: GO WITH CONDITIONS** — bounded runtime use; not an attested release.

| Severity | Count |
|---|---:|
| P0 | 0 |
| P1 | 1 |
| P2 | 7 |
| P3 | 34 |

**Blocking condition:** `FINAL-P1-001` — the committed launch attestation covers
commit `9125913` while HEAD is `38b34a9`; the runtime gate fails closed
(`commit_mismatch`). Re-attest at the released HEAD + migration head `0057` +
image digests.

**Reproduced evidence (lab):** npm ci/build/typecheck green; lint 0 errors/1
warning; 910 tests pass; gitleaks no leaks; migration-head OK (`0057`);
branch-protection self-test PASS.

**Top residual risks:** `SC-P2-001`, `SECRET-P2-001`, `SEC-P3-001`,
`ADMIN-P3-001`, `HYGIENE-P2-001`, `CHAIN-P2-001`.

Draft for review; no auto-merge and no self-approval. This run records a delta
only and does not change any prior verdict.
