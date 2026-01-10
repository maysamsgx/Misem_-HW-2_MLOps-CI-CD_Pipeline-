from contextlib import asynccontextmanager
import logging
import os
import sys

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ensure src.features is available for unpickling custom transformers
try:
    import src.features  # type: ignore # pylint: disable=unused-import
    # We might need explicit imports if the pickle expects them in namespace
    from src.features import (
        SkillsEmbeddingTransformer,
        HashedSkillsTransformer,
        FeatureCrossTransformer
    )
except ImportError as e:
    print(f"WARNING: Could not import src.features: {e}")

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model = None
label_encoder = None


def load_startup_artifacts():
    global model, label_encoder
    model_path = os.getenv("MODEL_PATH", "models/production_pipeline.pkl")
    le_path = os.getenv("LE_PATH", "models/label_encoder.pkl")

    try:
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            logger.warning(f"Model not found at {model_path}")

        if os.path.exists(le_path):
            label_encoder = joblib.load(le_path)
            logger.info(f"Loaded label encoder from {le_path}")
        else:
            logger.warning(f"Label encoder not found at {le_path}")

    except Exception as e:
        logger.critical(f"Failed to load artifacts: {e}")
        # We don't exit here to allow /health to return 503 instead of crash
        # But for 'production' fail-fast is often better.
        # Given the smoke test failure, we want to know why it crashed.
        # Re-raising might be better if we want container to exit and log.
        # But 'Connection Refused' implies it exited.
        # If we catch it, it stays up and returns 500/503.
        # Let's log and keep running so we can see logs via 'docker logs'.
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=redefined-outer-name, unused-argument
    # Load artifacts on startup
    logger.info("Service starting up...")
    load_startup_artifacts()
    yield
    logger.info("Service shutting down...")


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
    # Return 200 even if model missing, but indicate status
    # This allows container to stay 'Running' so we can debug
    status = "healthy" if model else "degraded_model_missing"
    return {"status": status, "model_loaded": model is not None}


@app.post("/predict", response_model=PredictionOutput)
def predict(candidate: CandidateInput):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded or failed to load")

    try:
        # Create DataFrame from input
        data = pd.DataFrame([candidate.model_dump()])

        # Predict Probabilities
        probs = model.predict_proba(data)[0]
        
        # Mapping probabilities
        if label_encoder:
            classes = label_encoder.classes_
        else:
            # Fallback if LE missing but model exists (unlikely)
            classes = [str(i) for i in range(len(probs))]

        prob_dict = {str(c): float(p) for c, p in zip(classes, probs)}

        # Determine top match
        top_match = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[top_match]

        # Algorithmic Fallback
        if confidence < 0.4:
            logger.info(f"Low confidence {confidence}. Using fallback.")
            s = candidate.skills.lower()
            if 'sql' in s or 'python' in s or 'data' in s:
                fallback_role = "Data Scientist"
            else:
                fallback_role = "Unknown"

            top_match = fallback_role
            confidence = 0.5
            prob_dict = {fallback_role: 0.5, "Model_Low_Conf": 0.5}

        # Data Logging
        try:
            with open("inference_log.csv", "a", encoding='utf-8') as f:
                f.write(f"{candidate.candidate_id},{top_match},{confidence}\n")
        except IOError as e:
            logger.error(f"Failed to write log: {e}")

        return PredictionOutput(
            candidate_id=candidate.candidate_id,
            job_role_probabilities=prob_dict,
            top_match=top_match,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def feedback(candidate_id: str, actual_role: str):
    try:
        with open("feedback_log.csv", "a", encoding='utf-8') as f:
            f.write(f"{candidate_id},{actual_role}\n")
    except IOError:
        pass
    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    # CRITICAL: Use 0.0.0.0 for Docker
    PORT = int(os.environ.get("PORT", 8000))
    # Log level info to debug startup
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
