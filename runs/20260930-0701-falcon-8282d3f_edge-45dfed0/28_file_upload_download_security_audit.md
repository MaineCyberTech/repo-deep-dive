# File Upload and Download Security Audit — Not Applicable / Future Readiness

## Audit Metadata

- Audit name: repo-deep-dive
- Run: 20260930-0701-falcon-8282d3f_edge-45dfed0
- Repositories: falcon-build @ 8282d3f (main, clean at run start); falcon-edge-build @ 45dfed0 (main, dirty — in-flight CI work)
- Generated at: 2026-09-30
- Auditor: repo-deep-dive wave-1 subagent (N/A set)
- Area code: FILE
- Status: N/A — no application upload/download flows; packages/SBOM integrity is covered by prompts 11/35
- Scope limitations: read-only; no upload or download was performed

## Verification Performed

| Check | Command (read-only) | Observed result |
|---|---|---|
| Upload primitives | `grep -rIln -i -E 'multipart\|presign\|file upload\|upload_file\|Content-Disposition' <code dirs>` | 2 files, both MCT integration docs describing the upstream IRIS API (`mct/integrations/velociraptor/dfir-iris-evidence-workflow.md`, `evidence-to-iris-workflow.md`); no first-party upload code |
| Control-plane file endpoints | `grep -nE '^  /' falcon-edge-build/api/openapi/falcon-edge-v1.yaml`; `grep -n 'application/' …` | 16 paths, JSON only; no download/upload/blob endpoints |
| Update artifact model | `api/schemas/UpdateArtifact.json` | `{url, sha256, sizeBytes}` — the control plane returns metadata; the agent fetches bytes and hash-verifies (delivery under 11/43) |
| UI file surfaces | 0 HTML/CSS/JS/TS files in both repos | No upload components, signed URLs, previews or attachment routes |
| Upstream IRIS storage | `compose/mct/iris-web/docker-compose.yml` | Volumes `iris-downloads`, `user_templates`, `server_data`, `db_data` belong to the upstream DFIR-IRIS app |
| Release artifact integrity | `automation/validation/build_review_package.sh`, `PACKAGE_MANIFEST.sha256`, `sbom/` | Package/SBOM digest + verification flows (prompts 11/35), not user file flows |

## Evidence Reviewed

- `/home/user/falcon-edge-build/api/schemas/UpdateArtifact.json` — URL + SHA-256 + size; no byte-proxying endpoint
- `/home/user/falcon-build/mct/integrations/velociraptor/evidence-to-iris-workflow.md` — documented multipart attach to upstream IRIS (`POST /api/case/<id>/evidence`)
- `/home/user/falcon-build/compose/mct/iris-web/docker-compose.yml` — upstream app's file volumes (`iris-downloads`, `user_templates`)
- `/home/user/falcon-build/docs/runbooks/OPERATOR_START_HERE.md` — operator flows are dashboards/runbooks; no file workflows
- `/home/user/falcon-build/PACKAGE_MANIFEST.sha256` — release package digest manifest (11/35 scope)

## Not Applicable / Future Readiness

**Why N/A.** Neither repository implements file upload, download, preview, attachment or signed-URL functionality. There is no first-party web app (zero web assets), no multipart/file-form handling in code, and the only control-plane artifact reference is `UpdateArtifact` metadata (`url`, `sha256`, `sizeBytes`) rather than a file-serving endpoint. The one multipart flow in the repo is documentation for attaching evidence to the **upstream** DFIR-IRIS API; storage, MIME validation and revocation for that flow are IRIS-owned. Domain score: **0 (not assessable)**.

**What the repo does own.** Release-package bytes: `automation/validation/build_review_package.sh`, `PACKAGE_MANIFEST.sha256`, `PACKAGE_DIGEST.txt` and `sbom/`. Their integrity, pinning and digest verification are audited by prompts 11 (supply chain) and 35 (SBOM/license), and delivery artifacts live in `/home/user/falcon-edge-delivery`.

**Future readiness trigger.** If a first-party file feature ships (evidence upload UI, report export endpoint, client document exchange), this prompt becomes applicable and needs: MIME/extension/size validation, malware scanning hooks, private-by-default storage, short-lived signed URLs, tenant scoping, revocation/retention, and cross-tenant file tests.

**Findings:** none — no applicable first-party surface.
