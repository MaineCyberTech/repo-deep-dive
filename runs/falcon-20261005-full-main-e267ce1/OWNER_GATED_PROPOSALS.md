# Owner-gated findings — proposals and residuals

Run: `falcon-20261005-full-main-e267ce1` · Target: `falcon` @ `e267ce1`

These two P1 findings are **owner decisions**. No infrastructure was changed for them. Each
entry records a concrete proposed option and the residual that remains until the owner
decides.

## ARCH-P1-001 — Single-host concentration: host loss is total pipeline loss

- **Evidence**: `README.md:57-62` (single Ubuntu 24.04 KVM host), `compose/central/docker-compose.yml`
  (one central stack, no warm standby).
- **Proposed option (recommended, lower effort)**: accept a **documented and tested RTO/RPO**
  rather than build a warm standby.
  - RPO 24 h — nightly offsite backup (`bootstrap/80-offsite-backup.sh`) is the recovery point.
  - RTO 24 h — cold restore of the encrypted config archive + OpenSearch snapshots onto a
    rebuilt host, using the now-gated end-to-end restore assertion
    (`ci/validate.py restore-assertion`, PR #48) as the tested recovery path.
  - Owner signs the RTO/RPO acceptance in `ledgers/decision_log.md` and `docs/CURRENT_STATE.md`;
    a restore drill on the rebuilt host is recorded as evidence.
- **Alternative**: procure/provision a warm standby host (large effort, ongoing cost).
- **Residual until decided**: host loss is total pipeline loss; recovery is a cold restore
  bounded by the (currently ungated) RTO/RPO. No warm standby exists.

## DATA-P1-001 — Wazuh and IRIS data have no retention (unbounded index growth)

- **Evidence**: `docs/runbooks/RETENTION_MATRIX.md`, `docs/runbooks/SCHEMA_AND_RETENTION.md`,
  `config/opensearch/falcon-eve-ism-policy.json` (falcon-eve only).
- **Proposed option**: apply OpenSearch ISM/ILM policies to the Wazuh and IRIS indices and
  record the policy ids:
  - Wazuh: hot 90 d, delete after 180 d (aligns with the incident-retention expectations in
    the retention matrix).
  - IRIS: hot 90 d, delete after 180 d.
  - Reuse the falcon-eve policy pattern; add a metrics check for unmanaged indices
    (`SEARCH-P2-001`) when the policies roll out.
- **Residual until decided**: Wazuh/IRIS indices grow unbounded (disk cost and unbounded
  search surface); applying retention is destructive and needs the owner-approved windows
  before it is enabled. No infra change was made.
