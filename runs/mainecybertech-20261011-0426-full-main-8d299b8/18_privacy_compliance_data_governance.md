# 18_privacy_compliance_data_governance — Prompt 18 - Privacy, Compliance, and Data Governance Audit

- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Target: `mainecybertech` @ `8d299b8` (branch `main`)
- Domain: `18_privacy_compliance_data_governance.md` (area PRIV, prompt)

## Verification Performed

# Privacy, Compliance, and Data Governance Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `mainecybertech-20261011-0426-full-main-8d299b8`
- Repository: `mainecybertech` (monorepo: apps/api, apps/web, apps/worker, supabase, infra, docs)
- Branch: `main`
- Commit SHA: `8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd`
- Generated at: 2026-10-11 (read-only pass)
- Auditor: domain subagent (area PRIV, prompt 18)
- Area code: PRIV
- Output path: `docs/audits/repo-deep-dive/mainecybertech-20261011-0426-full-main-8d299b8/18_privacy_compliance_data_governance.md`
- Scope limitations: repository-only evidence. Supabase provider controls (at-rest encryption, PITR), Google Analytics settings, Tawk.to, Teams/JSM/Stripe/Sentry vendor-side retention, the breach register (deliberately stored outside the repo, `docs/DATA_BREACH_RESPONSE.md:369-373`) and production data volumes were **not** inspected. No production systems were contacted.

## Scope

Reviewed in the repository at `8d299b8d`:

- Personal/sensitive data inventory and classification (code + migrations + `docs/DATA_BREACH_RESPONSE.md` §6.1).
- PII storage and field-level encryption (`profiles.encrypted_pii`), backup encryption, storage buckets.
- Auth records (`auth.users` usage, `mfa_recovery_codes`, JWT/session handling by reference).
- Audit logs (`audit_logs`, `impersonation_log`), audit export, audit PII redaction.
- Admin actions and impersonation (by reference to ADMIN/ACM/MT domains; re-verified only where privacy-relevant).
- Billing/payment references (Stripe ids, `billing_email`) at inventory level only (BILL domain owns findings).
- Uploaded documents and user content storage/deletion paths (FILE domain owns file findings; privacy angle only).
- Export/deletion paths, retention workers, consent/cookie flows, policies/terms, access controls at a summary level.
- Compliance documentation: privacy policy, terms, `SECURITY.md`, `docs/DATA_BREACH_RESPONSE.md`, `docs/INCIDENT_RESPONSE.md`, `docs/RTO_RPO.md`.

Not reviewed (owned by other domains in this run): RLS policy correctness (37), tenant-isolation attack paths (25), admin-console abuse (26), file upload/download hardening (28), billing reconciliation (29), search privacy internals (31), analytics/tracking privacy (39), backup/restore drills (32), incident tabletop (33).

## Evidence Reviewed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `apps/web/app/(public)/layout.tsx:49-78` | Code | GA/Tawk.to script injection, consent gate (absent) | Re-verified for PRIV-P2-001 |
| `apps/web/app/(public)/privacy/page.tsx:1-147` | Doc/UI | Published policy: collection, vendors, retention, rights | Last updated 2026-07-01 |
| `apps/web/app/(public)/terms/page.tsx:1-99` | Doc/UI | Terms of service | No data-processing terms |
| `apps/web/app/(public)/contact/actions.ts:7-36` | Code | Consent check + payload stripping before API call | Client/action-side only |
| `apps/web/components/marketing/ContactForm.tsx:313-333` | Code | Consent checkbox UI | Default unchecked |
| `apps/web/components/store/IntakeFormRenderer.tsx:43,111-121,244-264` | Code | Store intake consent | Same action, same gap |
| `apps/web/components/store/QuoteBuilderClient.tsx:160-200` | Code | Public quote form | No consent/privacy link |
| `apps/api/src/routes/public.ts:13-24,47-125,127-274` | Code | Public visitor init + lead submit; geo, Teams, JSM, audit | Stores raw IP/UA; http://ip-api.com |
| `supabase/migrations/5302033_public_interactions.sql:1-24` | Migration | public_interactions schema | No consent column |
| `supabase/migrations/5302117_public_interactions_retention.sql:1-14` | Migration | 90-day retention + comment | PII documented |
| `apps/worker/src/tasks/public-interaction-retention.ts:1-42` | Code | 90-day purge implementation | Unbounded delete |
| `apps/worker/src/main.ts:71-79` | Code | Daily purge schedule | setInterval, not schedule-config |
| `apps/worker/src/tasks/retention.ts:7-172` | Code | audit_logs 365d / notifications 90d purge | Batched (DATA-P1-002) |
| `apps/api/src/services/audit.ts:22-67` | Code | audit_logs writer + PII redaction | Shallow key filter |
| `apps/api/src/routes/audit.ts:22-105,163-164` | Code | Audit list/export, tenant scoping, export audit | Exports metadata |
| `apps/api/src/routes/profiles.ts:56-118,120-202` | Code | Profile read/update; encrypted_pii mirror | Plaintext remains source of truth |
| `apps/api/src/lib/profile-pii.ts:1-29` | Code | PII field list (full_name, email, phone, title) | `title` not redacted in audit |
| `apps/api/src/lib/field-encryption.ts:1-97` | Code | AES-256-GCM fail-closed field encryption | Mirror only |
| `apps/api/src/config/env.ts:95-108` | Code | Production fail-closed on missing key | SEC-P1-001 |
| `supabase/migrations/5302135_profiles_encrypted_pii.sql:1-39` | Migration | encrypted_pii jsonb + policy | Plaintext intentionally kept |
| `scripts/backfill-profile-pii.mjs:1-60` | Script | One-time backfill, refuses plaintext fallback | Run 2026-08-27 per review.md:945 |
| `apps/api/src/routes/memberships.ts:158-172` | Code | Membership removal | Leaves profile/auth user |
| `apps/api/src/routes/organizations.ts:96-130,403-419` | Code | Invite by email; hard org delete | Cascade (DATA-P2-005) |
| `apps/api/src/routes/store/quotes.ts:68-160` | Code | Public quote submit; audit metadata | PII in jsonb + audit |
| `apps/api/src/routes/billing.ts:234-360` | Code | Stripe sync; invoice/payment mirrors | No card data; billing_email plaintext (BILL) |
| `apps/api/src/lib/sentry.ts:1-12`, `apps/web/sentry.*.config.ts` | Code | Error tracking init | No explicit PII scrubbing configured |
| `apps/api/src/lib/email.ts:1-55` | Code | SMTP transport; recipient not logged | Vendor not in policy |
| `apps/worker/src/tasks/m365-calendar-sync.ts:94`, `jira-sync.ts:110` | Code | Outbound PII flows to M365/Jira | Not in policy |
| `supabase/migrations/5302427_mfa_recovery_codes.sql:20-21`, `apps/api/src/routes/auth.ts:560-700` | Code/Migration | Recovery codes hashed+salted, invalidated | Strength |
| `supabase/migrations/5302433_avatars_bucket_policies.sql:25-80` | Migration | avatars bucket public, per-user prefix | Public personal images |
| `supabase/migrations/5302026_...v3.sql:604-616,2297-2305` | Migration | audit_logs schema; documents bucket private | ip/ua columns unused |
| `scripts/backup-database.sh:1-140`, `scripts/backup-storage.sh:22-145`, `.github/workflows/db-backup.yml:22-44` | Script/CI | Encrypted 30-day backups | Strength |
| `docs/DATA_BREACH_RESPONSE.md:1-459` | Doc | Breach plan, category map, register schema | Stale alertmanager claims |
| `docs/INCIDENT_RESPONSE.md:110-145` | Doc | IR plan, gaps | Stale IR-P0-003 claim |
| `docs/RTO_RPO.md:10-36` | Doc | Backup/encryption/retention statements | Strength |
| `docs/VISITOR_ALERTS.md:1-50` | Doc | Visitor tracking + 90-day purge note | Confirms retention |
| `SECURITY.md:1-40` | Doc | Vulnerability reporting | No security.txt found |
| `docs/audits/repo-deep-dive/*` (committed previous runs) | Doc | Prior findings + patch plan context | PRIV-P2-001 origin |

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `git log -1 --format='%H %s'` | Command | Confirm audited commit | `8d299b8d... Merge PR #168: promote develop to main` |
| `git log --oneline 9c0b88c..8d299b8d` (113 commits) | Command | Detect changes affecting this domain | No commit touches `apps/web/app/(public)/layout.tsx`, `privacy/page.tsx`, `public.ts`, `services/audit.ts`, retention tasks, or backup scripts; changes are alerting/metrics/register sync |
| `grep -rn -i 'consent\|CookieBanner\|onetrust\|cookiebot' apps/web --include='*.tsx' --include='*.ts'` | Command | Consent/cookie gate search | Only form consent checkboxes; no consent manager or cookie banner |
| `grep -rn -i 'googletagmanager\|tawk\|gtag(' apps/web` | Command | GA/Tawk.to injection points | `layout.tsx:61,66,73` — unconditional |
| `grep -rn 'consent' apps/api/src` | Command | Server-side consent enforcement | No matches in the public submit path; `submitSchema` has no consent field |
| `grep -rn 'encrypted_pii\|profile-pii' apps/api/src` | Command | Encryption wiring | `profiles.ts:149,175` only; reads return plaintext columns |
| `grep -rn 'deleteUser' apps/api/src apps/worker/src` | Command | Account deletion path | Zero matches |
| `grep -rn 'ip_address' apps/api/src` | Command | Who records source IPs | `impersonation.ts:35`, `public.ts:81`, `analytics.ts:43` only — no `audit_logs` writer |
| `grep -rn 'logAuditEvent({' apps/api/src/routes` | Command | Audit metadata call sites | 62 files; `name`/`title` keys logged by `public.ts:263-274`, `profiles.ts:190-196`, `store/quotes.ts:148-151` |
| `grep -rn -i 'subject access\|erasure\|dsar\|gdpr' docs/runbooks docs/features` | Command | DSAR procedure search | Zero matches |
| `grep -rn -i 'subprocessor\|sub-processor' --include='*.md' .` | Command | Subprocessor inventory search | Only `DATA_BREACH_RESPONSE.md:232` and the previous run's patch plan |
| `ls docs \| grep -i -E 'privacy\|classification\|retention\|dpa'` | Command | Governance doc presence | No platform privacy/classification/retention/DPA doc; only product-module docs |
| `grep -rn 'alertmanager' docker-compose*.yml infra/digitalocean/*.yml .github/workflows/deploy-do.yml` | Command | Verify IR-P0-003 fix state | `infra/digitalocean/docker-compose.yml:244-293` + `prometheus.yml:15-17` + `deploy-do.yml:622-631` prove deployment |
| `sed -n '20,24p' apps/worker/src/tasks/public-interaction-retention.ts` | Read | Purge statement shape | Single unbounded delete |
| `grep -rhoE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' docs/audits` | Command | Redaction check of published audit artifacts | Only `security@`/`noreply@mainecybertech.com`, `someone@example.com`, a local test address — no personal data or secrets |
| `grep -rnE 'AKIA\|ghp_\|sk_live_\|BEGIN PRIVATE KEY' docs/audits` | Command | Secret check of published audit artifacts | Only scanner-pattern definitions; no secret values |
| Prior register read: `follow_up_register.md` rows with Area PRIV | Read | Verification duty | Only `PRIV-P2-001` (open at 9c0b88c); `AN-P3-001` and `ADMIN-P3-002` are owned by their domains |
| Prior domain report read: `runs/.../18_privacy_compliance_data_governance.md` | Read | Prior run scope | Reconciliation-only pass; PRIV-P2-001 was the sole finding |

