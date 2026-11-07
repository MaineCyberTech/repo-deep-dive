# Chat verify register — develop@49bf424

| ID | Sev | Status | Title |
|---|---|---|---|
| EXEC-P1-001 | P1 | open | Release gate must remain conditional pending P1/P2 remediation |
| FILE-P1-001 | P1 | open | Scheduled `expired_uploads` cleanup hard-deletes every chat-uploads object older than 7 days, including avatar |
| FINAL-P1-001 | P1 | open | Release gate must remain conditional pending P2 remediation |
| INFRA-P1-001 | P1 | open | Development and production share one Terraform state key and resource address |
| ACM-P2-001 | P2 | partially-fixed | RBAC matrix is enforced per-route but not documented as a single artifact |
| ADMIN-P2-002 | P2 | open | Admin compliance export authorizes the target workspace by membership, not admin role |
| AI-P2-001 | P2 | open | AI endpoint is a stub with no tenancy/data-governance or rate-limit contract |
| ARCH-P2-001 | P2 | open | Single-node topology: one droplet hosts all services and local Redis |
| BP-P2-001 | P2 | open | In-repo branch-protection gate covers only `main`, not `develop` |
| CHAIN-P2-001 | P2 | partially-fixed | Webhook SSRF + missing encryption key form a plausible internal-reach chain |
| CI-P2-001 | P2 | verified-fixed | `infra-development` destroys infra on every push to `develop` |
| CI-P2-002 | P2 | open | Auto-commit workflows hold `contents: write` and push to main/develop |
| CI-P2-003 | P2 | open | `develop` (auto-deploy target) is not covered by the branch-protection gate |
| CI-P2-005 | P2 | open | Pull requests targeting `develop` skip the validate/test workflow |
| CI-P2-006 | P2 | open | Development deploy is ungated and treats a cancelled CI run as success |
| CI-P2-007 | P2 | open | Scheduled validate pipeline is persistently red on the default branch |
| CI-P2-008 | P2 | open | Two workflows apply the same migrations concurrently on `develop` |
| DATA-P2-001 | P2 | owner-accepted | Duplicate `add_user_groups` migrations |
| DATA-P2-002 | P2 | partially-fixed | `gdpr_delete_user` is a hard multi-table delete with partial coverage |
| DATA-P2-003 | P2 | open | `user_groups` INSERT/UPDATE RLS policies omit workspace membership, allowing cross-tenant group creation |
| FILE-P2-001 | P2 | open | Uploads return a public URL from `chat-uploads` and trust client-declared content type |
| FINAL-P2-001 | P2 | open | Dependency risk-acceptances expire 2027-01-04 |
| INFRA-P2-001 | P2 | open | Single-droplet infrastructure has no environment isolation |
| INFRA-P2-002 | P2 | open | Production approval/deploy path is not configured: no `main` branch and no `production` environment |
| INV-P2-001 | P2 | verified-fixed | Stale generated reconciliation artifacts remain tracked at the repository root |
| NOTIF-P2-001 | P2 | partially-fixed | Notifications are delivered only via Web Push; no durable multi-channel delivery/retry |
| OBS-P2-001 | P2 | open | No distributed tracing / correlation to a collector |
| PRIV-P2-001 | P2 | partially-fixed | GDPR erasure path is a hard multi-table delete with partial coverage |
| PRIV-P2-002 | P2 | open | Account deletion is effectively unusable: API requires a password but the UI sends none and magic-link users h |
| RES-P2-001 | P2 | open | Single-node failure domains: API, worker, Redis and DB proxy co-resident |
| SC-P2-004 | P2 | open | Dependency risk-acceptances expire 2027-01-04 |
| SC-P2-005 | P2 | open | Org gitleaks baseline is local-only and not enforced in CI |
| SEC-P2-001 | P2 | verified-fixed | `WEBHOOK_ENCRYPTION_KEY` is not delivered by the production compose stack |
| SEC-P2-002 | P2 | partially-fixed | Webhook SSRF validation does not constrain redirects or DNS rebinding |
| SEC-P2-003 | P2 | open | Push subscription endpoints are stored without validation and fetched server-side (stored SSRF) |
| WH-P2-002 | P2 | partially-fixed | Webhook delivery follows redirects / does not pin the validated IP (SSRF) |
| WH-P2-003 | P2 | open | Any workspace member can create/update/delete webhook endpoints, exposing all workspace message content includ |
| ACM-P3-001 | P3 | open | Admin `/stats` leaks global cross-tenant counters |
| ADMIN-P3-001 | P3 | partially-fixed | Admin error buffer is in-memory only (lost on restart) |
| ARCH-P3-001 | P3 | open | Worker health/metrics bind loopback but rely on a shared token |
| BP-P3-001 | P3 | open | Server-side environment/ruleset configuration is not verifiable from source |
| CHAIN-P3-001 | P3 | open | Public upload URL + client-declared content type is a stored-content risk |
| CI-P3-001 | P3 | open | 13 workflows omit an explicit `permissions:` block |
| CTR-P3-001 | P3 | open | Containers lack runtime hardening beyond non-root and digest pinning |
| CTR-P3-002 | P3 | open | First-party images are referenced by mutable tag (`:latest`/`:dev`) |
| DET-P3-001 | P3 | open | [DEP] trivy not installed (dependency vuln scan skipped) |
| DET-P3-002 | P3 | open | [SUPPLY] 9 container image(s) without a digest pin |
| DET-P3-003 | P3 | open | [SUPPLY] hadolint not installed (Dockerfile lint skipped) |
| DOC-P3-001 | P3 | open | Deployment policy contradicts the development deploy workflow (DB changes) |
| DOC-P3-002 | P3 | verified-fixed | Stale one-off reconciliation docs remain in the tree |
| DR-P3-001 | P3 | open | No evidence of an executed restore drill / RPO-RTO validation |
| EVOL-P3-001 | P3 | open | No extension/plugin contract or versioned public API surface |
| FILE-P3-001 | P3 | open | No per-tenant/user quota or total-storage cap on uploads |
| FILE-P3-002 | P3 | open | Avatar upload accepts any `image/*` subtype (including SVG) and derives the storage path extension from client |
| HYGIENE-P3-002 | P3 | open | Duplicated logic/schema and one-off scripts remain |
| INFRA-P3-001 | P3 | open | Terraform state/backend and provider versions exist but drift checks are absent |
| INV-P3-001 | P3 | open | Committed audit/hardening bundles inflate the repository tree |
| INV-P3-002 | P3 | verified-fixed | Character-encoding (mojibake) artifacts remain in workflow/log text |
| IR-P3-001 | P3 | open | No evidence of a conducted incident tabletop exercise |
| MOB-P3-001 | P3 | open | Service worker offline strategy is not covered by tests or a documented cache policy |
| MT-P3-001 | P3 | open | Admin `/stats` returns global cross-tenant counts (residual) |
| NOTIF-P3-001 | P3 | open | Push subscription lifecycle (revocation/expiry) is not monitored |
| OBS-P3-001 | P3 | partially-fixed | Error tracking (Sentry) is optional and admin error buffer is in-memory |
| PERF-P3-001 | P3 | partially-fixed | No performance budget / regression gate in CI |
| PRIV-P3-001 | P3 | verified-fixed | No automated data-retention enforcement |
| REL-P3-001 | P3 | open | CHANGELOG has no generator/CI gate |
| RES-P3-001 | P3 | verified-fixed | Chaos and load tests are not part of a scheduled pipeline |
| SBOM-P3-001 | P3 | open | SBOMs are generated but not signed or attested |
| SBOM-P3-002 | P3 | open | No license policy / dependency-review gate |
| SC-P3-001 | P3 | partially-fixed | Large binary archives committed to the repository |
| SEARCH-P3-001 | P3 | open | No documented search data-flow / retention statement |
| SEC-P3-001 | P3 | open | Org gitleaks ruleset is local/opt-in only; CI relies on generic Trivy secret scanning |
| SECRET-P3-001 | P3 | open | Secret rotation is documented but not scheduled or monitored |
| SECRET-P3-002 | P3 | partially-fixed | `.env` example files diverge between environments |
| USE-P3-001 | P3 | open | No end-to-end onboarding assertion for the invitation/membership flow |
| UX-P3-001 | P3 | open | Accessibility is audited by an ad-hoc script, not a CI gate |
