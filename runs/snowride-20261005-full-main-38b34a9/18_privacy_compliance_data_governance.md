# 18_privacy_compliance_data_governance — Prompt 18 - Privacy, Compliance, and Data Governance Audit

- Run: `snowride-20261005-full-main-38b34a9`
- Target: `snowride` @ `38b34a9` (branch `main`)
- Domain: `18_privacy_compliance_data_governance.md` (area PRIV, prompt)

## Verification Performed

Privacy: a user-facing notice (privacy/page.tsx) mirrors the recorded PIA/subprocessor register; account self-service export/delete exists (PrivacyPanel, tests); VERSION_ANALYTICS_POLICY scopes PII to UUID+opaque tokens. Residual: account-deletion cascade is implemented in SQL but has no dedicated CI negative test (creator cascade does).

## Findings

| ID | Severity | Title |
|---|---|---|
| PRIV-P3-001 | P3 | Account-erasure cascade not covered by a SQL negative test |