## Executive Summary

The platform has real privacy building blocks: a published privacy policy and terms page, a substantive data-breach response plan with a data-category map, fail-closed AES-256-GCM field encryption for profile PII, encrypted 30-day backups, a scheduled 90-day purge of contact-form PII, hashed MFA recovery codes, tenant-scoped audit reads, and audited audit exports. The committed audit artifacts themselves contain no personal data or secret values (redaction check passed).

The gaps are governance and enforcement, not absence of intent:

1. **Consent is not enforceable or provable.** GA and Tawk.to load before consent (previous finding PRIV-P2-001, still open), the store quote form collects name/email/phone with no consent at all, and the API never records a consent event for any public form.
2. **Published retention does not match the code.** The policy says contact-form submissions are kept up to three years; the worker purges the PII table at 90 days.
3. **PII leaks into the audit trail.** The audit-log redactor is a shallow key-name filter; lead names and profile job titles persist in `audit_logs.metadata` for 365 days and are exported.
4. **No data-subject rights workflow.** There is no export/erasure path, no account deletion, and no DSAR runbook; removing a membership leaves the profile and auth user behind.
5. **Governance artifacts are missing.** No classification inventory, ROPA/subprocessor list, platform retention schedule or tenant DPA; the published vendor list omits processors that code actually uses (Stripe, Supabase, Cloudflare, Sentry, SMTP, M365, Jira).
6. **Two compliance docs are stale/wrong about controls** (Alertmanager "not deployed"; audit_logs "from which IP").

Recommended next actions: gate GA/Tawk.to behind Consent Mode v2 default-deny and persist consent server-side; align the retention statement with the 90-day purge; fix the audit redaction to an explicit allowlist with a regression test; add a DSAR runbook plus account deletion path; and publish classification/subprocessor/retention docs. None of this requires a schema-breaking change.

## Inventory

| Item | Path / symbol | Purpose | Current state | Risk | Notes |
|---|---|---|---|---|---|
| Public visitor records | `public_interactions` (5302033) | Store IP/UA/location/referrer + lead PII | Purged at 90 days; no consent column | Medium | Raw IP stored for every visitor |
| Contact/store leads | `/api/v1/public/submit`, `public.ts:127-274` | Lead capture + Teams/JSM forward | Consent client-side only | High | API accepts without consent |
| Store quotes | `store_quote_requests.customer`, `store/quotes.ts:68` | Public quote PII (name/email/phone) | No consent, no purge | High | Unbounded retention |
| Profiles PII | `profiles` + `encrypted_pii` (5302135) | Identity data | Plaintext source of truth + encrypted mirror | Medium | Field encryption additive (SEC domain finding) |
| Auth records | `auth.users`, `mfa_recovery_codes` (5302427) | Identity/2FA | Recovery codes hashed+salted; no account deletion path | Medium | Supabase-managed users |
| Audit logs | `audit_logs` (5302026:604) | Who/what/when | 365-day purge; metadata PII redaction shallow; ip/ua never written | Medium | No archive (DATA-P2-005) |
| Impersonation log | `impersonation_log`, `services/impersonation.ts:35-36` | Cross-tenant admin trail | Records IP/UA/reason; no purge | Medium | Reviewable only by super_admin |
| Billing refs | `billing_customers`, `subscriptions`, `invoices`, `payments` | Stripe mirrors | No card data; `billing_email` plaintext | Medium | BILL domain owns findings |
| Documents | `documents`, storage bucket `documents` (private) | Tenant files | Delete removes row + object; orphan cleanup reconciles | Medium | No per-store retention (DATA-P2-006) |
| Avatars | `avatars` bucket (public, 5302433) | Profile images | Public bucket, per-user prefix | Low | Public personal image by design |
| Notifications | `notifications` | User notifications | 90-day purge | Low | — |
| Backups | `scripts/backup-database.sh`, `backup-storage.sh` | DB + storage dumps | AES-256-CBC, 30-day retention, offsite option | Low | Key rotation documented |
| Privacy policy | `apps/web/app/(public)/privacy/page.tsx` | Public notice | Exists; retention mismatch; vendor list incomplete | Medium | Last updated 2026-07-01 |
| Terms | `apps/web/app/(public)/terms/page.tsx` | Contract terms | Exists; no data-processing terms | Low | DPA referenced to SOW |
| Breach plan | `docs/DATA_BREACH_RESPONSE.md` | Breach process | Strong; 2 stale/incorrect claims | Low | Register kept off-repo by design |
| IR plan | `docs/INCIDENT_RESPONSE.md` | Incident process | Exists; stale IR-P0-003 claim | Low | On-call rota unfilled |

