# Owner Decisions — run `20260930-0701-falcon-8282d3f_edge-45dfed0`

Dispositions recorded 2026-09-30: the owner approved the remediation plan and every decision below ("everything is approved"). The "best option" column is the audit's analysis; execution status records what has been implemented and what remains human or scheduled.

| # | Decision | Best option (analysis) | Disposition | Execution status |
|---|---|---|---|---|
| D1 | Reviewer artifact + independence (EVID-P0-002, REV-P0-001, REV-P1-001) | Proceed with the C1 re-review/rebind: a reviewer-produced disposition by a person distinct from the implementer, digested and bound; the historical transcription stands as history; the reviewer/installer disambiguation goes into the re-review scope | APPROVED (owner, 2026-09-30) | Re-review requested; mechanical rebind scheduled with C1; transcription preserved |
| D2 | P9-G04 reset approximation (REV-P2-006) | Re-approve the lab-only hard-reset approximation (physical cuts remain a production item), recorded so the gate note and the approval align | APPROVED (owner, 2026-09-30) | Recorded in the edge decision log (D-020); gate-note alignment appended |
| D3 | Edge alert routing (INTG-P1-001, OBS-P1-004, XREPO-P1-002) | Deploy the prepared edge rules via the central Grafana path, scoped to exclude RETIRED/REVOKED sensors; add a central control-plane probe; end-to-end delivery test | APPROVED (owner, 2026-09-30) | Implemented and deployed this session (rules + probe); delivery test recorded |
| D4 | Retention vs cold-offload (RES-P0-001, DR-P1-001, SEARCH-P2-001) | Keep 14-day retention with the new 15 GiB warning band; automate the R2 cold-copy before ISM deletion as the next engineering item; alert target remains the dual ntfy path | APPROVED (owner, 2026-09-30) | Warning band + backup alerts live; cold-copy automation scheduled |
| D5 | Secrets encryption + rotation (API-P0-001, SECRET-P1-003, SC-P2-001) | Encrypt edge secrets backups (AES-256, key in `/srv/falcon/secrets/backup_enc.key`), move them off the release surface, include in offsite; rotate the exposed Wazuh credential set (VT key from the owner's console; cluster keys in a maintenance window) and scrub the repo/package at the C1 rebuild | APPROVED (owner, 2026-09-30) | Encryption + offsite implemented this session; rotation scheduled (owner supplies the VT key); scrub at rebuild |
| D6 | Edge PKI/DB offsite custody (DR-P1-005, DR-P1-004, SECRET-P1-001) | Include the encrypted edge PKI/DB backup in the falcon offsite job; key custody root-0600; document the decrypt drill | APPROVED (owner, 2026-09-30) | Implemented this session (encrypted backup path + offsite upload); drill documented |
| D7 | Privacy authority for live telemetry (PRIV-P1-001) | The owner is the network owner: grant authority for live monitoring of the owner's own devices and sites (metadata only, no payloads); update the "synthetic-only" wording | APPROVED (owner, 2026-09-30) | Recorded in the falcon decision log; wording updates routed |
| D8 | Human independence for the production verdict (REV-P1-001, REV-P0-001) | Engage the independent human reviewer for C1; regenerate the verdict wording from the ledgers at rebind | APPROVED (owner, 2026-09-30) | Same path as D1; verdict regeneration scheduled with C1 |

## Scope of the approval

The dispositions authorize executing the audit's best options. Human-only steps remain: supplying the new VirusTotal key, the reviewer's identity/artifact, physical power cuts for the production target, and the final owner adoption at rebind.
