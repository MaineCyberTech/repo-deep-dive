# Changelog Draft — buddy `0.1.0` RC (audit delta)

> Audit-generated draft. The repo's `CHANGELOG.md` is the source of truth for shipped changes;
> this draft lists audit-relevant conditions for the release under review.

## Added / verified since `99abf29`

- Save versioning + runtime validation (`lib/storage/schema.ts`), validated on load/import.
- CI workflow (`ci.yml`) with pinned Actions, least-privilege permissions, gitleaks, and an
  intended dependency-review gate.
- Tag-driven release (`release.yml`) with SBOM, changelog, provenance attestation, and an
  intended `release` environment gate.
- Proprietary `LICENSE`/`NOTICE`, dependabot config, `.gitattributes` LF policy.
- Test suite grown to 19 files / 185 tests; component/persistence tests present.

## Conditions carried into this RC (see `RELEASE_GATE.md`)

- `ARCH-P1-001` client-authoritative (deferred, guest-only).
- `BP-P1-001` master unprotected; `BP-P1-002` `release` environment absent.
- `CI-P1-001` CI security job red at HEAD (nested postcss, accepted RA-001).
- `SC-P2-002` secret scanning / Dependabot security updates disabled.
- `DATA-P2-001` inventory item actions not persisted; `FILE-P2-001` export fails on Unicode.
- `UX-P2-001` pinch-zoom disabled (WCAG 1.4.4).

## Not claimed

No progress/feature claim is made here; the machine register (`findings.json`) is authoritative.
