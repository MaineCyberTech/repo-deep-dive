# Lenses

Lenses are cross-cutting overlays applied on top of the domain prompts. A domain prompt audits one area of the system; a lens audits the whole system through one viewpoint — and adds what the domain view misses.

## Available lenses

| Lens | File | Area code | Focus |
|---|---|---|---|
| New developer | `new_developer.md` | `ND` | Onboarding: can a competent stranger run and extend this without tribal knowledge? |
| Independent reviewer | `independent_reviewer.md` | `REV` | Claims vs evidence: reproduction, unearned statuses, independence |
| Integration | `integration.md` | `INTG` | Boundaries: interfaces, contracts, skew, failure modes |
| Live operations | `live_operations.md` | `LIVE` | The running system as the operator experiences it, including degraded modes |
| Security adversary | `security_adversary.md` | `ADV` | Trust ladders, privileged consumers of lower-trust input, claim falsification |

## How to apply

- Use the lens targets from `profiles/falcon-lab.md` §5 (or pick targets for a generic run).
- Each lens writes `lens_<id>.md` in the run folder using the shared report structure (see `templates/lens_report_template.md`).
- Lens findings use the lens area code and cross-reference domain finding IDs; they never duplicate domain findings.
- Lenses are read-only and follow the shared rules' verification discipline (claim samples, literal walks, configured-vs-exercised).

## Adding a lens

See `CONTRIBUTING.md` (Add a lens).
