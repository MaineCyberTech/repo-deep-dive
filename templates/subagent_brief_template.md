# Subagent Brief Template (Waves 1–2)

Copy, fill, and paste one brief per parallel subagent. Every brief carries
the same fields so fan-out reports come back comparable and checkable.

## Assignment

- Prompt file:
- Profile boundaries (file + section):
- Repo(s) in scope (path, branch, HEAD SHA, dirty state):
- Lens overlay (if any):
- Output path (`docs/audits/{name}/{run}/` + filename):
- Area code (finding IDs `AREA-Px-NNN`):

## Rules reminded

- Evidence discipline: every significant claim cites path / symbol / route / config / test; else `Unknown`.
- Verification discipline: sample and reproduce headline claims; record `supported` / `partially supported` / `unsupported` / `not reproducible`.
- Finding format: the shared format exactly (severity, confidence, evidence, fix, validation, owner, effort, dependencies, status, plus endpoint/data-path and attack-path where reachable).
- Audit-only: write only under the run folder; no application code, no live-system changes; secrets referenced by path + type only.

## Cross-references

- Domain IDs this brief must cross-reference (not duplicate):
- Lens targets (if lens brief): prompts to read first:

## Done means

- [ ] Report written at the output path with all required sections incl. `Verification Performed`
- [ ] Every finding has an `AREA-Px-NNN` ID under this brief's area code
- [ ] Open questions list what evidence is missing and where to get it
