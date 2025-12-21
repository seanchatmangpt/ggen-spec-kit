"""Tests for essential information-theoretic metrics (80/20 approach)."""

from __future__ import annotations

import math
import random

import pytest

from specify_cli.hyperdimensional.metrics_core import (
    conditional_entropy,
    cross_entropy,
    discretize,
    entropy,
    entropy_from_samples,
    feature_selection_score,
    gini_gain,
    gini_impurity,
    information_gain,
    jensen_shannon_divergence,
    joint_entropy,
    kullback_leibler,
    mutual_information,
    normalized_mutual_information,
    perplexity,
    redundancy_score,
    variation_of_information,
)


class TestEntropy:
    """Test Shannon entropy calculation."""

    def test_uniform_distribution(self) -> None:
        """Uniform distribution has maximum entropy."""
        assert entropy([1, 1, 1, 1]) == 2.0
        assert entropy([1, 1]) == 1.0

    def test_deterministic(self) -> None:
        """Single outcome has zero entropy."""
        assert entropy([1, 0, 0, 0]) == 0.0

    def test_mixed_distribution(self) -> None:
        """Test known entropy values."""
        # H([0.7, 0.3]) ≈ 0.881
        h = entropy([0.7, 0.3])
        assert 0.88 < h < 0.89

    def test_empty_data(self) -> None:
        """Empty data has zero entropy."""
        assert entropy([]) == 0.0
        assert entropy([0, 0, 0]) == 0.0


class TestMutualInformation:
    """Test mutual information calculation."""

    def test_identical_variables(self) -> None:
        """I(X;X) = H(X)."""
        x = [1, 1, 2, 2, 3, 3]
        mi = mutual_information(x, x)
        x_entropy = entropy([2.0, 2.0, 2.0])  # Each value appears twice
        assert abs(mi - x_entropy) < 0.01

    def test_independent_variables(self) -> None:
        """Independent variables have zero MI."""
        x = [1, 1, 1, 2, 2, 2]
        y = [1, 2, 3, 1, 2, 3]
        mi = mutual_information(x, y)
        assert abs(mi) < 0.01

    def test_perfect_correlation(self) -> None:
        """Perfectly correlated variables."""
        x = [1, 2, 3, 4]
        y = [1, 2, 3, 4]  # Same values
        mi = mutual_information(x, y)
        assert mi > 0  # Should be H(X) = H(Y)

    def test_mismatched_length(self) -> None:
        """Raise error on mismatched lengths."""
        with pytest.raises(ValueError, match="same length"):
            mutual_information([1, 2], [1, 2, 3])


class TestInformationGain:
    """Test information gain for feature selection."""

    def test_perfect_predictor(self) -> None:
        """Perfect feature has high IG."""
        feature = [0, 0, 1, 1]
        target = [0, 0, 1, 1]
        ig = information_gain(feature, target)
        assert ig > 0.9  # Should be 1.0

    def test_useless_feature(self) -> None:
        """Random feature has zero IG."""
        feature = [0, 1, 0, 1]
        target = [0, 0, 1, 1]
        ig = information_gain(feature, target)
        assert abs(ig) < 0.1


class TestKullbackLeibler:
    """Test KL divergence."""

    def test_identical_distributions(self) -> None:
        """D_KL(P||P) = 0."""
        p = {"a": 0.5, "b": 0.3, "c": 0.2}
        assert kullback_leibler(p, p) == 0.0

    def test_different_distributions(self) -> None:
        """D_KL(P||Q) > 0 when P != Q."""
        p = {"a": 0.5, "b": 0.5}
        q = {"a": 0.3, "b": 0.7}
        kl = kullback_leibler(p, q)
        assert kl > 0

    def test_zero_probability(self) -> None:
        """Handle zero probabilities gracefully."""
        p = {"a": 0.6, "b": 0.4}
        q = {"a": 0.5, "b": 0.5, "c": 0.0}
        kl = kullback_leibler(p, q)
        assert kl >= 0


class TestEntropyFromSamples:
    """Test entropy estimation from continuous samples."""

    def test_uniform_samples(self) -> None:
        """Uniform samples should have high entropy."""
        samples = list(range(100))
        h = entropy_from_samples([float(x) for x in samples], bins=10)
        assert h > 3.0  # 10 bins → max entropy ≈ 3.32 bits

    def test_concentrated_samples(self) -> None:
        """Concentrated samples have low entropy."""
        samples = [5.0] * 50 + [5.1] * 50
        h = entropy_from_samples(samples, bins=10)
        assert h < 2.0  # Most samples in few bins


