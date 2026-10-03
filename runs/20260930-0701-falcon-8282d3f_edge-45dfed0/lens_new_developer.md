# Lens — New Developer (Onboarding Experience)

## Audit Metadata

- Audit name: repo-deep-dive · Profile: falcon-lab v1.0.0 (pack v1.2.1) · Run: `20260930-0701-falcon-8282d3f_edge-45dfed0`
- Repos: falcon-build @ `8282d3f` (dirty: parallel-session REVIEW-FIX evidence edit + untracked audit folder) · falcon-edge-build @ `f1c5def` (run start `45dfed0`; clean at write time)
- Prompt: lens `new_developer` (`lenses/new_developer.md`, area `ND`) · Prior lens: `runs/20260930-0320-falcon-794ba31_edge-2b5bc8b/lens_new_developer.md`
- Targets: 01, 09, 10, 12, 16, 19, 21, 32, 41, 42 · Limitation: read-only account (no root/docker); mutating scripts inspected, never executed; live state from domain reports
- Output: `docs/audits/repo-deep-dive/20260930-0701-falcon-8282d3f_edge-45dfed0/lens_new_developer.md`

## Scope

The onboarding experience of both repos as a competent stranger: entry-document authority, literal quick-start walk (read-only steps only), dangerous-tooling labeling, prerequisites, vocabulary, first-week task discovery, hidden knowledge. Domain facts are owned by the target reports; this lens adds the onboarding view and cross-references, never duplicates.

## Evidence Reviewed

| Evidence | Why relevant |
|---|---|
| falcon `README.md`, `AGENTS.md`, `REPOSITORY.md`, `docs/README.md`, `docs/runbooks/OPERATOR_START_HERE.md`, `docs/phase9/VPN_ONBOARDING_CHECKLIST.md` | first-hour reading path, quick start, danger labels |
| falcon `ci/validate.py`, `bootstrap/run-all.sh`, `automation/vpn/test_{tunnel,closed_mode}.sh`, `automation/validation/{probe_pipeline_test,verify_publication_chain}.sh` | literal walk; safe-vs-mutating labeling |
| falcon ledgers/digest/closeout, `SENSOR_SILENCE.md:27-28`, `RESTORE.md:54-56`; edge `README.md`, `AGENTS.md`, `REPOSITORY.md`, `docs/{README,GITHUB_CI}.md`, `docs/phase1/TEST_PLAN.md` | status authority; incident docs; edge path |
| edge `ci/validate.sh`, `automation/evidence/capture.sh`, `.github/workflows/dependabot-merge.yml`, `closeout/OWNER_ACTIONS.md` + domain reports 01, 09, 10, 12, 16, 19, 21, 32, 41, 42 + prior lens | literal walk; record mutation; evidence base |

## Verification Performed

| Check | Method | Result |
|---|---|---|
| Entry-doc read/walk | README/AGENTS/REPOSITORY/docs maps, both repos | Reading order only at falcon `docs/README.md:3`; edge map has none |
| Literal quick start, falcon step 1 | `PYTHONDONTWRITEBYTECODE=1 python3 ci/validate.py` | exit 1 — `FAIL secret scan findings`, 3 × `long_hex` in this run's `01:6`, `02:6`, `43:8` (reproduced) |
| Literal quick start, falcon step 3 | `bash automation/validation/verify_publication_chain.sh` | exit 0, `publication_chain_failures=0`; two signed archives intact |
| Literal quick start, edge step 1 | `PYTHONDONTWRITEBYTECODE=1 bash ci/validate.sh` | exit 0 `validation: ALL PASS` (88 gates, 321 captures, 897 files); no test invocation observed |
| Scripts inspected read-only | run-all, probe test, VPN tests, capture.sh, ci scripts | Warnings inside scripts, not in README quick start; `capture.sh` writes evidence |
| Vocabulary/prereq greps | glossary, PyYAML, requirements, reading-order greps | No glossary; no `requirements*.txt`/`pyproject.toml`; PyYAML undocumented |
| Mutation check | `git status --short` before/after; `GITHUB_CI.md:73` vs cron `23 5 * * *` | No mutation (falcon dirty-state identical; edge clean); stale cadence confirmed |