## Domain Scorecard

| Category | Score | Evidence | Gap | Recommended action |
|---|---:|---|---|---|
| Personal/sensitive data | 3 | `DATA_BREACH_RESPONSE.md:240-257` category map; plaintext PII columns | No classification inventory/ROPA; encryption additive | Publish classification + ROPA |
| Auth records | 3 | `mfa_recovery_codes` hashed (5302427); no `deleteUser` path | No account lifecycle/deletion | Add admin deletion/anonymisation |
| Audit logs | 3 | `services/audit.ts`, tenant-scoped reads, audited export | Shallow redaction; no IP/UA; no archive | Allowlist redaction; correct docs |
| Admin actions | 3 | `impersonation_log`, `audit.export` event, admin scope fixes | Covered by ADMIN/ACM domains | See 24/26 domains |
| Billing/payment refs | 3 | Stripe mirrors, no PAN storage (`billing.ts`) | `billing_email` plaintext | See 29 domain |
| Uploaded docs | 3 | Private bucket, delete removes object, orphan cleanup | No retention policy; no AV | See 28/07 domains |
| User content | 2 | `store_quote_requests`, `tickets`, `chat_messages` | No consent record; unpurged stores | Retention inventory + consent fields |
| Export/deletion | 1 | No DSAR export/erasure; membership delete only | Procedure and tooling absent | DSAR runbook + account deletion |
| Retention | 3 | Worker purges audit 365d/notifications 90d/public 90d | Hardcoded; policy mismatch; stores unpurged | Publish schedule; wire `retention_policies` |
| Consent/cookie flows | 1 | Consent checkboxes UI-only; GA/Tawk pre-consent | No consent manager, no server record | Consent Mode v2 + persisted consent |
| Policies/terms | 2 | Privacy/terms pages exist | Retention + vendor list wrong; no cookie table/DPA | Update policy; add subprocessor doc |
| Access controls | 3 | RLS profiles/documents; tenant-scoped audit | Owned by 06/24/25/37 domains | See those domains |

## Detailed Review

### Item: Public consent flows (contact form, store intake, store quote)

- Evidence: `contact/actions.ts:20-25`; `ContactForm.tsx:313-333`; `IntakeFormRenderer.tsx:244-264`; `QuoteBuilderClient.tsx:160-200`; `public.ts:13-24`; `5302033:1-19`; `store/quotes.ts:68-113`.
- What it does: Contact and intake forms require an unchecked consent box in the browser; the Next.js action drops the flag and calls the API. The quote form has no consent UI. The API accepts all three without a consent field.
- How it appears to work: consent is a UI gate, not a recorded legal basis.
- Dependencies: `submitLead` server action; `/api/v1/public/submit`; `/api/v1/store/quotes`.
- Current controls: default-unchecked checkboxes; privacy link.
- Missing controls: consent persistence (who/when/version), server-side enforcement, marketing opt-in field.
- Risks: unprovable consent; PII collected without a lawful-basis record.
- Recommended improvement: add `consent`, `consent_at`, `consent_version` to the PII tables and require them at the API; add the checkbox to the quote form.
- Suggested tests: API rejects submit without consent; DB row carries consent timestamp; E2E asserts the quote form blocks without consent.
- Suggested docs: privacy page cookie/consent section; DSAR/consent runbook.

### Item: Cookie/analytics consent (GA, Tawk.to)

- Evidence: `layout.tsx:49-78`; `privacy/page.tsx:56-64`; no consent component anywhere.
- What it does: GA `gtag.js` and Tawk.to load on every public page after interactive; no Consent Mode default.
- Missing controls: consent manager, opt-out, cookie table.
- Risks: invalid consent for analytics/chat cookies; regulator exposure.
- Recommended improvement: Consent Mode v2 default-deny; load Tawk.to post-consent; persist choice.
- Suggested tests: unit test that scripts are absent when consent is denied; E2E for the banner.
- Suggested docs: privacy page; `docs/PRIVACY.md`.

### Item: Field-level PII encryption

- Evidence: `field-encryption.ts:39-58`; `profile-pii.ts:3`; `profiles.ts:149,175`; `5302135:1-39`; `env.ts:95-108`.
- What it does: AES-256-GCM mirror of full_name/email/phone/title in `profiles.encrypted_pii`, written on PATCH; prod boot fails without a 32-byte key.
- How it appears to work: fail-closed, but the plaintext columns remain the source of truth for reads (migration comment: "plaintext columns remain the source of truth").
- Current controls: fail-closed key validation; rotation procedure (`SECRETS_ROTATION.md:84-98`); backfill script refuses the dev fallback.
- Missing controls: no read path uses the ciphertext; no plan to drop plaintext.
- Risks: DB dumps/service-role reads still expose PII; the control reduces exposure only marginally. **Owned by the security domain** (`06_security_authz_tenancy_audit`: "PII field encryption is additive…"), so not re-filed here.
- Recommended improvement: migrate reads/writes to the encrypted column then drop plaintext, or document the mirror as defence-in-depth only.
- Suggested tests: existing `profile-pii.test.ts`; add a test that a DB row without the key cannot leak readable PII.
- Suggested docs: state the mirror's scope in the privacy/security docs.

### Item: Retention workers and the published retention statement

- Evidence: `retention.ts:12-15,23-31,129-135`; `public-interaction-retention.ts:5,20-24`; `main.ts:71-79`; `5302117:1-14`; `privacy/page.tsx:88-93`; `DATA-P2-006` (07 domain).
- What it does: daily purge of audit_logs >365d and notifications >90d (batched, honest failures); daily purge of public_interactions >90d (single statement); no purge for many timestamped stores.
- Missing controls: platform retention schedule; `retention_policies` is not consulted by the worker; policy text not aligned.
- Risks: transparency failure; unbounded PII stores; long transactions after backlog.
- Recommended improvement: extract `purgeInBatches` for reuse; publish the schedule; align the policy.
- Suggested tests: boundary test (fresh rows survive, expired rows are deleted); batched-backlog test.
- Suggested docs: `docs/DATA_RETENTION.md`; privacy page update.

### Item: Audit trail privacy and forensics

