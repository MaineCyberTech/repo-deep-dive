# Source Reports

The six original audits converted into this run folder. They are kept **byte-identical** to the originals in `/home/user/audits/2026-09-30/` (copied with preserved timestamps); the conversion added stable finding IDs (`AREA-Px-NNN`) and the run-level finals, but did not edit these narratives.

| File | Audit | Lens | Findings | sha256 |
|---|---|---|---|---|
| `01-falcon-build-new-developer.md` | falcon-build new developer | `ND` | 22 (F-01…F-22) | `795db75285caa6e2e336ab09d5f7567e13e272b78bd5d5805b7aaba2df0e02ea` |
| `02-falcon-build-reviewer.md` | falcon-build independent reviewer | `REV` | 9 (HIGH-1…LOW-3) | `47c7436143e70b437cead696ae14aaae7757ca9076c1de315dda1faab86dbd31` |
| `03-falcon-edge-new-developer.md` | falcon-edge new developer | `ND` | 12 (F-01…F-12) | `7299d2241f504cb155da4e7bd86b63d5f5b3aaff94d591b97083c4deb842996f` |
| `04-falcon-edge-reviewer.md` | falcon-edge independent reviewer | `REV` | 16 (F-01…F-16) | `fb7b32359508950a0c4fdd7ea63993b15e9e37932bddfa5e0986fe5300255bee` |
| `05-integration-two-repos.md` | cross-repo integration | `INTG` | 15 (C1…L4) | `9fffd846de174ef3e60dfb8621cb2753ea7246cd1622bcde8712c6f1aa533ad9` |
| `06-live-operations.md` | live operations | `LIVE` | 16 (derived) | `7945ef297b8b641490e26894d3cd8d5f4a07fa8adc66f6342e8dbcc9464b7512` |

Notes:

- ID mapping: each source finding's new ID is recorded in the corresponding lens report (`lens_*.md`); report 06 had no finding IDs in the source, so IDs were derived from its sections and prioritized recommendations.
- Severity mapping: `High→P1`, `Medium→P2`, `Low/Info→P3`; report 05 `Critical→P0`; report 06 source priorities `P0/P1/P2→P0/P1/P2`.
- If these files are ever edited (they should not be), the sha256 values above no longer apply.
