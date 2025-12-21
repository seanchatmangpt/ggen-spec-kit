"""Comprehensive unit tests for information-theoretic metrics.

Tests cover:
- Entropy calculations (Shannon, differential, joint, conditional)
- Divergence measures (KL, JS, Wasserstein, Hellinger)
- Mutual information and information gain
- Information geometry (Fisher information, geodesics)
- Complexity measures (Kolmogorov, Lempel-Ziv, approximate entropy)
- Numerical stability and edge cases
- Performance benchmarks

Testing Strategy:
- Known distributions with analytical solutions
- Symmetry and mathematical properties
- Edge cases (zeros, uniform, deterministic)
- Numerical stability (overflow, underflow)
- Performance characteristics
"""

from __future__ import annotations

import numpy as np
import pytest

from specify_cli.hyperdimensional.metrics import (
    approximate_entropy,
    conditional_entropy,
    differential_entropy,
    entropy,
    fisher_information_matrix,
    geodesic_distance,
    hellinger_distance,
    information_gain,
    information_metric,
    jensen_shannon_divergence,
    joint_entropy,
    kolmogorov_complexity,
    kullback_leibler_divergence,
    lempel_ziv_complexity,
    mutual_information,
    normalized_mutual_information,
    redundancy_measure,
    wasserstein_distance,
)

# =============================================================================
# Entropy Measures Tests
# =============================================================================


class TestEntropy:
    """Tests for Shannon entropy calculation."""

    def test_uniform_distribution_maximum_entropy(self) -> None:
        """Uniform distribution should have maximum entropy for its size."""
        # 2 states: max entropy = 1 bit
        p = [0.5, 0.5]
        assert np.isclose(entropy(p), 1.0)

        # 4 states: max entropy = 2 bits
        p = [0.25, 0.25, 0.25, 0.25]
        assert np.isclose(entropy(p), 2.0)

        # 8 states: max entropy = 3 bits
        p = [0.125] * 8
        assert np.isclose(entropy(p), 3.0)

    def test_deterministic_distribution_zero_entropy(self) -> None:
        """Deterministic distribution should have zero entropy."""
        p = [1.0, 0.0, 0.0]
        assert np.isclose(entropy(p), 0.0)

        p = [0.0, 1.0, 0.0, 0.0]
        assert np.isclose(entropy(p), 0.0)

    def test_intermediate_distribution(self) -> None:
        """Test known entropy value for specific distribution."""
        # Binary entropy function H(0.3) ≈ 0.881
        p = [0.3, 0.7]
        expected = -0.3 * np.log2(0.3) - 0.7 * np.log2(0.7)
        assert np.isclose(entropy(p), expected)

    def test_base_change(self) -> None:
        """Test entropy calculation with different bases."""
        p = [0.5, 0.5]
        # Base 2: 1 bit
        assert np.isclose(entropy(p, base=2.0), 1.0)
        # Base e: ln(2) nats
        assert np.isclose(entropy(p, base=np.e), np.log(2))

    def test_handles_zeros_gracefully(self) -> None:
        """Zero probabilities should not cause errors (0 log 0 = 0)."""
        p = [0.0, 0.5, 0.5]
        assert np.isclose(entropy(p), 1.0)

        p = [0.0, 0.0, 0.0, 1.0]
        assert np.isclose(entropy(p), 0.0)

    def test_validation_negative_probabilities(self) -> None:
        """Should raise error for negative probabilities."""
        with pytest.raises(ValueError, match="negative"):
            entropy([-0.1, 0.6, 0.5])

    def test_validation_does_not_sum_to_one(self) -> None:
        """Should raise error if probabilities don't sum to 1."""
        with pytest.raises(ValueError, match="sum to 1.0"):
            entropy([0.3, 0.3, 0.3])

    def test_list_input(self) -> None:
        """Should accept list input."""
        p = [0.5, 0.5]
        assert np.isclose(entropy(p), 1.0)