## Executive Summary

Both programs are real and evidence-disciplined, but day one is adversarial. The central README's first documented command fails in the delivered tree with a message that reads like a secret leak; the quick-start "health" block includes a root script that stops the central aggregator with no warning at the point of use; and `run-all.sh` prints "all stages complete" after 4 of 22 stages. Neither repo's onboarding docs list prerequisites (PyYAML is imported, no requirements manifest) or a glossary for "gates, ledgers, feeds, rebind, pairing, R2, EVE, ISM". Status authority is split across README/AGENTS, ledgers, digest and closeout with no declared precedence — the contradictions are domain-owned (DOC-P1-001/002, EVID-P1-003, HYGIENE-P2-003/004), but nothing tells a newcomer which wins. The edge quick start's evidence example mutates append-only records under a real gate ID. Findings: 1 × P1, 5 × P2, 1 × P3.

## Onboarding Walkthrough (literal journey, read-only)

### Central (falcon-build), first hour

1. Root docs are README/AGENTS/REPOSITORY; no CONTRIBUTING/START_HERE. `docs/README.md:3` declares a reading order but the root README never points to it. **Friction: authority/reading order unowned (ND-P1-001).**
2. README:8-13 says production "not supported" and P9 gates open; `AGENTS.md:71-73` lists closed gates as open; digest/ledgers say APPROVED / 101 PASS. **Documented-but-wrong (DOC-P1-001/EVID-P1-003).**
3. Step 1 `python3 ci/validate.py` → exit 1, "FAIL secret scan findings" pointing at this run's own audit reports; no known-failure note. **Undocumented-blocking (ND-P2-001).**
4. Step 2 `sudo bootstrap/run-all.sh` runs stages 10/20/30/40 then echoes "all stages complete" (`run-all.sh:5-11`); central compose needs stage-50 `central.env`. **Documented-but-wrong (DOC-P1-003/INFRA-P3-001); step 3 `docker compose up -d` then fails or leaves a partial stack — newcomer concludes the repo is broken.**
5. "# health + verification": README:45 lists `probe_pipeline_test.sh`; the script warns at :9-10 that test 3 stops the aggregator and `OPERATOR_START_HERE.md:51` marks it DISRUPTIVE, but README does not; VPN checklist :17-18 runs both VPN tests bare. **Undocumented-at-use (ND-P2-002).**
6. `verify_publication_chain.sh` → 0 failures (the one green step). It does not check the approval binding, so green coexists with EVID-P0-001/XREPO-P0-001. **False confidence.**
7. Incident runbooks still say "no VPN"/"no physical SPAN" (SENSOR_SILENCE:27-28) and no scheduled/offsite backup (RESTORE:54-56). **Documented-but-wrong (INFRA-P1-001).**
8. Secrets are root-only `/srv/falcon/secrets` + owner `/home/user/.env`; no newcomer path to obtain any credential. **Owner-gated, undocumented.**
9. No local test loop: falcon has no unit tests; 66/461 test rows cite `/tmp/opencode` scripts and 264/462 evidence metas bind a host symlink. First-week work lives in off-repo audit files (README:12-13) and ledgers; no roadmap/module template. **Not reproducible from a clone (ND-P2-004; TEST-P2-004/005); undocumented roadmap (EVOL-P2-001).**

### Edge (falcon-edge-build), first hour

1. README:24 says hardware proven, but `AGENTS.md:43-45` says adapters NOT attached and `REPOSITORY.md:22` says HARDWARE not present while the Pi is enrolled. **Documented-but-wrong (DOC-P1-002).**
2. Step 1 `ci/validate.sh` → ALL PASS (reproduced) but runs no tests; the suite command appears only in `docs/phase1/TEST_PLAN.md:25` and CI docs. **Undocumented-discoverable (TEST-P2-001).**
3. Step 2 `capture.sh --gate P0-G01 --name example -- …` appends `evidence/raw/P0-G01/…`; step 3 rewrites index/manifest — the "quick start" mutates append-only records under a real gate ID. **Undocumented-at-use (ND-P2-005).**
4. Docs map lists empty `phase10/`, README layout lists a non-existent `bootstrap/`, `GITHUB_CI.md:73` says "every 20 minutes" vs cron `23 5 * * *`, closeout says "120 tests" vs 163; the live control plane runs from the working tree (`WorkingDirectory=/home/user/falcon-edge-build`), so "deploy" is not reproducible from a clone. **Documented-but-wrong (DOC-P2-003, CI-P3-001, HYGIENE-P2-004; XREPO-P2-004).**

