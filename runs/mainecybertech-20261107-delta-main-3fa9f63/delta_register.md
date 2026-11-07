# Delta register — main@3fa9f636

| ID | Sev | Status | Title |
|---|---|---|---|
| DR-P0-001 | P0 | open | No successful backup has ever run: all four backup/restore workflows still have zero green runs, including the |
| IR-P0-003 | P0 | partially-fixed | The off-box dead-man's switch is configured and fail-closed, but the external heartbeat URL is still unset and |
| BP-P1-004 | P1 | still-open | PR #279 merged into main with required checks pending and zero reviews - live protection does not match the co |
| CI-P1-001 | P1 | still-open | Production application deploys have no working manual-approval gate |
| CI-P1-003 | P1 | still-open | Production deploy path cannot run; prod environment lacks secrets and protection rules |
| CI-P1-005 | P1 | verified-fixed | NEW: required E2E check is red at the promotion head (Start Supabase fails) |
| DR-P1-003 | P1 | verified-fixed | Restore-test backup location contract (S3_BUCKET/S3_PREFIX) is documented and shared by write/read paths |
| DR-P1-004 | P1 | partially-fixed | Encryption is now enforced, but the offsite/second-destination copy is optional, skipped in the documented dev |
| DR-P1-008 | P1 | open | Restore-test workflows hard-code ubuntu-latest and cannot reach the private Garage endpoint the backup workflo |
| MT-P1-005 | P1 | verified-fixed | A cross-tenant admin membership widens admin scope to orgs where the user is only a client/member |
| OBS-P1-002 | P1 | verified-fixed | Prod deploy health gate now uses the app-host API read and asserts the JSON success envelope instead of the re |
| SBOM-P1-006 | P1 | verified-fixed | NEW: PSF-2.0 is allowed by the full-tree gate but not the PR dependency-review gate or docs |
| SEC-P1-011 | P1 | verified-fixed | Client-visibility filtering is bypassed on comments/timeline side-channel endpoints |
| SEC-P1-012 | P1 | open | NEW: client roles can still read internal comments on tickets and project tasks (is_internal is not enforced o |
| ACM-P2-009 | P2 | verified-fixed | Module read endpoints are org-scoped but not permission-gated (catalog view grants are UI-only) |
| ADMIN-P2-010 | P2 | verified-fixed | Proposal client decisions can be recorded or overwritten by internal staff (no client-role or immutability che |
| CI-P2-012 | P2 | open | AI-review caller pins a SHA but the reusable workflow executes reviewer code from mutable main with all reposi |
| CI-P2-013 | P2 | open | Bot approval fails open when `gh pr checks --required` errors, approving without verified required checks |
| CTR-P2-007 | P2 | partially-fixed | NEW: global .trivyignore suppresses fixable HIGH CVEs in the new node-exporter image |
| DATA-P2-011 | P2 | verified-fixed | Preflight script aborts on its first check, so the duplicate-migration gate never runs and is not wired to CI |
| DR-P2-001 | P2 | verified-fixed | Storage backup listing pagination, partial-download count and archive-integrity gates remain in place |
| DR-P2-010 | P2 | open | The dev empty-mirror allowance records a zero-object archive as a successful backup, which the branch-agnostic |
| DR-P2-011 | P2 | open | Backup jobs run on persistent lab runners but leave plaintext dumps/downloaded user objects in the workspace w |
| EVOL-P2-003 | P2 | open | tailwind-merge 3.x is installed against Tailwind CSS 3.4, so class-conflict merging uses Tailwind v4 semantics |
| INFRA-P2-003 | P2 | partially-fixed | Operations documentation contradicts the current pipeline and configuration |
| IR-P2-011 | P2 | open | The first (and only) alert-path exercise failed and the IR evidence table still records no exercise |
| PRIV-P2-010 | P2 | verified-fixed | Direct anon INSERT on store_quotes bypasses the consent gate, validation and rate limits |
| SEC-P2-019 | P2 | verified-fixed | File-request upload listing and signed URLs skip the parent request's visibility check |
| SEC-P2-020 | P2 | verified-fixed | Client roles granted ai:view can read every AI draft output in the organization |
| TEST-P2-010 | P2 | verified-fixed | Promotion PRs merge before required checks, so the promoted commit has no green Test artifact (PR #333 recurre |
| TEST-P2-011 | P2 | verified-fixed | E2E Supabase image cache is not a reliable cold-start path: a cache hit loads, then `supabase start` still fai |
| CI-P3-016 | P3 | open | Dependabot Node-major hold is applied only to the root docker config, not the three app Dockerfile directories |
| CI-P3-017 | P3 | open | AI review fails on Dependabot PRs because required secrets are unavailable, creating red checks and blocking t |
| CI-P3-018 | P3 | open | Bot approval accepts any historical AI-review comment, so a review from an earlier push can satisfy the gate |
| CTR-P3-006 | P3 | partially-fixed | infra/digitalocean operator docs and `.env.example` drift from the deployed stack |
| DET-P3-003 | P3 | verified-fixed | [SUPPLY] third-party image scan header still says four images and omits node-exporter |
| DR-P3-008 | P3 | verified-fixed | Restore discovery now distinguishes 'cannot list the bucket' from 'bucket reachable but empty', with a negativ |
| DR-P3-009 | P3 | open | Backup retention deletes objects in place with no versioning, object lock or immutability on either destinatio |
| DR-P3-010 | P3 | open | The offsite-copy skip ignores S3_OFFSITE_PREFIX, so a same-bucket/different-prefix second copy is dropped; the |
| EVOL-P3-010 | P3 | verified-fixed | Supabase CLI pin in CI (2.107.0) no longer matches the lockfile (2.122.1) or package.json (^2.120.0) |
| INFRA-P3-011 | P3 | verified-fixed | NEW: promtool CI gate pins Prometheus v3.5.1 while production runs v3.15.1 |
| OBS-P3-008 | P3 | verified-fixed | node-exporter is now inside service-down alerting and is gated by a real HTTP/filesystem probe |
| OBS-P3-009 | P3 | open | Monitoring doc carries a duplicated stale health-check table and describes the deploy gate as node-exporter ra |
| RLS-P3-009 | P3 | verified-fixed | notifications INSERT policy allows any authenticated user to write a self-addressed row into an arbitrary orga |
| SBOM-P3-012 | P3 | open | docs/LICENSE_POLICY.md now lists the allowed-license block twice after the PSF-2.0 edit |
| SEC-P3-014 | P3 | partially-fixed | Client-visibility helper fails open and exempts API-key requests |
| SEC-P3-015 | P3 | verified-fixed | GET /ai/triage is the only AI route without an ai:view gate |
| SEC-P3-016 | P3 | open | NEW: GET /ai/triage returns every triage draft in the org (raw descriptions and first-response drafts) to clie |
| SEC-P3-017 | P3 | open | NEW: SSO callback forwards the caller's entire cookie jar (including mct_session and csrf_token) to the API wh |
| SEC-P3-018 | P3 | open | NEW: the SSO PKCE start route and the verifier-missing/negative callback paths have no regression tests |
