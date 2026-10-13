# 32_backup_restore_drill — Prompt 32 - Backup and Restore Drill Audit

- Run: `falcon-20261009-2117-full-08e20d1`
- Target: `falcon` @ `08e20d1` (branch `main`)
- Domain: `32_backup_restore_drill.md` (area DR, prompt)

## Verification Performed

# Backup and Restore Drill Audit

## Audit Metadata

- Audit name: repo-deep-dive
- Run: `falcon-20261009-2117-full-08e20d1`
- Repository: `falcon` @ `08e20d1` (branch `main`)
- Host observed read-only: `falcon` (live lab host, UTC)
- Generated at: 2026-10-09T21:55Z
- Auditor: subagent (DR)
- Area code: DR
- Scope limitation: read-only; the only live state examined is stamps, journals, the snapshot repository listing, and read-only cluster settings; no restore was executed by this audit.

## Scope

Reviewed the full backup lifecycle at `08e20d1`: OpenSearch snapshot job, encrypted configuration archive, new-services archive, Wazuh indexer snapshots, offsite upload/verification/retention, R2 cold copy, restore rehearsal and assertion, encryption/key custody, and RPO/RTO documentation. Live verification covered: backup/offsite success stamps, the local snapshot repository listing, the snapshot job's systemd journal for the last 8 days, the offsite log tail, edge-secrets archives, cluster settings, and alert delivery for backup-staleness. Supabase-specific items from the prompt are not applicable (this repository does not use Supabase); seeds/export tools are not present in the conventional sense and are marked accordingly.

## Evidence Reviewed

- `bootstrap/85-backup-job.sh`, `bootstrap/80-offsite-backup.sh`, `bootstrap/86-wazuh-indexer-backup.sh`, `bootstrap/92-cold-copy.sh`
- `automation/validation/restore_rehearsal.sh`, `restore_assertion.sh`, `offsite_verify_all.py`, `wazuh_indexer_backup.sh`, `r2_cold_copy.sh`, `backup_new_services.sh`
- `config/systemd/falcon-backup.{service,timer}`, `falcon-cold-copy.*`, `falcon-wazuh-backup.*`
- `ci/validate.py:386-400` (restore-assertion gate), `automation/validation/tests/restore_assertion_test.sh`, `tests/deadman_contract_test.sh`
- `docs/phase7/runbooks/RESTORE.md`, `docs/runbooks/WAZUH_INDEXER_BACKUP.md`, `docs/runbooks/R2_COLD_TIER.md`, `docs/security/CUSTODY_ATTESTATION.md`
- Live: `/srv/falcon/backups/*` stamps and logs, OpenSearch `_snapshot/_all` + `_cluster/settings` + `_cluster/health`, `journalctl -u falcon-backup.service`, `journalctl -u falcon-alert-relay.service`, `systemctl list-timers`

## Verification Performed

| Evidence | Type | Why relevant | Notes |
|---|---|---|---|
| `GET /_snapshot/falcon-backup/_all` | Live | Snapshot chain | Only `snap-20261007-033000`, `snap-20261009-164150` (SUCCESS) |
| `journalctl -u falcon-backup.service` | Live | Job reliability | Failed Oct 3, 8, 9; last scheduled success Oct 7 03:34Z |
| `.last_backup_epoch` / `.offsite-last-success` / `.offsite-dead-letter` | Live | Freshness truth | 16:49:51Z / 19:01:37Z / absent |
| Offsite log tail | Live | Offsite completeness | Full verify PASS 19:01Z (OpenSearch 1684, Wazuh 8450, mismatched=0) |
| `GET /_cluster/settings` | Live | Watermark state | Persistent low 93 / high 96 / flood 98 |
| `GET /_cluster/health` | Live | Cluster state | yellow, 44 unassigned shards |
| `ci/validate.py` + live tree check | Repo/Live | Restore assertion | In gate; file absent from live tree (`HEAD..origin/main` = 22) |
| Relay journal | Live | Alerting | `Backup stale` Oct 8 15:45Z → resolved Oct 9 16:51Z; `Offsite backup stale` → resolved Oct 9 19:00Z |

## Executive Summary

The designed backup lifecycle is strong on paper and mostly strong in practice: nightly OpenSearch snapshots with encrypted configuration archive, encrypted new-services and edge-secrets archives, Wazuh indexer snapshots (keep 14), a daily R2 cold copy of the oldest eligible index, a nightly full-object offsite verification (not a sample), bounded retry with a persistent dead-letter marker, and a live restore rehearsal that proved every encrypted artifact class decrypts and a 1.47M-document index restores in 21 s (2026-10-01). Offsite stamps were current at observation time (backup 16:49Z, offsite 19:01Z) after an operator recovery earlier the same day.