## Inventory

| Item | State | Onboarding risk |
|---|---|---|
| Central entry docs | Production state stale; closed gates listed open | High — ND-P1-001 |
| Green path to first task | None; validate red, run-all partial | High — ND-P2-001/003 |
| Safe-vs-mutating labeling | Scripts warn; README/checklist do not | Medium — ND-P2-002 |
| Prerequisites/dev loop | Undocumented; no requirements manifest | Medium — ND-P2-003 |
| Lab-host binding | Off-repo links, host-absolute metas, `/tmp` tests | Medium — ND-P2-004 |
| Edge quick start | Green validate; record-mutating example | Medium — ND-P2-005 |
| Glossary / cross-program orientation | Absent / falcon root silent on edge | Low — ND-P3-001 |

## Findings

### Finding ID: ND-P1-001 - No orientation layer tells a newcomer which status document is current

- Severity: P1 · Confidence: High · Area: ND (both repos)
- Evidence:
  - falcon `README.md:8-13` (production not supported; P9 gates open) and `AGENTS.md:71-73` (P8-G10/P9 open) vs `PACKAGE_DIGEST.txt` (APPROVED, open_gates=none) and gate ledgers (101 PASS/1 N/A per 01/16/41); `progress_ledger.md:17-18` (62 PASS, verdict IE) and `closeout/FINAL_RESPONSE.json` (IE, `12aa2fd`) stay quotable as current
  - edge `AGENTS.md:43-45` / `REPOSITORY.md:22` (adapters NOT attached; HARDWARE not present) vs `README.md:24` and P6-G05 PASS
  - No `CURRENT_STATE`/`START_HERE` artifact or superseded banners anywhere; edge `docs/README.md` has no reading order and lists empty `phase10/`; contradictions are domain-owned (DOC-P1-001, DOC-P1-002, EVID-P1-003, HYGIENE-P2-003/004)
- What is happening: the orientation surface mixes current ledgers with stale prose; no document declares precedence or reading order for a stranger.
- Why it matters: hour one produces the wrong model of production readiness and open work; agents then chase closed gates.
- User / business impact: wasted first week; false external statements; trust erosion in the evidence system.
- Security / privacy / reliability impact: indirect — wrong incident expectations (INFRA-P1-001) and misdirected effort.
- Recommended fix: generated `docs/CURRENT_STATE.md` in both repos (fields derived from ledgers/verdict), linked from README/AGENTS; dated superseded banners on phase history; single reading order.
- Suggested validation: CI drift check entry-doc fields vs ledger-derived values; grep for closed gate IDs in entry docs returns none.
- Owner suggestion: both maintainers · Effort estimate: S · Dependencies: DOC-P1-001/002, EVID-P1-003 · Status: still-open (prior ND-P1-002; absorbs prior ND-P1-005 edge residual)

### Finding ID: ND-P2-001 - The first documented command is red and reads like a secret leak

- Severity: P2 · Confidence: High · Area: ND (falcon-build)
- Evidence: `README.md:32-34` calls `python3 ci/validate.py` "safe, no root"; reproduced exit 1 with `FAIL secret scan findings` — 3 × `long_hex` commit SHAs in `docs/audits/…/{01,02,43}*.md`; `AGENTS.md:18-19` (rule 5) requires this gate before every commit; no known-failure note; root causes CI-P2-001 / HYGIENE-P2-001 / TEST-P2-002; the scan count grows with every audit report shipped.
- What is happening: the mandated gate is unpassable in the delivered tree for a benign reason, and the failure text mimics credential exposure.
- Why it matters: a newcomer must chase a false secret, rotate credentials, or learn to ignore the mandated gate in week one.
- User / business impact: onboarding blocked at step 1 of 3; gate-bypass habit; support load.
- Security / privacy / reliability impact: scanner signal degrades; real findings risk being dismissed.
- Recommended fix: allowlist `docs/audits/**` and benign 40-hex revision IDs; print a "known false-positive class" line; document the expected-red state until fixed.
- Suggested validation: `ci/validate.py` green with run folder present; planted secret under `docs/audits/**` still fails.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: CI-P2-001 · Status: still-open (prior ND-P2-003)

