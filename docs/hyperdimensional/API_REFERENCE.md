# Hyperdimensional Information Theory API Reference

**Version 1.0** | **Last Updated**: 2025-12-21

Complete API documentation for the hyperdimensional information theory toolkit.

---

## Core Classes

### HyperdimensionalEmbedding

Creates and manages semantic embeddings for RDF entities.

```python
class HyperdimensionalEmbedding:
    """Generate hyperdimensional embeddings for semantic entities."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        cache_dir: Path = Path(".specify/embeddings")
    ):
        """Initialize embedding generator.

        Args:
            model_name: SentenceTransformer model identifier
            dimension: Embedding dimensionality (default: 384)
            cache_dir: Directory for persistent embedding cache

        Example:
            embedder = HyperdimensionalEmbedding(model_name="all-mpnet-base-v2")
        """

    def embed(self, text: str, normalize: bool = True) -> np.ndarray:
        """Generate embedding for text.

        Args:
            text: Input text to embed
            normalize: Whether to L2-normalize embedding (default: True)

        Returns:
            np.ndarray: Embedding vector of shape (dimension,)

        Example:
            emb = embedder.embed("Initialize RDF specification project")
            assert emb.shape == (384,)
            assert np.linalg.norm(emb) == 1.0  # Normalized
        """

    def embed_entity(self, entity_uri: str, graph: rdflib.Graph) -> np.ndarray:
        """Embed RDF entity by extracting its description.

        Args:
            entity_uri: URI of RDF entity
            graph: RDF graph containing entity

        Returns:
            np.ndarray: Entity embedding

        Example:
            g = rdflib.Graph()
            g.parse("ontology/cli-commands.ttl")
            emb = embedder.embed_entity("http://.../InitCommand", g)
        """

    def batch_embed(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts in batch (more efficient).

        Args:
            texts: List of input texts

        Returns:
            np.ndarray: Embeddings of shape (len(texts), dimension)

        Example:
            texts = ["Initialize project", "Check dependencies", "Show version"]
            embeddings = embedder.batch_embed(texts)
            assert embeddings.shape == (3, 384)
        """
```

### SemanticSpace

Manages hyperdimensional semantic space for RDF ontology.

```python
class SemanticSpace:
    """Hyperdimensional semantic space for ontology entities."""

    def __init__(self, ontology_path: str, embedder: HyperdimensionalEmbedding):
        """Initialize semantic space from RDF ontology.

        Args:
            ontology_path: Path to RDF ontology file (Turtle format)
            embedder: HyperdimensionalEmbedding instance

        Example:
            embedder = HyperdimensionalEmbedding()
            space = SemanticSpace("ontology/cli-commands.ttl", embedder)
        """

    def embed_all_entities(self, entity_type: Optional[str] = None) -> Dict[str, np.ndarray]:
        """Embed all entities of given type (or all entities if None).

        Args:
            entity_type: RDF class URI to filter entities (optional)

        Returns:
            Dict mapping entity URIs to embeddings

        Example:
            # Embed all CLI commands
            embeddings = space.embed_all_entities("http://.../CLICommand")
            print(f"Embedded {len(embeddings)} commands")
        """

    def similarity(self, entity1: str, entity2: str) -> float:
        """Compute semantic similarity between two entities.

        Args:
            entity1: URI of first entity
            entity2: URI of second entity

        Returns:
            float: Cosine similarity in [0, 1]

        Example:
            sim = space.similarity("http://.../InitCommand",
                                   "http://.../CheckCommand")
            print(f"Similarity: {sim:.3f}")  # 0.782
        """

    def find_similar(
        self,
        entity_uri: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Find K most similar entities above threshold.

        Args:
            entity_uri: Query entity URI
            top_k: Number of results to return
            threshold: Minimum similarity score

        Returns:
            List of (entity_uri, similarity) tuples, sorted descending

        Example:
            similar = space.find_similar("http://.../DepsCommand", top_k=3)
            for uri, sim in similar:
                print(f"{uri}: {sim:.3f}")
        """

    def cluster_entities(
        self,
        entity_type: str,
        n_clusters: int = 5,
        method: str = "kmeans"
    ) -> Dict[str, int]:
        """Cluster entities of given type.

        Args:
            entity_type: RDF class URI to cluster
            n_clusters: Number of clusters
            method: Clustering algorithm ("kmeans", "hierarchical", "dbscan")

        Returns:
            Dict mapping entity URIs to cluster IDs

        Example:
            clusters = space.cluster_entities("http://.../Feature", n_clusters=3)
            # Result: {"http://.../Feature1": 0, "http://.../Feature2": 1, ...}
        """
```

