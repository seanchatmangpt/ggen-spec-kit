"""Hyperdimensional computing and information-theoretic metrics for spec-kit.

This package provides:
- Information-theoretic metrics (entropy, divergence, mutual information)
- Decision-theoretic optimization
- Hyperdimensional vector space operations
- Specification analysis and completeness measures

Mathematical Foundation
-----------------------
Information theory quantifies uncertainty, information content, and relationships
between random variables. Key concepts:

1. **Shannon Entropy**: H(X) = -Σ p(x) log p(x)
   - Measures average uncertainty in bits
   - Maximum when distribution is uniform
   - Zero for deterministic outcomes

2. **Mutual Information**: I(X;Y) = H(X) + H(Y) - H(X,Y)
   - Measures shared information between variables
   - Zero for independent variables
   - Bounded by min(H(X), H(Y))

3. **KL Divergence**: D_KL(P||Q) = Σ p(x) log(p(x)/q(x))
   - Measures information lost when Q approximates P
   - Non-negative, zero iff P = Q
   - Not symmetric

4. **Fisher Information**: I(θ) = E[(∂log p(x|θ)/∂θ)²]
   - Measures information about parameter θ
   - Basis for information geometry
   - Related to Cramér-Rao bound

Applications to Spec-Kit
-------------------------
1. **Specification Completeness**:
   - High entropy → many edge cases, potentially incomplete
   - Low entropy → well-constrained, likely complete
   - Optimal: minimize entropy subject to quality constraints

2. **Feature Compatibility**:
   - Information distance between feature specifications
   - Small distance → compatible features
   - Large distance → potential conflicts

3. **Job-Outcome Alignment**:
   - Mutual information between job requirements and outcomes
   - High MI → strongly related
   - Low MI → weak relationship, potential misalignment

4. **Optimization**:
   - Multi-objective: (quality, completeness, complexity)
   - Pareto frontier in information space
   - Constraint satisfaction via information projections

Examples
--------
>>> from specify_cli.hyperdimensional.metrics import entropy, mutual_information
>>> # Measure specification uncertainty
>>> spec_dist = [0.7, 0.2, 0.1]  # Probabilities of spec states
>>> uncertainty = entropy(spec_dist)  # Shannon entropy in bits
>>> # Measure feature relationship
>>> feature_x = [[1, 0], [0, 1], [1, 0]]
>>> feature_y = [[1, 0], [1, 0], [0, 1]]
>>> relationship = mutual_information(feature_x, feature_y)

References
----------
- Cover, T. M., & Thomas, J. A. (2006). Elements of Information Theory (2nd ed.)
- Amari, S., & Nagaoka, H. (2000). Methods of Information Geometry
- MacKay, D. J. (2003). Information Theory, Inference, and Learning Algorithms
"""

from specify_cli.hyperdimensional.agi_reasoning import (
    AutonomousReasoningEngine,
    Constraint,
    ReasoningStep,
    ReasoningStrategy,
    ReasoningTrace,
    Solution,
)
from specify_cli.hyperdimensional.embedding_store import (
    RDFLIB_AVAILABLE,
    EmbeddingMetadata,
    EmbeddingStore,
)
from specify_cli.hyperdimensional.embeddings import (
    HyperdimensionalEmbedding,
    VectorOperations,
    VectorStats,
)
from specify_cli.hyperdimensional.rdf_to_vector import (
    RDFVectorTransformer,
    TransformationResult,
    VectorizedConstraint,
)
from specify_cli.hyperdimensional.semantic_agents import (
    CollaborativeResult,
    DesignExplorer,
    DependencyResolver,
    ExplorationResult,
    SemanticAgent,
    SemanticPath,
    SpecificationAnalyzer,
)
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
from specify_cli.hyperdimensional.observability_core import (
    record_search_latency,
    record_vector_stats,
    track_embedding_operation,
    track_similarity_search,
    track_validation_check,
)
from specify_cli.hyperdimensional.prioritization import (
    # Data Structures
    Feature,
    PriorityItem,
    Task,
    # Market Opportunity
    addressable_market_size,
    # Complexity Analysis
    approximate_complexity,
    # Task Prioritization
    balance_objectives,
    # Feature Entropy Analysis
    calculate_feature_entropy,
    # Information Gain Analysis
    calculate_information_gain,
    competition_analysis,
    complexity_per_requirement,
    # Decision Support
    create_priority_matrix,
    # Information-Theoretic Ranking
    criticality_score,
    # Information Density
    edge_case_coverage_estimate,
    entropy_reduction_per_task,
    estimate_implementation_complexity,
    # Mutual Information Ranking
    feature_importance_ranking,
    feature_redundancy_analysis,
    find_strategic_initiatives,
    identify_blockers,
    identify_complex_requirements,
    identify_critical_path,
    # Adaptive Prioritization
    identify_dependencies,
    identify_quick_wins,
    identify_uncertain_features,
    information_density,
    market_timing_analysis,
    # Job-Outcome Prioritization
    maximize_job_coverage,
    measure_specification_quality,
    mutual_info_with_performance,
    mutual_info_with_quality,
    mutual_info_with_reliability,
    mutual_information_with_goals,
    opportunity_score,
    predict_effort_impact,
    prioritize_tasks,
    quantify_outcome_value,
    rank_features_by_gain,
    rank_jobs_by_frequency,
    rank_outcomes_by_importance,
    recommend_next_tasks,
    reprioritize_based_on_progress,
    select_features_maximizing_info,
    slack_time_analysis,
    spec_completeness_likelihood,
    suggest_parallel_work,
    suggest_task_ordering,
    uncertainty_reduction_rate,
)
from specify_cli.hyperdimensional.priority_core import (
    FeaturePriority,
    estimate_feature_effort,
    estimate_feature_value,
    prioritize_features,
    quick_wins,
    top_n_features,
)
from specify_cli.hyperdimensional.reasoning_core import (
    batch_compare,
    check_constraint_satisfied,
    compare_entities,
    find_similar_entities,
    get_violated_constraints,
    rank_by_objective,
)
from specify_cli.hyperdimensional.speckit_embeddings import (
    SPECKIT_COMMANDS,
    SPECKIT_CONSTRAINTS,
    SPECKIT_FEATURES,
    SPECKIT_JOBS,
    SPECKIT_OUTCOMES,
    get_command_embeddings,
    get_constraint_embeddings,
    get_feature_embeddings,
    get_job_embeddings,
    get_outcome_embeddings,
    initialize_speckit_embeddings,
)