### Finding ID: ND-P2-002 - Quick start lists a disruptive root script as a "health" step without warning

- Severity: P2 · Confidence: High · Area: ND (falcon-build)
- Evidence: `README.md:43-46` "# health + verification" includes `automation/validation/probe_pipeline_test.sh`; the script warns at :9-10 that test 3 stops the central aggregator; `OPERATOR_START_HERE.md:51` labels it DISRUPTIVE; `VPN_ONBOARDING_CHECKLIST.md:17-18` runs `test_tunnel.sh`/`test_closed_mode.sh` bare (both mutate network/mode state); tunnel test still dials 51820 (INFRA-P2-002); script WARN headers are recent (test_closed_mode.sh:5-7), so prior ND-P1-003 is partially fixed.
- What is happening: the safest-labeled section of the first document points at state-mutating root scripts; warnings live only inside scripts and one runbook.
- Why it matters: a first-week operator can take ingestion down or churn the firewall believing they are "checking health".
- User / business impact: unnecessary outage drill; downtime confusion; tunnel/firewall churn.
- Security / privacy / reliability impact: brief central-ingestion outage; WireGuard mode changes; verification targets the wrong port.
- Recommended fix: move mutating tests to a "mutating verification" section with inline warnings; point health checks at `central_health.sh`/`span_mirror_check.sh`; add checklist warnings; parameterize the tunnel port.
- Suggested validation: README/runbook grep shows no unlabeled mutating script under "health"; checklist carries warnings.
- Owner suggestion: falcon maintainer · Effort estimate: S · Dependencies: DOC-P2-001, INFRA-P2-002 · Status: still-open (prior ND-P1-003 partially-fixed)

### Finding ID: ND-P2-003 - A fresh checkout cannot reach a running dev/test environment

- Severity: P2 · Confidence: High · Area: ND (both repos)
- Evidence: no prerequisites in `README.md:30-47` or `docs/README.md`; `ci/validate.py:20` imports PyYAML (third-party) and neither repo has `requirements*.txt`/`pyproject.toml` (verified by `ls`); `run-all.sh:5-11` runs 4 of 22 stages then prints "all stages complete" (DOC-P1-003/INFRA-P3-001); falcon has no unit tests and its 461 test rows are live root executions (09); edge suite command exists only at `docs/phase1/TEST_PLAN.md:25` and in CI docs, while README/AGENTS flows stop at `ci/validate.sh` (TEST-P2-001).
- What is happening: the documented path assumes the owner's lab host and pre-installed tooling; there is no clean-clone setup or safe local test loop.
- Why it matters: a competent stranger cannot reach "green + tests" without asking the owner what to install and where to run.
- User / business impact: first-week setup depends on tribal host knowledge; reviewer onboarding repeats the same conversations.
- Security / privacy / reliability impact: ad-hoc setup may skip pinned tooling conventions.
- Recommended fix: add prerequisites (Python version, PyYAML, Docker, jq, openssl, host assumptions) plus pinned requirements; ship `QUICKSTART.md` per repo (validate → tests → CP/enroll; validate → ordered bootstrap stages); `run-all.sh --full` or explicit stage list.
- Suggested validation: new account follows QUICKSTART on a clean clone to green validate + suite; staged clean-host rehearsal reaches healthy compose.
- Owner suggestion: both maintainers · Effort estimate: S/M · Dependencies: DOC-P1-003, DOC-P2-003, TEST-P2-001 · Status: still-open (prior ND-P1-004)

### Finding ID: ND-P2-004 - Onboarding and verification artifacts are bound to the lab host

