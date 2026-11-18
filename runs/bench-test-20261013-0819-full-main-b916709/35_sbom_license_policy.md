# 35_sbom_license_policy — Prompt 35 - SBOM and License Policy Audit

- Run: `bench-test-20261013-0819-full-main-b916709`
- Target: `bench-test` @ `b916709` (branch `main`)
- Domain: `35_sbom_license_policy.md` (area SBOM, prompt)

## Verification Performed

# 35_sbom_license_policy - 35_sbom_license_policy.md

Domain subagent `35_sbom_license_policy` (area SBOM), read-only audit of `C:\temp\bench-test`.

## Checks / Evidence

- **P1 - No SBOM is produced for either shipped artifact set (PyInstaller app bundles and the live ISO)** (confidence: High)
  - `.github/workflows/build-app.yml:64-90 - builds dist/{bench-gui,bench-tui,bench-agent}, zips them and uploads only bench-app-<label>.zip; no SBOM step and no checksum is attached`
  - `.github/workflows/build-iso.yml:97-124 - collects only the ISO parts, SHA256SUMS and bench-version.txt; no CycloneDX/SPDX document is generated for the Arch package set or the pip wheels baked into the image`
  - `packaging/build_app.py:163-179 - the bundle ships tools/lhm (LibreHardwareMonitorLib.dll + ~35 transitive .NET DLLs) and the whole bench/ toolkit, so the shipped app contains third-party components not enumerated anywhere`
  - `live/packages.x86_64 - 43 package names (python-numpy, python-cryptography, ffmpeg, fio, vulkan-* ...) with no versions; the ISO's component set is whatever the mirror served at build time`
  - `grep over the tracked tree for sbom|cyclonedx|spdx|syft|grype|trivy|anchore returns 0 matches (only docs/FUTURE_WORK.md:45 mentions 'attestation' as future TPM work)`
  - Impact: Consumers of the public app bundles and ISO downloads have no machine-readable inventory of the third-party components (and their versions/licenses/known CVEs) they are executing. There is no way to answer 'what is in release X?' or to match a new CVE to shipped releases without manual reverse-engineering.
  - Recommendation: Add an SBOM step to both build workflows (e.g. syft/CycloneDX) over the built artifacts (pip freeze of the runner venv, the bundle contents, and the pacman package list) and attach the SBOM (plus its sha256) to the same release as the artifact; keep it alongside SHA256SUMS so SBOM and binary bind to the same build.
- **P1 - Third-party binary LibreHardwareMonitor is redistributed in release bundles with no tracked license/attribution (MPL-2.0 compliance gap)** (confidence: High)
  - `AGENTS.md:147 - 'The DLL is vendored under tools/lhm and shipped in the app bundle'`
  - `docs/DATA.md:16 - 'The DLL is vendored under tools/lhm and shipped in the app bundle, with a mirror + retries if a download is needed'`
  - `packaging/build_app.py:163-164,178-179 - if tools/lhm exists it is added to every bundle via --add-data, so the DLL and its dependencies ship in public app-<n> releases`
  - `.gitignore:22-23 - 'downloaded tools (LibreHardwareMonitor etc.)' then 'tools/' - so tools/lhm is untracked (git ls-files tools = 0 files) and never reviewed in the SBOM/CI`
  - `tools/lhm/ (working tree) contains LibreHardwareMonitorLib.dll plus ~35 bundled .NET assemblies (Aga.Controls.dll, OxyPlot.dll, HidSharp.dll, DiskInfoToolkit.dll, RAMSPDToolkit-NDD.dll, System.*.dll, ...); a recursive search for LICENSE/COPYING/NOTICE under tools/lhm returns nothing`
  - `LICENSE:1-3 - the repository is 'PROPRIETARY AND CONFIDENTIAL' while the repo remote is https://github.com/MaineCyberTech/bench-test.git and (per prior audit docs/audits/.../findings.json GOV-P3-001) is public`
  - Impact: A public release redistributes a third-party library under its own license (LibreHardwareMonitor is MPL-2.0) and its transitive dependencies (OxyPlot MIT, HidSharp Apache-2.0, etc.) without shipping their license texts/notices or listing them in an inventory. This is a license-compliance exposure and makes the shipped component set unauditable; proprietary LICENSE terms also create ambiguity about redistribution rights of the bundled components.
  - Recommendation: Track the vendored LHM tree (or pin+hash the exact upstream release), record each component's name/version/license in a third-party NOTICE/attribution file shipped in the bundle, and add a CI check that fails if a bundled binary has no corresponding license entry. Reconcile the proprietary LICENSE with the OSS components actually distributed.