__all__ = [
    "RDFLIB_AVAILABLE",
    # Spec-kit constants
    "SPECKIT_COMMANDS",
    "SPECKIT_CONSTRAINTS",
    "SPECKIT_FEATURES",
    "SPECKIT_JOBS",
    "SPECKIT_OUTCOMES",
    "EmbeddingMetadata",
    "EmbeddingStore",
    # Observability (OTEL instrumentation)
    "record_search_latency",
    "record_vector_stats",
    "track_embedding_operation",
    "track_similarity_search",
    "track_validation_check",
    # Prioritization - Data Structures
    "Feature",
    "FeaturePriority",
    # Core embedding classes
    "HyperdimensionalEmbedding",
    "PriorityItem",
    "Task",
    "VectorOperations",
    "VectorStats",
    "addressable_market_size",
    # Prioritization - Complexity
    "approximate_complexity",
    "approximate_entropy",
    "balance_objectives",
    # Reasoning core (80/20)
    "batch_compare",
    # Prioritization - Feature Entropy
    "calculate_feature_entropy",
    # Prioritization - Information Gain
    "calculate_information_gain",
    "check_constraint_satisfied",
    "compare_entities",
    "competition_analysis",
    "complexity_per_requirement",
    "conditional_entropy",
    # Prioritization - Decision Support
    "create_priority_matrix",
    "criticality_score",
    "differential_entropy",
    "edge_case_coverage_estimate",
    # Entropy measures
    "entropy",
    # Prioritization - Information-Theoretic Ranking
    "entropy_reduction_per_task",
    "estimate_feature_effort",
    "estimate_feature_value",
    "estimate_implementation_complexity",
    "feature_importance_ranking",
    "feature_redundancy_analysis",
    "find_similar_entities",
    "find_strategic_initiatives",
    # Information geometry
    "fisher_information_matrix",
    "geodesic_distance",
    "get_command_embeddings",
    "get_constraint_embeddings",
    "get_feature_embeddings",
    "get_job_embeddings",
    "get_outcome_embeddings",
    "get_violated_constraints",
    "hellinger_distance",
    "identify_blockers",
    "identify_complex_requirements",
    "identify_critical_path",
    "identify_dependencies",
    "identify_quick_wins",
    "identify_uncertain_features",
    # Prioritization - Information Density
    "information_density",
    "information_gain",
    "information_metric",
    # Embedding initialization
    "initialize_speckit_embeddings",
    "jensen_shannon_divergence",
    "joint_entropy",
    # Complexity measures
    "kolmogorov_complexity",
    # Divergence measures
    "kullback_leibler_divergence",
    "lempel_ziv_complexity",
    "market_timing_analysis",
    "maximize_job_coverage",
    "measure_specification_quality",
    "mutual_info_with_performance",
    # Prioritization - Mutual Information
    "mutual_info_with_quality",
    "mutual_info_with_reliability",
    # Mutual information
    "mutual_information",
    "mutual_information_with_goals",
    "normalized_mutual_information",
    # Prioritization - Market
    "opportunity_score",
    "predict_effort_impact",
    # Prioritization - Task Framework
    "prioritize_features",
    "prioritize_tasks",
    "quantify_outcome_value",
    "quick_wins",
    "rank_features_by_gain",
    # Prioritization - Job-Outcome
    "rank_by_objective",
    "rank_jobs_by_frequency",
    "rank_outcomes_by_importance",
    "recommend_next_tasks",
    "redundancy_measure",
    # Prioritization - Adaptive
    "reprioritize_based_on_progress",
    "select_features_maximizing_info",
    "slack_time_analysis",
    "spec_completeness_likelihood",
    "suggest_parallel_work",
    "suggest_task_ordering",
    "top_n_features",
    "uncertainty_reduction_rate",
    "wasserstein_distance",
]

__version__ = "0.0.25"
