# Access Control Matrix

- Run: `buddy-20261005-full-master-adcf767`
- Target: `buddy` @ `adcf767` (branch `master`)
- Domain: `24_access_control_matrix_audit` (area ACM)

## Subject

`buddy` is a **guest-only, local-first** PWA. There is no server, account, session, role, or
remote datastore (repo_inventory: routes 0, tables 0, containers 0; README:7-9). The only
principal is a locally generated guest id stored in the IndexedDB save
(`lib/storage/schema.ts` `guestId`; `components/hatch/HatchFlow.tsx:19-22`).

## Matrix

| Resource | Reader | Writer | Authorization decision | Evidence |
|---|---|---|---|---|
| Game save (IndexedDB) | Same-origin app only | Same-origin app only | None (no principals) | `lib/storage/indexeddb.ts` |
| Static assets / HTML | Anyone | Build pipeline | None | `next.config.js` |
| Service worker cache | Same-origin app only | SW runtime | None | `public/sw.js` |
| Exported save file | User | User | None | `lib/storage/indexeddb.ts:82-106` |

## Verdict

**Not applicable** for a role matrix: there are no protected resources and no authorization
decisions. Filing ACM findings would be inventing functionality.

## Future readiness

If accounts/cloud sync are introduced, this matrix must be reopened together with
`ARCH-P1-001` (client-authoritative, deferred) and `37_supabase_rls_policy_deep_dive.md`.
Until then, the local guest id must never be treated as an ownership/auth token.