- Severity: P2 · Confidence: High · Area: ND (both repos)
- Evidence: `README.md:12-13` points to `/home/user/falcon-full-review-2026-09-23.md` and `/home/user/falcon-audit-2026-09-24.md` — outside the repo, only on the shared host; `REPOSITORY.md:37-40` documents absolute evidence-metadata paths with a prefix-rewrite rule; 264/462 metas resolve only via the `/home/user/monitoring-build` symlink (TEST-P2-005); test rows cite `/tmp/opencode` scripts (66/461 falcon, 200/313 edge; TEST-P2-004); edge CP runs from the working tree (XREPO-P2-004); the edge mirror promised by `audit_manifest.json` is empty (HYGIENE-P2-001).
- What is happening: docs, evidence and "tests" that look reproducible are bound to one host's paths, symlinks and temp history.
- Why it matters: a reviewer, successor or off-host newcomer cannot open the referenced reviews or reproduce most test conclusions from the repo alone.
- User / business impact: external review trust gap; handover depends on the original machine.
- Security / privacy / reliability impact: evidence chain cannot be independently verified off-host.
- Recommended fix: bring state/review documents into the repo; store meta paths package-relative at index time; promote recurring `/tmp` procedures into `automation/validation/`; populate or document the edge mirror.
- Suggested validation: validators pass in a clean clone with no symlink; every README link resolves inside the repo.
- Owner suggestion: both maintainers · Effort estimate: M · Dependencies: TEST-P2-004/005, DOC-P2-002, XREPO-P2-004 · Status: still-open (prior ND-P2-011; ND-P2-009/010 partial)

### Finding ID: ND-P2-005 - Edge quick start's example mutates the append-only evidence record

- Severity: P2 · Confidence: High · Area: ND (falcon-edge-build)
- Evidence: `README.md:66-70` — step 2 is `automation/evidence/capture.sh --gate P0-G01 --name example -- <command>`; step 3 runs `index.sh` + `manifest.sh create`; `capture.sh` writes `evidence/raw/<GATE>/<timestamp>_<name>.out` + `.meta.json`; `AGENTS.md` hard rules 2-3 make those records append-only; the example uses a real program gate ID (`P0-G01`), has no `--dry-run`, and step 1 is labeled safe while step 2 is not.
- What is happening: following the documented quick start literally appends an "example" capture under a real gate and dirties tracked evidence/index/manifest files.
- Why it matters: gate-linked evidence noise on first contact; record discipline looks loose exactly when first touched.
- User / business impact: review confusion; cleanup effort; weaker gate-evidence hygiene.
- Security / privacy / reliability impact: none direct; record integrity only.
- Recommended fix: reorder the quick start (validate → tests → "recording changes"), use a clearly non-gate example or a `--dry-run`, and state what capture/index/manifest change.
- Suggested validation: dry-run capture leaves the tree clean; quick-start walk ends with `git status` clean.
- Owner suggestion: edge maintainer · Effort estimate: S · Dependencies: none · Status: open (new)

### Finding ID: ND-P3-001 - Orientation aids missing: no glossary, no cross-program signposting

- Severity: P3 · Confidence: High · Area: ND (both repos)
- Evidence: `grep -ri glossary` over both repos (excluding audit outputs) returns nothing while entry docs use gates, ledgers, doctrine, append-only, rebind, pairing, R2, EVE, ISM, DLQ, SPAN, canary without definitions; falcon `README.md` never mentions falcon-edge/falcon-edge-build or the pairing pin — first pointer is `REPOSITORY.md:58` under "Recent additions" plus `docs/edge/EDGE_RELEASE_PIN.md`; edge `README.md:10-11` does name the monitoring program.
- What is happening: project-specific terms are used from line 3 of the first documents, and a central newcomer can operate for days without learning the sibling program and live sensor exist.
- Why it matters: vocabulary must be inferred from ledgers; the sensor, tunnel and delivery dirs are needed to interpret host state and the stale pin (XREPO-P0-001).
- User / business impact: slower comprehension; incomplete mental model; duplicated discovery.
- Security / privacy / reliability impact: low.
- Recommended fix: add `docs/GLOSSARY.md` per repo and a "Related repositories / programs" section in the falcon README linking the pin and a one-paragraph pairing overview.
- Suggested validation: every README/AGENTS term appears in the glossary; README links resolve in-repo.
- Owner suggestion: both maintainers · Effort estimate: S · Dependencies: DOC-P2-002, XREPO-P0-001 · Status: open (new; prior ND-P3-007 partially-fixed)