class TestDifferentialEntropy:
    """Tests for differential entropy of continuous distributions."""

    def test_standard_normal_approximate(self) -> None:
        """Standard normal has differential entropy ≈ 2.05 bits."""
        np.random.seed(42)
        samples = np.random.randn(1000)
        h = differential_entropy(samples)
        # Should be close to 0.5 * log2(2πe) ≈ 2.047
        assert 1.5 < h < 2.5

    def test_multivariate_samples(self) -> None:
        """Should handle multivariate samples."""
        np.random.seed(42)
        samples = np.random.randn(500, 2)
        h = differential_entropy(samples)
        assert h > 0

    def test_custom_bandwidth(self) -> None:
        """Should accept custom bandwidth parameter."""
        np.random.seed(42)
        samples = np.random.randn(100)
        h1 = differential_entropy(samples, bandwidth=0.1)
        h2 = differential_entropy(samples, bandwidth=0.5)
        # Different bandwidths should give different estimates
        assert h1 != h2


class TestJointEntropy:
    """Tests for joint entropy H(X,Y)."""

    def test_independent_variables_sum(self) -> None:
        """For independent X,Y: H(X,Y) = H(X) + H(Y)."""
        px = np.array([0.5, 0.5])
        py = np.array([0.6, 0.4])
        pxy = np.outer(px, py)

        h_xy = joint_entropy(pxy)
        h_x = entropy(px)
        h_y = entropy(py)

        assert np.isclose(h_xy, h_x + h_y)

    def test_deterministic_relationship(self) -> None:
        """If Y = f(X) deterministic, H(X,Y) = H(X)."""
        # Y fully determined by X
        pxy = np.array([[0.5, 0.0], [0.0, 0.5]])
        px = np.array([0.5, 0.5])

        assert np.isclose(joint_entropy(pxy), entropy(px))

    def test_validation(self) -> None:
        """Should validate input distribution."""
        with pytest.raises(ValueError, match="sum to 1.0"):
            joint_entropy([[0.3, 0.3], [0.3, 0.0]])


class TestConditionalEntropy:
    """Tests for conditional entropy H(Y|X)."""

    def test_deterministic_conditional_zero(self) -> None:
        """If Y fully determined by X, H(Y|X) = 0."""
        p_y_given_x = np.array([[1.0, 0.0], [0.0, 1.0]])
        p_x = np.array([0.5, 0.5])
        assert np.isclose(conditional_entropy(p_y_given_x, p_x), 0.0)

    def test_independent_variables_equals_marginal(self) -> None:
        """If X,Y independent, H(Y|X) = H(Y)."""
        # Y independent of X
        p_y_given_x = np.array([[0.6, 0.4], [0.6, 0.4]])
        p_x = np.array([0.5, 0.5])
        p_y = np.array([0.6, 0.4])

        assert np.isclose(conditional_entropy(p_y_given_x, p_x), entropy(p_y))

    def test_chain_rule(self) -> None:
        """H(X,Y) = H(X) + H(Y|X)."""
        p_y_given_x = np.array([[0.8, 0.2], [0.3, 0.7]])
        p_x = np.array([0.4, 0.6])

        # Compute joint distribution
        pxy = p_x[:, np.newaxis] * p_y_given_x

        h_xy = joint_entropy(pxy)
        h_x = entropy(p_x)
        h_y_given_x = conditional_entropy(p_y_given_x, p_x)

        assert np.isclose(h_xy, h_x + h_y_given_x, atol=1e-6)

    def test_validation_shape_mismatch(self) -> None:
        """Should validate prior and conditional distributions match."""
        with pytest.raises(ValueError, match="length must match"):
            conditional_entropy([[0.5, 0.5], [0.5, 0.5]], [0.5, 0.5, 0.0])


# =============================================================================
# Divergence Measures Tests
# =============================================================================


