import requests
import sys
import time

# Helper script to check if the service is up and running correctly
# Usage: python tests/smoke_test.py [url]

def smoke_test(url="http://localhost:8000"):
    print(f"Running Smoke Test against {url}...")
    
    # Health/Root check (if exists) or just Try Connect
    # The app doesn't have a root endpoint in the provided code, so we hit predict directly
    
    payload = {
        "candidate_id": "smoke_test_001",
        "skills": "Python, Docker, CI/CD",
        "qualification": "Bachelors",
        "experience_level": "Mid"
    }
    
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.post(f"{url}/predict", json=payload, timeout=5)
            
            if response.status_code == 200:
                print("SUCCESS: Service responded with 200 OK")
                print("Response:", response.json())
                sys.exit(0)
            elif response.status_code == 503:
                print("WARNING: Service ready but model not loaded (503). Retrying...")
            else:
                print(f"FAILURE: Unexpected status code {response.status_code}")
                print(response.text)
                sys.exit(1)
        
        except requests.exceptions.ConnectionError:
            print(f"Connection failed. Service might be starting up... (Attempt {i+1}/{max_retries})")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
            
    print("FAILURE: Service did not respond successfully after retries.")
    sys.exit(1)

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    smoke_test(target_url)