## Cross-References

| ND-ID | Related domain ID(s) | Relationship |
|---|---|---|
| ND-P1-001 | DOC-P1-001, DOC-P1-002, EVID-P1-003, HYGIENE-P2-003/004 | same contradictions; lens adds the missing orientation/authority layer |
| ND-P2-001 | CI-P2-001, HYGIENE-P2-001, TEST-P2-002 | root causes domain-owned; lens adds first-step impact and triage gap |
| ND-P2-002 | DOC-P2-001, INFRA-P2-002 | checklist/runbook residual + stale VPN tools |
| ND-P2-003 | DOC-P1-003, DOC-P2-003, TEST-P2-001, INFRA-P3-001 | deploy/prereq/test-loop gaps from a clean clone |
| ND-P2-004 | TEST-P2-004/005, DOC-P2-002, XREPO-P2-004, HYGIENE-P2-001 | host-bound paths, /tmp tests, empty mirror |
| ND-P2-005 | DOC-P2-003 (related quickstart gap) | edge quick-start record mutation; no domain duplicate |
| ND-P3-001 | DOC-P2-002, EVOL-P2-001, prior ND-P3-007, XREPO-P0-001 | vocabulary + sibling visibility; pairing pin stale |

## Prior-Run ND Findings at Current Commits

| Prior ND | Status now | Current evidence / successor |
|---|---|---|
| ND-P1-001 | verified-fixed | derived verdict, chain 0 failures; residual N/A omission = HYGIENE-P2-002 |
| ND-P1-002, ND-P1-004 | still-open | DOC-P1-001/EVID-P1-003; DOC-P1-003/INFRA-P3-001 |
| ND-P1-003, ND-P1-005 | partially-fixed | ND-P2-002/DOC-P2-001; DOC-P1-002 (AGENTS/REPOSITORY stale, README fixed) |
| ND-P2-001/002/003 | still-open | HYGIENE-P2-002; HYGIENE-P2-003/EVID-P1-002; TEST-P2-002 |
| ND-P2-004, ND-P2-006/007/008 | still-open | INFRA-P2-001; INFRA-P2-002; DOC-P2-001/INFRA-P1-001; EVID-P2-003 |
| ND-P2-005, ND-P2-009/010, ND-P2-015, ND-P2-017 | partially-fixed | INFRA-P2-002 (trap fixed, port stale); INFRA-P2-003; 07/44; XREPO-P0-001/P1-001 |
| ND-P2-011/012/013/014/016/018 | still-open | TEST-P2-005; CI-P2-004; HYGIENE-P2-004; TEST-P2-003/07/13; INFRA-P2-003; 44 |
| ND-P3-001/002/003/004/005/008/010 | still-open | 001/002/003 → DOC-P2-002; 004 → HYGIENE-P2-002; 005 → HYGIENE-P3-002/EVID-P2-003; 008 → HYGIENE-P3-002; 010 → HYGIENE-P3-002/ACM-P2-001 |
| ND-P3-006, ND-P3-007, ND-P3-009, ND-P3-011 | partially-fixed | CI exists but unexercised (CI-P2-001/002); ND-P3-001/DOC-P2-003; DOC-P2-003; TEST-P2-001/CI-P2-004 |

## Risks

| Risk | Severity | Likelihood | Impact | Evidence | Mitigation |
|---|---|---|---|---|---|
| Newcomer adopts stale state as truth | High | High | wrong work/statements | ND-P1-001 | CURRENT_STATE + drift check |
| First command red → gate bypass | Medium | High | real findings dismissed later | ND-P2-001 | scanner allowlist + known-failure note |
| Disruptive script run as health check | Medium | Medium | ingestion outage | ND-P2-002 | inline warning + reorder |
| Onboarding depends on owner/lab-host knowledge | Medium | High | slow handover | ND-P2-003/004 | QUICKSTART + prerequisites + portable paths |
| Quick start pollutes append-only records | Medium | Medium | evidence hygiene | ND-P2-005 | dry-run/reorder |