### InformationMetrics

Compute information-theoretic metrics on distributions.

```python
class InformationMetrics:
    """Information theory metrics for specification analysis."""

    @staticmethod
    def shannon_entropy(probabilities: List[float]) -> float:
        """Compute Shannon entropy H(X) = -Σ p(x) log₂ p(x).

        Args:
            probabilities: Probability distribution (must sum to 1)

        Returns:
            float: Entropy in bits

        Example:
            # Uniform distribution over 4 outcomes
            H = InformationMetrics.shannon_entropy([0.25, 0.25, 0.25, 0.25])
            assert H == 2.0  # log₂(4)
        """

    @staticmethod
    def kl_divergence(P: Dict, Q: Dict) -> float:
        """Compute KL divergence D_KL(P || Q).

        Args:
            P: True distribution (dict mapping outcomes to probabilities)
            Q: Approximate distribution

        Returns:
            float: KL divergence in bits (≥ 0)

        Example:
            P = {"A": 0.5, "B": 0.5}
            Q = {"A": 0.8, "B": 0.2}
            divergence = InformationMetrics.kl_divergence(P, Q)
            print(f"Divergence: {divergence:.3f} bits")
        """

    @staticmethod
    def mutual_information(X: pd.Series, Y: pd.Series) -> float:
        """Compute mutual information I(X; Y).

        Args:
            X: First random variable (pandas Series)
            Y: Second random variable

        Returns:
            float: Mutual information in bits

        Example:
            import pandas as pd
            X = pd.Series([0, 0, 1, 1, 0, 1])
            Y = pd.Series([0, 0, 1, 1, 1, 1])
            mi = InformationMetrics.mutual_information(X, Y)
            print(f"I(X; Y) = {mi:.3f} bits")
        """

    @staticmethod
    def information_gain(
        data: pd.DataFrame,
        target_col: str,
        feature_col: str
    ) -> float:
        """Compute information gain of feature for predicting target.

        Args:
            data: Dataset
            target_col: Target variable column name
            feature_col: Feature column name

        Returns:
            float: Information gain in bits

        Example:
            df = pd.DataFrame({
                "satisfaction": ["high", "low", "high", "low"],
                "speed": ["fast", "slow", "fast", "slow"]
            })
            ig = InformationMetrics.information_gain(df, "satisfaction", "speed")
        """

    @staticmethod
    def conditional_entropy(X: pd.Series, Y: pd.Series) -> float:
        """Compute conditional entropy H(X|Y).

        Args:
            X: Target variable
            Y: Conditioning variable

        Returns:
            float: Conditional entropy in bits

        Example:
            H_cond = InformationMetrics.conditional_entropy(X, Y)
            # Interpretation: Uncertainty in X after observing Y
        """
```

### ReasoningEngine

Semantic reasoning over hyperdimensional spaces.

