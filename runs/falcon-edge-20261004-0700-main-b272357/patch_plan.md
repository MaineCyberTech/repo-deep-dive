# Patch plan

## GIT-P3-001 - No repository LICENSE file (deterministic real)

Add an explicit LICENSE (and optional NOTICE) matching the intended distribution terms and reference it from README.md.

## PORT-P3-001 - Four tracked shell scripts lack the executable bit (deterministic real, impact limited)

git update-index --chmod=+x for the four paths and add a CI assertion that every tracked *.sh is mode 100755.

## PORT-P3-002 - False positive: '14 CRLF files' are intentional byte-exact evidence (*.out -text)

None for these files; keep the -text policy. Scope any future renormalization to text config/scripts only.

## SEC-P3-001 - False positive: gitleaks generic-api-key hits are allowlisted public/identifier values

No change; keep the allowlist line-scoped so a real secret on another line still alerts.

## AUTH-P2-001 - Device mTLS private key is group-readable (0640), contradicting its documented 0600

Keep the sensor identity key at 0600 and give Vector its own client certificate/identity; only widen the certificate (not the private key) to 0640. Update identity.py's docstring and SECURITY_BOUNDARY.md.

## SEC-P2-001 - mTLS clients never verify the control-plane hostname

Enable check_hostname with SANs on the control-plane certificate, or pin the control-plane certificate fingerprint / signing keyId at enrollment; document the policy.

## CI-P2-001 - bake-image interpolates secrets directly into shell script text

Pass these values via step env: and reference "$WIFI_SSID" etc. inside the script; never place ${{ secrets.* }} inside run: text.

## CI-P2-002 - Branch protection / required checks cannot be enforced; main is only advisory-gated

Upgrade to GitHub Pro/Team and apply the ready payload (BRANCH_PROTECTION.md:53-64); until then keep compensating controls and re-review at each plan/cost review.

## SUPPLY-P2-001 - Shipped sensor image auto-applies signed updates without a per-update human gate

Default update_auto_apply to false for stable/production (keep true for lab/canary) or require an explicit operator release action; align DEPENDENCY_POLICY.md with actual behavior.

## SUPPLY-P3-001 - Dependabot watches only GitHub Actions, not hash-pinned dev dependencies

Add a pip ecosystem entry for / to dependabot.yml and document the hash-update procedure.

## SEC-P3-002 - Lab tooling disables SSH host-key and TLS verification

Pin lab host keys via managed known_hosts and verify TLS with the lab CA, mirroring inventory_metrics.py.

## CI-P3-001 - Documentation overstates the dependabot-merge gate specificity

Implement the named-check gate in the workflow or correct the documentation to match implemented behavior.

## SEC-P3-003 - No step-by-step emergency rotation procedure for the CA key / signing seed

Add docs/runbooks/root-key-compromise.md covering CA + signing-seed rotation, fleet re-enrollment and evidence preservation; link it from runbooks/INDEX.md.

## CONF-P3-001 - Lab configs ship permissive defaults (TOFU enrollment; control plane binds all interfaces)

Mark lab configs LAB ONLY, add startup guards (refuse insecure enrollment without an explicit lab flag; warn on 0.0.0.0 bind), and keep the safe defaults in shipped images.

