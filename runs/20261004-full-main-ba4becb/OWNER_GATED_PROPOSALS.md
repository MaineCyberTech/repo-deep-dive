# Owner-gated findings — proposals and residuals

Run: `20261004-full-main-ba4becb` · Target: `falcon-edge` @ `ba4becb`

This run has **no open P0/P1 code-fixable findings** — the three P1s are verified-fixed history
(`EXEC-P1-001`, `FINAL-P1-001`, `SEC-P1-001`, all one root cause, closed by PS-001/#17), and
`AUTH-P2-001` was fixed post-run by PR #46 (`a549337`, see `verification_log.md`).

The items below are the remaining **owner decisions**. No infrastructure was changed for them.
Each entry records a concrete proposed option and the residual that remains until the owner
decides.

## ARCH-P2-001 — Control plane executes a mutable working tree (dirty-guarded, not pinned)

- **Evidence**: `src/falcon_control/*` health surfaces `source_commit`/`source_dirty`; the deploy
  path runs the checked-out tree with only a dirty guard (run finding 02).
- **Proposed option (lower effort)**: keep the dirty guard and adopt a **pinned release bundle**
  (immutable artifact + SHA-256) as the deploy source; verify the digest at start and record the
  bundle id in health.
- **Alternative (heavier)**: containerise the control plane and deploy immutable images.
- **Residual until decided**: a compromised/edited working tree can still be executed; the guard
  only detects dirt, it does not pin provenance.

## ARCH-P2-002 / RES-P2-001 — Single-host control plane has no warm standby or tested failover

- **Evidence**: one lab host runs the control plane; no replica and no dated failover exercise
  (run findings 02 and 13).
- **Proposed option (recommended)**: accept a **documented and tested RTO/RPO** instead of a warm
  standby — e.g. RPO 24 h (nightly backup) and RTO 24 h (cold restore onto a rebuilt host), with
  the existing backup/verify/restore tooling (`backup/`, `automation/`) recorded as evidence.
- **Alternative**: provision an isolated host or warm standby with a documented failover.
- **Residual until decided**: host loss is total control-plane loss; recovery is a cold restore
  bounded by the (currently undated) RTO/RPO.

## BP-P2-001 — Branch protection / required checks are plan-gated

- **Evidence**: the ready payload is documented (`docs/.../BRANCH_PROTECTION.md`) but cannot be
  enforced on the current GitHub plan.
- **Proposed option**: upgrade to GitHub Pro/Team and apply the ready payload; until then retain
  the compensating CI gate (unresolved P0/P1 gate).
- **Residual until decided**: server-side required checks remain unenforceable; only client-side
  gates apply.

## SC-P2-004 — Credential-bearing image artifacts rely solely on private-repo access

- **Evidence**: image releases carry baked credentials and are protected only by repository
  visibility (run finding 11).
- **Proposed option**: keep the repo private, **rotate baked credentials per release**, and record
  the rotation; move to artifact-level access control if the exposure window must shrink.
- **Residual until decided**: anyone with repo read access can pull a release containing baked
  credentials.

## OBS-P2-001 / NOTIF-P2-001 — No alert delivery path (rules visible only in Prometheus/Grafana)

- **Evidence**: alert rules exist but no Alertmanager/pager receiver is wired (run findings 14/30).
- **Proposed option**: either wire the edge rules to an Alertmanager/receiver, or document the
  central stack's receiver as the authoritative delivery path and link it from the edge runbooks.
- **Residual until decided**: alerts are passive dashboards; no push notification on breach.

## AUTH-P2-001 residual — Dedicated Vector client certificate

- **Evidence**: fixed commit `a549337` keeps the sensor key `0600` and delivers it to Vector via
  systemd `LoadCredential`; Vector still presents the **sensor's** identity.
- **Proposed option**: issue a distinct, independently revocable Vector client certificate
  (CA voucher or a control-plane relay identity accepting a second cert), plus an image re-bake.
- **Residual until decided**: Vector shares the sensor identity (it no longer reads the sensor key
  file, and the key is no longer group-shared).
