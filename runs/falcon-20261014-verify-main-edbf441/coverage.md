# Coverage — verification pass

Re-checked the 126 findings of `falcon-20261011-0416-full-f5cb7c9` at `edbf441`, grouped into
eight themed verification reports (see `90..97_verification_*.md`), plus the machine
deterministic pass (`lens_deterministic.md`).

| Theme | Report | Findings |
|---|---|---:|
| ARCH / FEAT / CTR / INFRA / RES | `90_verification_arch-feat-ctr-infra-res.md` | 17 |
| CI / BP / SC / SBOM / DET | `91_verification_ci-bp-sc-sbom-det.md` | 18 |
| DATA / SEARCH / API / WH / DR | `92_verification_data-search-api-wh-dr.md` | 16 |
| HYGIENE / INV / AI / DOC | `93_verification_hygiene-inv-ai-doc.md` | 15 |
| ORCH / CHAIN / TEST | `94_verification_orch-chain-test.md` | 10 |
| PERF / OBS / NOTIF | `95_verification_perf-obs-notif.md` | 16 |
| PRIV / IR / REL / EVOL | `96_verification_priv-ir-rel-evol.md` | 18 |
| SEC / ACM / ADMIN / SECRET | `97_verification_sec-acm-admin-secret.md` | 16 |
| deterministic (machine) | `lens_deterministic.md` | 4 (1 new) |

Method: repo inspection at `edbf441` + read-only live checks (docker/systemctl/journalctl,
Prometheus/Grafana read APIs, textfile metrics). No mutations; secrets never reproduced.