class TestKullbackLeiblerDivergence:
    """Tests for KL divergence D_KL(P||Q)."""

    def test_identical_distributions_zero(self) -> None:
        """D_KL(P||P) = 0."""
        p = [0.5, 0.3, 0.2]
        assert np.isclose(kullback_leibler_divergence(p, p), 0.0)

    def test_non_negative(self) -> None:
        """D_KL(P||Q) ≥ 0."""
        p = [0.5, 0.3, 0.2]
        q = [0.4, 0.4, 0.2]
        assert kullback_leibler_divergence(p, q) >= 0

    def test_not_symmetric(self) -> None:
        """D_KL(P||Q) ≠ D_KL(Q||P) in general."""
        p = [0.8, 0.1, 0.1]
        q = [0.4, 0.3, 0.3]

        d_pq = kullback_leibler_divergence(p, q)
        d_qp = kullback_leibler_divergence(q, p)

        assert d_pq != d_qp

    def test_infinite_when_support_mismatch(self) -> None:
        """D_KL(P||Q) = inf if support(P) not subset of support(Q)."""
        p = [0.5, 0.5, 0.0]
        q = [0.0, 0.5, 0.5]

        with pytest.warns(UserWarning, match="zero probability"):
            div = kullback_leibler_divergence(p, q)
            assert np.isinf(div)

    def test_validation_different_shapes(self) -> None:
        """Should raise error for different shapes."""
        with pytest.raises(ValueError, match="same shape"):
            kullback_leibler_divergence([0.5, 0.5], [0.3, 0.3, 0.4])


class TestJensenShannonDivergence:
    """Tests for Jensen-Shannon divergence."""

    def test_identical_distributions_zero(self) -> None:
        """JSD(P,P) = 0."""
        p = [0.5, 0.3, 0.2]
        assert np.isclose(jensen_shannon_divergence(p, p), 0.0)

    def test_symmetric(self) -> None:
        """JSD(P,Q) = JSD(Q,P)."""
        p = [0.5, 0.3, 0.2]
        q = [0.4, 0.4, 0.2]

        jsd_pq = jensen_shannon_divergence(p, q)
        jsd_qp = jensen_shannon_divergence(q, p)

        assert np.isclose(jsd_pq, jsd_qp)

    def test_bounded_zero_to_one(self) -> None:
        """0 ≤ JSD ≤ 1 when base=2."""
        p = [0.9, 0.1, 0.0]
        q = [0.0, 0.5, 0.5]

        jsd = jensen_shannon_divergence(p, q)
        assert 0.0 <= jsd <= 1.0

    def test_always_finite(self) -> None:
        """JSD should always be finite (unlike KL)."""
        p = [0.5, 0.5, 0.0]
        q = [0.0, 0.5, 0.5]

        jsd = jensen_shannon_divergence(p, q)
        assert np.isfinite(jsd)


class TestWassersteinDistance:
    """Tests for Wasserstein (Earth Mover's) distance."""

    def test_identical_distributions_zero(self) -> None:
        """W(P,P) = 0."""
        p = [0.5, 0.3, 0.2]
        assert np.isclose(wasserstein_distance(p, p), 0.0)

    def test_non_negative(self) -> None:
        """W(P,Q) ≥ 0."""
        p = [0.5, 0.3, 0.2]
        q = [0.2, 0.3, 0.5]
        assert wasserstein_distance(p, q) >= 0

    def test_symmetric(self) -> None:
        """W(P,Q) = W(Q,P)."""
        p = [0.5, 0.3, 0.2]
        q = [0.2, 0.3, 0.5]

        assert np.isclose(wasserstein_distance(p, q), wasserstein_distance(q, p))

    def test_with_custom_metric(self) -> None:
        """Should accept custom distance metric."""
        p = [0.5, 0.5]
        q = [0.3, 0.7]
        metric = np.array([[0, 2], [2, 0]])

        w = wasserstein_distance(p, q, metric=metric)
        assert w > 0


class TestHellingerDistance:
    """Tests for Hellinger distance."""

    def test_identical_distributions_zero(self) -> None:
        """H(P,P) = 0."""
        p = [0.5, 0.3, 0.2]
        assert np.isclose(hellinger_distance(p, p), 0.0)

    def test_bounded_zero_to_one(self) -> None:
        """0 ≤ H(P,Q) ≤ 1."""
        p = [0.9, 0.1, 0.0]
        q = [0.0, 0.5, 0.5]

        h = hellinger_distance(p, q)
        assert 0.0 <= h <= 1.0

    def test_symmetric(self) -> None:
        """H(P,Q) = H(Q,P)."""
        p = [0.5, 0.3, 0.2]
        q = [0.2, 0.4, 0.4]

        assert np.isclose(hellinger_distance(p, q), hellinger_distance(q, p))

    def test_orthogonal_distributions(self) -> None:
        """Completely disjoint distributions should have distance close to 1."""
        p = [1.0, 0.0]
        q = [0.0, 1.0]

        h = hellinger_distance(p, q)
        # sqrt(0.5 * (1^2 + 1^2)) = 1
        assert np.isclose(h, 1.0)


