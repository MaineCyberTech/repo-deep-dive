# Patch plan

## CI-P1-001 - P1 secret gate in the org scan is inert: it matches 'SEC-' IDs but deterministic findings are namespaced 'DET-'

Match on the subcode instead of the ID, e.g. `if f.get('severity') == 'P1' and str(f.get('title','')).startswith('[SEC]')`, or (preferred) have deterministic_checks.py emit a machine-readable `subcode`/`area` field on each finding and gate on that. Add a unit/CI test that feeds a synthetic P1 SEC deterministic-findings.json through the gate and asserts a non-zero exit.

## SEC-P2-001 - PAT embedded in git clone URL in three workflows (contradicts the hardened extraheader pattern)

Use the extraheader form from deep-dive-deterministic.yml (or `git -c credential.helper=` with a header) in remediation.yml, verify-remediation.yml and lab-tests.yml; never interpolate GH_TOKEN into the remote URL. Optionally use a short-lived GitHub App installation token or GITHUB_TOKEN with scoped permissions instead of a long-lived PAT.

## CI-P2-001 - verify-remediation executes arbitrary commands from a PR-controllable plan on the self-hosted lab runner

Constrain `run`/`ref` to trusted refs (default branch, or an allowlisted set), pin the plan to a commit whose digest is verified, and run verification in an ephemeral/microVM runner or container with no org secrets. Treat remediation_plan.json verification commands as untrusted input and require an explicit approval-protected environment before executing them.

## SUPPLY-P2-001 - 15 GitHub Action refs are tag-pinned (@v4/@v5), not commit-SHA pinned

Pin all external `uses:` to full commit SHAs with a trailing `# vX.Y.Z` comment (Dependabot already updates github-actions weekly per .github/dependabot.yml, so pins stay current). Add a lint in tools/deterministic_checks.py (already exists) as a required check so tagged refs fail the pack CI.

## SUPPLY-P2-002 - Two large third-party binaries are committed into an archived run with no checksum record

Remove the binaries from the archived run (keep the verify.sh that downloads them by pinned version+SHA), or add a SHA256SUMS file and a check that verifies it before use. If the blobs must stay for provenance, move them to Git LFS and record their sha256 in the run manifest.

## SEC-P2-002 - publish_audit.py publishes findings/reports to the pack and a target-repo PR without a secret scan

Before writing/PR-ing, run gitleaks (--redact) over the assembled file set and fail closed on any hit; strip or redact secret-like strings in evidence; record the scan result in the run manifest. Alternatively call the existing deterministic secret check on the source dir and block publication on P1.

## CI-P3-001 - The changed-run gate enforces only P0 and only on pull_request; pushes to main skip it

Run the changed-run gate on push to main as well as pull_request, and make the gate severity configurable (fail on P0 by default, optionally P1). Keep documenting the admin/force-push bypass, but pair it with a branch-protection checklist and an auditable CHANGELOG exception entry (CONTRIBUTING.md:74 already asks for the latter).

## PORT-P3-001 - 35 tracked shell scripts carry mode 100644 (no exec bit)

Run `git update-index --chmod=+x` for the 35 scripts (a one-line loop over `git ls-files -s | awk '$1=="100644" && /[.]sh$/ {print $4}'`), and add a lint (already detected by deterministic_checks.py check_portability) as a required check so new exports do not regress.

## CI-P3-002 - actionlint reports shellcheck SC2015/SC2018 notes in four workflows

Rewrite the three guards as explicit `if [ -z "$HOST" ] || [ -z "$USER" ]; then echo ...; exit 1; fi` and replace `tr 'A-Z' 'a-z'` with `tr '[:upper:]' '[:lower:]'`. Alternatively add a targeted actionlint shellcheck-ignore if the idiom is intentional.

## CONF-P3-001 - gitleaks generic-api-key hits in shipped runs/ artifacts are false positives; allowlist does not cover them

Confirm the remaining seven hits and allowlist the known-safe run paths in .gitleaks.toml (e.g. `runs/.*/(diff\.patch|pr_body\.md)$` plus the long-hex manifest pattern), or move published run artifacts to a gitleaks-clean serialization. Prefer narrowing by rule (`generic-api-key` with entropy/length guards) over broad path allowlists so a real key in a diff is still caught.

## CONF-P3-002 - secrets: inherit passes every repo/org secret into the reusable lab-preflight workflow

Replace `secrets: inherit` with an explicit `secrets: LAB_ENDPOINT_SSH_KEY: ${{ secrets.LAB_ENDPOINT_SSH_KEY }}` mapping in all three callers, matching the workflow_call contract already declared in lab-preflight.yml.

## CI-P3-003 - lab-tests.yml interpolates a dispatch input directly into a shell command on the lab runner

Pass the command through an `env:` variable (e.g. `CMD: ${{ inputs.command }}`) and run `bash -o pipefail -c "$CMD"` so the value is data, not script text; keep dispatch restricted to trusted users and drop GH_TOKEN from the step env unless needed.

