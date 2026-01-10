from contextlib import asynccontextmanager
import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Global variables
model = None
label_encoder = None


def load_startup_artifacts():
    global model, label_encoder
    # [Anas]: Bootstrapping the artifacts.
    model_path = os.getenv("MODEL_PATH", "models/production_pipeline.pkl")
    le_path = os.getenv("LE_PATH", "models/label_encoder.pkl")

    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"Loaded model from {model_path}")

    if os.path.exists(le_path):
        label_encoder = joblib.load(le_path)
        print(f"Loaded label encoder from {le_path}")

    if not model or not label_encoder:
        print("Warning: Missing artifacts. Service will fail predictions.")


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=redefined-outer-name, unused-argument
    # Load artifacts on startup
    load_startup_artifacts()
    yield


app = FastAPI(title="Candidate Matching Service", version="1.0.0", lifespan=lifespan)


# Input Schema
class CandidateInput(BaseModel):
    candidate_id: str
    skills: str
    qualification: str
    experience_level: str


# Output Schema
class PredictionOutput(BaseModel):
    candidate_id: str
    job_role_probabilities: dict
    top_match: str
    confidence: float


@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictionOutput)
def predict(candidate: CandidateInput):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Create DataFrame from input
    data = pd.DataFrame([candidate.model_dump()])

    # Predict Probabilities
    try:
        # [Misem]: Reframing pattern.
        probs = model.predict_proba(data)[0]
        # [Misem]: Mapping probabilities.
        classes = label_encoder.classes_
        prob_dict = {str(c): float(p) for c, p in zip(classes, probs)}

        # Determine top match initially
        top_match = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[top_match]

        # [Misem]: Algorithmic Fallback Pattern.
        if confidence < 0.4:
            print(f"Confidence {confidence} below threshold. Fallback.")
            s = candidate.skills.lower()
            if 'sql' in s or 'python' in s or 'data' in s:
                fallback_role = "Data Scientist"
            else:
                fallback_role = "Unknown"

            top_match = fallback_role
            confidence = 0.5
            prob_dict = {fallback_role: 0.5, "Model_Low_Conf": 0.5}

        # [Mohammed Ali]: CME Data Logging.
        with open("inference_log.csv", "a", encoding='utf-8') as f:
            f.write(f"{candidate.candidate_id},{top_match},{confidence}\n")

        return PredictionOutput(
            candidate_id=candidate.candidate_id,
            job_role_probabilities=prob_dict,
            top_match=top_match,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def feedback(candidate_id: str, actual_role: str):
    # [Misem]: Responsible AI pattern.
    with open("feedback_log.csv", "a", encoding='utf-8') as f:
        f.write(f"{candidate_id},{actual_role}\n")
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    # CRITICAL: Use 0.0.0.0 for Docker
    PORT = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
