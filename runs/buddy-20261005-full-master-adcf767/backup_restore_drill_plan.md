# Backup / Restore Drill Plan

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Related findings: `DR-P2-001`, `FILE-P2-001`, `RES-P3-002`

## Current state

All state lives in the browser's IndexedDB under one key per origin
(`lib/storage/indexeddb.ts:5-30`). The only recovery path is manual export/import
(`exportSave`/`importSave`, `lib/storage/indexeddb.ts:82-106`). No drill has been recorded,
and the export path itself can throw on non-Latin-1 content (`FILE-P2-001`).

## Drill (recommended, per release)

1. Hatch a buddy; record species, level, coins, and inventory.
2. Exercise a representative save including a Unicode nickname (emoji or accented text).
3. `exportSave()` and persist the blob to an external file.
4. Clear site data (or use a fresh profile) so IndexedDB is empty.
5. `importSave()` the blob and assert the restored save deep-equals the captured state.
6. Repeat with a tampered payload (missing `version`, oversized body) and assert a safe rejection.
7. Record the artifact (commit SHA, browser/OS, pass/fail) next to the release.

## Pass criteria

- Representative save round-trips with no data loss.
- Unicode content does not break export.
- Malformed imports are rejected and do not overwrite an existing save.

## Exit criteria for DR-P2-001

A recorded drill at a release commit. Fix `FILE-P2-001` first or the Unicode step fails.
