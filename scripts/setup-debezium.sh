#!/bin/bash
# Register Debezium connector
echo "Waiting for Debezium Connect to be ready..."
until curl -f http://localhost:8083/; do
  sleep 5
done

echo "Registering PostgreSQL connector..."
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
  http://localhost:8083/connectors/ \
  -d @debezium/register-postgres.json

echo "Debezium connector registered successfully!"