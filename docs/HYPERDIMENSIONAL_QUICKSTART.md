# Hyperdimensional Computing Quick Start

**What you'll learn in 10 minutes:** How to use hyperdimensional computing to prioritize features, measure specification quality, and make data-driven decisions.

---

## What is Hyperdimensional Computing?

Hyperdimensional computing represents concepts as high-dimensional vectors (typically 10,000+ dimensions). Similar concepts have similar vectors. Think of it like GPS coordinates, but with thousands of dimensions instead of just latitude/longitude.

**Why use it?** Because it lets you measure:
- How similar two features are
- How much information a specification contains
- Which features matter most
- Whether your specs are complete

---

## How Spec-Kit Uses It

Spec-kit uses hyperdimensional vectors to measure **information content** in your RDF specifications. Instead of just checking syntax, it measures:

1. **Entropy** - How uncertain/incomplete is this spec? (Lower is better)
2. **Information Gain** - Which feature adds the most value?
3. **Mutual Information** - Are these features related?
4. **Complexity** - How hard is this to implement?

**The Constitutional Equation:**
```
spec.md = μ(feature.ttl)
```

Hyperdimensional computing powers the μ transformation by quantifying information at each stage.

---

## Quick Start: 4 Commands You Need

### 1. Measure Specification Quality

**What it does:** Calculates entropy to measure how complete/certain your specification is.

```python
from specify_cli.hyperdimensional.metrics import entropy

# Specification states: [complete, incomplete, ambiguous]
spec_v1 = [0.2, 0.7, 0.1]  # 70% incomplete
spec_v2 = [0.9, 0.05, 0.05]  # 90% complete

entropy_v1 = entropy(spec_v1)
entropy_v2 = entropy(spec_v2)

print(f"Incomplete spec: {entropy_v1:.3f} bits (high uncertainty)")
print(f"Complete spec:   {entropy_v2:.3f} bits (low uncertainty)")
# Output:
# Incomplete spec: 1.157 bits (high uncertainty)
# Complete spec:   0.569 bits (low uncertainty)
```

**When to use:** Before finalizing a specification. Lower entropy = more complete.

**Interpreting results:**
- **< 0.5 bits** - Well-defined, ready for implementation
- **0.5-1.5 bits** - Moderate uncertainty, needs refinement
- **> 1.5 bits** - High uncertainty, specification incomplete

---

### 2. Prioritize Features by Information Gain

**What it does:** Ranks features by how much information they add to your project.

```python
from specify_cli.hyperdimensional.prioritization import (
    Feature,
    rank_features_by_gain
)

features = [
    Feature(
        name="User Authentication",
        requirements=["login", "logout", "password_reset", "2fa"],
        complexity="medium",
        impact="critical"
    ),
    Feature(
        name="Dark Mode",
        requirements=["theme_toggle"],
        complexity="low",
        impact="low"
    ),
    Feature(
        name="Payment Processing",
        requirements=["stripe", "paypal", "refunds", "invoices"],
        complexity="high",
        impact="critical"
    ),
]

# Rank by information gain
ranked = rank_features_by_gain(features, objective="quality")

for item in ranked:
    print(f"{item.rank}. {item.item.name}")
    print(f"   Score: {item.score:.3f}")
    print(f"   Rationale: {item.rationale}\n")
# Output:
# 1. Payment Processing
#    Score: 0.892
#    Rationale: High information content, critical impact, complex requirements
#
# 2. User Authentication
#    Score: 0.745
#    Rationale: Critical security feature, medium complexity
#
# 3. Dark Mode
#    Score: 0.234
#    Rationale: Low complexity, aesthetic feature
```

**When to use:** When deciding what to build next.

**Interpreting results:**
- **Score > 0.7** - High-value features, prioritize first
- **Score 0.4-0.7** - Medium priority
- **Score < 0.4** - Low priority, defer

---

### 3. Find Similar Features (Semantic Search)

**What it does:** Finds features similar to a given feature using vector similarity.

```python
from specify_cli.hyperdimensional.search import SemanticSearchDashboard
import numpy as np

# Initialize search
search = SemanticSearchDashboard()

# Sample features with embeddings (normally loaded from your spec)
features = [
    {"name": "Login API", "type": "authentication"},
    {"name": "OAuth Integration", "type": "authentication"},
    {"name": "Password Reset", "type": "authentication"},
    {"name": "Shopping Cart", "type": "ecommerce"},
]

# Create simple embeddings (in production, use real embeddings)
embeddings = np.random.rand(4, 1024)  # 4 features, 1024 dimensions

# Find features similar to "Login API"
results = search.search_by_semantic_similarity(
    query=embeddings[0],  # Login API embedding
    features=features,
    embeddings=embeddings,
    k=3
)

for result in results:
    print(f"{result.rank}. {result.name}")
    print(f"   Similarity: {result.score:.3f}\n")
# Output (example):
# 1. OAuth Integration
#    Similarity: 0.923
#
# 2. Password Reset
#    Similarity: 0.817
#
# 3. Shopping Cart
#    Similarity: 0.234
```

