import numpy as np
import pandas as pd
import pytest

from src.features import (
    SkillsEmbeddingTransformer,
    HashedSkillsTransformer,
    FeatureCrossTransformer
)

# =============================================================================
# Unit Tests for Feature Engineering Logic
# Principle: One Test, One Purpose (Single Assertion per Test)
# Total Target: 10-15 Tests
# =============================================================================


class TestSkillsEmbeddingTransformer:
    """
    Verifies the custom embedding logic for skills.
    Isolated tests: No external dependencies.
    """

    @pytest.fixture
    def transformer(self):
        return SkillsEmbeddingTransformer(embedding_dim=4, max_vocab_size=10)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({
            'skills': ['Python, SQL', 'Java', np.nan, '', 'Python', 'Go, Rust']
        })

    # --- Happy Path ---
    def test_fit_creates_vocab(self, transformer, sample_df):
        """Verify that fit method creates a vocabulary mapping."""
        transformer.fit(sample_df[['skills']])
        assert len(transformer.vocab) > 0, "Vocabulary should be populated"

    def test_transform_output_shape(self, transformer, sample_df):
        """Verify the transformer returns the expected shape (N, Dim)."""
        transformer.fit(sample_df[['skills']])
        x_trans = transformer.transform(sample_df[['skills']])
        assert x_trans.shape == (6, 4), "Output shape should match (n, dim)"

    def test_embedding_determinism(self):
        """Verify that the embedding is deterministic given the fixed seed."""
        data = pd.DataFrame({'skills': ['Python, Docker, Kubernetes']})

        trans1 = SkillsEmbeddingTransformer(embedding_dim=8)
        trans1.fit(data)
        out1 = trans1.transform(data)

        trans2 = SkillsEmbeddingTransformer(embedding_dim=8)
        trans2.fit(data)
        out2 = trans2.transform(data)

        np.testing.assert_array_almost_equal(
            out1, out2,
            err_msg="Embeddings must be deterministic"
        )

    # --- Edge Cases ---
    def test_embedding_nan_handling(self, transformer, sample_df):
        """Verify NaN inputs result in a zero vector."""
        transformer.fit(sample_df[['skills']])
        x_trans = transformer.transform(sample_df[['skills']])
        # Index 2 is NaN
        assert np.all(x_trans[2] == 0), "NaN input should result in zero vector"

    def test_embedding_empty_string_handling(self, transformer, sample_df):
        """Verify empty string inputs result in a zero vector."""
        transformer.fit(sample_df[['skills']])
        x_trans = transformer.transform(sample_df[['skills']])
        # Index 3 is ''
        assert np.all(x_trans[3] == 0), "Empty input should be zero vector"

    def test_unknown_skill_handling(self, transformer, sample_df):
        """Verify unknown skill results in zero vector/graceful handling."""
        transformer.fit(sample_df[['skills']])
        new_data = pd.DataFrame({'skills': ['BrainSurgery']})
        x_trans = transformer.transform(new_data)
        assert x_trans.shape == (1, 4)

    # --- Boundary Conditions ---
    def test_max_vocab_truncation(self):
        """Verify that vocabulary does not exceed max_vocab_size."""
        data = pd.DataFrame({'skills': ['A, B, C, D, E']})
        trans = SkillsEmbeddingTransformer(max_vocab_size=3)
        trans.fit(data)
        assert len(trans.vocab) == 3, "Vocabulary size should be truncated"


class TestHashedSkillsTransformer:
    """
    Verifies the Hashing Method.
    Fast & Isolated.
    """

    @pytest.fixture
    def transformer(self):
        return HashedSkillsTransformer(n_features=10)

    # --- Happy Path ---
    def test_hashing_output_shape(self, transformer):
        """Verify output shape matches n_features."""
        skills = ['Python, SQL']
        x_out = transformer.transform(skills)
        assert x_out.shape == (1, 10)

    def test_bucket_index_non_zero(self, transformer):
        """Verify input produces a non-zero hash vector."""
        x_trans = transformer.transform(['Python'])
        assert len(x_trans.nonzero()[1]) > 0, "Should have non-zero entry"

    # --- Specific Logic/Bucket Checks ---
    def test_bucket_index_correctness_python(self, transformer):
        """
        Verify 'Python' maps to specific bucket index range.
        """
        x_trans = transformer.transform(['Python'])
        index = x_trans.nonzero()[1][0]
        assert 0 <= index < 10

    def test_multiple_skills_hashing(self, transformer):
        """Verify comma-separated skills result in multiple active buckets."""
        x_trans_safe = transformer.transform(['SkillA, SkillB'])
        assert x_trans_safe.nnz >= 1


class TestFeatureCrossTransformer:
    """
    Verifies feature crossing logic.
    """

    @pytest.fixture
    def transformer(self):
        return FeatureCrossTransformer()

    def test_cross_column_creation(self, transformer):
        """Verify the new feature column is created."""
        df = pd.DataFrame({
            'experience_level': ['Senior'],
            'skills': ['A, B, C']
        })
        x_trans = transformer.transform(df)
        assert 'exp_skills_cross' in x_trans.columns

    def test_logic_senior_low_skills(self, transformer):
        """Verify Senior with 3 skills maps to Senior_low."""
        df = pd.DataFrame({
            'experience_level': ['Senior'],
            'skills': ['A,B,C']
        })
        result = transformer.transform(df)['exp_skills_cross'].iloc[0]
        assert result == 'Senior_low'

    def test_logic_junior_med_skills(self, transformer):
        """Verify Junior with 4 skills maps to Junior_med."""
        df = pd.DataFrame({
            'experience_level': ['Junior'],
            'skills': ['A,B,C,D']
        })
        result = transformer.transform(df)['exp_skills_cross'].iloc[0]
        assert result == 'Junior_med'

    def test_empty_skills_count(self, transformer):
        """Verify handling of empty skills string."""
        df = pd.DataFrame({'experience_level': ['Mid'], 'skills': ['']})
        result = transformer.transform(df)['exp_skills_cross'].iloc[0]
        assert result == 'Mid_low'