- **P2 - No package manifest or lockfile anywhere; dependencies are installed unpinned at runtime, so no reproducible dependency set exists to inventory** (confidence: High)
  - `Tracked tree has no requirements.txt, pyproject.toml, setup.py/cfg, Pipfile, poetry.lock, package.json or package-lock.json (git ls-files search returns none)`
  - `bench/bootstrap.py:38 - BASE_PACKAGES = ["numpy", "psutil", "cryptography"]; :42 - "dml": ["onnxruntime-directml", "onnx"]; :278 - pip install --upgrade <pkgs> (no version pins, no --require-hashes)`
  - `live/ci-build.sh:48-50 and :77-79 - pip install torch numpy psutil cryptography --index-url https://download.pytorch.org/whl/cu126 --extra-index-url https://pypi.org/simple (unpinned, extra index)`
  - `.github/workflows/build-app.yml:49,54 - pip install --upgrade pip pyinstaller / pip install windows-curses (unpinned build deps)`
  - `README.md:84-85 and bench-gui.cmd:14,16 / bench-tui.cmd:14,16 - pip install numpy psutil cryptography / torch with no versions`
  - `live/packages.x86_64 - Arch package names only, no versions (see ISO finding)`
  - Impact: Two builds of the same commit can resolve different dependency versions; there is no single artifact that an SBOM generator or a reviewer can read to learn what the project depends on. Vulnerability triage and license review have no authoritative source, and 'it worked yesterday' cannot be reproduced.
  - Recommendation: Commit a pinned, hash-pinned dependency set (constraints.txt / requirements.lock with --require-hashes) for the runtime and build deps; have bootstrap.py and ci-build.sh install from it (--require-hashes); pin the Arch package set (or record resolved versions) so the ISO is reproducible. This lockfile then becomes the SBOM source of truth.
- **P2 - GitHub Actions dependencies are mutable major tags and there is no Dependabot, dependency-review or vulnerability scanning** (confidence: High)
  - `.github/workflows/build-app.yml:39,41,87,96,100,104 - actions/checkout@v4, actions/setup-python@v5, actions/upload-artifact@v4, actions/download-artifact@v4, softprops/action-gh-release@v2 (all mutable tags, none SHA-pinned)`
  - `.github/workflows/build-iso.yml:56,116 - actions/checkout@v4, softprops/action-gh-release@v2`
  - `.github/workflows/release.yml:36 - actions/checkout@v4 with contents:write`
  - `.github contains only build-app.yml, build-iso.yml, release.yml - no dependabot.yml, no dependency-review workflow, no CodeQL/secret scan`
  - `docs/audits/repo-deep-dive/20261007-1731-main-4ecee97/findings.json CI-P3-001 - prior audit already flagged 'no CI, dependency automation, or secret scanning'; Dependabot still absent at this commit`
  - Impact: A compromised or retagged upstream action (a real supply-chain attack vector) runs inside workflows that hold contents:write and bake repo secrets, with no pinning or review gate. Stale/vulnerable actions and dependencies are never surfaced, and no PR gate blocks a vulnerable or disallowed-license dependency from being added.
  - Recommendation: Pin every action to a full commit SHA (with a comment naming the version); add .github/dependabot.yml for github-actions + pip, and enable GitHub dependency-review on PRs (or an equivalent license/vuln gate) so a PR adding a dependency fails on a disallowed license or a known CVE.
- **P2 - No release provenance: no build attestation/signing, and app/ISO release tags are run-number based rather than commit-bound** (confidence: High)
  - `.github/workflows/build-iso.yml:102 - sha256sum of the ISO is generated (integrity only), then attached at :116-124; no signature, no SLSA/provenance attestation, no sigstore/cosign`
  - `.github/workflows/build-iso.yml:128 - the workflow's own note: 'the tag's run number does not map to a commit, so check this before flashing' (tag iso-<gpu>-<run_number>)`
  - `.github/workflows/build-app.yml:104-108 - release tag_name: app-${{ github.run_number }} with make_latest:false; only *.zip attached, no checksums and no attestation`
  - `.github/workflows/release.yml:104-105 - git tag -a ... ; git push origin "$tag" (annotated tag, not signed; no artifact attestation step)`
  - `grep for provenance|attestation|cosign|sigstore over the tracked tree returns 0 implementation matches (only docs/FUTURE_WORK.md:45 future-work line)`
  - Impact: A downloaded ISO or app bundle cannot be cryptographically tied to the commit that produced it: the SHA256SUMS file is itself an unsigned asset from the same release, and app releases carry no checksum at all. Consumers cannot verify that a release was built by this repo's CI from a specific commit (no verifiable build provenance / SLSA level).
  - Recommendation: Emit a provenance attestation (actions/attest-build-provenance or slsa-github-generator) for the ISO and the app zips, sign release assets (sigstore/cosign), and publish checksums for the app bundle too. Tag app/ISO releases with the commit (or include and sign the commit SHA) instead of relying on run_number.
