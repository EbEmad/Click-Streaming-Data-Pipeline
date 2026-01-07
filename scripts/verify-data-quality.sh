#!/bin/bash
# Quick verification script for LLM Data Quality Integration

set -e

echo "=== LLM Data Quality Integration Verification ==="
echo ""

# Check if services are running
echo "1. Checking if data-quality service is running..."
if docker ps | grep -q docs-data-quality; then
    echo "   ✓ Data quality service is running"
else
    echo "   ✗ Data quality service is NOT running"
    echo "   Run: docker-compose up -d data-quality-service"
    exit 1
fi

# Check Kafka topics
echo ""
echo "2. Checking Kafka topics..."
docker exec docs-kafka kafka-topics --bootstrap-server localhost:9092 --list | grep -E "(cdc.documents|quality.checks)" || echo "   Topics not created yet (will be created on first message)"

# Create a test document
echo ""
echo "3. Creating test document..."
DOC_ID=$(curl -s -X POST http://localhost:8005/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Quality Check Document",
    "content": "This is a comprehensive test document with sufficient content to pass quality checks. It contains proper structure and clear language.",
    "created_by": "verification@test.com"
  }' | jq -r '.id')

if [ -z "$DOC_ID" ] || [ "$DOC_ID" = "null" ]; then
    echo "   ✗ Failed to create document"
    exit 1
fi

echo "   ✓ Document created: $DOC_ID"

# Wait for processing
echo ""
echo "4. Waiting 10 seconds for LLM validation and indexing..."
sleep 10

# Check if document appears in search with quality score
echo ""
echo "5. Searching for document with quality metadata..."
RESULT=$(curl -s "http://localhost:8003/search?q=quality+check" | jq -r '.documents[0]')

if [ -z "$RESULT" ] || [ "$RESULT" = "null" ]; then
    echo "   ✗ Document not found in search results"
    echo "   Check logs: docker logs docs-data-quality"
    exit 1
fi

QUALITY_SCORE=$(echo "$RESULT" | jq -r '.quality_score')
HAS_PII=$(echo "$RESULT" | jq -r '.has_pii')

echo "   ✓ Document found in search"
echo "   Quality Score: $QUALITY_SCORE"
echo "   Has PII: $HAS_PII"

if [ "$QUALITY_SCORE" != "null" ]; then
    echo "   ✓ Quality metadata is present!"
else
    echo "   ✗ Quality metadata is missing"
    exit 1
fi

# Test quality filtering
echo ""
echo "6. Testing quality score filtering..."
HIGH_QUALITY=$(curl -s "http://localhost:8003/search?q=test&min_quality_score=80" | jq -r '.total')
echo "   Documents with quality >= 80: $HIGH_QUALITY"

echo ""
echo "=== Verification Complete ==="
echo "✓ All checks passed!"
echo ""
echo "Next steps:"
echo "  - View quality-checked events: docker exec -it docs-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic quality.checks --from-beginning"
echo "  - Check service logs: docker logs docs-data-quality -f"
echo "  - View Elasticsearch data: curl 'http://localhost:9200/documents/_search?pretty'"
