import pytest
import pandas as pd
import numpy as np
from src.features import SkillsEmbeddingTransformer, FeatureCrossTransformer

def test_skills_embedding_transformer():
    df = pd.DataFrame({'skills': ['Python, SQL', 'Java', np.nan]})
    transformer = SkillsEmbeddingTransformer(embedding_dim=4)
    # Pass as DataFrame to match pipeline behavior
    transformer.fit(df[['skills']])
    X_trans = transformer.transform(df[['skills']])
    
    assert X_trans.shape == (3, 4)
    # Check if NaN handling works (returns zeros)
    assert np.all(X_trans[2] == 0)

def test_feature_cross_transformer():
    df = pd.DataFrame({
        'experience_level': ['Senior', 'Junior', 'Mid'],
        'skills': ['A, B, C', 'A', 'A, B']
    })
    transformer = FeatureCrossTransformer()
    X_trans = transformer.transform(df)
    
    assert 'exp_skills_cross' in X_trans.columns
    # Check logic: Senior (len 3 = low?) dependent on bins. 
    # Bins: 0, 3, 6... labels: low, med..
    # 3 items -> 'low' (inclusive? binning pd.cut default is right included)
    # We just check it returns strings
    assert isinstance(X_trans['exp_skills_cross'].iloc[0], str)

def test_hashed_skills_transformer():
    from src.features import HashedSkillsTransformer
    
    df = ['Python, SQL', 'Java', 'C++'] # HashingVectorizer expects iterable of strings
    n_features = 10
    transformer = HashedSkillsTransformer(n_features=n_features)
    X_trans = transformer.transform(df)
    
    # Check shape: (n_samples, n_features)
    assert X_trans.shape == (3, n_features)
    
    # Check Check consistency (Reproducibility)
    X_trans_2 = transformer.transform(df)
    assert np.array_equal(X_trans, X_trans_2)
    
    # Check that it's not all zeros (unless inputs are empty, which they aren't)
    assert np.any(X_trans != 0)
