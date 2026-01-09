from fastapi.testclient import TestClient
from src.inference import app
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

client = TestClient(app)

# Mocking the model and label encoder since we might not have the pkl files in the CI environment
# or we want to isolate the test.
@pytest.fixture
def mock_artifacts():
    with patch('src.inference.model') as mock_model, \
         patch('src.inference.label_encoder') as mock_le:
        
        # Setup Mock Model behavior
        # predict_proba returns [n_samples, n_classes]
        mock_model.predict_proba.return_value = np.array([[0.1, 0.8, 0.1]])
        
        # Setup Mock Label Encoder behavior
        mock_le.classes_ = np.array(['Data Analyst', 'Data Scientist', 'Machine Learning Engineer'])
        
        yield mock_model, mock_le

def test_prediction_endpoint_integration(mock_artifacts):
    """
    Component Test:
    Verifies that the API correctly receives input, interacts with the (mocked) model,
    and returns a formatted response.
    """
    mock_model, mock_le = mock_artifacts
    
    payload = {
        "candidate_id": "123",
        "skills": "Python, SQL, Machine Learning",
        "qualification": "Master's",
        "experience_level": "Senior"
    }
    
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['candidate_id'] == "123"
    assert data['top_match'] == "Data Scientist" # Based on our mock [0.1, 0.8, 0.1]
    assert data['confidence'] == 0.8
    assert "job_role_probabilities" in data
    assert data['job_role_probabilities']['Data Scientist'] == 0.8

def test_prediction_fallback_logic(mock_artifacts):
    """
    Test the 'Stop the Line' / Fallback logic if confidence is low.
    """
    mock_model, mock_le = mock_artifacts
    # Low confidence mock
    mock_model.predict_proba.return_value = np.array([[0.33, 0.33, 0.34]]) 
    
    payload = {
        "candidate_id": "456",
        "skills": "Python, SQL", # Trigger keyword heuristic
        "qualification": "Bachelor's",
        "experience_level": "Entry"
    }
    
    response = client.post("/predict", json=payload)
    
    # Should technically still be 200 OK but handled by fallback
    assert response.status_code == 200
    data = response.json()
    
    # The heuristic in inference.py sets confidence to 0.5 if fallback triggers
    # and if "Python" or "SQL" is present, it forces "Data Scientist"
    assert data['top_match'] == "Data Scientist" 
    assert data['confidence'] == 0.5
