# Operator Quickstart — Falcon Lab Edition

## Purpose

Run the Repo Deep-Dive Full Hardening audit against the falcon monitoring lab (central + edge + shared live host) using the falcon-lab profile.

## Preconditions

1. The pack is available at `/home/user/Prompts/repo-deep-dive/` (or vendored into the central repo — see "Vendoring" below).
2. Read `profiles/falcon-lab.md` — especially the boundaries (§3), applicability matrix (§4), and reconciliation rule (§9).
3. Know the repo state: branch, HEAD SHA, dirty state for both repos. If a parallel session is active, note it.
4. Confirm the live-host access mode for this run: read-only by default; any sanctioned destructive step must be listed before starting.
5. New to these repos (or reusing this pack elsewhere)? Read `docs/AUTOMATION_GUIDE.md` and keep `runbooks/OPERATOR_TROUBLESHOOTING.md` handy.

## Steps

1. **Pick the runner.** Open `prompts/MASTER_RUNNER_FALCON_LAB.md` and paste it into your AI coding agent with both repos accessible.
2. **Set the run name.** `{run}` = `YYYYMMDD-HHMM-falcon-<sha7>_edge-<sha7>` (fallback `YYYYMMDD-HHMM-manual`).
3. **Confirm the agent creates both run folders:**
   - Canonical: `<falcon>/docs/audits/repo-deep-dive/{run}/`
   - Edge mirror: `<edge>/docs/audits/repo-deep-dive/{run}/`
4. **Wave 0 first.** Verify the recon outputs before the fan-out: `INDEX.md` skeleton, `audit_manifest.json` (schema: `examples/audit_manifest.falcon-lab.example.json`), repo/host snapshot, prompt status list.
5. **Wave 1 (domains), Wave 2 (lenses), Wave 3 (synthesis), Wave 4 (wiring).** The runner defines the order; do not skip wave 0.
6. **Review the final files in this order:**
   - `EXECUTIVE_SUMMARY.md`
   - `RELEASE_GATE.md` (audit opinion — reconcile with program verdicts, never overrides them)
   - `risk_register.md`
   - `patch_plan.md`
   - `follow_up_register.md`
   - Lens reports (`lens_*.md`)
   - Detailed domain reports
7. **Apply the doctrine wiring** (operator, not the audit): add the proposed decision-log entry; update the repos' risk registers/follow-up tracking through the normal flow.

## Vendoring (optional)

By default the pack runs from its own location and only run folders are written into the repos. To vendor it into the central repo, copy the pack to `<falcon>/docs/audits/repo-deep-dive/` and record the pack version in the run manifest. Do not vendor while a parallel session is mid-change; coordinate first.

## Audit-only guardrail

During an audit run the agent must not modify application code, configs, ledgers, gates, pins, or live systems. It writes markdown audit artifacts under the run folders only.

## Recommended remediation flow

1. Fix P0 findings first.
2. Fix P1 release blockers next.
3. Add regression tests (or validation scripts) for every fixed finding.
4. Update docs and runbooks.
5. Re-run the relevant domain prompt(s).
6. Re-run prompts `22`, `23`, and `40` to refresh the risk register, release gate, and changelog.

## Verification-only pass

For findings already fixed, run the runner's verification mode: re-check evidence at the current SHA, mark `verified-fixed` / `partially-fixed` / `still-open` / `regressed` in `verification_log.md`, append notes to the original findings, and refresh `22`/`23`/`40`. This is the fast path after a remediation round and the correct input for the next independent review.
