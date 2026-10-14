# Reconciliation — bench-test full-domain run

This run is bound to `bench-test` @ `b9167095` (VERSION 1.11.3). It was executed on
2026-10-13 while the target was actively moving (see `verification_log.md`). This file
records (a) adjudications of findings whose headline claim did not reproduce, and
(b) the upstream drift observed since the pin.

## Adjudications (headline claims that did not reproduce)

| Finding | Claim | Verdict | Evidence |
|---|---|---|---|
| INV-P3-002 | "multi-MB result screenshots **and a signing key**" | **partially-not-reproducible** — there is no private signing key | `live/keys/omarchy.gpg` is a **PGP public key block** (645 bytes; `file` reports "PGP public key block"; no `PRIVATE KEY` marker). It is the Omarchy/Arch package verification key, public by design. The screenshots half is accurate: the largest tracked example PNGs are ~3.2–3.9 MB under `examples/`. Keep P3, reword to drop "signing key". |
| ORCH-P3-001 | "Deterministic finding DET-P3-002 is dropped from the aggregate with no exclusion record" | **not-reproducible** | `findings.json` contains all five deterministic findings, including `DET-P3-002` (`[DEP] trivy not installed`). Nothing was excluded. |

## Upstream drift since the pin (informational)

The target advanced well past `b9167095` while the audit and remediation ran
(`1.11.3` → `1.12.x`). At the time of writing, these run findings are **fixed
upstream** and should be re-checked before remediation:

- `ARCH-P3-002` / `DATA-P2-001` / `PERF-P1-001` / `PRIV-P2-004` / `SEARCH-P2-001` —
  upstream now has a retention policy (`RETENTION_DAYS` + `retain_old_data`).
- `SEC-P3-001` — the static handler now uses a real containment check (upstream test
  `static file serving uses a real containment check`).

All other findings remain open at the current commit unless addressed by the
remediation PR stack referenced from `docs/KNOWN_ISSUES.md` in the target.

*Recorded by the audit operator; no finding was rewritten — this is an append-only
reconciliation note.*

## Remediation outcome (appended 2026-10-14)

The remediation stack was rebased onto the moving `main` and merged. **Nothing here
is `verified-fixed` against the audit pin (`b9167095`)**: the target advanced
(1.11.3 → 1.21.x) while the work ran, and several findings were fixed upstream in
parallel. The table records what landed and how to re-check it.

| Wave | PR(s) | Scope |
|---|---|---|
| CI/CD | #39 (closed #8/#22/#32) | test workflow on push/PR, Dependabot, SHA-pinned actions, gitleaks, trivy, SBOM artifact, release provenance, PowerShell/JS syntax checks |
| Docs | #30 (closed #26) | incident-response runbook, CHANGELOG + releasing guide, operations/rollback/DR, ADRs, governance files |
| Ops/ISO | #41 (closed #38) | ISO build drops `--privileged` (cap-scoped, read-only repo), build drills, GUI cleanup guard |
| Web | #28 (closed #16/#24), #49, #50, #40 | capped-view totals, PWA, command acks + idle terminals + start-form validation, a11y test module |
| Server A | #7, #51, #52 | fail-closed auth, machine_id adoption proof; atomic run delete + `/health` capacity + backup/restore; **registration-only join token** |
| Server B | #53, #54, #55 | rate limiting + audit trail + CORS/body hardening; structured logs/request ids + `/ready` + `/metrics`; schema version + FK + atomic phase upsert + hashed api keys |
| Server C | #23, #56, #57 | 4xx validation + late-finish guard + command re-queue + verified artifact hashes; artifact delete/retention + version stamps; alert webhook + stats cache |
| Server D | #58, #59 | destructive-command confirm + exec allow/deny + key rotation/TTL + artifact limits; OpenAPI contract + command-kind registry |
| Client | #37 (closed #18/#25/#29/#33) | finish retries, atomic agent start, safe extraction, retry/backoff + circuit breaker, env-drift handling, phase registry, opt-in PII redaction + upload consent |
| Independents | #10, #13, #20, #9, #15 | IR docs; `results/` untracked (host PII); dependency manifests + CycloneDX SBOM + license policy; ISO checksum fail-closed + pinned third-party verification; version-drift/license/Windows-dep docs + CONTRIBUTING |

Superseded and closed without merge: #21 (bounded SSE + cached commit compare —
`main` had already implemented the same PERF-P2 behaviour).

Still open (maintainer's call, not part of this stack): Dependabot bumps #44–#48.

**Re-check before claiming any finding fixed:** rebase the audit pin onto current
`main`, re-run `tools/deterministic_checks.py` + the target's `tests/run_all.py`,
and confirm each finding's evidence against the current commit.

## Post-stack follow-up (appended 2026-10-14, later)

After the stack merged, the newly-added CI was made to actually pass, and the
bake/onboarding path was finished:

| Item | Change | PR |
|---|---|---|
| Dependabot bumps | #44–#48 merged (checkout v7, setup-python v7, upload-artifact v7, gitleaks-action v3, action-gh-release v3) | — |
| Bake/onboarding | the client now honours a baked `BENCHD_JOIN_TOKEN`, so a release can onboard without baking the operator token (the workflows' bake guard refuses `BENCHD_TOKEN=`); live launcher allow-list + docs updated | #60 |
| Linux CI | the Tests workflow had never completed a Linux run: venv deps (numpy/psutil) + xvfb + `--allow-skips`, Windows-only checks record a skip, POSIX-safe base-python assertion, deterministic SSE-overflow assertion, PowerShell check uses the interpreter it finds | #61 |
| Repo hygiene | 4337 generated `results/` files (a live-ISO run, host logs) untracked again — the CI check that caught them is the one from this stack | #61 |
| Secret scanning | gitleaks-action v3 needs a paid licence for orgs → replaced with the pinned, checksum-verified gitleaks CLI plus a scoped `.gitleaks.toml` for two false positives (a test placeholder and an actions/cache key) | #61 |
| Supply chain | dependency-review made advisory (needs the repo's Dependency graph enabled — recorded NEEDS-HUMAN); SARIF upload bumped off the deprecated CodeQL v3 | #61 |

Repository settings changed during the follow-up (owner identity, admin scope):
**secret scanning**, **push protection** and **Dependabot security updates**
enabled. `BENCH_AGENT_JOIN_CONF` created with a generated registration-only join
token; **the lab `benchd` must set `BENCHD_JOIN_TOKEN` to the same value** before
a baked artifact can register (owner action). Branch protection remains unset —
recorded as NEEDS-HUMAN rather than imposed.
