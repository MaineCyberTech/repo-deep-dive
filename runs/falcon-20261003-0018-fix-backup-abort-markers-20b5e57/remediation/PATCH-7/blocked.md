# PATCH-7 (DATA-P1-001) — BLOCKED, no PR opened

- Finding: `DATA-P1-001` — Wazuh and IRIS data have no retention (unbounded index growth)
- Patch set: `PATCH-7` (planned files: `bootstrap/61-search-policies.sh`,
  `automation/validation/ism_retention_metrics.sh`)
- Repo / base: `MaineCyberTech/falcon` @ `origin/main` (`430da82274af4c0821542627fdb9e6ab74afa826`)
- Outcome: **blocked on an owner policy decision** — no code change, no branch, no commit, no PR
- Evidence: `remediation/PATCH-7/verify.log`

## Why it still reproduces

At `origin/main` only central OpenSearch classes have ISM retention
(`falcon-eve-*`, `security-auditlog-*`, `top_queries-*`, ISM history, test fixtures). There is no
retention policy or lifecycle for:

- `wazuh-*` / `wazuh-monitoring-*` — and those indices are **not in the central cluster** the
  patch-set files manage; they live in a separate 3-node Wazuh indexer cluster
  (`multi-node-wazuh*.indexer-1`, `127.0.0.1:9200`).
- IRIS case data — a PostgreSQL DB (`compose/mct/iris-web`), not an OpenSearch index, so an ISM
  policy does not apply.

`bootstrap/61-search-policies.sh` talks to `falcon-central-opensearch-1` only, and
`automation/validation/ism_retention_metrics.sh` queries the central cluster's ISM history only.
A `config/opensearch/falcon-wazuh-ism-policy.json` plus a `POLICIES` row would not reach the
Wazuh indexer cluster.

## Why a fix needs the owner

The retention **window** is explicitly an owner policy decision with **no default**:

- `docs/runbooks/RETENTION_MATRIX.md` — Wazuh estate `none configured (GAP)`, "Owner decision
  needed … (suggested: alerts 90 d, statistics 30 d)"; IRIS `no retention (GAP)`, "owner decision
  for case-data lifecycle".
- `docs/phase9/OWNER_ACTIONS.md` C1 — "Suggested values are **suggestions only — owner must
  confirm**; **no default for IRIS**".
- `docs/OWNER_DECISION_PACKAGE_2026-10-02.md` E-3 (IRIS) sign-off table is empty.
- `docs/audits/AUDIT_REMEDIATION_HANDOFF.md` — "Wazuh/IRIS retention — owner policy; the Wazuh
  indices live in a separate indexer."

The remediation runner guardrail is explicit: *"If any change is ambiguous or needs a product
decision, stop and record an open question instead of guessing."* Recording a guessed window (and
writing a script that cannot reach the target cluster) would be a no-op at best and fabricated
evidence at worst, so no PR was opened.

## Open question (owner input required)

1. Wazuh indexer estate: confirm the retention windows (suggested alerts 90 d / statistics 30 d)
   and who applies ISM on that separate cluster.
2. IRIS: confirm case-data retention/RPO and whether attachments/volumes are in scope.

Once recorded in `ledgers/decision_log.md`, PATCH-7 can be implemented (likely as a new script
targeting the Wazuh indexer plus an IRIS lifecycle path, beyond the two planned files).
