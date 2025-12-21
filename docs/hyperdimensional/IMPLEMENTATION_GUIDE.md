# Hyperdimensional Information Theory: Practical Implementation Guide

**Version 1.0** | **Last Updated**: 2025-12-21 | **Audience**: Developers, Architects, Data Scientists

This guide provides step-by-step instructions for implementing hyperdimensional information theory calculus in spec-kit projects.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Creating Embeddings](#creating-embeddings)
- [Information Analysis](#information-analysis)
- [Decision Making](#decision-making)
- [Validation](#validation)
- [Integration Patterns](#integration-patterns)

---

<a name="getting-started"></a>
## Getting Started

### Installing Hyperdimensional Toolkit

```bash
# Core dependencies
uv add sentence-transformers  # Text embeddings
uv add rdflib                 # RDF graph operations
uv add numpy scipy            # Numerical operations
uv add scikit-learn           # ML utilities
uv add pandas                 # Data manipulation

# Optional: Graph embeddings
uv add node2vec networkx

# Optional: Visualization
uv add matplotlib seaborn plotly
```

### Setting Up Embeddings Database

```python
# src/specify_cli/hyperdimensional/__init__.py
from pathlib import Path
import pickle
from typing import Dict
import numpy as np

class EmbeddingsDB:
    """Persistent storage for entity embeddings."""

    def __init__(self, db_path: Path = Path(".specify/embeddings.pkl")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.embeddings: Dict[str, np.ndarray] = self._load()

    def _load(self) -> Dict[str, np.ndarray]:
        """Load embeddings from disk."""
        if self.db_path.exists():
            with open(self.db_path, 'rb') as f:
                return pickle.load(f)
        return {}

    def save(self) -> None:
        """Persist embeddings to disk."""
        with open(self.db_path, 'wb') as f:
            pickle.dump(self.embeddings, f)

    def get(self, entity_uri: str) -> np.ndarray | None:
        """Retrieve embedding for entity."""
        return self.embeddings.get(entity_uri)

    def set(self, entity_uri: str, embedding: np.ndarray) -> None:
        """Store embedding for entity."""
        self.embeddings[entity_uri] = embedding
        self.save()

    def contains(self, entity_uri: str) -> bool:
        """Check if entity has embedding."""
        return entity_uri in self.embeddings
```

### Initializing Semantic Space

```python
# src/specify_cli/hyperdimensional/semantic_space.py
from sentence_transformers import SentenceTransformer
import rdflib
import numpy as np
from typing import List, Tuple

class SemanticSpace:
    """Hyperdimensional semantic space for spec-kit entities."""

    def __init__(self, ontology_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.graph = rdflib.Graph()
        self.graph.parse(ontology_path, format="turtle")
        self.embeddings_db = EmbeddingsDB()
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_entity(self, entity_uri: str, force_recompute: bool = False) -> np.ndarray:
        """Embed RDF entity in semantic space."""
        # Check cache
        if not force_recompute and self.embeddings_db.contains(entity_uri):
            return self.embeddings_db.get(entity_uri)

        # Extract description
        description = self._extract_description(entity_uri)

        # Compute embedding
        embedding = self.model.encode(description, normalize_embeddings=True)

        # Cache and return
        self.embeddings_db.set(entity_uri, embedding)
        return embedding

    def _extract_description(self, entity_uri: str) -> str:
        """Extract natural language description from RDF."""
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sk: <http://github.com/github/spec-kit#>
        PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>

        SELECT ?label ?comment ?description ?jobDescription
        WHERE {{
            <{entity_uri}> rdfs:label ?label .
            OPTIONAL {{ <{entity_uri}> rdfs:comment ?comment }}
            OPTIONAL {{ <{entity_uri}> sk:documentDescription ?description }}
            OPTIONAL {{ <{entity_uri}> jtbd:jobDescription ?jobDescription }}
        }}
        """

        results = list(self.graph.query(query))
        if not results:
            return entity_uri  # Fallback to URI

        parts = []
        row = results[0]
        if row.label:
            parts.append(str(row.label))
        if row.comment:
            parts.append(str(row.comment))
        if row.description:
            parts.append(str(row.description))
        if row.jobDescription:
            parts.append(str(row.jobDescription))

        return " ".join(parts) if parts else entity_uri

    def find_similar(self, entity_uri: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find K most similar entities to given entity."""
        # Get query embedding
        query_emb = self.embed_entity(entity_uri)

        # Compute similarities to all cached entities
        similarities = []
        for other_uri in self.embeddings_db.embeddings.keys():
            if other_uri == entity_uri:
                continue  # Skip self

            other_emb = self.embeddings_db.get(other_uri)
            sim = self._cosine_similarity(query_emb, other_emb)
            similarities.append((other_uri, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### Loading Spec-Kit Entities

```python
# Example: Embed all CLI commands
from pathlib import Path

# Initialize semantic space
space = SemanticSpace("ontology/cli-commands.ttl")

# Query for all CLI commands
query = """
PREFIX sk: <http://github.com/github/spec-kit#>

SELECT ?command
WHERE {
    ?command a sk:CLICommand .
}
"""

results = space.graph.query(query)

# Embed all commands
for row in results:
    command_uri = str(row.command)
    embedding = space.embed_entity(command_uri)
    print(f"Embedded {command_uri}: shape {embedding.shape}")

# Example output:
# Embedded http://github.com/github/spec-kit#InitCommand: shape (384,)
# Embedded http://github.com/github/spec-kit#CheckCommand: shape (384,)
# Embedded http://github.com/github/spec-kit#VersionCommand: shape (384,)
```

---

<a name="creating-embeddings"></a>
## Creating Embeddings

### Step-by-Step: Embedding a New Command

**Scenario**: You're adding a new `specify deps` command.

**Step 1: Define RDF Specification**

```turtle
# ontology/cli-commands-updated.ttl
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

sk:DepsCommand a sk:CLICommand ;
    rdfs:label "Dependency Management Command" ;
    rdfs:comment "Analyze and manage project dependencies for spec-kit projects" ;
    sk:documentDescription "The deps command validates dependency configurations, detects version conflicts, and generates dependency graphs for RDF-first projects." ;
    sk:complexity 0.6 ;
    sk:testCoverage 88.5 ;
    sk:dependencyCount 5 .
```

**Step 2: Embed in Semantic Space**

```python
# Reload graph with updated ontology
space = SemanticSpace("ontology/cli-commands-updated.ttl")

# Embed new command
deps_embedding = space.embed_entity("http://github.com/github/spec-kit#DepsCommand")

print(f"Deps command embedding: {deps_embedding.shape}")  # (384,)
print(f"First 5 dimensions: {deps_embedding[:5]}")

# Example output:
# Deps command embedding: (384,)
# First 5 dimensions: [ 0.123 -0.456  0.789 -0.234  0.567]
```

**Step 3: Test Embedding Quality**

```python
# Verify similarity to related commands
similar = space.find_similar("http://github.com/github/spec-kit#DepsCommand", top_k=3)

print("Most similar commands:")
for uri, similarity in similar:
    print(f"  {uri}: {similarity:.3f}")

# Expected output:
# Most similar commands:
#   .../spec-kit#CheckCommand: 0.782  (both validate/check things)
#   .../spec-kit#InitCommand: 0.651   (both deal with project setup)
#   .../spec-kit#VersionCommand: 0.423 (less related)
```

### Testing Embeddings for Correctness

**Sanity Check 1: Self-Similarity**

```python
def test_self_similarity(space: SemanticSpace, entity_uri: str):
    """Entity should be maximally similar to itself."""
    emb1 = space.embed_entity(entity_uri)
    emb2 = space.embed_entity(entity_uri, force_recompute=True)

    sim = space._cosine_similarity(emb1, emb2)
    assert sim > 0.99, f"Self-similarity {sim} too low!"
    print(f"✓ Self-similarity: {sim:.4f}")

test_self_similarity(space, "http://github.com/github/spec-kit#DepsCommand")
```

**Sanity Check 2: Semantic Consistency**

```python
def test_semantic_consistency(space: SemanticSpace):
    """Related concepts should have high similarity."""
    # Commands that manage projects should cluster together
    init_emb = space.embed_entity(".../InitCommand")
    deps_emb = space.embed_entity(".../DepsCommand")
    check_emb = space.embed_entity(".../CheckCommand")

    # Project management commands should be similar
    sim_init_deps = space._cosine_similarity(init_emb, deps_emb)
    sim_init_check = space._cosine_similarity(init_emb, check_emb)
    sim_deps_check = space._cosine_similarity(deps_emb, check_emb)

    assert sim_init_deps > 0.5, "init-deps similarity too low!"
    assert sim_init_check > 0.5, "init-check similarity too low!"
    assert sim_deps_check > 0.6, "deps-check similarity too low!"

    print(f"✓ init-deps: {sim_init_deps:.3f}")
    print(f"✓ init-check: {sim_init_check:.3f}")
    print(f"✓ deps-check: {sim_deps_check:.3f}")

test_semantic_consistency(space)
```

### Measuring Embedding Quality

**Intrinsic Evaluation: Dimensionality Check**

```python
from sklearn.decomposition import PCA

def measure_embedding_quality(embeddings: np.ndarray, target_variance: float = 0.95):
    """Measure intrinsic dimensionality of embeddings."""
    pca = PCA()
    pca.fit(embeddings)

    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    intrinsic_dim = np.argmax(cumulative_variance >= target_variance) + 1

    print(f"Intrinsic dimensionality: {intrinsic_dim} (captures {target_variance*100}% variance)")
    print(f"Total dimensions: {embeddings.shape[1]}")
    print(f"Compression ratio: {intrinsic_dim / embeddings.shape[1]:.2%}")

    return intrinsic_dim

# Collect all embeddings
all_embeddings = np.array([
    space.embeddings_db.get(uri)
    for uri in space.embeddings_db.embeddings.keys()
])

intrinsic_dim = measure_embedding_quality(all_embeddings)
# Example output:
# Intrinsic dimensionality: 87 (captures 95% variance)
# Total dimensions: 384
# Compression ratio: 22.66%
```

**Extrinsic Evaluation: Downstream Task Performance**

```python
def test_downstream_task(space: SemanticSpace):
    """Test embedding quality on similarity ranking task."""
    # Ground truth: manually labeled similar pairs
    similar_pairs = [
        ("InitCommand", "CheckCommand", 0.8),   # Should be similar
        ("DepsCommand", "VersionCommand", 0.3), # Should be dissimilar
        ("InitCommand", "DepsCommand", 0.7),    # Moderately similar
    ]

    errors = []
    for cmd1, cmd2, expected_sim in similar_pairs:
        uri1 = f"http://github.com/github/spec-kit#{cmd1}"
        uri2 = f"http://github.com/github/spec-kit#{cmd2}"

        emb1 = space.embed_entity(uri1)
        emb2 = space.embed_entity(uri2)
        actual_sim = space._cosine_similarity(emb1, emb2)

        error = abs(actual_sim - expected_sim)
        errors.append(error)

        print(f"{cmd1} - {cmd2}: expected={expected_sim:.2f}, actual={actual_sim:.2f}, error={error:.2f}")

    mean_error = np.mean(errors)
    print(f"\nMean Absolute Error: {mean_error:.3f}")
    assert mean_error < 0.2, "Embedding quality too low!"

test_downstream_task(space)
```

### Debugging Embedding Issues

**Issue 1: All Embeddings Collapse to Same Point**

**Symptoms**: All similarities > 0.95

**Diagnosis**:
```python
def diagnose_collapse(embeddings: np.ndarray):
    """Check if embeddings have collapsed."""
    # Compute pairwise similarities
    from sklearn.metrics.pairwise import cosine_similarity

    sims = cosine_similarity(embeddings)
    # Set diagonal to 0 (ignore self-similarity)
    np.fill_diagonal(sims, 0)

    mean_sim = sims.mean()
    std_sim = sims.std()

    print(f"Mean pairwise similarity: {mean_sim:.3f}")
    print(f"Std pairwise similarity: {std_sim:.3f}")

    if mean_sim > 0.9 and std_sim < 0.05:
        print("⚠️  WARNING: Embeddings have collapsed!")
        print("Possible causes:")
        print("- Text descriptions too similar")
        print("- Model not properly loaded")
        print("- Normalization issue")
    else:
        print("✓ Embeddings have healthy diversity")

diagnose_collapse(all_embeddings)
```

**Solution**:
1. Enrich RDF descriptions with more specific details
2. Use domain-specific fine-tuning
3. Add feature dimensions (complexity, coverage, etc.)

**Issue 2: Semantically Similar Entities Have Low Similarity**

**Symptoms**: Expected similar pairs score < 0.5

**Diagnosis**:
```python
def diagnose_poor_similarity(space: SemanticSpace, entity1: str, entity2: str):
    """Debug why two entities have low similarity."""
    desc1 = space._extract_description(entity1)
    desc2 = space._extract_description(entity2)

    print(f"Entity 1: {entity1}")
    print(f"Description: {desc1}")
    print()
    print(f"Entity 2: {entity2}")
    print(f"Description: {desc2}")
    print()

    # Check token overlap
    tokens1 = set(desc1.lower().split())
    tokens2 = set(desc2.lower().split())

    jaccard = len(tokens1 & tokens2) / len(tokens1 | tokens2)
    print(f"Token overlap (Jaccard): {jaccard:.3f}")

    if jaccard < 0.1:
        print("⚠️  Very low token overlap - descriptions may be too different")

diagnose_poor_similarity(space,
                         "http://github.com/github/spec-kit#InitCommand",
                         "http://github.com/github/spec-kit#CheckCommand")
```

**Solution**:
1. Add more shared vocabulary to RDF descriptions
2. Use hierarchical embeddings (class + instance)
3. Incorporate relationship embeddings (not just text)

---

<a name="information-analysis"></a>
## Information Analysis

### Computing Entropy for a Specification

**Example**: Measure ambiguity in `specify init` requirements

```python
# src/specify_cli/hyperdimensional/information_theory.py
import numpy as np
from typing import Dict, List

def shannon_entropy(probabilities: List[float]) -> float:
    """Compute Shannon entropy H(X) = -Σ p(x) log₂ p(x)."""
    p = np.array([p for p in probabilities if p > 0])
    if len(p) == 0:
        return 0.0
    return -np.sum(p * np.log2(p))

def measure_specification_ambiguity(spec_path: str) -> Dict[str, float]:
    """Analyze specification for ambiguous requirements."""
    import rdflib

    g = rdflib.Graph()
    g.parse(spec_path, format="turtle")

    # Query: How many interpretations does each requirement have?
    query = """
    PREFIX sk: <http://github.com/github/spec-kit#>

    SELECT ?req (GROUP_CONCAT(?interpretation; separator="||") as ?interpretations)
    WHERE {
        ?req a sk:Requirement ;
             sk:requirementText ?text .
        OPTIONAL {
            ?interpretation sk:interpretsRequirement ?req ;
                            sk:interpretationText ?interpText .
        }
    }
    GROUP BY ?req
    """

    results = {}
    for row in g.query(query):
        req_uri = str(row.req)
        interpretations = str(row.interpretations).split("||") if row.interpretations else [req_uri]

        # Uniform distribution over interpretations (no prior knowledge)
        n = len(interpretations)
        probs = [1/n] * n

        entropy = shannon_entropy(probs)
        results[req_uri] = entropy

    return results

# Usage:
ambiguities = measure_specification_ambiguity("memory/jtbd-customer-jobs.ttl")

for req, entropy in sorted(ambiguities.items(), key=lambda x: x[1], reverse=True):
    status = "✗" if entropy > 1.5 else "⚠️ " if entropy > 0.5 else "✓"
    print(f"{status} {req}: {entropy:.2f} bits")

# Example output:
# ✗ http://.../Req1: 2.32 bits (HIGH ambiguity - 5 interpretations)
# ⚠️  http://.../Req2: 0.81 bits (MODERATE - 2 interpretations)
# ✓ http://.../Req3: 0.00 bits (CLEAR - 1 interpretation)
```

### Analyzing Mutual Information Between Features

**Example**: Detect feature coupling

```python
import pandas as pd

def analyze_feature_coupling(change_log_path: str) -> pd.DataFrame:
    """Compute mutual information between features based on change history."""
    # Load change log (commits × features changed)
    changes = pd.read_csv(change_log_path)
    # Format: commit_sha, init_changed, check_changed, deps_changed, ...

    features = [col for col in changes.columns if col.endswith("_changed")]

    coupling_matrix = pd.DataFrame(index=features, columns=features, dtype=float)

    for f1 in features:
        for f2 in features:
            if f1 == f2:
                coupling_matrix.loc[f1, f2] = 1.0  # Self-coupling
            else:
                # Compute mutual information
                mi = mutual_information(changes[f1], changes[f2])
                coupling_matrix.loc[f1, f2] = mi

    return coupling_matrix

def mutual_information(X: pd.Series, Y: pd.Series) -> float:
    """Compute I(X; Y)."""
    joint_counts = pd.crosstab(X, Y)
    joint_probs = joint_counts / joint_counts.sum().sum()

    px = joint_probs.sum(axis=1)
    py = joint_probs.sum(axis=0)

    mi = 0.0
    for i in range(len(px)):
        for j in range(len(py)):
            if joint_probs.iloc[i, j] > 0:
                mi += joint_probs.iloc[i, j] * np.log2(
                    joint_probs.iloc[i, j] / (px.iloc[i] * py.iloc[j])
                )
    return mi

# Usage:
coupling = analyze_feature_coupling("data/git_changes.csv")

# Visualize
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 8))
sns.heatmap(coupling, annot=True, fmt=".2f", cmap="YlOrRd")
plt.title("Feature Coupling (Mutual Information)")
plt.show()

# Identify highly coupled pairs
threshold = 0.5
for f1 in coupling.index:
    for f2 in coupling.columns:
        if f1 < f2:  # Avoid duplicates
            mi = coupling.loc[f1, f2]
            if mi > threshold:
                print(f"⚠️  High coupling: {f1} ↔ {f2} (I = {mi:.3f} bits)")
```

### Calculating Information Gain for Feature Selection

**Example**: Which JTBD outcomes drive customer satisfaction?

```python
def calculate_information_gain_jtbd(data_path: str) -> pd.Series:
    """Rank JTBD outcomes by information gain for satisfaction."""
    import pandas as pd
    from scipy.stats import entropy

    # Load data: satisfaction × outcome_metrics
    data = pd.read_csv(data_path)
    # Format: satisfaction, time_to_init, error_rate, test_coverage, ...

    target = "satisfaction"
    features = [col for col in data.columns if col != target]

    # Compute IG for each feature
    information_gains = {}

    # Target entropy
    H_target = entropy(data[target].value_counts(normalize=True), base=2)

    for feature in features:
        # Weighted average entropy after split
        H_conditional = 0.0
        for value in data[feature].unique():
            subset = data[data[feature] == value]
            weight = len(subset) / len(data)
            H_subset = entropy(subset[target].value_counts(normalize=True), base=2)
            H_conditional += weight * H_subset

        # Information gain
        ig = H_target - H_conditional
        information_gains[feature] = ig

    # Sort by IG descending
    return pd.Series(information_gains).sort_values(ascending=False)

# Usage:
ig_results = calculate_information_gain_jtbd("data/jtbd_satisfaction.csv")

print("Feature Importance (Information Gain):")
for feature, ig in ig_results.items():
    priority = "HIGH" if ig > 0.7 else "MEDIUM" if ig > 0.3 else "LOW"
    print(f"  [{priority}] {feature}: {ig:.3f} bits")

# Example output:
# Feature Importance (Information Gain):
#   [HIGH] time_to_init: 0.811 bits
#   [MEDIUM] error_rate: 0.523 bits
#   [MEDIUM] test_coverage: 0.412 bits
#   [LOW] documentation_quality: 0.187 bits
```

### Interpreting Metric Results

**Guideline Table**:

| Metric | Low | Medium | High | Interpretation |
|--------|-----|--------|------|----------------|
| **Entropy (ambiguity)** | < 0.5 | 0.5-1.5 | > 1.5 | High = ambiguous, needs clarification |
| **KL Divergence (drift)** | < 0.1 | 0.1-0.3 | > 0.3 | High = spec/impl misaligned |
| **Mutual Information (coupling)** | < 0.3 | 0.3-0.7 | > 0.7 | High = tightly coupled features |
| **Information Gain (importance)** | < 0.3 | 0.3-0.7 | > 0.7 | High = strong predictor, optimize first |

**Example Report**:

```python
def generate_analysis_report(spec_path: str) -> str:
    """Generate comprehensive information theory analysis report."""
    import rdflib

    g = rdflib.Graph()
    g.parse(spec_path, format="turtle")

    # Measure all metrics
    ambiguity = measure_specification_ambiguity(spec_path)
    # ... (other metrics)

    report = []
    report.append("# Specification Quality Report")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("")

    # Ambiguity section
    avg_ambiguity = np.mean(list(ambiguity.values()))
    report.append(f"## Ambiguity Analysis")
    report.append(f"Average entropy: {avg_ambiguity:.2f} bits")

    if avg_ambiguity < 0.5:
        report.append("✓ Low ambiguity - specifications are clear")
    elif avg_ambiguity < 1.5:
        report.append("⚠️  Moderate ambiguity - some requirements need clarification")
    else:
        report.append("✗ High ambiguity - critical clarity issues")

    # ... (add other sections)

    return "\n".join(report)

# Usage:
report = generate_analysis_report("memory/jtbd-customer-jobs.ttl")
print(report)

# Save to file
with open(".specify/analysis_report.md", "w") as f:
    f.write(report)
```

---

**[Continued in next sections: Decision Making, Validation, Integration Patterns...]**

*This implementation guide is designed to be immediately actionable with copy-paste code examples and real spec-kit integration patterns.*
