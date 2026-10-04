#!/usr/bin/env bash
# PATCH-008 guard verification: prove the app.seed_demo gate defaults to SKIP
# and runs only when explicitly enabled, using a throwaway Postgres container.
set -u
IMG="ghcr.io/supabase/postgres:17.11.0.002"
NAME="patch008-guarddb"
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --rm --name "$NAME" -e POSTGRES_PASSWORD=postgres "$IMG" >/dev/null
# wait for readiness
for i in $(seq 1 30); do
  if docker exec "$NAME" pg_isready -U postgres >/dev/null 2>&1; then break; fi
  sleep 1
done
if ! docker exec "$NAME" pg_isready -U postgres >/dev/null 2>&1; then
  echo "GUARD_DB_ERROR: postgres did not become ready"
  docker logs "$NAME" 2>&1 | tail -20
  docker rm -f "$NAME" >/dev/null 2>&1
  exit 2
fi
echo "server: $(docker exec "$NAME" psql -U postgres -Atc 'select version();' | cut -d, -f1)"
echo "default (unset flag) skip? -> $(docker exec "$NAME" psql -U postgres -Atc "select coalesce(current_setting('app.seed_demo', true), '') <> 'true';")"
echo "explicit 'true' skip?     -> $(docker exec "$NAME" psql -U postgres -Atc "set app.seed_demo='true'; select coalesce(current_setting('app.seed_demo', true), '') <> 'true';" | tail -1)"
echo "explicit 'false' skip?    -> $(docker exec "$NAME" psql -U postgres -Atc "set app.seed_demo='false'; select coalesce(current_setting('app.seed_demo', true), '') <> 'true';" | tail -1)"
docker rm -f "$NAME" >/dev/null 2>&1
echo "GUARD_DB_OK"