class TestJointEntropy:
    """Test joint entropy calculation."""

    def test_independent_variables(self) -> None:
        """H(X,Y) = H(X) + H(Y) for independent X,Y."""
        x = [1, 1, 2, 2]
        y = [1, 2, 1, 2]
        h_xy = joint_entropy(x, y)
        h_x = entropy([2.0, 2.0])
        h_y = entropy([2.0, 2.0])
        assert abs(h_xy - (h_x + h_y)) < 0.01

    def test_identical_variables(self) -> None:
        """H(X,X) = H(X)."""
        x = [1, 2, 3, 4]
        h_xx = joint_entropy(x, x)
        h_x = entropy([1.0, 1.0, 1.0, 1.0])
        assert abs(h_xx - h_x) < 0.01


class TestConditionalEntropy:
    """Test conditional entropy calculation."""

    def test_deterministic_relation(self) -> None:
        """H(Y|X) = 0 when Y determined by X."""
        x = [1, 1, 2, 2]
        y = [1, 1, 2, 2]  # y = x
        h_yx = conditional_entropy(x, y)
        assert abs(h_yx) < 0.01

    def test_independent_variables(self) -> None:
        """H(Y|X) = H(Y) for independent X,Y."""
        x = [1, 1, 2, 2]
        y = [1, 2, 1, 2]
        h_yx = conditional_entropy(x, y)
        h_y = entropy([2.0, 2.0])
        assert abs(h_yx - h_y) < 0.1


class TestNormalizedMutualInformation:
    """Test normalized MI."""

    def test_identical_variables(self) -> None:
        """NMI(X,X) = 1."""
        x = [1, 2, 3, 1, 2, 3]
        nmi = normalized_mutual_information(x, x)
        assert abs(nmi - 1.0) < 0.01

    def test_independent_variables(self) -> None:
        """NMI(X,Y) ≈ 0 for independent X,Y."""
        x = [1, 1, 1, 2, 2, 2]
        y = [1, 2, 3, 1, 2, 3]
        nmi = normalized_mutual_information(x, y)
        assert abs(nmi) < 0.1

    def test_bounded(self) -> None:
        """NMI is in [0,1]."""
        x = [1, 2, 3, 4]
        y = [4, 3, 2, 1]
        nmi = normalized_mutual_information(x, y)
        assert 0 <= nmi <= 1


class TestDiscretize:
    """Test continuous value discretization."""

    def test_uniform_values(self) -> None:
        """Uniform values distributed across bins."""
        values = list(range(100))
        discrete = discretize([float(x) for x in values], bins=10)
        unique_bins = len(set(discrete))
        assert unique_bins >= 8  # Should use most bins

    def test_concentrated_values(self) -> None:
        """Concentrated values in few bins."""
        values = [5.0] * 100
        discrete = discretize(values, bins=10)
        assert len(set(discrete)) <= 2  # Only 1-2 bins used

    def test_empty_list(self) -> None:
        """Handle empty list."""
        assert discretize([]) == []


class TestFeatureSelectionScore:
    """Test feature selection scoring."""

    def test_relevant_feature(self) -> None:
        """Relevant feature has positive score."""
        feature = [1.0, 2.0, 3.0, 4.0] * 25
        target = [0] * 50 + [1] * 50
        score = feature_selection_score(feature, target, bins=4)
        assert score > 0  # Should have some information gain

    def test_irrelevant_feature(self) -> None:
        """Irrelevant feature has low score."""
        random.seed(42)
        feature = [random.random() for _ in range(100)]
        target = [0] * 50 + [1] * 50
        score = feature_selection_score(feature, target, bins=10)
        assert score < 0.3


class TestRedundancyScore:
    """Test feature redundancy measurement."""

    def test_identical_features(self) -> None:
        """Identical features have high redundancy."""
        feature1 = [1.0, 2.0, 3.0, 4.0] * 25
        feature2 = feature1.copy()
        score = redundancy_score(feature1, feature2, bins=4)
        assert score > 1.5  # High mutual information

    def test_independent_features(self) -> None:
        """Independent features have lower redundancy than identical."""
        random.seed(42)
        feature1 = [random.random() for _ in range(100)]
        random.seed(43)
        feature2 = [random.random() for _ in range(100)]

        # Compare to identical features
        identical_score = redundancy_score(feature1, feature1, bins=10)
        independent_score = redundancy_score(feature1, feature2, bins=10)
        assert independent_score < identical_score