The core problem is the local snapshot half of the chain: the nightly job failed on Oct 3, Oct 8 and Oct 9 ("snapshot failed (state=)"), leaving no local snapshot for Oct 8 or Oct 9 03:30 and an RPO gap of ~37 hours until a manual run at 16:41Z. The probable root cause is the OpenSearch cluster being RED under data-volume watermark pressure (the cluster red alert was continuously firing from Oct 7 19:20Z to Oct 9 16:41Z; recovery evidence shows 51 unassigned shards at 90% data-LV usage). The job has a single attempt, no unit-level retry, does not log the API response, and only surfaces via a 36-hour staleness rule that fired ~12 hours after the first failed run. The prior run's DR-P3-001 (no scheduled restore assertion) remains open: the merged offline assertion is in `ci/validate.py` but is not present in the live tree (22 commits behind origin/main) and is not scheduled.

## Findings Summary

| # | Prior ID | Severity | Title | Status |
|---|---|---|---|---|
| 1 | — | P1 | Nightly backup job failed 3× in 7 days; Oct 8–9 snapshot hole; RPO gap ~37 h | open |
| 2 | DR-P3-001 | P3 | No scheduled end-to-end restore assertion; merged assertion absent from live tree | still-open |
| 3 | — | P2 | OpenSearch watermarks left relaxed (93/96/98) after the Oct 9 incident | open |
| 4 | — | P2 | Bulk telemetry snapshot repositories stored offsite unencrypted | open |
| 5 | — | P3 | Local snapshot retention ad hoc; recovery evidence contains failing delete commands | open |

## Detailed Findings

### 1. Nightly backup job failed 3× in 7 days; Oct 8–9 snapshot hole; RPO gap ~37 h (P1)

`falcon-backup.service` runs daily at 03:30 UTC and makes one snapshot attempt (`bootstrap/85-backup-job.sh:29-35`); the unit defines no `Restart=`/`OnFailure=` (`config/systemd/falcon-backup.service`). The journal shows instant failures at Oct 3 03:30:01, Oct 8 03:30:05 and Oct 9 03:30:16 ("snapshot failed (state=); not updating freshness"), each leaving an abort marker for the next run. The last scheduled success was Oct 7 03:34:52; the next success was a manual run on Oct 9 16:41:50 after the data-volume recovery, so the effective RPO for the local snapshot chain was ~37 h and snapshots `snap-20261008-*` / `snap-20261009-0330*` do not exist. The failure correlates with a RED cluster: "OpenSearch cluster red" fired continuously Oct 7 19:20Z → Oct 9 16:41Z, and the recovery evidence shows the data LV at 90% with 51 unassigned shards. The exact API response was not captured, and the OpenSearch container was later recreated, so root cause cannot be fully proven from logs (evidence gap). Detection was late by design: `falcon-backup-stale` (36 h threshold) fired Oct 8 15:45Z, ~12 h after the failed run.

**Fix:** add bounded retry with backoff to the snapshot step (mirror `80-offsite-backup.sh:75-91`), log the OpenSearch response body on failure, add an immediate failure signal (systemd `OnFailure=` unit or a short-deadline freshness rule on `.last_backup_epoch`), and check cluster health before snapshotting with a clear operator message. **Validation:** force a snapshot failure in a scratch repository and assert retry, the immediate alert, and the abort-marker lifecycle.

### 2. No scheduled end-to-end restore assertion; merged assertion absent from live tree (P3, prior DR-P3-001)

`automation/validation/restore_assertion.sh` (happy path + corrupt-object + wrong-key fail-closed cases) is wired into `ci/validate.py` (`check_restore_assertion`, lines 386-400), but it runs only in the release gate, and the live runtime tree `/home/user/falcon-build` does not contain the file (`git rev-list --count HEAD..origin/main` = 22; `ls automation/validation/restore_assertion.sh` → missing). The last live restore rehearsal is the 2026-10-01 C5 run (decrypt + 1.47M-doc restore in 21 s; `RESTORE.md` addendum). The prior run's follow-up register already marked DR-P3-001 still-open; the post-audit note (DO TLS forwarder restored, offsite catch-up stamp 19:01Z) does not change this.

**Fix:** deploy the merged tree to the lab, then add a scheduled (e.g., monthly) timer that runs the offline assertion plus a bounded live restore rehearsal with a success stamp and staleness alert. **Validation:** a recorded drill artifact with exit code, durations and byte-for-byte results.

### 3. OpenSearch watermarks left relaxed (93/96/98) after the Oct 9 incident (P2)

During the Oct 9 recovery the cluster watermarks were raised persistently (low 93%, high 96%, flood 98%; `GET /_cluster/settings`; recovery evidence step 2). The data LV is now at ~60% and root at 83% after the snapshot-repo relocation, so the relaxation is no longer needed; the decision-log row (2026-10-09T20:15Z) notes "Watermarks remain 93/96/98 persistent" without an explicit owner acceptance. With flood stage at 98%, writes continue far closer to a full volume than the 95% default, on a host that reached 90% and RED two days earlier. The cluster remains yellow with 44 unassigned shards. **Fix:** revert to defaults or record an explicit owner acceptance; document the expected single-node yellow state.

### 4. Bulk telemetry snapshot repositories stored offsite unencrypted (P2)

