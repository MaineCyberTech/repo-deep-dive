# 06_security_authz_tenancy_audit — Prompt 06 - Security, Authorization, and Tenancy Audit

- Run: `falcon-20261004-0333-fast-main-f9cb67d`
- Target: `falcon` @ `f9cb67d` (branch `main`)
- Domain: `06_security_authz_tenancy_audit.md` (area SEC, prompt)

## Verification Performed

Read-only review of the security/authn surface at `f9cb67d`: Traefik dynamic routing (`config/traefik/dynamic.yml`), the inherited-credential rotation tracker, and the secret-scanning configuration. Reconciled against the focused lens run `falcon-20261004-0700-main-ff868e5` and the 2026-10-03 full-domain run.

- `git grep ntfy-auth` shows `config/traefik/dynamic.yml:26` defines `ntfy-auth` but no router uses it; only `falcon-ntop` carries `falcon-basic-auth`.
- `docs/security/INHERITED_CREDENTIAL_ROTATION.md:7,91` still records `20/20 PENDING`; `automation/validation/rotation_status.py` prints `20 items, 0 rotated, 20 pending` against the real tracker.
- `.gitleaks.toml` now anchors the curl-auth-user allowlist to runtime-variable/placeholder values (SEC-001 fix retained).

No secrets were printed; only names/hashes were read.

## Findings

| ID | Severity | Title |
|---|---|---|
| SEC-P2-001 | P2 | Public-facing routers rely only on Cloudflare Access; `ntfy-auth` is dead config |
| SEC-P2-002 | P2 | All 20 inherited credentials remain PENDING rotation; 28 vendored scripts source credential files wholesale |
