# Verification log

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-03T05:36:41Z | PATCH-01 | open | partially-fixed | 1b9b0ca096b9493936e7d7c74600e330082542f8 | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| 2026-10-03T05:36:58Z | PATCH-01 | open | partially-fixed | 1b9b0ca096b9493936e7d7c74600e330082542f8 | Draft PR #56 opened; deletion-only change removes deploy-time Management API SQL (RLS users_select USING(true), workspace_members DDL, auth token/identity/password UPDATEs, seed-file execution) from both deploy workflows. |
| 2026-10-03T05:59:16Z | PATCH-16 | open | partially-fixed | https://github.com/MaineCyberTech/chat/pull/57 |  |
| 2026-10-03T06:35:24Z | PATCH-04 | open | partially-fixed | c41aa79994f291f22b12a0b9504edb88170c1ff8 | draft PR #58 commit c41aa79; SEC-P1-004/005/006 fixed too but not mapped in remediation_plan.json |
| 2026-10-03T06:36:51Z | PATCH-04 | open | partially-fixed | c41aa79994f291f22b12a0b9504edb88170c1ff8 |  |
| 2026-10-03T06:49:30Z | PATCH-05 | open | partially-fixed | 9bd4f88f22cbee0f2de45c635fcdfc6f04deb052 |  |
| 2026-10-03T06:49:47Z | PATCH-05 | open | partially-fixed | 9bd4f88f22cbee0f2de45c635fcdfc6f04deb052 | Draft PR #59 commit 9bd4f88: webhooks+push use service-role client, socket builds per-user client from JWT; FEAT-P1-002 durable BullMQ retries deferred to PATCH-09 |
| 2026-10-03T06:57:13Z | PATCH-02 | open | partially-fixed | 3fc2091f6cea856e90d492220b926bbf0da73801 | removed+ignored credential; rotation required out-of-band |
| 2026-10-03T07:03:04Z | PATCH-03 | open | partially-fixed | 6733291c22a8c21a7c2b094e52886ade75229d8e | Draft PR #61 commit 6733291c: removed --volumes from docker system prune in both deploy workflows (prod :287/:527, dev :219); named volumes preserved. |
| 2026-10-03T07:12:43Z | PATCH-06 | open | partially-fixed | 7481c5f4e9186c28eb17bd080e232a302c121d40 |  |
| 2026-10-03T07:27:06Z | PATCH-07 | open | partially-fixed | 0432329731582dc61933b124084b628ffb0b7b4b | draft PR; blocking gates + time-boxed exceptions; see remediation/PATCH-07/verify.log |
| 2026-10-03T08:24:12Z | PATCH-07 | open | partially-fixed | 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2 | draft PR; security gates blocking + time-boxed exceptions; E2E setup verified, test run blocked on lab; see remediation/PATCH-07/verify.log |
| 2026-10-03T08:38:48Z | PATCH-09 | open | partially-fixed | 7e1f260a804dfb7896a970c342274d45c2defa24 | Draft PR #64 commit 7e1f260: durable BullMQ webhook retries with jobId/delay, cumulative retry count + DLQ in worker, stable per-delivery idempotency key, decrypted-secret signing; FEAT-P1-003 in the plan is not a real finding (FEAT-P2-003 idempotency gap addressed). |
| 2026-10-03T09:35:33Z | PATCH-07 | open | partially-fixed | 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2 https://github.com/MaineCyberTech/chat/pull/63 | draft PR; security gates blocking + time-boxed exceptions; E2E gate blocking, auth spec fails identically at base a72b8cc (pre-existing /login render issue); see remediation/PATCH-07/verify.log |
| 2026-10-03T09:36:23Z | PATCH-09 | open | partially-fixed | 7e1f260a804dfb7896a970c342274d45c2defa24 https://github.com/MaineCyberTech/chat/pull/64 |  |
| 2026-10-03T09:36:23Z | PATCH-07 | open | partially-fixed | 9afa84904cfc7c23abbbf3d204c584fdc4df5aa2 https://github.com/MaineCyberTech/chat/pull/63 |  |
| 2026-10-03T09:48:50Z | PATCH-08 | open | partially-fixed | 9feae529cc04e0f53e87abb1539b7307dbf62dbf https://github.com/MaineCyberTech/chat/pull/65 | Draft PR #65: restrict /metrics to METRICS_TOKEN, drop channel_id label. |
| 2026-10-03T09:59:29Z | PATCH-12 | open | partially-fixed | d458b82e1a6ba11dd87b91b07d60aa7c53396f28 https://github.com/MaineCyberTech/chat/pull/66 |  |
| 2026-10-03T10:10:59Z | PS-U11 | open | partially-fixed | 52588c328c4a8521ff155ce0882733c9e7ceb95f https://github.com/MaineCyberTech/chat/pull/67 | PS-U11 draft PR #67; webhook secrets required (>=16), CSRF length check, socket joined-room guard; lab 492 tests pass, gitleaks clean |
| 2026-10-03T10:16:30Z | PS-U03 | open | partially-fixed | 8e5ab8a47a84f97d6e77847d0a33d4c70ca20fb3 https://github.com/MaineCyberTech/chat/pull/68 | Draft PR #68 (PS-U03). CI-P2-006/007 fixed in workflow code; CI-P1-001 in-repo branch-rules gate fixed, production environment reviewers + required PR review remain repo settings. |
| 2026-10-03T10:23:29Z | PS-U06 | open | partially-fixed | 92ef54074256aec75e3858f3339a28c21a980d4e https://github.com/MaineCyberTech/chat/pull/69 |  |
| 2026-10-03T10:33:25Z | PS-U07 | open | partially-fixed | f4bcb403785130f14d73e644996266226af25add https://github.com/MaineCyberTech/chat/pull/70 | docs: database change & deploy governance (FINAL-P1-002); workflow DDL/DML removal owned by PATCH-01 #56 |
| 2026-10-03T10:39:55Z | PS-U05 | open | partially-fixed | 82f8eaa2c8525febd24f6fbaa7c0ef93de28de82 https://github.com/MaineCyberTech/chat/pull/71 |  |
| 2026-10-03T10:50:24Z | PS-U01 | open | partially-fixed | 43ad5e62db6ce224c696cf4c24c7887333ae41c5 https://github.com/MaineCyberTech/chat/pull/72 | draft PR #72 |
| 2026-10-03T10:55:42Z | PS-U02 | open | partially-fixed | 5dbe6652c1039f3d0b0bb518fef45ae2eca64c0d https://github.com/MaineCyberTech/chat/pull/73 |  |
| 2026-10-03T11:10:09Z | PS-U04 | open | partially-fixed | 937b43983fd3efc836f19af8407e4f06e8fcfbc2 https://github.com/MaineCyberTech/chat/pull/74 |  |
| 2026-10-03T11:17:35Z | PS-U08 | open | partially-fixed | cc41daee2b2e7d8bc4b27beafafe43ad59708a7b https://github.com/MaineCyberTech/chat/pull/75 |  |
| 2026-10-03T11:27:23Z | PS-U09 | open | partially-fixed | 3a46f2f8c3ab723d3f07402e1559bca9094e21a1 https://github.com/MaineCyberTech/chat/pull/76 |  |
| 2026-10-03T11:33:32Z | PS-U10 | open | partially-fixed | fdadf5941c86b0b27182c8289e4812300455e7ce https://github.com/MaineCyberTech/chat/pull/77 |  |
| 2026-10-03T11:41:07Z | PS-U12 | open | partially-fixed | a202fad83cd2fceb244dc6e815d76da7d8cb9978 https://github.com/MaineCyberTech/chat/pull/78 |  |
| 2026-10-03T11:49:16Z | PS-U13 | open | partially-fixed | fe04ab3a01cd04ff3dcc8c9a4cce6153c0340f9b https://github.com/MaineCyberTech/chat/pull/79 |  |