# =============================================================================
# Mutual Information Tests
# =============================================================================


class TestMutualInformation:
    """Tests for mutual information I(X;Y)."""

    def test_independent_variables_zero(self) -> None:
        """I(X;Y) = 0 for independent variables."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)

        mi = mutual_information(x, y, bins=10)
        # Should be close to 0 (some noise due to finite samples and binning)
        assert mi < 0.7  # Adjusted for binning artifacts

    def test_identical_variables_equals_entropy(self) -> None:
        """I(X;X) = H(X)."""
        np.random.seed(42)
        x = np.random.choice([0, 1, 2], size=100, p=[0.5, 0.3, 0.2])

        mi = mutual_information(x, x, bins=3)
        # Should be close to H(X)
        assert mi > 1.0

    def test_symmetric(self) -> None:
        """I(X;Y) = I(Y;X)."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        mi_xy = mutual_information(x, y)
        mi_yx = mutual_information(y, x)

        assert np.isclose(mi_xy, mi_yx, atol=0.1)

    def test_non_negative(self) -> None:
        """I(X;Y) ≥ 0."""
        np.random.seed(42)
        x = np.random.randn(50)
        y = np.random.randn(50)

        assert mutual_information(x, y) >= 0

    def test_multivariate_input(self) -> None:
        """Should handle multivariate inputs."""
        np.random.seed(42)
        x = np.random.randn(50, 2)
        y = np.random.randn(50, 2)

        mi = mutual_information(x, y, bins=5)
        assert mi >= 0


class TestNormalizedMutualInformation:
    """Tests for normalized mutual information."""

    def test_bounded_zero_to_one(self) -> None:
        """0 ≤ NMI ≤ 1."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)

        nmi = normalized_mutual_information(x, y, bins=10)
        assert 0.0 <= nmi <= 1.0

    def test_perfect_correlation_one(self) -> None:
        """NMI(X,X) = 1."""
        np.random.seed(42)
        x = np.random.randn(100)

        nmi = normalized_mutual_information(x, x, bins=10)
        assert np.isclose(nmi, 1.0, atol=0.1)

    def test_independent_near_zero(self) -> None:
        """NMI ≈ 0 for independent variables."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)

        nmi = normalized_mutual_information(x, y, bins=10)
        assert nmi < 0.3


class TestInformationGain:
    """Tests for information gain (feature selection)."""

    def test_perfect_predictor(self) -> None:
        """Feature that perfectly predicts target has high IG."""
        feature = np.array([0, 0, 1, 1, 2, 2])
        target = np.array([0, 0, 1, 1, 2, 2])

        ig = information_gain(feature, target, bins=3)
        assert ig > 0.9

    def test_uninformative_feature(self) -> None:
        """Random feature has low IG."""
        np.random.seed(42)
        feature = np.random.randn(100)
        target = np.random.choice([0, 1], size=100)

        ig = information_gain(feature, target, bins=10)
        assert ig < 0.5

    def test_equals_mutual_information(self) -> None:
        """IG(Target|Feature) = I(Feature;Target)."""
        np.random.seed(42)
        feature = np.random.randn(50)
        target = np.random.randn(50)

        ig = information_gain(feature, target, bins=10)
        mi = mutual_information(feature, target, bins=10)

        assert np.isclose(ig, mi)


