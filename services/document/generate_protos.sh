#!/bin/bash

set -e

echo "Generating gRPC code from proto files..."

python -m grpc_tools.protoc \
  -I../protos \
  --python_out=./app/db \
  --grpc_python_out=./app/db \
  ../protos/document_service.proto
sed -i 's/import document_service_pb2 as document__service__pb2/from . import document_service_pb2 as document__service__pb2/' ./app/db/*.py