## Recommendations

### Immediate / Release Blocking
- Scanner allowlist + known-failure note so the documented first step can be followed (ND-P2-001 ↔ CI-P2-001).
- Publish `docs/CURRENT_STATE.md` in both repos, linked from README/AGENTS (ND-P1-001 ↔ DOC-P1-001/002, EVID-P1-003).

### This Week / This Month
- Fix the README "health + verification" block and the VPN checklist (ND-P2-002 ↔ DOC-P2-001); add prerequisites + QUICKSTART per repo and reorder the edge quick start (ND-P2-003/005); bring the off-repo review/audit documents in-repo (ND-P2-004).
- Portable evidence meta paths and in-repo recurring procedures (ND-P2-004 ↔ TEST-P2-004/005); glossary + related-repositories sections (ND-P3-001); roadmap pointer (EVOL-P2-001).

## Quick Wins

| Quick win | Why it helps | Files | Validation |
|---|---|---|---|
| Allowlist `docs/audits/**` 40-hex IDs | unblocks first documented step | `secret_scan.py`, `.gitleaks.toml` | validate green with run folder |
| Move probe test out of "health" | removes outage footgun | `README.md` | README grep |
| "Not in repo" banners on off-repo links | stops dead ends | `README.md:12-13` | links resolve |
| Five-line prerequisites block | unblocks clean clones | both `README.md` | fresh-clone walk |

## Hardening Backlog

| Backlog item | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|
| CURRENT_STATE + doc-drift CI | P1 | both maintainers | M | digest derivation |
| Portable evidence/index paths | P2 | falcon maintainer | M | package rebuild |
| QUICKSTART + prerequisites + pinned requirements | P2 | both maintainers | S/M | none |
| Glossary + cross-program section | P3 | both maintainers | S | none |

## Suggested Tests

- CI doc-drift: entry-doc gate/verdict fields vs ledger-derived values; fail closed.
- CI scanner fixture: run folder present → PASS; planted secret under `docs/audits/**` → FAIL.
- Onboarding smoke: clean clone, no host symlinks → validate + suite green following QUICKSTART only.
- Quick-start hygiene: after the edge walk, `git status` clean (example appends nothing).

## Suggested Documentation Updates

- New: `docs/CURRENT_STATE.md`, `docs/GLOSSARY.md`, `QUICKSTART.md` (both repos); "Related repositories" section (falcon README).
- Update: falcon README quick start ("health" vs "mutating"), AGENTS gate list, prerequisites; edge README quick-start order, AGENTS:43-45/REPOSITORY:22 hardware lines, `GITHUB_CI.md:73` cadence; superseded banners (DOC-P2-001).

## Open Questions

1. Who owns keeping a current-state document true — maintainer or owner? (ND-P1-001)
2. Is PyYAML-as-host-tool accepted, or should both repos ship pinned requirements? (ND-P2-003)
3. Should audit run folders be committed (with scanner allowlist) or archived outside the repos? (ND-P2-001; HYGIENE-P2-001)
4. Does edge intend a newcomer quick start separate from the owner actions list? (ND-P2-003/005)

## Appendix

- Read-only commands: `git log/status/rev-parse`, `python3 ci/validate.py` (exit 1), `bash automation/validation/verify_publication_chain.sh` (0 failures), `bash ci/validate.sh` edge (ALL PASS), `head/sed/grep/ls`; `git status` re-check showed no mutation.
- Not executed: bootstrap stages, docker compose, probe/VPN tests, `capture.sh`, `manifest.sh create`, live-host or GitHub actions.
- Counts: ND findings 7 (P1 ×1, P2 ×5, P3 ×1); prior ND statuses 34 (verified-fixed 1, partially-fixed 11, still-open 22). Secrets: none reproduced; paths/types only.