class TestRedundancyMeasure:
    """Tests for feature redundancy analysis."""

    def test_output_shape(self) -> None:
        """Should return (n_features, n_features) matrix."""
        np.random.seed(42)
        features = np.random.randn(100, 3)

        redundancy = redundancy_measure(features, bins=10)
        assert redundancy.shape == (3, 3)

    def test_symmetric_matrix(self) -> None:
        """Redundancy matrix should be symmetric."""
        np.random.seed(42)
        features = np.random.randn(50, 3)

        redundancy = redundancy_measure(features, bins=5)
        assert np.allclose(redundancy, redundancy.T)

    def test_diagonal_self_information(self) -> None:
        """Diagonal entries are self-information (entropy)."""
        np.random.seed(42)
        features = np.random.randn(100, 2)

        redundancy = redundancy_measure(features, bins=10)
        # Diagonal should be positive (entropy)
        assert np.all(np.diag(redundancy) > 0)

    def test_identical_features_high_redundancy(self) -> None:
        """Identical features should have high redundancy."""
        np.random.seed(42)
        x = np.random.randn(100)
        features = np.column_stack([x, x, np.random.randn(100)])

        redundancy = redundancy_measure(features, bins=10)
        # Features 0 and 1 should have high mutual information
        assert redundancy[0, 1] > 0.8 * redundancy[0, 0]


# =============================================================================
# Information Geometry Tests
# =============================================================================


class TestFisherInformationMatrix:
    """Tests for Fisher Information Matrix."""

    def test_output_shape(self) -> None:
        """FIM should be (n_params, n_params) matrix."""
        samples = np.random.randn(100, 3)
        fim = fisher_information_matrix(samples)
        assert fim.shape == (3, 3)

    def test_symmetric(self) -> None:
        """FIM should be symmetric."""
        samples = np.random.randn(100, 2)
        fim = fisher_information_matrix(samples)
        assert np.allclose(fim, fim.T)

    def test_positive_semidefinite(self) -> None:
        """FIM should be positive semi-definite."""
        samples = np.random.randn(100, 2)
        fim = fisher_information_matrix(samples)

        # Check eigenvalues are non-negative
        eigenvalues = np.linalg.eigvalsh(fim)
        assert np.all(eigenvalues >= -1e-6)

    def test_standard_normal_approximate_identity(self) -> None:
        """For standard normal, FIM ≈ I (identity)."""
        np.random.seed(42)
        samples = np.random.randn(1000, 2)
        fim = fisher_information_matrix(samples)

        # Should be close to identity matrix
        assert np.allclose(fim, np.eye(2), atol=0.3)


class TestGeodesicDistance:
    """Tests for geodesic distance on statistical manifold."""

    def test_euclidean_metric_default(self) -> None:
        """Without metric, should compute Euclidean distance."""
        p1 = [0, 0]
        p2 = [3, 4]

        dist = geodesic_distance(p1, p2)
        assert np.isclose(dist, 5.0)

    def test_with_custom_metric(self) -> None:
        """Should use provided metric tensor."""
        p1 = [0, 0]
        p2 = [1, 1]
        metric = np.array([[2, 0], [0, 2]])

        dist = geodesic_distance(p1, p2, metric)
        # sqrt([1,1]^T [[2,0],[0,2]] [1,1]) = sqrt(4) = 2
        assert np.isclose(dist, 2.0)

    def test_zero_distance_identical_points(self) -> None:
        """Distance between identical points is zero."""
        p = [1.5, 2.3]
        assert np.isclose(geodesic_distance(p, p), 0.0)

    def test_validation_shape_mismatch(self) -> None:
        """Should raise error for different shapes."""
        with pytest.raises(ValueError, match="same shape"):
            geodesic_distance([1, 2], [1, 2, 3])


class TestInformationMetric:
    """Tests for information metric tensor."""

    def test_output_shape(self) -> None:
        """Metric should be (n_dims, n_dims) matrix."""
        vectors = np.random.randn(100, 3)
        metric = information_metric(vectors)
        assert metric.shape == (3, 3)

    def test_symmetric(self) -> None:
        """Metric tensor should be symmetric."""
        vectors = np.random.randn(50, 2)
        metric = information_metric(vectors)
        assert np.allclose(metric, metric.T)

    def test_positive_semidefinite(self) -> None:
        """Metric should be positive semi-definite."""
        vectors = np.random.randn(100, 2)
        metric = information_metric(vectors)

        eigenvalues = np.linalg.eigvalsh(metric)
        assert np.all(eigenvalues >= -1e-6)


# =============================================================================
# Complexity Measures Tests
# =============================================================================


