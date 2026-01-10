#!/bin/bash
set -e

# Smoke Test Script for CI/CD Pipeline
# Verifies the service is up and responds to prediction requests.

URL="http://localhost:8000"
MAX_RETRIES=30
SLEEP_TIME=2

echo "Starting Smoke Test..."

# 1. Wait for Service Readiness
echo "Waiting for service at $URL..."
count=0
while ! curl -s "$URL/health" > /dev/null; do
  echo "Service not ready yet. Retrying ($count/$MAX_RETRIES)..."
  sleep $SLEEP_TIME
  count=$((count+1))
  if [ $count -ge $MAX_RETRIES ]; then
    echo "TIMEOUT: Service failed to start."
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
  exit 1
fi

# Cleanup is handled by GitHub Actions (container stop)
exit 0
