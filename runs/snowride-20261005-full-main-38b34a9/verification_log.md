# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-05T06:20:00Z | PS-01 | draft | partially-fixed | ef15f414f1d4213d236369e4a247bf67430fc58d https://github.com/MaineCyberTech/snowride/pull/44 | Draft PR #44: launch gate binds to the running commit (GIT_COMMIT/LAUNCH_EXPECTED_COMMIT); missing/stale => attestation_commit_unverified. Owner signature at the released commit still pending. |
| 2026-10-05T06:20:00Z | PS-02 | open | partially-fixed | - | OWNER-GATED: capture a fresh detached owner signature over the released commit + migration head 0057 + built image digests, and re-pin LAUNCH_ATTESTED_COMMIT. No infra change made. See OWNER_GATED_PROPOSALS.md. |