- Evidence: `services/audit.ts:22-67`; `audit.ts:58-101,163-164`; `public.ts:263-274`; `profiles.ts:190-196`; `5302026:604-616`; `DATA_BREACH_RESPONSE.md:134,249,255-257`.
- What it does: single writer inserts actor/action/entity/metadata; key-substring redaction; 365-day retention; org-scoped read and CSV export; export itself audited.
- Missing controls: value-level/nested redaction; source IP/UA; archive.
- Risks: person names/titles persist a year and export; breach scoping misled by doc claims.
- Recommended improvement: allowlist + recursive redaction with a regression test; either record IP/UA or correct the docs.
- Suggested tests: metadata with `name`/nested `email` never lands; export contains no raw names.
- Suggested docs: correct `DATA_BREACH_RESPONSE.md` §3/§6.1.

### Item: Data-subject rights and account lifecycle

- Evidence: `privacy/page.tsx:96-110`; no export/delete routes; `memberships.ts:158-172`; `users.ts` (no DELETE); no DSAR runbook.
- What it does: rights are exercised by email; removing a membership leaves profile/auth identity.
- Missing controls: DSAR procedure, export query set, erasure/anonymisation, response tracking.
- Risks: cannot demonstrate Art. 15/17 handling; stale identities.
- Recommended improvement: runbook + admin deletion path.
- Suggested tests: admin deletion removes profile and auth user (or anonymises); export returns the subject's rows only.
- Suggested docs: `docs/runbooks/dsar.md`; privacy page link.

### Item: Vendor/processor inventory

- Evidence: `privacy/page.tsx:46-82`; `billing.ts:234-267`; `sentry.ts:5-11`; `public.ts:33`; `email.ts:20-40`; `m365-calendar-sync.ts:94`; `jira-sync.ts:110`; `DATA_BREACH_RESPONSE.md:224-233`.
- What it does: five vendors disclosed; code touches at least eight more processors.
- Missing controls: subprocessor list, DPA status, data categories, regions.
- Risks: tenant due-diligence failures; inaccurate notice.
- Recommended improvement: `docs/SUBPROCESSORS.md` + DPA template.
- Suggested tests: CI check that new outbound vendor env vars appear in the subprocessor doc (optional).
- Suggested docs: subprocessor list linked from the privacy page.

### Item: Backups and encryption at rest

- Evidence: `backup-database.sh:14-22,76-96,118-134`; `backup-storage.sh:108-145`; `db-backup.yml:40-44`; `RTO_RPO.md:24-25`; `5302433` (avatars public); `documents` private bucket.
- What it does: encrypted (AES-256-CBC/PBKDF2) 30-day backups with offsite option; storage objects private except avatars; provider at-rest encryption is not documented.
- Current controls: `REQUIRE_BACKUP_ENCRYPTION=1` in CI; empty-dump guard.
- Missing controls: documented at-rest encryption assumption for DB/storage; backup copies of deleted PII are not addressed in the policy.
- Risks: low; mainly documentation.
- Recommended improvement: state the encryption assumptions (Supabase/DigitalOcean managed at rest, TLS in transit) in `docs/PRIVACY.md`/`RTO_RPO.md`.
- Suggested tests: restore drill already owned by 32.
- Suggested docs: encryption assumptions section.

## Scenario / Control Matrix

| ID | Scenario or control | Evidence | Current control | Gap | Severity | Recommendation |
|---|---|---|---|---|---|---|
| PRIV-001 | Personal/sensitive data | `DATA_BREACH_RESPONSE.md:240-257`; `profiles` plaintext | Category map; field-encryption mirror | No classification/ROPA; plaintext columns | P2 | Publish classification + ROPA |
| PRIV-002 | Auth records | `5302427`; `auth.ts:560-700`; no `deleteUser` | Hashed recovery codes; Supabase auth | No deletion path | P2 | Add admin deletion/anonymisation |
| PRIV-003 | Audit logs | `services/audit.ts`; `audit.ts` | Tenant-scoped; export audited; 365d purge | Shallow redaction; no IP/UA; no archive | P2 | Allowlist redaction; correct docs |
| PRIV-004 | Admin actions | `impersonation.ts`; `audit.ts:107+` | Impersonation log review by super_admin | Owned by 26/06 | P3 | See 26 domain |
| PRIV-005 | Billing/payment refs | `billing.ts:234-360`; schema `billing_email` | No PAN; Stripe ids only | Plaintext billing email | P2 | See 29 domain |
| PRIV-006 | Uploaded docs | `documents.ts:565-606`; `documents` bucket | Private bucket; delete removes object | No retention; no AV | P2 | See 28/07 domains |
| PRIV-007 | User content | `store_quote_requests`; `tickets`; `chat_messages` | RLS per org | No consent record; unpurged stores | P2 | Retention inventory + consent fields |
| PRIV-008 | Export/deletion | No routes; `memberships.ts:158-172` | Manual email only | No DSAR tooling/runbook | P2 | Runbook + deletion path |
| PRIV-009 | Retention | Workers + `privacy/page.tsx:88-93` | 90d/365d purges | Policy mismatch; hardcoded; unpurged stores | P2 | Publish schedule; align policy |
| PRIV-010 | Consent/cookie flows | `layout.tsx:58-78`; `public.ts`; quote form | Checkboxes (UI only) | No gate/record/opt-out | P2 | Consent Mode v2 + persisted consent |
| PRIV-011 | Policies/terms | `privacy/page.tsx`; `terms/page.tsx` | Published pages | Retention + vendors wrong; no cookie/DPA | P2 | Update + subprocessor doc |
| PRIV-012 | Access controls | `profiles` RLS; `audit.ts:22-35` | Tenant-scoped reads | Owned by 06/24/25/37 | P3 | See those domains |

## Findings

Finding IDs (`PRIV-Px-NNN`) are assigned by the aggregator; titles below match the JSON artifact 1:1. Format follows `00_SHARED_AUDIT_RULES.md`.

### Finding: Google Analytics and Tawk.to load on public pages with no cookie-consent or opt-out gate

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/web/app/(public)/layout.tsx:58-69` — GA `gtag.js` + `gtag('config', ...)` injected whenever `NEXT_PUBLIC_GA_ID` is set, with no consent check
  - `apps/web/app/(public)/layout.tsx:71-78` — Tawk.to script injected whenever `NEXT_PUBLIC_TAWKTO_ID` is set, with no consent check
  - No consent manager/cookie banner exists anywhere in `apps/web` (grep for `consent|CookieBanner|onetrust|cookiebot`)
  - `apps/web/app/(public)/privacy/page.tsx:56-64` — vendors disclosed, no opt-out offered; no Consent Mode default
  - `git log 9c0b88c..8d299b8d -- apps/web/app/(public)/layout.tsx` — no commits; unchanged since the previous run
- What is happening: non-essential third-party scripts load for every public visitor before any consent choice is made.
- Why it matters: analytics/chat cookies are set without a valid basis or an opt-out, and the policy implies user choice that does not exist.
- User / business impact: visitors are tracked without consent; the business carries regulatory and reputational risk for a cheap-to-fix defect.
- Security / privacy / reliability impact: privacy — cookie/identifier processing without consent (GDPR/ePrivacy); CCPA notice-at-collection/opt-out gap.
- Recommended fix: introduce a consent manager; default-deny with Google Consent Mode v2 (`analytics_storage: denied`); load Tawk.to only after opt-in; persist the choice; add a cookie table to the privacy page.
- Suggested validation: unit test asserting scripts are not rendered when consent is denied; Playwright E2E accept/deny asserting GA/Tawk network requests.
- Owner suggestion: @web (frontend lead)
- Effort estimate: M
- Dependencies: none
- Status: still-open (previous row `PRIV-P2-001`, open at 9c0b88c)
- Endpoint / data path: public layout → GA/Tawk.to third-party scripts (client-side)
- Attack path: none identified (privacy, not exploit)

### Finding: Consent is captured only in the browser and never recorded or enforced server-side; the store quote form collects PII with no consent at all

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/web/app/(public)/contact/actions.ts:20-25` — consent checked in the server action, then stripped before `POST /api/v1/public/submit`
  - `apps/api/src/routes/public.ts:13-24` — `submitSchema` has no consent field; the API stores PII without any consent assertion
  - `supabase/migrations/5302033_public_interactions.sql:1-19` — no consent column (status/company/client_*/submitted_at only)
  - `apps/web/components/store/QuoteBuilderClient.tsx:160-200` — public quote form submits name/email/phone with no consent checkbox and no privacy link
  - `apps/api/src/routes/store/quotes.ts:68-113` + `supabase/migrations/5302114_store_conversion_modules.sql:6-16` — public endpoint stores `customer` jsonb PII
  - `apps/web/components/marketing/ContactForm.tsx:313-333`, `apps/web/components/store/IntakeFormRenderer.tsx:244-264` — checkbox is UI state only
