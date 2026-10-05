# 38_env_secret_rotation — Prompt 38 - Environment and Secret Rotation Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `38_env_secret_rotation.md` (area SECRET, prompt)

## Verification Performed

Secrets: no secrets committed; gitleaks no-leak; host-only secrets live in /home/user/.env and the service-role key is env-injected. Residual: config.ts defaults RM_SUPABASE_SERVICE_ROLE_KEY to '' and supabase.ts returns null when empty, so a misconfigured production deploy runs without trusted persistence instead of failing closed; METRICS_TOKEN has no rotation procedure.

## Findings

| ID | Severity | Title |
|---|---|---|
| SECRET-P2-001 | P2 | Empty service-role key silently disables trusted persistence |
| SECRET-P3-001 | P3 | METRICS_TOKEN has no rotation path |
