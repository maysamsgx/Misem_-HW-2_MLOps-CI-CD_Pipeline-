# 🚀 Ocean Flow - Complete Installation & Execution Guide

This guide ensures **anyone** can run the system with **zero errors** on a fresh Windows machine.

---

## ✅ Prerequisites
Before starting, ensure you have:
1. **Python 3.11** installed ([Download here](https://www.python.org/downloads/))
2. **Git** installed ([Download here](https://git-scm.com/downloads))
3. **Windows PowerShell** (comes with Windows 10/11)

---

## 📦 Step 1: Clone the Repository

Open **PowerShell** and run:

```powershell
cd C:\Users\YourUsername\Desktop
git clone https://github.com/maysaamsgx/mlops-candidate-matching.git
cd mlops-candidate-matching
```

---

## 🔧 Step 2: Run the Automated Demo Script

The system includes a **one-click setup script** that handles everything:

```powershell
.\run_system_e2e_demo.bat
```

### What This Script Does:
1. ✅ Creates a Python virtual environment (`.venv`)
2. ✅ Installs all dependencies from `requirements.txt`
3. ✅ Runs the Prefect training pipeline
4. ✅ Starts the FastAPI prediction service on port 8000

### Expected Output:
You should see:
```
===================================================
  Candidate Matching System - Automated Demo Run
  Maintained by Misem (Project Lead)
===================================================
[1/4] Checking python environment...
[2/4] Installing dependencies...
[3/4] Running Training Pipeline (Prefect)...
[4/4] Starting FastAPI Server...

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
Loaded model from models/production_pipeline.pkl
Loaded label encoder from models/label_encoder.pkl
```

---

## 🌐 Step 3: Access the Live Services

Once the script completes, you have **3 dashboards** running:

### 1. **Prediction API (FastAPI Swagger)**
- **URL**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **What to do**: 
  1. Click `POST /predict`
  2. Click **"Try it out"**
  3. Paste this JSON:
     ```json
     {
       "candidate_id": "DEMO_001",
       "skills": "Python, Machine Learning, SQL",
       "qualification": "Master",
       "experience_level": "Senior"
     }
     ```
  4. Click **"Execute"**
  5. **Expected Result**: You should see a **200 OK** response with `job_role_probabilities` showing the full distribution.

### 2. **MLflow Tracking Dashboard**
- **URL**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **What to see**: All training runs, metrics (F1-Score, Log Loss), and the Model Registry.

### 3. **Prefect Workflow Dashboard**
- **URL**: [http://127.0.0.1:4200](http://127.0.0.1:4200)
- **What to see**: The automated pipeline execution with task statuses.

---

## 🛠️ Troubleshooting

### Issue 1: "Python not found"
**Solution**: Ensure Python 3.11 is installed and added to PATH. Verify with:
```powershell
python --version
```

### Issue 2: "Port 8000 already in use"
**Solution**: Kill the existing process:
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
```
Then re-run the demo script.

### Issue 3: "ModuleNotFoundError"
**Solution**: The script automatically sets `PYTHONPATH`. If you run Python commands manually, ensure you set it:
```powershell
$env:PYTHONPATH = $PWD
```

### Issue 4: "Great Expectations Error"
**Solution**: This has been fixed in the current version. Ensure you have the latest code:
```powershell
git pull origin main
```

---

## 🎓 For Presentation Demo

Follow this exact sequence:

1. **Start the System**:
   ```powershell
   .\run_system_e2e_demo.bat
   ```
   Wait for "Application startup complete."

2. **Open Browser Tabs** (in this order):
   - Tab 1: [http://127.0.0.1:4200](http://127.0.0.1:4200) (Prefect)
   - Tab 2: [http://127.0.0.1:5000](http://127.0.0.1:5000) (MLflow)
   - Tab 3: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (API)

3. **Demo Flow**:
   - Show Prefect → Show MLflow → Execute API Prediction

---

## ✅ Success Criteria

You know the system is working correctly when:
- ✅ API returns **200 OK** with probability distributions
- ✅ MLflow shows experiment runs with metrics
- ✅ Prefect shows completed flow runs with green status
- ✅ No error messages in the terminal

---

**System Status**: 🟢 Production Ready  
**Maintained by**: Misem Mohamed (Lead Architect)