- What is happening: consent is a browser-side gate; no consent event is persisted for any public form, and one form never asks.
- Why it matters: GDPR Art. 7(1) requires demonstrable consent; direct API calls can store PII with none.
- User / business impact: users cannot see or prove what they agreed to; the business cannot evidence its lawful basis in a complaint or audit.
- Security / privacy / reliability impact: privacy — accountability failure; marketing opt-in claimed in the policy (`privacy/page.tsx:41-42`) has no schema support.
- Recommended fix: add `consent`, `consent_at`, `consent_version` to the PII tables; require and persist them in `/public/submit` and `/store/quotes`; add the checkbox + privacy link to the quote form.
- Suggested validation: API tests rejecting missing/false consent; DB assertions on stored consent; E2E for the quote form.
- Owner suggestion: API platform + @web
- Effort estimate: M
- Dependencies: migration for consent columns
- Status: open
- Endpoint / data path: `POST /api/v1/public/submit`, `POST /api/v1/store/quotes` → public_interactions / store_quote_requests
- Attack path: none identified

### Finding: Published retention statement (three years) contradicts the 90-day contact-form PII purge

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/web/app/(public)/privacy/page.tsx:88-93` — "Contact form submissions are retained for up to three years."
  - `apps/worker/src/tasks/public-interaction-retention.ts:5,20-24` — `RETENTION_DAYS = 90`; all older rows deleted
  - `supabase/migrations/5302117_public_interactions_retention.sql:1-14` — schema comment documents the 90-day purge
  - `apps/worker/src/main.ts:71-79` — purge runs daily; `docs/VISITOR_ALERTS.md:33-35` repeats 90 days
- What is happening: the published policy and the enforced purge disagree by an order of magnitude.
- Why it matters: the notice is inaccurate; records can vanish earlier than promised, and forwarded Teams/JSM copies are outside this control.
- User / business impact: transparency failure; lead records may be gone when the business expects them.
- Security / privacy / reliability impact: privacy — notice accuracy/accountability; no data-loss impact (deletion is the safe direction).
- Recommended fix: align the policy text with the 90-day purge (and state the retention of forwarded copies), or change the purge window to the published period.
- Suggested validation: CI doc check that the policy figure matches the worker constant (single source of truth).
- Owner suggestion: security lead / @web
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: worker `public-interaction-retention` → `public_interactions`
- Attack path: none identified

### Finding: Audit-log PII redaction is a shallow key-name filter; person names and job titles are persisted for 365 days

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/api/src/services/audit.ts:34-45` — only top-level keys containing full_name/email/phone/password/token/secret are replaced; `name`, `title`, `job_title` and nested values pass through
  - `apps/api/src/routes/public.ts:263-274` — `public.lead.submit` logs the lead's `name` and `company`
  - `apps/api/src/routes/profiles.ts:149,190-196` — profile PATCH logs `updateData` including `title`; `apps/api/src/lib/profile-pii.ts:3` declares `title` PII
  - `apps/api/src/routes/store/quotes.ts:148-151` — quote submit logs `name` and `email`
  - `apps/worker/src/tasks/retention.ts:129-132` and `apps/api/src/routes/audit.ts:58-101` — 365-day retention and CSV export of metadata
  - No unit test covers `services/audit.ts` redaction
- What is happening: personal names and job titles persist in `audit_logs.metadata` in plaintext and are exported to any org admin.
- Why it matters: contradicts `docs/DATA_BREACH_RESPONSE.md:255-257` ("PII-redacted at write time") and widens the PII access surface beyond the source table.
- User / business impact: personal data outlives the business purpose and appears in admin exports.
- Security / privacy / reliability impact: privacy — excessive retention/exposure of personal data; forensics — false confidence in redaction.
- Recommended fix: replace the substring filter with an explicit allowlist or recursive value-level scrubbing covering `name`/`title`/`job_title`; add a regression test.
- Suggested validation: unit test logging metadata with `name` and nested `email`, asserting the insert payload contains no PII.
- Owner suggestion: API platform / security
- Effort estimate: M
- Dependencies: none
- Status: open
- Endpoint / data path: any `logAuditEvent` caller → `audit_logs` → `GET /api/v1/audit/export`
- Attack path: none identified

### Finding: No data-subject access/export/erasure path or DSAR runbook; offboarding never removes profile or auth records

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/web/app/(public)/privacy/page.tsx:96-110` — rights exercised only by emailing contact@mainecybertech.com
  - No export/erasure endpoint and no `auth.admin.deleteUser` anywhere (grep of apps/api, apps/worker)
  - `apps/api/src/routes/memberships.ts:158-172` — membership delete leaves the profile and auth user
  - `apps/api/src/routes/users.ts` — no DELETE route
  - No DSAR/erasure runbook in `docs/runbooks`/`docs/features`
- What is happening: rights requests have no documented procedure or tooling; offboarding leaves identity records indefinitely.
- Why it matters: Art. 15/17/20 requests (and processor assistance to tenants) cannot be demonstrated; stale PII accumulates.
- User / business impact: slow or inconsistent responses to data requests; staff identities persist after leaving.
- Security / privacy / reliability impact: privacy — rights fulfilment and storage limitation gaps.
- Recommended fix: add `docs/runbooks/dsar.md` and an admin-triggered account deletion/anonymisation path (auth user + profile scrub) with an audit event.
- Suggested validation: integration test that deletion removes/anonymises the profile and auth user; a DSAR tabletop with recorded timings.
- Owner suggestion: security lead + API platform
- Effort estimate: L
- Dependencies: legal review of retention obligations
- Status: open
- Endpoint / data path: (to be created) admin user deletion → `auth.users` + `profiles`
- Attack path: none identified

### Finding: Visitor IP addresses are sent to ip-api.com over plaintext HTTP for geolocation

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/api/src/routes/public.ts:60-77` — `http://ip-api.com/json/<visitor IP>` (plain HTTP, no TLS)
  - `apps/api/src/lib/http-client.ts:141` — generic `geo` client, 5s timeout, no TLS enforcement
  - `apps/web/app/(public)/privacy/page.tsx:76-80` — ip-api.com disclosed; "No data is permanently stored"
  - `apps/api/src/routes/public.ts:79-87,177,221` — the result and raw IP are stored and forwarded to Teams/JSM