```python
class ReasoningEngine:
    """Semantic reasoning in hyperdimensional space."""

    def __init__(self, semantic_space: SemanticSpace):
        """Initialize reasoning engine.

        Args:
            semantic_space: SemanticSpace instance
        """

    def answer_query(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float, str]]:
        """Answer natural language query using semantic search.

        Args:
            query: Natural language question
            top_k: Number of results

        Returns:
            List of (entity_uri, relevance_score, explanation) tuples

        Example:
            results = engine.answer_query(
                "Which command validates dependencies?",
                top_k=3
            )
            for uri, score, explanation in results:
                print(f"{uri}: {score:.3f} - {explanation}")
        """

    def find_analogies(
        self,
        entity_a: str,
        entity_b: str,
        entity_c: str
    ) -> List[Tuple[str, float]]:
        """Find entity D such that A:B :: C:D (analogy reasoning).

        Args:
            entity_a: First entity URI
            entity_b: Second entity URI
            entity_c: Third entity URI

        Returns:
            List of (candidate_d, confidence) tuples

        Example:
            # If InitCommand:CheckCommand :: DepsCommand:?
            analogies = engine.find_analogies(
                "http://.../InitCommand",
                "http://.../CheckCommand",
                "http://.../DepsCommand"
            )
            # Expected: ValidationCommand (deps validation is to deps as check is to init)
        """

    def detect_contradictions(
        self,
        specification_uri: str
    ) -> List[Tuple[str, str, str]]:
        """Detect contradictory requirements in specification.

        Args:
            specification_uri: URI of specification to analyze

        Returns:
            List of (req1_uri, req2_uri, contradiction_explanation) tuples

        Example:
            contradictions = engine.detect_contradictions("http://.../InitSpec")
            if contradictions:
                print(f"Found {len(contradictions)} contradictions!")
                for r1, r2, explanation in contradictions:
                    print(f"  {r1} contradicts {r2}: {explanation}")
        """

    def recommend_features(
        self,
        job_uri: str,
        outcome_uri: str,
        top_k: int = 5
    ) -> List[Tuple[str, float, Dict]]:
        """Recommend features for a JTBD job and desired outcome.

        Args:
            job_uri: JTBD job URI
            outcome_uri: Desired outcome URI
            top_k: Number of recommendations

        Returns:
            List of (feature_uri, confidence, metadata) tuples

        Example:
            recommendations = engine.recommend_features(
                "http://.../Job_OD_ModelDomainKnowledge",
                "http://.../Outcome_OD_1",  # Minimize time to create spec
                top_k=3
            )
        """
```

### ValidationFramework

Validate specifications using HDIT principles.

```python
class ValidationFramework:
    """Comprehensive specification validation."""

    def __init__(
        self,
        semantic_space: SemanticSpace,
        metrics: InformationMetrics
    ):
        """Initialize validation framework.

        Args:
            semantic_space: SemanticSpace instance
            metrics: InformationMetrics instance
        """

    def validate_specification(
        self,
        spec_path: str
    ) -> ValidationResult:
        """Comprehensive validation of RDF specification.

        Args:
            spec_path: Path to specification TTL file

        Returns:
            ValidationResult with scores and recommendations

        Example:
            result = validator.validate_specification("memory/feature.ttl")
            print(f"Overall score: {result.score}/100")
            print(f"Status: {result.status}")  # PASS, WARN, FAIL
            for issue in result.issues:
                print(f"  - {issue.severity}: {issue.description}")
        """

    def check_completeness(
        self,
        spec_uri: str,
        required_dimensions: List[str]
    ) -> CompletenessReport:
        """Check if specification covers all required dimensions.

        Args:
            spec_uri: Specification URI
            required_dimensions: List of dimension URIs to check

        Returns:
            CompletenessReport with coverage metrics

        Example:
            report = validator.check_completeness(
                "http://.../InitFeatureSpec",
                required_dimensions=[
                    "http://.../RequirementDimension",
                    "http://.../TestCoverageDimension",
                    "http://.../PerformanceDimension",
                ]
            )
            print(f"Coverage: {report.coverage_percentage:.1f}%")
        """

    def measure_ambiguity(
        self,
        requirement_uris: List[str]
    ) -> Dict[str, float]:
        """Measure ambiguity of requirements using entropy.

        Args:
            requirement_uris: List of requirement URIs to analyze

        Returns:
            Dict mapping requirement URIs to entropy scores

        Example:
            ambiguity = validator.measure_ambiguity([
                "http://.../Req1",
                "http://.../Req2",
            ])
            for req, entropy in ambiguity.items():
                if entropy > 1.5:
                    print(f"⚠️  High ambiguity: {req} (H={entropy:.2f} bits)")
        """

    def detect_drift(
        self,
        spec_uri: str,
        implementation_uri: str
    ) -> DriftReport:
        """Detect specification-implementation drift.

        Args:
            spec_uri: Specification URI
            implementation_uri: Implementation URI

        Returns:
            DriftReport with KL divergence and specific drift points

        Example:
            drift = validator.detect_drift(
                "http://.../InitFeatureSpec",
                "http://.../InitCommandImpl"
            )
            if drift.kl_divergence > 0.3:
                print(f"⚠️  Significant drift: {drift.kl_divergence:.3f} bits")
                for point in drift.drift_points:
                    print(f"  - {point.dimension}: {point.description}")
        """
```

