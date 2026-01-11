"""
Smoke test for MLOps service deployment verification.
Ensures service is running and responding correctly.
Diagnostic enabled: Checks Docker container status on failure.
"""

import sys
import time
import subprocess
import requests


def get_docker_logs(container_name="mlops-service"):
    """Retrieve and print last 20 lines of container logs."""
    print(f"\n[DIAGNOSTIC] Retrieving logs for {container_name}...")
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "50", container_name],
            capture_output=True,
            text=True,
            check=False
        )
        print("=== CONTAINER LOGS START ===")
        print(result.stdout)
        print(result.stderr)
        print("=== CONTAINER LOGS END ===")
    except FileNotFoundError:
        print("Docker command not found.")
    except Exception as e:  # pylint: disable=broad-except
        print(f"Failed to get logs: {e}")


def check_container_status(container_name="mlops-service"):
    """Check if container is running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
            capture_output=True,
            text=True,
            check=False
        )
        status = result.stdout.strip()
        if not status:
            print(f"[DIAGNOSTIC] Inspect failed. Stderr: {result.stderr}")
        else:
            print(f"[DIAGNOSTIC] Container Status: {status}")
        return status == "running"
    except Exception as e:  # pylint: disable=broad-except
        print(f"[DIAGNOSTIC] Check failed with exception: {e}")
        return False


def wait_for_service(
    url: str,
    max_retries: int = 30,
    retry_delay: int = 2
) -> bool:
    """
    Wait for service to become available.
    """
    print(f"Waiting for service at {url}...")

    for attempt in range(1, max_retries + 1):
        # Fail-Fast: Check if container is dead
        if not check_container_status():
            print("❌ CRITICAL: Container is NOT running.")
            get_docker_logs()
            return False

        try:
            response = requests.get(
                f"{url}/health",
                timeout=5
            )

            if response.status_code == 200:
                print(f"✅ Service is UP (attempt {attempt})")
                return True

            print(f"Attempt {attempt}: Status {response.status_code}")

        except (requests.RequestException, ConnectionError) as e:
            # Short error format
            print(f"Attempt {attempt}/{max_retries}: {e}")

        time.sleep(retry_delay)

    return False


def test_prediction_endpoint(url: str) -> bool:
    """
    Test prediction endpoint with sample data.
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
            print(response.text)
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
    """
    service_url = "http://localhost:8000"

    print("=" * 50)
    print("MLOps Service Smoke Test")
    print("=" * 50)

    # Wait for service
    if not wait_for_service(service_url, max_retries=30):
        print("❌ FAILED: Service did not start")
        # Retry with 127.0.0.1 just in case
        print("Retrying with 127.0.0.1...")
        if not wait_for_service("http://127.0.0.1:8000", max_retries=5):
            get_docker_logs()  # Dump logs if we fail completely
            return 1

    # Test prediction
    if not test_prediction_endpoint(service_url):
        print("❌ FAILED: Prediction test failed")
        get_docker_logs()
        return 1

    print("=" * 50)
    print("✅ ALL SMOKE TESTS PASSED")
    print("=" * 50)
    return 0



if __name__ == "__main__":
    sys.exit(main())

