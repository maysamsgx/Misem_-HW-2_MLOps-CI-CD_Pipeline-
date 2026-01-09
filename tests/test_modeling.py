import pytest
import numpy as np
from src.modeling import CandidateMatcherEnsemble

def test_ensemble_initialization():
    model = CandidateMatcherEnsemble(use_stacking=True)
    assert model.use_stacking is True
    assert model.clf is None

from unittest.mock import patch
from sklearn.linear_model import LogisticRegression

def test_ensemble_fit_predict():
    """
    [Optimization]: We mock the heavy base models (XGB/LGBM) with simple LogisticRegression.
    This ensures we test the *orchestration* logic (Stacking/Checkpointing) without
    paying the training cost in CI.
    """
    # Mock data
    X = np.random.rand(20, 10)
    y = np.random.randint(0, 3, size=20)
    
    # Patch the heavy model generator to return fast models
    with patch.object(CandidateMatcherEnsemble, '_get_base_models') as mock_base:
        mock_base.return_value = [
            ('mock_lr_1', LogisticRegression()),
            ('mock_lr_2', LogisticRegression())
        ]
        
        # Test Stacking Path (The Logic)
        model = CandidateMatcherEnsemble(use_stacking=True)
        
        # We need to ensure StackingClassifier doesn't take forever, 
        # but with LR base models it should be instant.
        model.fit(X, y)
        
        preds = model.predict(X)
        assert len(preds) == 20
        
        probs = model.predict_proba(X)
        assert probs.shape == (20, 3)

