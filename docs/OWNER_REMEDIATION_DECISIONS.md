# Owner remediation decisions

Human owner decisions raised during the remediation of the repo-deep-dive audits. These were
**not** auto-decided: each remediation PR either deferred them with an open question or documented
them as owner/provisioning actions. Grouped by repo. Severity is the associated finding's.

> Generated registers (`OWNER_DECISIONS.md`) list machine status; this file lists the substantive
> decisions. Provide a decision + owner + date, then reconcile via `tools/remediation_status.py`.

## falcon
- **DATA-P1-001** — Retention windows for Wazuh indices (suggested alerts 90 d / stats 30 d) and IRIS
  Postgres (no default exists). The target stores are outside the central OpenSearch deploy path.
  Owner: ops/data. *(still-open)*
- **CI-P1-002** — Branch protection / required checks; required reviewers for the merge environment
  are plan-gated on the current GitHub plan. Owner: repo admin.
- **OBS-P2-001** — Alert delivery receiver (central Alertmanager vs Grafana-managed). Owner: monitoring.
- **ARCH-P1-001** — Single-host concentration: warm standby / RTO / independent external dead-man.
  Owner: ops.
- **HYG-HYG-P0-001 / FINAL-P0-001 (C1)** — Reviewer-produced disposition + verdict rebind/release
  authorization. Owner: reviewer/owner.
- **SUPPLY waivers** — `mct/compose` (archive-only) + Wazuh helper images, tracked in
  `pins/supply-chain-waivers.json` (root + ref glob, reason, owner, `review_by`). Owner: supply-chain.

## falcon-edge
- **SEC-P2-001** — Independent origin auth (mTLS/basic/OIDC) for the public routers, or a recorded
  testable owner acceptance. Owner: security/ops.
- **OBS-P2-001** — Alert delivery receiver (central Alertmanager vs Grafana unified alerting).
  Owner: monitoring.
- **SC-P2-004** — Encrypt credential side-files; scope releases to a protected environment; rotate
  baked credentials after first boot; schedule an access-revocation drill. Owner: security.
- **ARCH-P2-002** — Accept shared-host availability risk or fund a dedicated host + break-glass.
  Owner: hardware/ops.
- **HYG-P3-002** — License choice (open-source vs proprietary vs internal). Owner: legal/product.
- **EXEC-P2-001** — Production readiness remains `INSUFFICIENT_EVIDENCE`; complete the P10 gates.
  Owner: program.

## chat
- **DATA-P2-003** — Authorization intent for the duplicate `add_user_groups` migration (the second
  adds permissive policies that OR-combine). Owner: product/security.
- **HYG-P2-001** — Externalize the committed prompt/audit corpus to a separate repo/artifact store.
  Owner: org/DevEx.
- **Provisioning**: `METRICS_TOKEN`, `ALERT_EMAIL`/`ALERT_WEBHOOK_URL`, `SENTRY_DSN`,
  `WEBHOOK_ENCRYPTION_KEY`, `ERROR_LOG_FILE` volume. Owner: ops.
- **Lockfile** — broken `pnpm-lock.yaml` on `develop` (frozen install fails); fix PR in flight.

## mainecybertech
- **HYG-P2-001 / HYG-P2-002** — Externalize the prompt corpus; reconcile divergent product catalogs
  (declared intentional). Owner: org / content workflow.
- **CI-P3-001** — Promote/rename the default branch. Owner: repo admin.
- **OBS-P2-003** — Green restore drill on the deployed branch (Spaces credentials/ops).
- **Provisioning**: `FIELD_ENCRYPTION_KEY`, `TURNSTILE_SECRET_KEY`, `METRICS_TOKEN`, `DO_API_TOKEN`
  (rotation), `TF_DRIFT_PLAN_ENABLED`. Owner: ops.
- **License** — confirm ISC posture / policy.

## buddy
- **SUPPLY-P1-001 / INV-P3-001** — Final license choice; the `LICENSE` is an all-rights-reserved
  placeholder pending a product/legal decision. Owner: legal/product.
- **API-P2-001** — No server/API exists to version; deferred to future cloud work. Owner: product.

## snowride
- **SEC-P3-001** — Correct invoker signal under `SECURITY DEFINER` (`session_user`/`has_role`) +
  negative SQL suite. Owner: security/data.
- **SEC-P3-002** — Move `RM_SUPABASE_SERVICE_ROLE_KEY` to a Docker secret with boot read-order +
  deploy rehearsal. Owner: ops.
- **OBS-P1-001** — Commit the crontab/systemd schedule + alert rules and capture a live firing drill.
  Owner: ops.
- **P1-1** — Confirm the release-signature scheme/key type and supply fresh image digest out-of-band.
  Owner: owner/reviewer.

## repo-deep-dive
- **License** — final license choice (placeholder pending). Owner: legal/product.
- **Branch protection** — require PR + review + the `pack lint + self-test` / `changed-run gate`
  checks on `main`; CODEOWNERS owner handle confirmation. Owner: repo admin.
- **PS-017 / INV-P2-002** — Python-stack inventory support (routes/tables/entry points); the
  canonical tool was extended upstream.