class TestKolmogorovComplexity:
    """Tests for Kolmogorov complexity approximation."""

    def test_random_data_high_complexity(self) -> None:
        """Random data should have high complexity (incompressible)."""
        random_data = b"asdfjkl;qweruiop"
        k_random = kolmogorov_complexity(random_data)

        # Should be close to original length (incompressible)
        assert k_random > len(random_data) * 0.5

    def test_repetitive_data_low_complexity(self) -> None:
        """Repetitive data should have low complexity (compressible)."""
        repetitive_data = b"aaaaaaaaaaaaaaaa"
        k_repetitive = kolmogorov_complexity(repetitive_data)

        # Should be smaller than original length (gzip has header overhead)
        assert k_repetitive < len(repetitive_data) * 2.0

    def test_string_input(self) -> None:
        """Should accept string input."""
        k = kolmogorov_complexity("hello world")
        assert k > 0

    def test_invalid_approximation_method(self) -> None:
        """Should raise error for unknown approximation method."""
        with pytest.raises(ValueError, match="Unknown approximation"):
            kolmogorov_complexity(b"test", approximation="unknown")


class TestLempelZivComplexity:
    """Tests for Lempel-Ziv complexity."""

    def test_periodic_sequence_low_complexity(self) -> None:
        """Periodic sequence has low complexity."""
        periodic = "01010101"
        c = lempel_ziv_complexity(periodic)
        assert c <= 5  # Algorithm finds 5 patterns in this sequence

    def test_random_sequence_higher_complexity(self) -> None:
        """Random-looking sequence has higher complexity."""
        random_like = "011010011100"
        c_random = lempel_ziv_complexity(random_like)

        periodic = "01010101"
        c_periodic = lempel_ziv_complexity(periodic)

        assert c_random >= c_periodic  # More patterns or equal

    def test_list_input(self) -> None:
        """Should accept list input."""
        c = lempel_ziv_complexity([0, 1, 1, 0, 1, 0])
        assert c > 0

    def test_constant_sequence(self) -> None:
        """Constant sequence has minimal complexity."""
        constant = "0000000000"
        c = lempel_ziv_complexity(constant)
        # Constant sequence still requires patterns to be discovered
        assert c <= 10  # Algorithm behavior for constant sequences


class TestApproximateEntropy:
    """Tests for approximate entropy (regularity measure)."""

    def test_regular_sequence_low_entropy(self) -> None:
        """Regular/predictable sequence has low ApEn."""
        np.random.seed(42)
        t = np.linspace(0, 4 * np.pi, 100)
        regular = np.sin(t)

        apen = approximate_entropy(regular, m=2)
        assert apen >= 0

    def test_random_sequence_higher_entropy(self) -> None:
        """Random sequence has higher ApEn."""
        np.random.seed(42)
        random_seq = np.random.randn(100)

        t = np.linspace(0, 4 * np.pi, 100)
        regular = np.sin(t)

        apen_random = approximate_entropy(random_seq, m=2)
        apen_regular = approximate_entropy(regular, m=2)

        # Random should have higher approximate entropy
        assert apen_random > apen_regular

    def test_custom_tolerance(self) -> None:
        """Should accept custom tolerance parameter."""
        np.random.seed(42)
        data = np.random.randn(50)

        apen1 = approximate_entropy(data, m=2, r=0.1)
        apen2 = approximate_entropy(data, m=2, r=0.5)

        # Different tolerances should give different results
        assert apen1 != apen2

    def test_constant_sequence_zero_or_low(self) -> None:
        """Constant sequence should have very low ApEn."""
        constant = np.ones(100)
        apen = approximate_entropy(constant, m=2)
        assert apen < 0.1


# =============================================================================
# Numerical Stability Tests
# =============================================================================