`bootstrap/80-offsite-backup.sh` encrypts the config, new-services and edge-secrets archives but uploads the OpenSearch and Wazuh indexer snapshot repositories as plain files (`:545-564`), and the rclone config sets no server-side encryption (`:489-503`). These repositories contain syslog, flow, IDS and Wazuh alert data. The Spaces key is access-controlled, but there is no encryption-at-rest evidence for these objects; the archive key itself is escrowed only by owner attestation (`CUSTODY_ATTESTATION.md`) and that escrow has not been drilled. **Fix:** owner-accept the plaintext-repo decision explicitly or enable SSE on the bucket/objects; add a decrypt-from-escrow drill for `backup_enc.key`.

### 5. Local snapshot retention ad hoc; recovery evidence contains failing delete commands (P3)

There is no designed local retention policy for the `falcon-backup` repository (only remote inventories are pruned). Local snapshots accumulated until the data LV hit its watermark; the Oct 9 recovery evidence shows six DELETE attempts that failed with "contains unrecognized parameter: [wait_for_completion]", and the repository now holds only two snapshots. **Fix:** document a local keep-N policy, provide a dry-run-safe prune command, correct the failing examples, and keep at least the offsite-verified window local.

## Strengths (verified)

- Nightly full-object offsite verification passed 2026-10-09 (OpenSearch 1684 files, Wazuh 8450 files, mismatched=0) with a retained-union, fail-closed prune.
- Offsite retry/backoff and a persistent dead-letter marker (`falcon_backup_offsite_dlq`), with an immediate critical rule defined in code.
- Encrypted archive classes all proven decryptable and restorable at lab scale (2026-10-01 rehearsal); Wazuh snapshots kept 14; R2 cold copy progressed through `falcon-eve-2026.09.27` (markers daily Oct 5–9).
- `backup_new_services.sh` covers WireGuard keys, Wazuh registry/config, IRIS dump, enrollment state; archives are 0600 and keep newest 7.

## Prior-Run Comparison

| Prior finding | Prior status | Current evidence | Current disposition |
|---|---|---|---|
| DR-P3-001 (no scheduled restore assertion) | still-open | Assertion merged to code and gate; absent from live tree; not scheduled | still-open (finding 2) |
| DO-side dead-man / offsite residual (post-audit note) | partially restored | `.offsite-last-success` 19:01Z; DO TLS forwarder fix commit `c13a416` on origin/main | observed, not a finding |

## Scorecard

| Category | Score | Evidence | Gap |
|---|---:|---|---|
| Database backups | 3 | Nightly snapshots + offsite; 3 failures/week; no retry | Reliability + diagnostics |
| Supabase restore docs | 0 | N/A — repository does not use Supabase | Not applicable |
| Storage backups | 3 | Snapshot repos offsite, full verify | Unencrypted; local retention ad hoc |
| Uploaded docs/files | 2 | IRIS dump + edge secrets covered | No user-file store in scope; edge rehearsal partial |
| Secrets backup | 3 | new-services + edge-secrets encrypted; key escrow attested | Escrow not drilled; plaintext repos |
| Infra config | 4 | Encrypted config archive + rehearsal | Plaintext local copy remains |
| Migration rollback | 3 | Rollback rehearsals (Sep 21; rename drill Oct 2) | Not re-run since; live tree drift |
| Export tools | 3 | offsite_verify_all, restore scripts, verify tools | — |
| Seeds | 0 | N/A — no DB seed pipeline | Not applicable |
| Restore scripts | 3 | Rehearsal + assertion; assertion not live/scheduled | Deployment gap |
| DR runbooks | 4 | RESTORE/WAZUH/R2 runbooks with residual honesty | RESTORE §3 dated 2026-09-30 |
| RPO/RTO | 2 | RPO per service documented; no formal RTO | Production-scale RPO/RTO owner-side |

## Limitations

- No restore was performed; all restore claims are from repository artifacts and the 2026-10-01 rehearsal record.
- The Oct 8–9 OpenSearch logs were lost with the container recreation, so the snapshot failure's exact API error is unknown (stated as probable cause).
- Spaces object contents/encryption were not independently inspected (no credentials used); the finding is based on script/config evidence.
- Concurrent operator work (C7 retirement, snapshot-repo relocation) was in progress during observation; stamps are quoted with UTC timestamps.

## Findings

| ID | Severity | Title |
|---|---|---|
| DR-P1-001 | P1 | Nightly backup job failed 3 times in 7 days; Oct 8-9 snapshot hole; RPO gap ~37 h; no retry and no immediate alert |
| DR-P3-001 | P3 | Scheduled end-to-end restore assertion still absent; merged assertion not present in the live tree |
| DR-P2-001 | P2 | OpenSearch disk watermarks left relaxed (93/96/98) after the Oct 9 incident; cluster still yellow with 44 unassigned shards |
| DR-P2-002 | P2 | Bulk telemetry snapshot repositories are stored offsite unencrypted; only config/secrets archives are encrypted |
| DR-P3-002 | P3 | Local snapshot retention was ad hoc under pressure; recovery evidence contains failing delete commands |