- What is happening: the visitor's IP is disclosed to a third party without encryption, and the response feeds stored records and alerts.
- Why it matters: cleartext disclosure can be observed/tampered; spoofed geolocation reaches fraud-prevention inputs.
- User / business impact: personal data handled without transport protection; alert data can be manipulated.
- Security / privacy / reliability impact: privacy — unencrypted third-party disclosure; integrity — unauthenticated geolocation input.
- Recommended fix: use an HTTPS-capable provider (or ip-api's paid endpoint), or make the lookup consent-gated; add the vendor to the subprocessor list.
- Suggested validation: unit test asserting an `https://` URL; integration test with geo disabled.
- Owner suggestion: @web + API platform
- Effort estimate: S
- Dependencies: provider selection
- Status: open
- Endpoint / data path: `GET /api/v1/public/init` → ip-api.com → public_interactions
- Attack path: on-path attacker spoofs geolocation shown in lead/traffic alerts (fraud-prevention bypass assist)

### Finding: Privacy governance documentation set is missing and the published vendor list omits processors used in code

- Severity: P2
- Confidence: High
- Area: PRIV
- Evidence:
  - `ls docs`: no `PRIVACY.md`, classification, ROPA, DPA/subprocessor or platform retention-schedule document
  - `apps/web/app/(public)/privacy/page.tsx:46-82` — only GA, Tawk.to, Teams, JSM, ip-api.com listed
  - Additional processors in code: Supabase (`services/supabase.ts`), Stripe (`routes/billing.ts:234-267`), Cloudflare Turnstile (`routes/public.ts:33`), Sentry (`lib/sentry.ts:5-11`), SMTP (`lib/email.ts:20-40`), M365 Graph (`tasks/m365-calendar-sync.ts:94`), Jira (`tasks/jira-sync.ts:110`), DigitalOcean (`infra/`)
  - `docs/DATA_BREACH_RESPONSE.md:240-257` — the only category map, embedded in the breach plan
  - `docs/MODULE_SPECS_GAP_AUDIT_2026-08-05.md:411-413` — `retention_policies` is product-side, not the platform schedule
- What is happening: governance artifacts exist only as fragments and the public vendor list is narrower than the processing chain.
- Why it matters: tenant due diligence, DPA obligations and transparency cannot be answered from the repository.
- User / business impact: blocked or slow enterprise/tenant onboarding; inaccurate notice.
- Security / privacy / reliability impact: privacy — accountability/documentation gaps (Art. 30/28).
- Recommended fix: publish `docs/PRIVACY.md` (classification + retention schedule), `docs/SUBPROCESSORS.md` (vendor/purpose/data/region/DPA) and a tenant DPA template; link from the policy.
- Suggested validation: doc review; optional CI check that outbound-vendor env vars appear in the subprocessor doc.
- Owner suggestion: security lead / compliance sponsor
- Effort estimate: M
- Dependencies: counsel input for DPA/transfer wording
- Status: open
- Endpoint / data path: n/a (documentation)
- Attack path: none identified

### Finding: Breach-response and IR plans still claim Alertmanager is not deployed and IR-P0-003 is open

- Severity: P3
- Confidence: High
- Area: PRIV
- Evidence:
  - `docs/DATA_BREACH_RESPONSE.md:143-147` — "Alertmanager is not deployed … The Watchdog rule has no receiver"
  - `docs/DATA_BREACH_RESPONSE.md:444-456` — known-gaps list still includes IR-P0-003
  - `docs/INCIDENT_RESPONSE.md:123-128` — same stale claim
  - `infra/digitalocean/docker-compose.yml:244-293`, `infra/digitalocean/prometheus.yml:15-17`, `.github/workflows/deploy-do.yml:622-631` — Alertmanager is deployed and wired; previous register IR-P0-003 verified-fixed
- What is happening: compliance docs contradict the deployed monitoring path.
- Why it matters: responders are told a detection path is absent when it exists, distorting breach timelines.
- User / business impact: slower, less accurate incident communication.
- Security / privacy / reliability impact: reliability — incident-response accuracy.
- Recommended fix: update both documents' detection/gap sections and record the last dead-man's-switch test.
- Suggested validation: doc review against `docs/MONITORING_AND_ALERTING.md` §9.
- Owner suggestion: security lead
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: n/a (documentation)
- Attack path: none identified

### Finding: DATA_BREACH_RESPONSE claims audit_logs records source IP/user-agent; no runtime writer populates them

- Severity: P3
- Confidence: High
- Area: PRIV
- Evidence:
  - `supabase/migrations/5302026_supabase_consolidated_fresh_bootstrap_20260529.corrected.v3.sql:604-616` — `ip_address`, `user_agent` columns exist
  - `apps/api/src/services/audit.ts:22-50` — the only runtime insert never sets them
  - `grep 'ip_address' apps/api/src` — only `services/impersonation.ts:35`, `routes/public.ts:81`, `routes/analytics.ts:43` write IPs (not audit_logs)
  - `docs/DATA_BREACH_RESPONSE.md:134,249,255-257` — claims audit_logs records "from which IP" and contains IP/UA
  - `apps/api/src/routes/audit.ts:163-164` — CSV export includes the (NULL) columns
- What is happening: the documented forensic field is never populated at runtime.
- Why it matters: breach scoping may rely on data that does not exist.
- User / business impact: slower, less precise breach assessment.
- Security / privacy / reliability impact: reliability — forensic capability misrepresented.
- Recommended fix: populate ip/user_agent in `logAuditEvent` from the request, or correct the data map to point at `impersonation_log`.
- Suggested validation: test asserting a logged event carries the request IP (if populated); doc review otherwise.
- Owner suggestion: API platform / security
- Effort estimate: S
- Dependencies: privacy review of retaining IPs in audit logs (retention 365d)
- Status: open
- Endpoint / data path: `logAuditEvent` → `audit_logs`
- Attack path: none identified

### Finding: public-interaction-retention performs an unbounded single-statement delete and is not covered by the DATA-P1-002 batching fix

- Severity: P3
- Confidence: High
- Area: PRIV
- Evidence:
  - `apps/worker/src/tasks/public-interaction-retention.ts:20-24` — one `.delete().lt('created_at', cutoff)` statement deletes the whole backlog
  - `apps/worker/src/tasks/retention.ts:23-31,49-89` — the sibling purge is batched (BATCH_SIZE/MAX_BATCHES) and reports counts
  - `apps/worker/src/tasks/public-interaction-retention.ts:34-36` — returns `ok:true` without a count in the result
  - `apps/worker/src/main.ts:71-79` — scheduled via bespoke setInterval, absent from `apps/worker/src/schedule-config.ts:17-55`
  - No test references `public-interaction-retention`
- What is happening: the contact-form PII purge lacks the batching/lock-safety guarantee applied to audit/notification purges.
- Why it matters: after worker downtime a large backlog could hold a long transaction on a PII table; the asymmetry is easy to miss.
- User / business impact: possible lock/timeout during catch-up; slower lead tooling.
- Security / privacy / reliability impact: reliability — retention job robustness.
- Recommended fix: extract `purgeInBatches` to a shared helper, reuse it, return the deleted count, and register the task in `schedule-config`.
- Suggested validation: worker unit test for boundary + backlog batching (the missing test is separately tracked by 07's P3).
- Owner suggestion: backend/data governance
- Effort estimate: S
- Dependencies: none
- Status: open
- Endpoint / data path: worker `public-interaction-retention` → `public_interactions`
- Attack path: none identified

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Pre-consent tracking/chat cookies | P2 | High | Regulatory + trust | `layout.tsx:58-78` | Consent Mode v2 default-deny |
| Unprovable consent for collected PII | P2 | High | GDPR Art. 7 accountability | `public.ts:13-24`; `5302033` | Persist consent server-side |
| Policy/retention mismatch | P2 | Certain | Transparency failure | `privacy/page.tsx:88-93` vs worker | Align text/code |
| PII in audit trail | P2 | High | Excess personal data retention | `services/audit.ts:34-45` | Allowlist redaction |
| DSAR/erasure inability | P2 | Medium | Art. 15/17 failure; stale identities | No routes/runbook | Runbook + deletion path |
| Plaintext third-party IP disclosure | P2 | High | Privacy + integrity | `public.ts:64` | HTTPS provider |
| Missing governance docs/DPAs | P2 | High | Due-diligence failure | No docs; vendor gaps | Publish docs |
| Stale compliance docs | P3 | Certain | Misguided incident response | `DATA_BREACH_RESPONSE.md:143` | Update docs |
| Unbounded PII purge | P3 | Low | Lock/timeout after backlog | `public-interaction-retention.ts:20` | Batch the purge |

## Recommendations

### Immediate / Release Blocking

- None. No P0/P1 privacy finding was identified; the P2s below should be scheduled but do not block release.

### This Week

- Gate GA/Tawk.to behind a consent manager (Consent Mode v2 default-deny) and add the visible opt-out (`layout.tsx`).
- Add the consent checkbox + privacy link to the store quote form.
- Correct the retention sentence in `privacy/page.tsx` (or the worker window) so the published policy matches the code.

### This Month

- Persist consent (`consent`, `consent_at`, `consent_version`) and enforce it in `/public/submit` and `/store/quotes`.
- Replace the audit redaction with an explicit allowlist/recursive scrub + regression test.
- Add a DSAR runbook and an admin account-deletion/anonymisation path.
- Switch the geo lookup to HTTPS or make it consent-gated.
- Publish `docs/PRIVACY.md` (classification + retention schedule) and `docs/SUBPROCESSORS.md`; fix the two stale/incorrect breach/IR doc claims.
- Extract `purgeInBatches` for `public-interaction-retention` and register it in `schedule-config`.

### Later / Platform Evolution

- Wire `retention_policies` into the platform purge (or document why internal purges are hardcoded) — coordinate with DATA-P2-006.
- Migrate profile reads/writes to the encrypted column and drop plaintext, or formally document the mirror as defence-in-depth (coordinate with the security domain).
- Add CI guards: policy-vs-code retention check; outbound-vendor doc check; consent regression tests.
- Plan the quarterly DSAR tabletop and breach-register review.

## Quick Wins

| Quick win | Why it helps | Files likely involved | Validation |
|---|---|---|---|
| Fix the retention sentence | Removes a public misstatement | `privacy/page.tsx` | Doc review |
| Add consent checkbox to quote form | Closes the only form with no consent UI | `QuoteBuilderClient.tsx` | E2E |
| Add `name`/`title`/`job_title` to the redaction list (interim) | Stops the biggest audit-PII leak | `services/audit.ts` | Unit test |
| Use `https://ip-api.com` (paid) or disable geo | Removes cleartext disclosure | `public.ts`, `http-client.ts` | Unit test |
| Correct the alertmanager/IP claims in the breach plan | Keeps responders accurate | `DATA_BREACH_RESPONSE.md`, `INCIDENT_RESPONSE.md` | Doc review |
| Reuse `purgeInBatches` | One-line import + loop | `public-interaction-retention.ts` | Worker test |

## Hardening Backlog

| Backlog item | Priority | Owner suggestion | Effort | Dependency |
|---|---|---|---|---|
| Consent manager + Consent Mode v2 | P2 | @web | M | none |
| Server-side consent persistence | P2 | API platform | M | migration |
| Audit redaction allowlist + tests | P2 | API platform | M | none |
| DSAR runbook + account deletion | P2 | security lead + API | L | legal review |
| HTTPS geo provider | P2 | API platform | S | vendor |
| Privacy/classification/subprocessor docs | P2 | compliance sponsor | M | counsel input |
| Retention schedule + policy alignment | P2 | security lead | S | none |
| Batched PII purge + schedule-config registration | P3 | backend/data | S | none |
| Wire `retention_policies` into purge | P3 | backend/data | M | DATA-P2-006 decision |
| Policy-vs-code CI guard | P3 | platform/CI | S | docs |

## Suggested Tests

- Unit: audit metadata with `name`, `title`, nested `email` never reaches the insert payload (`services/audit.ts`).
- Unit: consent required — POST `/public/submit` and `/store/quotes` reject missing/false consent; consent fields persisted.
- Unit: `public-interaction-retention` deletes only rows older than the cutoff and reports the count (mock currently ignores the cutoff per 07's P3).
- Unit: geo lookup uses HTTPS (or is skipped) — assert the URL scheme.
- Integration: profile deletion/anonymisation removes the profile row and auth user (or scrubs identifiers) and writes an audit event.
- E2E: cookie banner deny/accept changes whether GA/Tawk.to requests are issued (network assertions).
- E2E: quote form blocks submission without consent.
- CI: doc check that the retention figure in `privacy/page.tsx` matches the worker constant; optional vendor-doc check for new outbound env vars.
- Security/regression: export an audit CSV and assert no raw person names appear.
- Manual: tabletop a DSAR (access + erasure) and record timings; quarterly breach-register review.

## Suggested Documentation Updates

- Create `docs/PRIVACY.md`: data classification, retention schedule (table → window → owner), encryption assumptions, DSAR pointer.
- Create `docs/SUBPROCESSORS.md`: vendor, purpose, data categories, region, DPA status; link from the privacy page.
- Create `docs/runbooks/dsar.md`: intake, identity verification, export query set, erasure/anonymisation, response clock.
- Update `apps/web/app/(public)/privacy/page.tsx`: retention alignment, cookie table, consent/opt-out, vendor completeness.
- Update `docs/DATA_BREACH_RESPONSE.md`: detection sources (alertmanager deployed), audit_logs field truth, gap list.
- Update `docs/INCIDENT_RESPONSE.md` §8: remove the stale IR-P0-003 gap statement.
- Update `docs/VISITOR_ALERTS.md` / add a retention note: policy-vs-purge relationship.
- Update `docs/SECRETS_ROTATION.md` (already good) with a pointer from the privacy doc for `FIELD_ENCRYPTION_KEY`/`BACKUP_ENCRYPTION_KEY`.

## Open Questions

| Question | Why it matters | Evidence needed |
|---|---|---|
| Is `FIELD_ENCRYPTION_KEY`/`BACKUP_ENCRYPTION_KEY` escrowed, and where? | Key loss breaks decryption/restores | Escrow location + last drill |
| What is the retention of Teams/JSM/Sentry/Stripe copies of lead data? | The policy claims 3 years; vendor-side retention unknown | Vendor settings/exports |
| Is Supabase/DigitalOcean at-rest encryption contractually guaranteed? | Underpins the encryption-at-rest claim | Provider docs/DPA |
| Does the breach register exist and has a row ever been exercised? | Plan completeness | Register excerpt (off-repo) |
| What is the DSAR volume and who owns responses? | Sizing the runbook | Support metrics |
| Is GA configured with a retention setting and IP anonymisation? | Policy claim | GA property settings |
| Are `store_analytics_events` (IP/UA, no purge) and `impersonation_log` (no purge) intended to be permanent? | Retention inventory completeness | Owner decision |

## Appendix

### A. Data classification inventory (repository-derived)

| Class | Data | Stores (evidence) | Retention today | Protection today |
|---|---|---|---|---|
| Identity/contact | name, email, phone, title, avatar | `profiles` (+`encrypted_pii`), `memberships`, `contract_signers` | none | RLS org-scoped; AES-GCM mirror (additive) |
| Prospect/lead | name, email, phone, company, message, IP, UA | `public_interactions` (90d purge), `store_quote_requests` (none), `store_leads` | partial | RLS off for public_interactions (insert-only by design); purge worker |
| Tenant employee (client of tenant) | email, name | `phishing_targets`, `offboarding_checklists`, `identity_verifications` | none | RLS org-scoped |
| Auth/security | email, password hash, MFA secrets, recovery code hashes | `auth.users` (Supabase), `mfa_recovery_codes`, `api_keys`, `break_glass_accounts` | none | hashed codes; Supabase-managed |
| Activity/audit | actor id, action, metadata, IP/UA | `audit_logs` (365d), `impersonation_log` (none), `store_analytics_events` (none) | partial | org-scoped reads; shallow redaction |
| Billing | billing email, Stripe ids, amounts | `billing_customers`, `subscriptions`, `invoices`, `payments`, `organizations.billing_email` | none | Stripe-hosted card data; plaintext email |
| Content | files, messages, tickets, forms | `documents`, `chat_messages`, `tickets`, `dynamic_form_submissions`, `satisfaction_pulses` | none | private bucket; RLS |
| Backups | full DB + storage | S3/Spaces dumps | 30 days | AES-256-CBC, offsite option |

### B. Control readiness matrix (lenses only — no compliance claimed)

| Lens | Relevant control | State | Evidence |
|---|---|---|---|
| GDPR | Consent (Art. 7) | ✗ partial | UI-only checkboxes; no record |
| GDPR | DSAR (Art. 15-17) | ✗ absent | No tooling/runbook |
| GDPR | Security of processing (Art. 32) | ~ partial | Field encryption mirror; encrypted backups; plaintext PII |
| GDPR | Transparency (Art. 13-14) | ~ partial | Policy exists; retention/vendors inaccurate |
| CCPA | Notice at collection / opt-out | ~ partial | Policy exists; no cookie opt-out |
| SOC 2 (privacy) | Data retention & disposal | ~ partial | Purges exist; schedule unpublished; stores unpurged |
| ISO 27001 | Asset/records inventory | ✗ absent | No classification/ROPA |
| NIST 800-53 | AU-* audit content | ~ partial | Audit trail exists; IP/UA missing; redaction shallow |
| CIS | Data protection controls | ~ partial | Encryption keys managed; at-rest assumption undocumented |
| HIPAA (if applicable) | ePHI handling | Unknown | No ePHI-specific controls; MCT is MSP processor |
| PCI DSS | Card data | ✓ n/a | Stripe-hosted; no PAN storage (`billing.ts`) |
| CMMC | Records management | ~ partial | Governance module is product-side; platform docs missing |

### C. Privacy workflow review

1. **Visitor lands on a public page** → `layout.tsx` loads GA + Tawk.to pre-consent; `/init` stores IP/UA/location/referrer (geo over HTTP) in `public_interactions`; bot rows filtered from alerts.
2. **Visitor submits contact/intake** → consent checkbox (client) → `/public/submit` (no consent field) → PII stored + Teams card + JSM ticket → audit event with `name` → 90-day purge; forwarded copies persist at vendors.
3. **Visitor submits a quote** → no consent → `store_quote_requests.customer` jsonb + `store_leads` + audit with name/email → no purge.
4. **User invited** → `auth.admin.inviteUserByEmail` + profile upsert (`organizations.ts:96-130`); profile PATCH writes `encrypted_pii`; avatar upload to public bucket.
5. **User offboarded** → membership row deleted only (`memberships.ts:158-172`); profile/auth user remain.
6. **Admin reviews/export** → `/audit` org-scoped list/export (export audited); metadata may contain names/titles.
7. **Breach** → `DATA_BREACH_RESPONSE.md` (register off-repo); detection relies on audit_logs/impersonation_log/Sentry/Prometheus; audit_logs IP/UA are NULL.
8. **Retention** → daily worker purges audit_logs (365d) + notifications (90d) + public_interactions (90d); everything else unbounded.

### D. Cross-domain references (not re-filed here)

- `06_security_authz_tenancy_audit`: "PII field encryption is additive…" (P2, open) — same subject, security owner.
- `07_data_schema_migration_runtime_validation`: DATA-P2-005 (audit cascade/archive), DATA-P2-006 (stores lack retention; `retention_policies` unused), P3 (PII purge untested).
- `26_admin_console_abuse_case_audit`: ADMIN-P2-002 (org delete unrecoverable), ADMIN-P2-004 (destructive deletes not audit-logged).
- `29_billing_payments_reconciliation_audit`: billing email plaintext, Stripe lifecycle.
- `31_search_indexing_privacy_audit`: search-term hashing (verified-fixed), PII projection fixes.
- `39_analytics_tracking_privacy` (planned): AN-P3-001 consent-mode signalling; `store_analytics_events` IP/UA and lack of purge.
- `28_file_upload_download_security_audit`: documents retention/AV/backup.

### E. Command log (read-only)

```
git log -1 --format='%H %s'                          → 8d299b8dc271c410b9ae2ceeda3d2c6c997af8fd Merge PR #168...
git log --oneline 9c0b88c..8d299b8d | wc -l          → 113 (no privacy-surface commits)
grep -rn -i 'consent|CookieBanner|onetrust|cookiebot' apps/web ...   → form checkboxes only
grep -rn -i 'googletagmanager|tawk|gtag(' apps/web   → layout.tsx:61,66,73
grep -rn 'consent' apps/api/src/routes/public.ts     → no matches
grep -rn 'deleteUser' apps/api/src apps/worker/src   → no matches
grep -rn 'ip_address' apps/api/src                   → impersonation.ts:35, public.ts:81, analytics.ts:43
grep -rhoE '<email regex>' docs/audits               → security@/noreply@mainecybertech.com, someone@example.com only
grep -rnE 'AKIA|ghp_|sk_live_|BEGIN PRIVATE KEY' docs/audits → scanner pattern definitions only
```

## Findings

| ID | Severity | Title |
|---|---|---|
| PRIV-P2-001 | P2 | Google Analytics and Tawk.to load on public pages with no cookie-consent or opt-out gate |
| PRIV-P2-002 | P2 | Consent is captured only in the browser and never recorded or enforced server-side; the store quote form collects PII with no consent at all |
| PRIV-P2-003 | P2 | Published retention statement (three years) contradicts the 90-day contact-form PII purge |
| PRIV-P2-004 | P2 | Audit-log PII redaction is a shallow key-name filter; person names and job titles are persisted for 365 days |
| PRIV-P2-005 | P2 | No data-subject access/export/erasure path or DSAR runbook; offboarding never removes profile or auth records |
| PRIV-P2-006 | P2 | Visitor IP addresses are sent to ip-api.com over plaintext HTTP for geolocation |
| PRIV-P2-007 | P2 | Privacy governance documentation set is missing and the published vendor list omits processors used in code |
| PRIV-P3-001 | P3 | Breach-response and IR plans still claim Alertmanager is not deployed and IR-P0-003 is open |
| PRIV-P3-002 | P3 | DATA_BREACH_RESPONSE claims audit_logs records source IP/user-agent; no runtime writer populates them |
| PRIV-P3-003 | P3 | public-interaction-retention performs an unbounded single-statement delete and is not covered by the DATA-P1-002 batching fix |
