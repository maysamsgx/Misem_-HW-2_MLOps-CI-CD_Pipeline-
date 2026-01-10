#!/bin/bash
set -e

# MLOps Smoke Test Script
# Verifies service health and prediction capability.

URL="http://127.0.0.1:8000"
MAX_RETRIES=60
SLEEP_TIME=2

echo "Starting Smoke Test against $URL..."

# 1. Wait for Service Readiness (with Fail-Fast)
count=0
while ! curl -s "$URL/health" > /dev/null; do
  # Fail Fast: Check if container crashed
  if ! docker ps | grep -q "mlops-service"; then
    echo "CRITICAL FAILURE: Container crashed unexpectedly."
    echo "=== CONTAINER LOGS START ==="
    docker logs mlops-service
    echo "=== CONTAINER LOGS END ==="
    exit 1
  fi

  echo "Service not ready yet. Retrying ($count/$MAX_RETRIES)..."
  sleep $SLEEP_TIME
  count=$((count+1))
  
  if [ $count -ge $MAX_RETRIES ]; then
    echo "TIMEOUT: Service failed to start within $((MAX_RETRIES * SLEEP_TIME)) seconds."
    echo "=== CONTAINER LOGS START ==="
    docker logs mlops-service
    echo "=== CONTAINER LOGS END ==="
    exit 1
  fi
done

echo "Service is UP!"

# 2. Test Prediction Endpoint
echo "Sending prediction request..."
RESPONSE=$(curl -s -X POST "$URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "smoke_test_123",
    "skills": "Python, SQL, Machine Learning",
    "qualification": "Master",
    "experience_level": "Senior"
  }')

echo "Response: $RESPONSE"

# 3. Verify Response Content
if [[ $RESPONSE == *"top_match"* ]] && [[ $RESPONSE == *"confidence"* ]]; then
  echo "SUCCESS: Prediction verification passed!"
else
  echo "FAILURE: Response invalid."
  echo "=== CONTAINER LOGS START ==="
  docker logs mlops-service
  echo "=== CONTAINER LOGS END ==="
  exit 1
fi

exit 0
