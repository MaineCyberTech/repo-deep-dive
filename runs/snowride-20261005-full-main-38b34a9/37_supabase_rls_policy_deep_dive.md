# 37_supabase_rls_policy_deep_dive — Prompt 37 - Supabase RLS Policy Deep-Dive Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `37_supabase_rls_policy_deep_dive.md` (area RLS, prompt)

## Verification Performed

RLS deep dive: 43 CREATE POLICY statements, 106 SECURITY DEFINER functions, owner-scoped SELECT with service-role writes, and 16 SQL negative suites run in CI. Residual: some social_guard_* SQL paths treat a caller with no JWT claims as trusted (resolved earlier as SEC-P3-001), which is safe only while those functions remain service-role-only.

## Findings

| ID | Severity | Title |
|---|---|---|
| RLS-P3-001 | P3 | Claim-less SQL callers are treated as trusted by social_guard_* |
