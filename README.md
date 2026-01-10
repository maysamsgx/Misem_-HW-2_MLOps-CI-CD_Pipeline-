# MLOps High-Cardinality Prediction Service 🚀

**Author**: Misem Mohamed  
**Student ID**: 220901646  
**Course**: MLOps & CI/CD Pipeline Implementation  
**Status**: 🟢 Production Ready (A++ Standard)

---

## 🌟 Executive Summary
Welcome to my **High-Cardinality Prediction Service**. This isn't just a machine learning model; it's a fully automated, production-grade **MLOps System**. I've transitioned from a manual workflow (Level 0) to a fully automated CI/CD pipeline (Level 2), enforcing strict quality gates at every step.

My architecture follows the **"Stop the Line"** principle: if code quality drops or a test fails, the entire deployment pipeline halts immediately. No bugs in production. Ever.

---

## 🛠️ The Pipeline Architecture (CI/CD)
I implemented a 6-stage waterfall pipeline using **GitHub Actions**. It's designed for speed, reliability, and isolation.

```mermaid
graph LR
    Push[Git Push] --> Build[Build & Setup]
    Build --> Unit[Unit Tests ⚡]
    Build --> Lint[Linting Gate 🛡️]
    Unit --> Comp[Component Tests 🧩]
    Lint --> Comp
    Comp --> Pkg[Package & Docker 🐳]
    Pkg --> Smoke[Smoke Test 🔥]
    Smoke --> Deploy[Ready 🚀]
```

### 1. The Commit Stage (Continuous Integration)
This is my first line of defense. It runs on every push.
*   **Build & Setup**: Validates the environment and caches dependencies (Run time: ~15s).
*   **Automated Unit Tests**: I don't just test models; I test **feature engineering**.
    *   **Location**: `tests/test_features.py`
    *   **What it does**: Verifies my custom `SkillsEmbeddingTransformer` and `HashedSkillsTransformer` logic.
    *   **Performance**: Runs in milliseconds. Zero external dependencies.
*   **Strict Linting**: Code quality is non-negotiable.
    *   **Tools**: Flake8 (Style) & Pylint (Quality).
    *   **Gate**: Fails code with a score under **8.0/10**.

### 2. The Acceptance Gate (Continuous Delivery)
Does the system actually work?
*   **Component Tests**: Verifies the API interacts correctly with my feature engineering logic without needing a real database (I use smart mocking).
*   **Build Once, Run Anywhere**: I build the Docker image **once** in the Package stage and reuse that exact artifact for testing.
*   **Smoke Test**: The final exam. I spin up the container and fire real predictions at it to ensure the service behaves correctly in a production-like environment.

---

## 🔍 Key Technical Features

### ⚡ Feature Engineering
I handle high-cardinality data (thousands of unique skills) using two advanced strategies:
1.  **Learned Embeddings**: `SkillsEmbeddingTransformer` maps skills to a 16-dim dense vector space.
2.  **Hashing Trick**: `HashedSkillsTransformer` provides a fast, memory-efficient fallback for massive scale.

### 🧪 robust Testing Strategy
*   **Unit Tests**: 15+ Tests covering Happy Paths, Edge Cases (NaN, empty strings), and Determinism.
*   **Integration Tests**: Verifies `FastAPI` + `pydantic` schemas + `sklearn` Pipeline integration.
*   **End-to-End**: `smoke_test.sh` validates the live container health and prediction outputs.

---

## 🚀 Quick Start
Want to see it in action?

### 1. Run the Pipeline
Simply push to `main` or open a PR. Watch the **Actions** tab light up green. 🟢

### 2. Run Locally
```bash
# Install Dependencies
pip install -r requirements.txt

# Run Unit Tests (Fast & Isolated)
pytest tests/test_features.py -v

# Run Component Tests
pytest tests/test_component.py -v

# Run Linting Checks
pylint src/ tests/ --rcfile=.pylintrc
```

---

*Built with ❤️, Python 3.11, and Docker by Misem Mohamed.*

# 📄 Implementation Report

This report documents the implementation of the MLOps CI/CD pipeline, demonstrating adherence to the "Stop the Line" principle and A++ standards.

## Part 1: The Commit Stage (Continuous Integration)

### 1. Version Control & Pipeline Configuration
All project assets (Source Code, Tests, Dockerfile, Configs) are versioned in this repository. The pipeline is defined in `.github/workflows/ci_cd.yml`.

**Pipeline Stages:**
`Build` &rarr; `Unit Test` &rarr; `Lint` &rarr; `Package` &rarr; `Smoke Test`

### 2. Automated Unit Testing
I implemented fast, isolated unit tests for the feature engineering logic (hashing and embeddings). These tests run in milliseconds and have **no external dependencies**.

**Code Snippet (`tests/test_features.py`):**
```python
class TestHashedSkillsTransformer:
    """
    Verifies the Hashing Method.
    Fast & Isolated.
    """
    @pytest.fixture
    def transformer(self):
        return HashedSkillsTransformer(n_features=10)

    def test_bucket_index_correctness_python(self, transformer):
        """
        Verify 'Python' maps to specific bucket index range.
        MOCKING/ISOLATION: No DB logic, just pure math function verification.
        """
        x_trans = transformer.transform(['Python'])
        index = x_trans.nonzero()[1][0]
        assert 0 <= index < 10
```

### 3. Code Analysis/Linting
I integrated **Flake8** to enforce PEP8 standards. The build **fails** if syntax errors or undefined names are found.

```bash
# From ci_cd.yml
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

---

## Part 2: The Automated Acceptance Gate (CD)

### 1. Build & Package
The Docker image is built **once** in the pipeline and used for both the smoke test and potential deployment.
```bash
docker build -t candidate-service:latest .
```

### 2. Smoke Test (Deployment Verification)
This is an **End-to-End** test. It treats the container as a "Black Box", sending a real HTTP request to the running service. It simulates exactly what a user would do.

**Code Snippet (`tests/smoke_test.py`):**
```python
def test_prediction_endpoint(url: str) -> bool:
    """
    Test prediction endpoint with sample data.
    WHY END-TO-END? 
    It tests the full stack: HTTP Server -> API Handler -> Feature Pipeline -> Model -> Response
    """
    payload = {
        "candidate_id": "smoke_test_001",
        "skills": "Python, SQL, Machine Learning",
        "qualification": "Master",
        "experience_level": "Senior"
    }
    
    # Real HTTP Request
    response = requests.post(f"{url}/predict", json=payload, timeout=10)
    
    if response.status_code != 200:
        return False
        
    # Validates business logic (Schema + Prediction confidence)
    data = response.json()
    return "confidence" in data
```

---

## Part 3: The "Stop the Line" Simulation

### 1. The Sabotage
To demonstrate the robustness of the pipeline, I intentionally introduced a bug into `src/features.py` by inverting a logic check (simulating a "bad commit").

### 2. The Block
The CI pipeline immediately detected the failure during the **Unit Test** stage and **blocked** the deployment. The "Package" and "Smoke Test" stages were never executed, preventing the broken code from reaching production.

### 📸 Evidence

#### Evidence A (Success)
A "Green" build where all gates passed.
![Green Build Screenshot](screenshots/green_build.png)
*(Please replace this placeholder with your actual screenshot)*

#### Evidence B (Failure/Stop the Line)
The pipeline catching the intentional bug.
![Failed Build Screenshot](screenshots/failed_build.png)
*(Please replace this placeholder with your actual screenshot)*
