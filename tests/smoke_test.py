"""
Smoke test for MLOps service deployment verification.
Ensures service is running and responding correctly.
"""

import sys
import time

import requests


def wait_for_service(
    url: str,
    max_retries: int = 30,
    retry_delay: int = 2
) -> bool:
    """
    Wait for service to become available.
    
    Args:
        url: Service health check URL
        max_retries: Maximum number of retry attempts
        retry_delay: Seconds to wait between retries
        
    Returns:
        True if service is available, False otherwise
    """
    print(f"Waiting for service at {url}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                f"{url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Service is UP (attempt {attempt})")
                return True
                
        except (requests.RequestException, ConnectionError) as e:
            print(f"Attempt {attempt}/{max_retries}: {e}")
            
        time.sleep(retry_delay)
    
    return False


def test_prediction_endpoint(url: str) -> bool:
    """
    Test prediction endpoint with sample data.
    
    Args:
        url: Service base URL
        
    Returns:
        True if prediction succeeds, False otherwise
    """
    payload = {
        "candidate_id": "smoke_test_001",
        "skills": "Python, SQL, Machine Learning",
        "qualification": "Master",
        "experience_level": "Senior"
    }
    
    try:
        response = requests.post(
            f"{url}/predict",
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Prediction failed: HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Validate response structure
        required_fields = ["top_match", "confidence"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing field: {field}")
                return False
        
        print("✅ Prediction endpoint working")
        return True
        
    except (requests.RequestException, ValueError) as e:
        print(f"❌ Prediction test failed: {e}")
        return False


def main() -> int:
    """
    Main smoke test execution.
    
    Returns:
        0 on success, 1 on failure
    """
    # Use localhost as this runs outside the container (on host/runner)
    service_url = "http://localhost:8000"
    
    print("=" * 50)
    print("MLOps Service Smoke Test")
    print("=" * 50)
    
    # Wait for service
    if not wait_for_service(service_url, max_retries=30):
        print("❌ FAILED: Service did not start")
        # Try 127.0.0.1 fallback just in case
        print("Retrying with 127.0.0.1...")
        if not wait_for_service("http://127.0.0.1:8000", max_retries=5):
             return 1
    
    # Test prediction
    if not test_prediction_endpoint(service_url):
        print("❌ FAILED: Prediction test failed")
        return 1
    
    print("=" * 50)
    print("✅ ALL SMOKE TESTS PASSED")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