class TestJensenShannonDivergence:
    """Test Jensen-Shannon divergence."""

    def test_identical_distributions(self) -> None:
        """JSD(P,P) = 0."""
        p = {"a": 0.5, "b": 0.3, "c": 0.2}
        jsd = jensen_shannon_divergence(p, p)
        assert abs(jsd) < 0.01

    def test_symmetric(self) -> None:
        """JSD(P,Q) = JSD(Q,P)."""
        p = {"a": 0.5, "b": 0.5}
        q = {"a": 0.3, "b": 0.7}
        jsd_pq = jensen_shannon_divergence(p, q)
        jsd_qp = jensen_shannon_divergence(q, p)
        assert abs(jsd_pq - jsd_qp) < 0.01

    def test_bounded(self) -> None:
        """JSD is bounded by 1."""
        p = {"a": 1.0}
        q = {"b": 1.0}
        jsd = jensen_shannon_divergence(p, q)
        assert 0 <= jsd <= 1


class TestCrossEntropy:
    """Test cross-entropy calculation."""

    def test_identical_distributions(self) -> None:
        """H(P,P) = H(P)."""
        p = {"a": 0.5, "b": 0.5}
        ce = cross_entropy(p, p)
        expected = sum(-pv * math.log2(pv) for pv in p.values() if pv > 0)
        assert abs(ce - expected) < 0.01

    def test_different_distributions(self) -> None:
        """H(P,Q) > H(P) when P != Q."""
        p = {"a": 0.5, "b": 0.5}
        q = {"a": 0.3, "b": 0.7}
        ce = cross_entropy(p, q)
        h_p = sum(-pv * math.log2(pv) for pv in p.values() if pv > 0)
        assert ce >= h_p


class TestGiniImpurity:
    """Test Gini impurity calculation."""

    def test_pure_node(self) -> None:
        """Pure node has zero Gini impurity."""
        assert gini_impurity([100, 0, 0]) == 0.0
        assert gini_impurity([0, 0, 50]) == 0.0

    def test_maximum_impurity(self) -> None:
        """Maximum impurity for balanced classes."""
        # Two classes: max = 0.5
        gini = gini_impurity([50, 50])
        assert abs(gini - 0.5) < 0.01

    def test_empty_counts(self) -> None:
        """Handle empty counts."""
        assert gini_impurity([0, 0, 0]) == 0.0


class TestGiniGain:
    """Test Gini-based information gain."""

    def test_perfect_split(self) -> None:
        """Perfect split has high Gini gain."""
        feature = [0, 0, 1, 1]
        target = [0, 0, 1, 1]
        gain = gini_gain(feature, target)
        assert gain > 0.4

    def test_no_split(self) -> None:
        """No information gain from useless feature."""
        feature = [0] * 100
        target = [0] * 50 + [1] * 50
        gain = gini_gain(feature, target)
        assert abs(gain) < 0.01


class TestPerplexity:
    """Test perplexity calculation."""

    def test_uniform_distribution(self) -> None:
        """Perplexity of uniform distribution equals number of outcomes."""
        p = {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}
        perp = perplexity(p)
        assert abs(perp - 4.0) < 0.01

    def test_deterministic(self) -> None:
        """Perplexity of deterministic distribution is 1."""
        p = {"a": 1.0}
        perp = perplexity(p)
        assert abs(perp - 1.0) < 0.01


class TestVariationOfInformation:
    """Test variation of information."""

    def test_identical_variables(self) -> None:
        """VI(X,X) = 0."""
        x = [1, 2, 3, 1, 2, 3]
        vi = variation_of_information(x, x)
        assert abs(vi) < 0.01

    def test_symmetric(self) -> None:
        """VI(X,Y) = VI(Y,X)."""
        x = [1, 1, 2, 2]
        y = [1, 2, 1, 2]
        vi_xy = variation_of_information(x, y)
        vi_yx = variation_of_information(y, x)
        assert abs(vi_xy - vi_yx) < 0.01
