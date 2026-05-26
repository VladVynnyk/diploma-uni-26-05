#!/bin/sh
set -eu

echo "Starting backend container..."
echo "DB_URI=${DB_URI:-not-set}"

attempt=1
max_attempts=30

until cd /backend/core/database && alembic upgrade head; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Alembic migration failed after ${max_attempts} attempts."
    exit 1
  fi

  echo "Database is not ready yet. Retry ${attempt}/${max_attempts} in 2 seconds..."
  attempt=$((attempt + 1))
  sleep 2
done

echo "Migrations applied successfully."

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "SEED_DEMO_DATA=true. Running demo data seed..."
  cd /backend/core
  python seed.py
else
  echo "SEED_DEMO_DATA is not enabled. Skipping demo data seed."
fi

cd /backend/core
UVICORN_RELOAD_FLAG=""
if [ "${UVICORN_RELOAD:-false}" = "true" ]; then
  UVICORN_RELOAD_FLAG="--reload"
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 ${UVICORN_RELOAD_FLAG} --root-path /api
