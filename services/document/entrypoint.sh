#!/bin/bash
set -e

# Sync generated proto files from the build backup to the mounted volume
# This ensures that even if a volume hides the build directory, we restore the generated files.
if [ -d "/app/proto_backup" ]; then
    echo "Syncing generated protos from backup to mounted volume..."
    # Only copy the generated proto python files to avoid overwriting other source files
    cp /app/proto_backup/*_pb2*.py /app/db/ 2>/dev/null || true
fi

# Execute the passed command (e.g., uvicorn)
exec "$@"
