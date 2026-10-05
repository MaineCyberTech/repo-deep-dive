# Verification log

Run: `20261004-full-main-ba4becb` · Target: `falcon-edge` @ `ba4becb` · Profile: base

Re-verification at a **newer** commit (`a549337`, `main`). The run is bound to `ba4becb`; the
original finding reports are not rewritten. Statuses below are the reconciled post-run verdicts.

| When | Patch set | State | Finding status | Evidence | Note |
|---|---|---|---|---|---|
| 2026-10-05T05:40:00Z | PS-AUTH-001 | merged | verified-fixed | falcon-edge#46 @ a549337 | AUTH-P2-001 (device mTLS key group-readable). Re-verified at `a549337`: key is written `0600` on first enrollment and on rotation, certificate stays `0640` (`src/falcon_agent/identity.py`); Vector no longer reads the sensor key path — it receives a `0400` runtime copy via systemd `LoadCredential` (`profiles/sensor/vector/vector.service.d/60-falcon.conf`). `ci/validate.sh` → `validation: ALL PASS`; full suite 347 tests, the only failure is a `/mnt/c` DrvFs chmod artifact that passes on a native ext4 checkout. At the run commit `ba4becb` this was genuinely still-open; PR #46 merged after the run. Residual: a dedicated Vector client certificate (owner-gated). |
| 2026-10-05T05:40:00Z | PS-AUTH-001 | merged | verified-fixed | falcon-edge#46 @ a549337 | EXEC-P1-001 / FINAL-P1-001 / SEC-P1-001 remain verified-fixed history (re-audit 2026-10-04): re-enrollment cannot resurrect a `REVOKED`/`RETIRED` identity (`src/falcon_control/service.py`, `renewal`/`ingest_vector` routes return `SENSOR_REVOKED`/`SENSOR_RETIRED`). Confirmed unchanged at `a549337`. |
