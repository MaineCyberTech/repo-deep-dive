# Verification findings - post-merge re-audit

- Repo: `MaineCyberTech/falcon` @ `584e1a3` (main)
- Original run: `falcon-20261009-2117-full-08e20d1`
- Procedure: `runbooks/POST_MERGE_REAUDIT.md`
- The 114 original findings were re-checked at the merged commit (per-finding evidence in
  `verification_log.md`; the full per-group reports are under `verification/`).

## New findings (this pass)

| ID | Severity | Title |
|---|---|---|
| INFRA-P1-002 | P1 | Wazuh VPN proxy sockets left dead by a reboot; no alert on the listeners |
| CI-P2-004 | P2 | Publication equality gate red after post-publication code commits (rebind owed) |
| INFRA-P1-003 | P1 | enroll.mainecybertech.us dead: dropped from the effective tunnel ingress |
| INFRA-P2-004 | P2 | Tunnel ingress source-of-truth drift (remote-managed config vs local file) |