---

## Key Functions

### embed_entity

```python
def embed_entity(
    entity_uri: str,
    graph: rdflib.Graph,
    embedder: HyperdimensionalEmbedding
) -> np.ndarray:
    """Convenience function to embed RDF entity.

    Args:
        entity_uri: URI of entity to embed
        graph: RDF graph containing entity
        embedder: Embedding generator instance

    Returns:
        np.ndarray: Entity embedding vector

    Example:
        g = rdflib.Graph()
        g.parse("ontology/cli-commands.ttl")
        embedder = HyperdimensionalEmbedding()

        emb = embed_entity("http://.../InitCommand", g, embedder)
        print(f"Embedding shape: {emb.shape}")  # (384,)
    """
```

### compute_entropy

```python
def compute_entropy(distribution: Union[List[float], Dict[Any, float]]) -> float:
    """Compute Shannon entropy of distribution.

    Args:
        distribution: Probability distribution (list or dict of probabilities)

    Returns:
        float: Entropy in bits

    Raises:
        ValueError: If probabilities don't sum to 1.0 (within tolerance)

    Example:
        # Uniform distribution
        H = compute_entropy([0.25, 0.25, 0.25, 0.25])
        assert H == 2.0

        # Non-uniform distribution
        H2 = compute_entropy([0.7, 0.2, 0.1])
        assert H2 < 2.0  # Less uncertain
    """
```

### calculate_mutual_information

```python
def calculate_mutual_information(
    X: Union[pd.Series, np.ndarray],
    Y: Union[pd.Series, np.ndarray],
    bins: Optional[int] = None
) -> float:
    """Calculate mutual information I(X; Y).

    Args:
        X: First variable (discrete or continuous)
        Y: Second variable
        bins: Number of bins for continuous variables (optional)

    Returns:
        float: Mutual information in bits

    Example:
        # Discrete variables
        X = pd.Series([0, 0, 1, 1, 0, 1])
        Y = pd.Series([0, 0, 1, 1, 1, 1])
        mi = calculate_mutual_information(X, Y)

        # Continuous variables (discretized)
        X_cont = np.random.randn(1000)
        Y_cont = X_cont + np.random.randn(1000) * 0.5
        mi_cont = calculate_mutual_information(X_cont, Y_cont, bins=10)
    """
```

### find_similar_entities

```python
def find_similar_entities(
    entity_uri: str,
    semantic_space: SemanticSpace,
    distance_threshold: float = 0.7,
    top_k: int = 10
) -> List[Tuple[str, float]]:
    """Find entities similar to query entity.

    Args:
        entity_uri: Query entity URI
        semantic_space: Semantic space containing embeddings
        distance_threshold: Minimum cosine similarity (0-1)
        top_k: Maximum number of results

    Returns:
        List of (entity_uri, similarity) tuples, sorted by similarity

    Example:
        similar = find_similar_entities(
            "http://.../DepsCommand",
            space,
            distance_threshold=0.6,
            top_k=5
        )
        for uri, sim in similar:
            print(f"{uri}: {sim:.3f}")
    """
```

### recommend_features

