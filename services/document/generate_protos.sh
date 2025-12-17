#!/bin/bash

set -e

echo "Generating gRPC code from proto files..."

python -m grpc_tools.protoc \
  -I./protos \
  --python_out=./db \
  --grpc_python_out=./db \
  ./protos/document_service.proto
sed -i 's/import document_service_pb2 as document__service__pb2/from . import document_service_pb2 as document__service__pb2/' ./db/*.py