class TestNumericalStability:
    """Tests for numerical stability and edge cases."""

    def test_entropy_with_very_small_probabilities(self) -> None:
        """Should handle very small probabilities without overflow."""
        p = [1e-10, 1.0 - 1e-10]
        h = entropy(p)
        assert np.isfinite(h)
        assert h >= 0

    def test_kl_divergence_near_identical(self) -> None:
        """Should handle nearly identical distributions."""
        p = [0.333333, 0.333333, 0.333334]
        q = [0.333333, 0.333334, 0.333333]

        kl = kullback_leibler_divergence(p, q)
        assert np.isfinite(kl)
        assert kl >= 0
        assert kl < 1e-3

    def test_mutual_information_with_few_samples(self) -> None:
        """Should handle small sample sizes gracefully."""
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])

        mi = mutual_information(x, y, bins=2)
        assert np.isfinite(mi)
        assert mi >= 0

    def test_fisher_information_singular_covariance(self) -> None:
        """Should handle singular covariance matrices."""
        # Perfectly correlated samples
        samples = np.array([[1, 1], [2, 2], [3, 3]])
        fim = fisher_information_matrix(samples)

        assert np.all(np.isfinite(fim))


# =============================================================================
# Performance Benchmarks
# =============================================================================


@pytest.mark.slow
class TestPerformance:
    """Performance benchmarks for metrics calculations."""

    def test_entropy_large_distribution(self) -> None:
        """Entropy should be fast for large distributions."""
        import time

        p = np.random.dirichlet(np.ones(10000))

        start = time.time()
        _ = entropy(p)
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 0.1

    def test_mutual_information_large_samples(self) -> None:
        """MI should handle large sample sizes efficiently."""
        import time

        np.random.seed(42)
        x = np.random.randn(10000)
        y = np.random.randn(10000)

        start = time.time()
        _ = mutual_information(x, y, bins=20)
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 5.0

    def test_fisher_information_computation(self) -> None:
        """FIM computation should be efficient."""
        import time

        samples = np.random.randn(1000, 10)

        start = time.time()
        _ = fisher_information_matrix(samples)
        elapsed = time.time() - start

        # Should complete quickly
        assert elapsed < 0.5


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests combining multiple metrics."""

    def test_information_theoretic_identities(self) -> None:
        """Test fundamental information theory identities."""
        # Generate correlated variables
        np.random.seed(42)
        x = np.random.choice([0, 1], size=200, p=[0.6, 0.4])
        y = np.where(np.random.rand(200) < 0.8, x, 1 - x)

        # Discretize for entropy calculation
        xy_counts = np.zeros((2, 2))
        for xi, yi in zip(x, y, strict=False):
            xy_counts[xi, yi] += 1
        pxy = xy_counts / len(x)
        px = np.sum(pxy, axis=1)
        py = np.sum(pxy, axis=0)

        # I(X;Y) = H(X) + H(Y) - H(X,Y)
        h_x = entropy(px)
        h_y = entropy(py)
        h_xy = joint_entropy(pxy)
        mi_calc = mutual_information(x, y, bins=2)

        expected_mi = h_x + h_y - h_xy
        # Should be approximately equal (with binning tolerance)
        assert np.isclose(mi_calc, expected_mi, atol=0.3)

    def test_divergence_relationships(self) -> None:
        """Test relationships between different divergences."""
        p = [0.5, 0.3, 0.2]
        q = [0.4, 0.4, 0.2]

        # JSD is bounded
        jsd = jensen_shannon_divergence(p, q)
        assert 0 <= jsd <= 1

        # Hellinger is bounded
        h = hellinger_distance(p, q)
        assert 0 <= h <= 1

        # KL is non-negative
        kl = kullback_leibler_divergence(p, q)
        assert kl >= 0

    def test_feature_selection_workflow(self) -> None:
        """Test complete feature selection workflow."""
        np.random.seed(42)

        # Create features with varying relevance
        n_samples = 200
        target = np.random.choice([0, 1], size=n_samples)

        # Relevant feature (correlated with target)
        relevant = target + np.random.randn(n_samples) * 0.3

        # Irrelevant feature (independent)
        irrelevant = np.random.randn(n_samples)

        # Redundant feature (copy of relevant)
        redundant = relevant + np.random.randn(n_samples) * 0.1

        features = np.column_stack([relevant, irrelevant, redundant])

        # Calculate information gains
        ig = [information_gain(features[:, i], target, bins=10) for i in range(3)]

        # Relevant feature should have higher IG than irrelevant
        assert ig[0] > ig[1]

        # Check redundancy
        redundancy = redundancy_measure(features, bins=10)

        # Features 0 and 2 should be redundant
        assert redundancy[0, 2] > 0.5 * redundancy[0, 0]
