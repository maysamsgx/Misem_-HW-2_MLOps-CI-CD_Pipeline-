#!/bin/bash
# tests/smoke_test.sh
# Professional smoke test with comprehensive diagnostics

set -e  # Exit on error

# =============================================================================
# CONFIGURATION
# =============================================================================
SERVICE_URL="${SERVICE_URL:-http://127.0.0.1:8000}"
CONTAINER_NAME="${CONTAINER_NAME:-mlops-service}"
MAX_RETRIES=30
RETRY_DELAY=2

echo "=========================================="
echo "MLOps Smoke Test - Deployment Verification"
echo "=========================================="
echo "Service URL: $SERVICE_URL"
echo "Container: $CONTAINER_NAME"
echo "Max Retries: $MAX_RETRIES"
echo ""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

check_container_running() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

show_container_logs() {
    echo ""
    echo "=== CONTAINER LOGS (Last 50 lines) ==="
    docker logs --tail 50 "$CONTAINER_NAME" 2>&1 || echo "Could not retrieve logs"
    echo "=== END CONTAINER LOGS ==="
    echo ""
}

check_container_health() {
    local health_status
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
    echo "Container health status: $health_status"
    return 0
}

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

echo "Step 1: Pre-flight Checks"
echo "-------------------------------------------"

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ CRITICAL: Container '$CONTAINER_NAME' does not exist!"
    echo "Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    exit 1
fi

# Check if container is running
if ! check_container_running; then
    echo "❌ CRITICAL: Container '$CONTAINER_NAME' is not running!"
    echo "Container status:"
    docker ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    show_container_logs
    exit 1
fi

echo "✅ Container is running"

# Show container details
echo ""
echo "Container Details:"
docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check port mapping
echo "Checking port mapping..."
PORT_MAPPING=$(docker port "$CONTAINER_NAME" 2>/dev/null || echo "No port mapping found")
echo "Port mapping: $PORT_MAPPING"
echo ""

# =============================================================================
# WAIT FOR SERVICE READINESS
# =============================================================================

echo "Step 2: Waiting for Service Readiness"
echo "-------------------------------------------"

attempt=0
service_ready=false

while [ $attempt -lt $MAX_RETRIES ]; do
    attempt=$((attempt + 1))
    
    # Check container still running
    if ! check_container_running; then
        echo "❌ CRITICAL: Container stopped running!"
        show_container_logs
        exit 1
    fi
    
    # Try health check endpoint
    echo -n "Attempt $attempt/$MAX_RETRIES: Checking $SERVICE_URL/health... "
    
    if response=$(curl -s -f -m 5 "$SERVICE_URL/health" 2>&1); then
        echo "✅ SUCCESS"
        echo "Health response: $response"
        service_ready=true
        break
    else
        echo "❌ Connection failed"
        
        # Show more detailed error on first few attempts
        if [ $attempt -le 3 ]; then
            echo "   Curl error: $response"
        fi
        
        # Every 5 attempts, show container logs
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "   Checking container logs (attempt $attempt)..."
            docker logs --tail 10 "$CONTAINER_NAME" 2>&1 | sed 's/^/   /'
        fi
        
        sleep $RETRY_DELAY
    fi
done

if [ "$service_ready" = false ]; then
    echo ""
    echo "❌ TIMEOUT: Service did not respond after $MAX_RETRIES attempts"
    echo "Total wait time: $((MAX_RETRIES * RETRY_DELAY)) seconds"
    echo ""
    show_container_logs
    
    # Additional diagnostics
    echo "=== NETWORK DIAGNOSTICS ==="
    echo "Testing localhost connectivity:"
    curl -v http://localhost:8000/health 2>&1 | head -20 || true
    echo ""
    echo "Testing 127.0.0.1 connectivity:"
    curl -v http://127.0.0.1:8000/health 2>&1 | head -20 || true
    echo ""
    echo "Container processes:"
    docker top "$CONTAINER_NAME" || true
    echo "=== END DIAGNOSTICS ==="
    
    exit 1
fi

# =============================================================================
# TEST HEALTH ENDPOINT
# =============================================================================

echo ""
echo "Step 3: Testing Health Endpoint"
echo "-------------------------------------------"

health_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$SERVICE_URL/health")
health_body=$(echo "$health_response" | sed -n '1,/^HTTP_CODE:/p' | sed '$d')
health_code=$(echo "$health_response" | grep "HTTP_CODE:" | cut -d':' -f2)

echo "HTTP Status: $health_code"
echo "Response Body: $health_body"

if [ "$health_code" != "200" ]; then
    echo "❌ FAILED: Health check returned status $health_code (expected 200)"
    show_container_logs
    exit 1
fi

if ! echo "$health_body" | grep -q "status"; then
    echo "⚠️  WARNING: Health response doesn't contain 'status' field"
fi

echo "✅ Health check passed"

# =============================================================================
# TEST PREDICTION ENDPOINT
# =============================================================================

echo ""
echo "Step 4: Testing Prediction Endpoint"
echo "-------------------------------------------"

prediction_payload='{
    "candidate_id": "smoke_test_candidate_001",
    "skills": "Python, SQL, Machine Learning, Docker",
    "qualification": "Master",
    "experience_level": "Senior"
}'

echo "Sending prediction request..."
echo "Payload: $prediction_payload"
echo ""

prediction_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST \
    "$SERVICE_URL/predict" \
    -H "Content-Type: application/json" \
    -d "$prediction_payload")

prediction_body=$(echo "$prediction_response" | sed -n '1,/^HTTP_CODE:/p' | sed '$d')
prediction_code=$(echo "$prediction_response" | grep "HTTP_CODE:" | cut -d':' -f2)

echo "HTTP Status: $prediction_code"
echo "Response Body: $prediction_body"

# Validate HTTP status
if [ "$prediction_code" != "200" ]; then
    echo "❌ FAILED: Prediction returned status $prediction_code (expected 200)"
    show_container_logs
    exit 1
fi

# Validate response structure
echo ""
echo "Validating response structure..."

validation_failed=false

# Check for required fields based on your API contract
if ! echo "$prediction_body" | grep -q "top_match\|prediction\|match_score"; then
    echo "❌ Response missing prediction field (top_match/prediction/match_score)"
    validation_failed=true
fi

if ! echo "$prediction_body" | grep -q "confidence\|score"; then
    echo "❌ Response missing confidence/score field"
    validation_failed=true
fi

if [ "$validation_failed" = true ]; then
    echo "❌ FAILED: Response validation failed"
    show_container_logs
    exit 1
fi

echo "✅ Response structure validated"
echo "✅ Prediction endpoint passed"

# =============================================================================
# FINAL SUMMARY
# =============================================================================

echo ""
echo "=========================================="
echo "✅ ALL SMOKE TESTS PASSED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ Container running and healthy"
echo "  ✅ Health endpoint responding (200 OK)"
echo "  ✅ Prediction endpoint responding (200 OK)"
echo "  ✅ Response structure validated"
echo "  ✅ Service is operational and ready for deployment"
echo ""
echo "Service URL: $SERVICE_URL"
echo "Container: $CONTAINER_NAME"
echo "Test Duration: ~$((attempt * RETRY_DELAY)) seconds"
echo ""

exit 0