- **P2 - No license policy, allow/deny list, CI license gate or exception process** (confidence: High)
  - `LICENSE:1-16 - project LICENSE is proprietary ('All rights reserved', 'PROPRIETARY AND CONFIDENTIAL'); README.md:365-367 '## License - Proprietary - see LICENSE'`
  - `No license-policy/allowlist file, no tool config (no .github/dependabot.yml, no .licensee.yml, no reuse/FOSSA/pip-licenses config) anywhere in the tracked tree`
  - `No test or CI step inspects dependency licenses (search of tests/*.py for license|sbom|depend returns 0 matches)`
  - `Dependencies pulled in include copyleft/notice-bearing components: tools/lhm (LibreHardwareMonitor, MPL-2.0) and its transitive .NET assemblies; .venv shows torch (BSD-3 + NOTICE), numpy (BSD + many bundled licenses), pyinstaller (GPL-with-exception)`
  - Impact: There is no defined rule for which licenses are acceptable in a shipped artifact, no automated gate that would catch a disallowed license entering the build, and no documented exception/approval path. For a product shipped as a public download this leaves license risk entirely to chance.
  - Recommendation: Add a docs/license-policy.md with an explicit allow/deny list (and a documented exception process with owner + expiry), and enforce it in CI with a license scanner (e.g. pip-licenses / licensecheck / a dependency-review license gate) that fails on a deny-list license or an allow-listed-but-unnoticed change.
- **P3 - Live ISO package set is version-unpinned, so the shipped image is neither reproducible nor fully inventoried** (confidence: Medium)
  - `live/packages.x86_64 - 43 entries listed by name only (python, python-numpy, python-psutil, python-cryptography, tk, ffmpeg, lm_sensors, fio, iperf3, stress-ng, vulkan-tools, mesa-utils, ...), no versions`
  - `live/packages-amd.x86_64 (6), live/packages-hybrid.x86_64 (16), live/packages-nvidia.x86_64 (4), live/packages-nvidia-legacy.x86_64 (8) - same name-only style`
  - `live/Build-LiveUSB.sh + live/ci-build.sh - build pulls from the rolling Arch mirrors at build time; no record of resolved package versions is emitted with the release`
  - Impact: Each ISO build silently incorporates whatever package versions the mirror held, so an ISO from tag/run N cannot be reproduced and its exact third-party set (and CVEs) is unknown after the fact. Only the ISO's hash is recorded, not its contents.
  - Recommendation: Emit the resolved package list with versions (pacman -Q / -Qe) into the release assets alongside the SBOM, and pin to a dated snapshot/archive mirror (or commit a lock) so an ISO build is reproducible.

## Verification Performed

Read-only source review of the target at commit `b916709`; the evidence above was
recorded by the domain subagent and normalized by `tools/full_domain.py` (mechanical
report body derived from that recorded findings JSON).

## Findings

| ID | Severity | Title |
|---|---|---|
| SBOM-P1-001 | P1 | No SBOM is produced for either shipped artifact set (PyInstaller app bundles and the live ISO) |
| SBOM-P1-002 | P1 | Third-party binary LibreHardwareMonitor is redistributed in release bundles with no tracked license/attribution (MPL-2.0 compliance gap) |
| SBOM-P2-001 | P2 | No package manifest or lockfile anywhere; dependencies are installed unpinned at runtime, so no reproducible dependency set exists to inventory |
| SBOM-P2-002 | P2 | GitHub Actions dependencies are mutable major tags and there is no Dependabot, dependency-review or vulnerability scanning |
| SBOM-P2-003 | P2 | No release provenance: no build attestation/signing, and app/ISO release tags are run-number based rather than commit-bound |
| SBOM-P2-004 | P2 | No license policy, allow/deny list, CI license gate or exception process |
| SBOM-P3-001 | P3 | Live ISO package set is version-unpinned, so the shipped image is neither reproducible nor fully inventoried |
