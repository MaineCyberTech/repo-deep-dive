# 17_mobile_pwa_responsive_access — Prompt 17 - Mobile, PWA, and Responsive Access Audit

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `17_mobile_pwa_responsive_access.md` (area MOB, prompt)

## Verification Performed

PWA manifest + service worker + offline indicator are present and the app is mobile-first. Manifest uses SVG icons marked `any maskable`, and the runtime cache is unbounded. No apple-touch-icon or PNG fallback is provided.

## Findings

| ID | Severity | Title |
|---|---|---|
| MOB-P3-001 | P3 | Manifest relies on SVG icons flagged maskable; no PNG/apple-touch fallback |
| MOB-P3-002 | P3 | Service worker caches all runtime responses without a storage budget |
