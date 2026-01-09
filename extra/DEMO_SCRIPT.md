# JobMatch System: Live Demo Script

**Objective:** Demonstrate MLOps Level 2 Maturity (Automation, Tracking, Serving) to Senior Management.

---

## Phase 1: System Initialization
*Narrative: "First, we initialize our distributed MLOps environment. This single command handles the end-to-end orchestration."*

**1. Start the System**
Open a terminal and run the all-in-one automation script:
```powershell
.\run_system_e2e_demo.bat
```
*Note: This script automatically triggers the Prefect pipeline, retrains the model on fresh data, and launches the API server.*

**2. Open Monitoring Dashboards**
While the system is running, open two new terminal tabs to launch the governance dashboards:

*   **Terminal 2 (Experiment Tracking):**
    ```powershell
    mlflow ui
    ```
*   **Terminal 3 (Workflow Orchestration):**
    ```powershell
    prefect server start
    ```

---

## Phase 2: Workflow & Governance (The "Back Office")
*Narrative: "Before we make predictions, let's verify our governance layer."*

**3. Inspect Pipeline Orchestration (Prefect)**
*   **Go to:** [http://127.0.0.1:4200](http://127.0.0.1:4200)
*   **Action:** Click on the `candidate-matching-pipeline` flow.
*   **What to Show:**
    *   Point to the **DAG (Directed Acyclic Graph)** visual.
    *   Explain the steps: `load_data` -> `validate_data` -> `train_model`.
    *   *Script:* "Here you see the automated workflow. If any step fails (e.g., bad data), the pipeline stops immediately, preventing corrupt models from reaching production."

**4. Inspect Experiment Tracking (MLflow)**
*   **Go to:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
*   **Action:** Click on `candidate_matching_experiment`.
*   **What to Show:**
    *   Click on the latest "Run".
    *   Scroll to **Metrics**: Show `f1_weighted`, `accuracy`, and `auc_roc`.
    *   Scroll to **Artifacts**: Show the saved model and `classification_report.txt`.
    *   *Script:* "We track every single training run. We know exactly which code and data produced this model, ensuring 100% auditability."

---

## Phase 3: The Prediction Service (The "Front Office")
*Narrative: "Now that we trust the model, let's see it in action."*

**5. Query the Prediction API**
*   **Go to:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI)
*   **Action:**
    1.  Click **POST /predict**.
    2.  Click **Try it out**.
    3.  Paste the following "Mobile Developer" test case:
        ```json
        {
          "candidate_id": "100",
          "skills": "Java, Android Development, Kotlin, REST APIs",
          "qualification": "Bachelor",
          "experience_level": "Mid"
        }
        ```
    4.  Click **Execute**.

**6. Interpret the Result**
*   **Scroll down to "Response body":**
    ```json
    {
      "candidate_id": "100",
      "job_role_probabilities": {
        "Android Developer": 0.85,
        "Software Engineer": 0.10,
        ...
      },
      "top_match": "Android Developer",
      "confidence": 0.85
    }
    ```
*   *Script:* "The system instantly analyzed the skills 'Kotlin' and 'Android' and matched them to **Android Developer** with **85% confidence**. It didn't just guess; it calculated the probability against all possible roles."

---

## Phase 4: Reliability Check (Optional)
*Narrative: "What happens if we send something ambiguous?"*

**7. Test the "Safety Net" (Fallback)**
*   **Action:** Modify the input to contain conflicting info (e.g., "Accounting skills" but "Mid Engineer").
*   **Result:** Confidence will drop.
*   *Script:* "If the model is unsure (Confidence < 40%), our **Algorithmic Fallback** kicks in to prevent hallucinations, ensuring operational safety."