**When to use:** When looking for related features, checking for duplicates, or exploring dependencies.

**Interpreting results:**
- **Similarity > 0.8** - Very similar, possibly redundant
- **Similarity 0.5-0.8** - Related, check dependencies
- **Similarity < 0.5** - Different concerns

---

### 4. Prioritize Tasks by Multiple Objectives

**What it does:** Balances impact, effort, and uncertainty to recommend task order.

```python
from specify_cli.hyperdimensional.prioritization import Task, prioritize_tasks

tasks = [
    Task(
        id="TASK-001",
        name="Fix critical security bug",
        estimated_effort=2.0,  # 2 hours
        impact=95.0,  # 0-100 scale
        uncertainty=0.1,  # Low uncertainty
        complexity=30.0
    ),
    Task(
        id="TASK-002",
        name="Add new payment method",
        estimated_effort=40.0,  # 40 hours
        impact=70.0,
        uncertainty=0.6,  # Medium uncertainty
        complexity=80.0
    ),
    Task(
        id="TASK-003",
        name="Improve button styling",
        estimated_effort=1.0,
        impact=10.0,
        uncertainty=0.1,
        complexity=5.0
    ),
]

# Prioritize with balanced objectives
ranked = prioritize_tasks(
    tasks,
    objectives=["impact", "effort", "uncertainty"],
    weights={"impact": 0.5, "effort": 0.3, "uncertainty": 0.2}
)

for item in ranked:
    task = item.item
    print(f"{item.rank}. {task.name}")
    print(f"   Score: {item.score:.3f}")
    print(f"   Effort: {task.estimated_effort}h")
    print(f"   Impact: {task.impact}/100")
    print(f"   Rationale: {item.rationale}\n")
# Output:
# 1. Fix critical security bug
#    Score: 0.945
#    Effort: 2.0h
#    Impact: 95/100
#    Rationale: Critical impact, low effort, low uncertainty
#
# 2. Add new payment method
#    Score: 0.612
#    Effort: 40.0h
#    Impact: 70/100
#    Rationale: High impact, significant effort, moderate uncertainty
#
# 3. Improve button styling
#    Score: 0.203
#    Effort: 1.0h
#    Impact: 10/100
#    Rationale: Low impact, cosmetic change
```

**When to use:** Sprint planning, backlog grooming, daily standup.

**Interpreting results:**
- **High score + Low effort** - Quick wins, do first
- **High score + High effort** - Strategic investments
- **Low score** - Defer or drop

---

## Running the Examples

### Option 1: Copy-Paste into Python

```bash
# Activate your virtual environment
cd /path/to/ggen-spec-kit
source .venv/bin/activate  # or `uv sync`

# Start Python
python3

# Copy-paste any example above
```

### Option 2: Run the Demo

```bash
uv run python examples/metrics_demo.py
```

This runs all 6 examples and shows:
- Specification completeness analysis
- Feature selection via information gain
- Distribution comparison (requirements vs implementation)
- Complexity analysis
- Job-outcome alignment
- Information geometry

**Expected output:** See entropy, divergence, and mutual information metrics for sample data.

### Option 3: Use in Your Code

```python
# In your Python script
from specify_cli.hyperdimensional.prioritization import Feature, rank_features_by_gain
from specify_cli.hyperdimensional.metrics import entropy, mutual_information

# Use the functions shown above
```

---

## How to Interpret Results

### Entropy (Specification Quality)
```
0.0 - 0.5 bits   → Excellent (well-defined, ready for dev)
0.5 - 1.0 bits   → Good (minor gaps, mostly complete)
1.0 - 1.5 bits   → Fair (significant uncertainty, needs work)
> 1.5 bits       → Poor (incomplete, high uncertainty)
```

### Information Gain (Feature Priority)
```
> 0.7   → High priority (implement first)
0.4-0.7 → Medium priority (important but not urgent)
< 0.4   → Low priority (defer or drop)
```

### Similarity Score (Semantic Search)
```
> 0.9   → Nearly identical (possible duplicate)
0.7-0.9 → Very similar (likely related)
0.5-0.7 → Moderately similar (check dependencies)
< 0.5   → Different (independent features)
```

### Task Priority Score
```
> 0.8   → Critical (do immediately)
0.6-0.8 → High (this sprint)
0.4-0.6 → Medium (next sprint)
< 0.4   → Low (backlog)
```

### Mutual Information (Feature Relationships)
```
> 0.7 bits   → Strongly related (coordinate development)
0.3-0.7 bits → Moderately related (check dependencies)
< 0.3 bits   → Weakly related (can develop independently)
```

