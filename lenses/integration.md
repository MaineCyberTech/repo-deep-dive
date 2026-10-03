# Lens — Integration

## Purpose

Evaluate the falcon ↔ falcon-edge pair and the shared host as an **integrated system**: every boundary, contract, coupling, and failure mode at the seams. Domain audits see one repo at a time; this lens sees the joint.

This lens is an overlay; cross-reference domain IDs instead of re-filing domain findings.

## Area code

Findings from this lens use `INTG`:

- `INTG-P0-001`
- `INTG-P1-001`
- `INTG-P2-001`
- `INTG-P3-001`

## When to apply

Targets per the falcon-lab profile: `02`, `08`, `12`, `13`, `14`, `30`, `32`, `42` (and the live stack where read-only).

## Question set

1. Enumerate **every interface** between the two repos and the shared host: files, pins, ports, protocols, sockets, users, directories, containers, networks, tunnels, credentials, data formats.
2. For each interface: where is the contract defined and versioned? Is there a single owner for the shared resource?
3. What breaks when one side changes without the other? Enumerate skew scenarios (edge newer/older than pin; central config changed without edge; protocol drift).
4. Does the pin/pairing record match reality — digest, versions, claimed capabilities?
5. Are cross-repo docs consistent with each other (claims, ports, paths, procedures)? Where do they disagree?
6. Which shared resources create hidden coupling (host ports, service users, `/srv` paths, Docker networks, WG peers, certificates)?
7. What happens at boundary failures: edge offline, central offline, tunnel down, clock skew, certificate expiry, DNS failure?
8. Is the additive rule enforced in practice — edge changes cannot weaken central; central changes cannot silently break edge?
9. How is a paired upgrade performed, and can it be rolled back atomically? What is the order of operations?
10. Where do cross-repo findings and decisions get recorded, and do both sides see them?
11. Does the delivery pipeline (build → manifest → pin → deploy) preserve traceability end-to-end?
12. Which integration assumptions are only true "today" (addresses, paths, versions) and would break on the next change?

## Evidence expectations

- Build an **interface inventory table**: interface · where defined · owner · contract · failure mode.
- Cite both sides of every cross-repo claim (e.g., the pin file in falcon *and* the release record in edge).
- For skew scenarios, describe the concrete failure (what stops working, what corrupts, what is silent) with evidence from code/config.

## Output shape

Write `lens_integration.md` in the run folder using the shared report structure, with:

- The interface inventory table.
- Findings in the shared finding format with area `INTG`.
- A cross-reference table: `INTG-ID ↔ related domain ID`.

## Traps to avoid

- Do not audit one side and assume the other.
- Do not treat a documented procedure as a tested procedure.
- Do not re-file domain findings; cross-reference them.
