#!/bin/bash
set -e

# Start Debezium Connect in the background using the original entrypoint
echo "Starting Debezium Connect..."
/docker-entrypoint.sh start &

# Wait for Debezium Connect to be ready
echo "Waiting for Debezium Connect to be ready..."
until curl -sf http://localhost:8083/ > /dev/null; do
  echo "Debezium not ready yet, waiting..."
  sleep 5
done

echo "Debezium is ready! Registering PostgreSQL connector..."
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
  http://localhost:8083/connectors/ \
  -d @/debezium/register-postgres.json

echo "Debezium connector registered successfully!"

# Keep the container running
wait