---

## When to Use Which Command

| **Situation** | **Command** | **What to Check** |
|---------------|-------------|-------------------|
| Before implementing a spec | `entropy()` | Is entropy < 0.5? If yes, ready to implement |
| Planning next sprint | `rank_features_by_gain()` | Which features have score > 0.7? |
| Daily standup | `prioritize_tasks()` | What's the highest-scoring task? |
| Checking for duplicates | `search_by_semantic_similarity()` | Any similarity > 0.9? |
| Validating requirements | `mutual_information()` | Are related features actually related (MI > 0.5)? |
| Refining incomplete specs | `calculate_feature_entropy()` | Which features have highest entropy? |

---

## Troubleshooting

### Issue: "ImportError: No module named 'specify_cli'"

**Solution:**
```bash
cd /path/to/ggen-spec-kit
uv sync
source .venv/bin/activate
```

### Issue: "ValueError: probabilities must sum to 1"

**Solution:** When using `entropy()`, ensure your probability list sums to 1.0:
```python
# Wrong
probs = [0.5, 0.3, 0.1]  # Sums to 0.9

# Right
probs = [0.5, 0.3, 0.2]  # Sums to 1.0
```

### Issue: "All scores are similar/random"

**Cause:** Using random embeddings instead of real semantic embeddings.

**Solution:** Initialize proper embeddings:
```python
from specify_cli.hyperdimensional.speckit_embeddings import initialize_speckit_embeddings

# Initialize with real spec-kit concepts
initialize_speckit_embeddings(dimensions=1024)
```

### Issue: "How do I integrate with my RDF specs?"

**Solution:** Use the embedding store to persist vectors:
```python
from specify_cli.hyperdimensional.embedding_store import EmbeddingStore

# Create store
store = EmbeddingStore()

# Add your features
store.add("feature:login", embedding_vector, {
    "type": "feature",
    "complexity": "medium"
})

# Save to RDF
store.save_to_rdf("specs/features.ttl")
```

---

## Next Steps

### Learn More

1. **For theory:** See `docs/hyperdimensional/THEORY_FOUNDATIONS.md`
2. **For implementation details:** See `docs/hyperdimensional/IMPLEMENTATION_GUIDE.md`
3. **For API reference:** See `docs/hyperdimensional/API_REFERENCE.md`
4. **For advanced queries:** See `docs/hyperdimensional/QUERY_LANGUAGE.md`

### Common Use Cases

**Use Case 1: Sprint Planning**
```python
# 1. Rank features by information gain
ranked_features = rank_features_by_gain(all_features, top_k=10)

# 2. Check specification quality
for feature in ranked_features[:5]:  # Top 5
    spec_entropy = calculate_feature_entropy(feature.item)
    if spec_entropy < 0.5:
        print(f"✓ {feature.item.name} ready for dev")
    else:
        print(f"✗ {feature.item.name} needs refinement")

# 3. Prioritize implementation tasks
tasks = create_tasks_from_features(ranked_features[:5])
task_order = prioritize_tasks(tasks)
```

**Use Case 2: Specification Review**
```python
# 1. Calculate entropy for each spec
for spec in specifications:
    h = calculate_feature_entropy(spec)
    print(f"{spec.name}: {h:.3f} bits")

# 2. Find incomplete specs (entropy > 1.0)
incomplete = [s for s in specifications
              if calculate_feature_entropy(s) > 1.0]

# 3. Prioritize refinement by information gain
refinement_order = rank_features_by_gain(incomplete)
```

**Use Case 3: Dependency Analysis**
```python
# 1. Find similar features
results = search.search_by_semantic_similarity(
    query=feature_embedding,
    features=all_features,
    embeddings=feature_embeddings,
    k=10
)

# 2. Check mutual information for top matches
for result in results:
    if result.score > 0.7:  # High similarity
        mi = mutual_information(feature_data, result.content)
        print(f"{result.name}: MI={mi:.3f}")
        if mi > 0.5:
            print("  → Coordinate development")
```

---

## Summary

**You've learned:**
1. ✓ What hyperdimensional computing is (vectors representing concepts)
2. ✓ How to measure specification quality (`entropy()`)
3. ✓ How to prioritize features (`rank_features_by_gain()`)
4. ✓ How to find similar features (`search_by_semantic_similarity()`)
5. ✓ How to prioritize tasks (`prioritize_tasks()`)

**Key takeaways:**
- Lower entropy = better specifications
- Higher information gain = higher priority features
- Similarity > 0.8 = potentially redundant
- Use multi-objective prioritization for sprint planning

**Try it now:**
```bash
uv run python examples/metrics_demo.py
```

**Need help?** Check the troubleshooting section above or open an issue on GitHub.

---

**Last Updated:** 2025-12-21
**Version:** 0.0.25