```python
def recommend_features(
    objective: str,
    context: Dict[str, Any],
    reasoning_engine: ReasoningEngine,
    top_k: int = 5
) -> List[FeatureRecommendation]:
    """Recommend features to achieve objective.

    Args:
        objective: Natural language objective or JTBD job URI
        context: Additional context (persona, constraints, etc.)
        reasoning_engine: ReasoningEngine instance
        top_k: Number of recommendations

    Returns:
        List of FeatureRecommendation objects

    Example:
        recommendations = recommend_features(
            objective="Reduce time to initialize projects",
            context={
                "persona": "http://.../Persona_OntologyDesigner",
                "current_time": 360,  # seconds
                "target_time": 60,
                "priority": "high"
            },
            reasoning_engine=engine,
            top_k=3
        )

        for rec in recommendations:
            print(f"Feature: {rec.feature_uri}")
            print(f"Confidence: {rec.confidence:.2f}")
            print(f"Expected impact: {rec.estimated_impact}")
            print(f"Rationale: {rec.rationale}")
            print()
    """
```

---

## Data Structures

### SemanticVector

```python
@dataclass(frozen=True)
class SemanticVector:
    """Hyperdimensional semantic vector."""

    values: np.ndarray          # D-dimensional vector
    entity_uri: str             # Source entity URI
    dimension: int              # Dimensionality (D)
    normalized: bool            # Whether L2-normalized
    metadata: Dict[str, Any]    # Additional metadata

    def similarity(self, other: 'SemanticVector') -> float:
        """Compute cosine similarity with another vector."""

    def distance(self, other: 'SemanticVector', metric: str = "cosine") -> float:
        """Compute distance using specified metric (cosine, euclidean, manhattan)."""

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""

    @classmethod
    def from_dict(cls, data: Dict) -> 'SemanticVector':
        """Deserialize from dictionary."""
```

### QueryResult

```python
@dataclass
class QueryResult:
    """Result from semantic query."""

    entity_uri: str             # Matched entity URI
    relevance_score: float      # Relevance to query [0, 1]
    explanation: str            # Human-readable explanation
    metadata: Dict[str, Any]    # Additional information

    def __lt__(self, other: 'QueryResult') -> bool:
        """Enable sorting by relevance score."""
        return self.relevance_score < other.relevance_score
```

### MetricSet

```python
@dataclass
class MetricSet:
    """Collection of information-theoretic metrics."""

    entropy: Dict[str, float]           # Entropy scores by dimension
    kl_divergence: Dict[str, float]     # KL divergences
    mutual_information: Dict[Tuple[str, str], float]  # MI between dimension pairs
    information_gain: Dict[str, float]  # IG scores

    def summary_statistics(self) -> Dict[str, float]:
        """Compute summary statistics across all metrics."""

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for analysis."""

    def visualize(self, output_path: Optional[str] = None) -> None:
        """Generate visualization of metrics."""
```

### RecommendationSet

```python
@dataclass
class RecommendationSet:
    """Ranked feature recommendations."""

    recommendations: List[FeatureRecommendation]
    query_objective: str
    query_context: Dict[str, Any]
    generated_at: datetime

    def top(self, k: int) -> List[FeatureRecommendation]:
        """Get top K recommendations."""

    def filter_by_confidence(self, min_confidence: float) -> List[FeatureRecommendation]:
        """Filter by minimum confidence threshold."""

    def to_markdown(self) -> str:
        """Generate Markdown report of recommendations."""

@dataclass
class FeatureRecommendation:
    """Single feature recommendation."""

    feature_uri: str
    feature_name: str
    confidence: float               # [0, 1]
    estimated_impact: float         # Expected improvement
    rationale: str                  # Why recommended
    prerequisites: List[str]        # Required dependencies
    estimated_effort: str           # "low", "medium", "high"
    priority_score: float           # Composite priority
```

---

*This API reference provides complete type signatures, parameter documentation, return values, and usage examples for all core classes and functions in the hyperdimensional toolkit.*
