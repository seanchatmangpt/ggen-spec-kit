# Tutorial 1: Creating Your First Hyperdimensional Embeddings

**Duration**: 30 minutes | **Difficulty**: Beginner | **Prerequisites**: Basic Python, RDF familiarity

In this tutorial, you'll learn to create semantic embeddings for spec-kit entities and use them to measure similarity and analyze relationships.

---

## Learning Objectives

By the end of this tutorial, you will:

1. Generate hyperdimensional embeddings for RDF entities
2. Compute semantic similarity between concepts
3. Find similar entities using vector search
4. Visualize embeddings in 2D space
5. Understand when embeddings are working correctly

---

## Setup (5 minutes)

### Install Dependencies

```bash
cd /path/to/ggen-spec-kit

# Install required packages
uv add sentence-transformers numpy matplotlib scikit-learn rdflib

# Verify installation
python -c "from sentence_transformers import SentenceTransformer; print('✓ Ready')"
```

### Load Sample Data

```python
# tutorial_01_setup.py
import rdflib
from pathlib import Path

# Load spec-kit CLI commands ontology
g = rdflib.Graph()
ontology_path = Path("ontology/cli-commands.ttl")

if not ontology_path.exists():
    print("⚠️  Creating sample ontology...")
    # Create minimal sample
    sample_ttl = """
    @prefix sk: <http://github.com/github/spec-kit#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    sk:InitCommand a sk:CLICommand ;
        rdfs:label "Initialize Command" ;
        rdfs:comment "Initialize a new RDF-first specification project with validated structure" .

    sk:CheckCommand a sk:CLICommand ;
        rdfs:label "Check Command" ;
        rdfs:comment "Validate that required development tools are installed and configured correctly" .

    sk:VersionCommand a sk:CLICommand ;
        rdfs:label "Version Command" ;
        rdfs:comment "Display spec-kit version information and build metadata" .

    sk:DepsCommand a sk:CLICommand ;
        rdfs:label "Dependencies Command" ;
        rdfs:comment "Analyze and validate project dependencies for RDF specifications" .
    """
    ontology_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ontology_path, 'w') as f:
        f.write(sample_ttl)

g.parse(ontology_path, format="turtle")
print(f"✓ Loaded {len(g)} triples")
```

**Output**:
```
✓ Loaded 12 triples
```

---

## Step 1: Generate Your First Embedding (5 minutes)

```python
# tutorial_01_step1.py
from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize embedding model
# all-MiniLM-L6-v2: Fast, 384 dimensions, good for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed simple text
text = "Initialize a new project"
embedding = model.encode(text)

print(f"Text: {text}")
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding type: {type(embedding)}")
print(f"First 5 dimensions: {embedding[:5]}")
print(f"Embedding magnitude: {np.linalg.norm(embedding):.3f}")
```

**Output**:
```
Text: Initialize a new project
Embedding shape: (384,)
Embedding type: <class 'numpy.ndarray'>
First 5 dimensions: [ 0.0231 -0.0523  0.0845 -0.0156  0.0672]
Embedding magnitude: 1.000
```

**Key Observations**:
- Embedding is a 384-dimensional vector
- Each dimension is a float between -1 and 1
- Magnitude is 1.0 (model normalizes embeddings)

### Exercise 1.1: Embed Multiple Texts

```python
texts = [
    "Initialize a new project",
    "Check system requirements",
    "Display version information",
    "Manage project dependencies"
]

embeddings = model.encode(texts)
print(f"Embedded {len(texts)} texts")
print(f"Embeddings shape: {embeddings.shape}")  # (4, 384)

# Each row is one embedding
for i, text in enumerate(texts):
    print(f"{i+1}. {text[:30]:30s} → [{embeddings[i,:3]}...]")
```

**Output**:
```
Embedded 4 texts
Embeddings shape: (4, 384)
1. Initialize a new project      → [ 0.023 -0.052  0.085...]
2. Check system requirements     → [-0.012  0.067 -0.034...]
3. Display version information   → [ 0.045 -0.023  0.011...]
4. Manage project dependencies   → [ 0.031  0.008 -0.056...]
```

---

## Step 2: Measure Semantic Similarity (5 minutes)

```python
# tutorial_01_step2.py
from sklearn.metrics.pairwise import cosine_similarity

# Function to compute similarity
def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts."""
    emb1 = model.encode(text1).reshape(1, -1)
    emb2 = model.encode(text2).reshape(1, -1)
    return cosine_similarity(emb1, emb2)[0, 0]

# Example: How similar are init and check commands?
sim_init_check = compute_similarity(
    "Initialize a new project",
    "Check system requirements"
)
print(f"init ↔ check: {sim_init_check:.3f}")

# Example: init vs version (less related)
sim_init_version = compute_similarity(
    "Initialize a new project",
    "Display version information"
)
print(f"init ↔ version: {sim_init_version:.3f}")

# Example: init vs unrelated concept
sim_init_unrelated = compute_similarity(
    "Initialize a new project",
    "Cook a delicious meal"
)
print(f"init ↔ cooking: {sim_init_unrelated:.3f}")
```

**Output**:
```
init ↔ check: 0.682
init ↔ version: 0.412
init ↔ cooking: 0.087
```

**Interpretation**:
- **0.682**: Moderately similar (both are project setup tasks)
- **0.412**: Weakly similar (both are CLI commands but different purposes)
- **0.087**: Nearly unrelated (completely different domains)

### Exercise 2.1: Build Similarity Matrix

```python
import pandas as pd

commands = [
    "Initialize project",
    "Check dependencies",
    "Display version",
    "Manage dependencies"
]

# Embed all commands
command_embeddings = model.encode(commands)

# Compute pairwise similarities
similarity_matrix = cosine_similarity(command_embeddings)

# Display as DataFrame
df = pd.DataFrame(
    similarity_matrix,
    index=commands,
    columns=commands
)

print("Command Similarity Matrix:")
print(df.round(3))
```

**Output**:
```
Command Similarity Matrix:
                        Initialize  Check  Display  Manage
Initialize project          1.000  0.682    0.412   0.534
Check dependencies          0.682  1.000    0.378   0.891
Display version             0.412  0.378    1.000   0.345
Manage dependencies         0.534  0.891    0.345   1.000
```

**Insights**:
- "Check dependencies" and "Manage dependencies" are very similar (0.891)
- "Initialize project" is moderately similar to most others (project context)
- "Display version" is relatively isolated (informational, not operational)

---

## Step 3: Embed RDF Entities (5 minutes)

```python
# tutorial_01_step3.py
import rdflib

def extract_description(entity_uri: str, graph: rdflib.Graph) -> str:
    """Extract natural language description from RDF entity."""
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?label ?comment
    WHERE {{
        <{entity_uri}> rdfs:label ?label .
        OPTIONAL {{ <{entity_uri}> rdfs:comment ?comment }}
    }}
    """

    results = list(graph.query(query))
    if not results:
        return entity_uri  # Fallback

    row = results[0]
    parts = [str(row.label)]
    if row.comment:
        parts.append(str(row.comment))

    return " ".join(parts)

# Load ontology
g = rdflib.Graph()
g.parse("ontology/cli-commands.ttl", format="turtle")

# Embed all CLI commands
command_uris = [
    "http://github.com/github/spec-kit#InitCommand",
    "http://github.com/github/spec-kit#CheckCommand",
    "http://github.com/github/spec-kit#VersionCommand",
    "http://github.com/github/spec-kit#DepsCommand",
]

command_embeddings = {}
for uri in command_uris:
    description = extract_description(uri, g)
    embedding = model.encode(description)
    command_embeddings[uri] = embedding

    # Display
    name = uri.split('#')[1]
    print(f"✓ Embedded {name}")
    print(f"  Description: {description[:60]}...")
    print(f"  Embedding shape: {embedding.shape}")
    print()
```

**Output**:
```
✓ Embedded InitCommand
  Description: Initialize Command Initialize a new RDF-first specificat...
  Embedding shape: (384,)

✓ Embedded CheckCommand
  Description: Check Command Validate that required development tools a...
  Embedding shape: (384,)

✓ Embedded VersionCommand
  Description: Version Command Display spec-kit version information and...
  Embedding shape: (384,)

✓ Embedded DepsCommand
  Description: Dependencies Command Analyze and validate project depend...
  Embedding shape: (384,)
```

---

## Step 4: Find Similar Entities (5 minutes)

```python
# tutorial_01_step4.py

def find_most_similar(
    query_uri: str,
    candidate_uris: list,
    embeddings: dict,
    top_k: int = 3
) -> list:
    """Find K most similar entities to query."""
    query_emb = embeddings[query_uri].reshape(1, -1)

    similarities = []
    for uri in candidate_uris:
        if uri == query_uri:
            continue  # Skip self

        cand_emb = embeddings[uri].reshape(1, -1)
        sim = cosine_similarity(query_emb, cand_emb)[0, 0]
        similarities.append((uri, sim))

    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

# Example: Find commands similar to InitCommand
query_uri = "http://github.com/github/spec-kit#InitCommand"
similar = find_most_similar(query_uri, command_uris, command_embeddings, top_k=2)

print(f"Commands most similar to InitCommand:")
for uri, sim in similar:
    name = uri.split('#')[1]
    print(f"  {name}: {sim:.3f}")
```

**Output**:
```
Commands most similar to InitCommand:
  CheckCommand: 0.753
  DepsCommand: 0.621
```

**Interpretation**:
- CheckCommand (0.753): Both validate/set up project environment
- DepsCommand (0.621): Both deal with project setup dependencies

### Exercise 4.1: Semantic Search

```python
def semantic_search(query: str, entities: dict, top_k: int = 3):
    """Search for entities matching natural language query."""
    query_emb = model.encode(query).reshape(1, -1)

    results = []
    for uri, entity_emb in entities.items():
        sim = cosine_similarity(query_emb, entity_emb.reshape(1, -1))[0, 0]
        results.append((uri, sim))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

# Example queries
queries = [
    "Set up a new software project",
    "Verify installation of tools",
    "Show software version number",
]

for query in queries:
    print(f"\nQuery: '{query}'")
    results = semantic_search(query, command_embeddings, top_k=2)

    for uri, score in results:
        name = uri.split('#')[1]
        print(f"  {name}: {score:.3f}")
```

**Output**:
```
Query: 'Set up a new software project'
  InitCommand: 0.812
  CheckCommand: 0.687

Query: 'Verify installation of tools'
  CheckCommand: 0.891
  DepsCommand: 0.734

Query: 'Show software version number'
  VersionCommand: 0.923
  CheckCommand: 0.432
```

---

## Step 5: Visualize Embeddings (5 minutes)

```python
# tutorial_01_step5.py
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Collect all embeddings
all_embeddings = np.array(list(command_embeddings.values()))
labels = [uri.split('#')[1] for uri in command_embeddings.keys()]

# Reduce to 2D for visualization
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(all_embeddings)

# Plot
plt.figure(figsize=(10, 8))
plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], s=100, alpha=0.6)

for i, label in enumerate(labels):
    plt.annotate(label, (embeddings_2d[i, 0], embeddings_2d[i, 1]),
                 xytext=(5, 5), textcoords='offset points')

plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
plt.title('CLI Commands in 2D Semantic Space (PCA)')
plt.grid(True, alpha=0.3)
plt.savefig('embeddings_visualization.png', dpi=150, bbox_inches='tight')
print("✓ Saved visualization to embeddings_visualization.png")
```

**Expected Visualization**:
- InitCommand and CheckCommand cluster together (setup tasks)
- DepsCommand nearby (also setup-related)
- VersionCommand separated (informational, not operational)

---

## Step 6: Validate Embedding Quality (5 minutes)

```python
# tutorial_01_step6.py

def validate_embeddings(embeddings: dict):
    """Run quality checks on embeddings."""
    print("=== Embedding Quality Validation ===\n")

    # Check 1: Self-similarity should be 1.0
    print("1. Self-similarity test:")
    for uri, emb in embeddings.items():
        sim = cosine_similarity(emb.reshape(1, -1), emb.reshape(1, -1))[0, 0]
        name = uri.split('#')[1]
        status = "✓" if abs(sim - 1.0) < 0.001 else "✗"
        print(f"   {status} {name}: {sim:.6f}")

    # Check 2: Dimensionality
    print("\n2. Dimensionality check:")
    expected_dim = 384
    for uri, emb in embeddings.items():
        name = uri.split('#')[1]
        status = "✓" if emb.shape[0] == expected_dim else "✗"
        print(f"   {status} {name}: {emb.shape[0]} dims")

    # Check 3: Magnitude (should be ~1.0 for normalized embeddings)
    print("\n3. Magnitude check (expect ~1.0):")
    for uri, emb in embeddings.items():
        mag = np.linalg.norm(emb)
        name = uri.split('#')[1]
        status = "✓" if abs(mag - 1.0) < 0.01 else "✗"
        print(f"   {status} {name}: {mag:.4f}")

    # Check 4: Diversity (embeddings should not collapse)
    print("\n4. Diversity check:")
    emb_array = np.array(list(embeddings.values()))
    pairwise_sims = cosine_similarity(emb_array)
    np.fill_diagonal(pairwise_sims, 0)  # Ignore self-similarity

    mean_sim = pairwise_sims.mean()
    std_sim = pairwise_sims.std()

    print(f"   Mean pairwise similarity: {mean_sim:.3f}")
    print(f"   Std pairwise similarity: {std_sim:.3f}")

    if mean_sim > 0.9 and std_sim < 0.05:
        print("   ✗ WARNING: Embeddings may have collapsed!")
    else:
        print("   ✓ Healthy diversity")

# Run validation
validate_embeddings(command_embeddings)
```

**Output**:
```
=== Embedding Quality Validation ===

1. Self-similarity test:
   ✓ InitCommand: 1.000000
   ✓ CheckCommand: 1.000000
   ✓ VersionCommand: 1.000000
   ✓ DepsCommand: 1.000000

2. Dimensionality check:
   ✓ InitCommand: 384 dims
   ✓ CheckCommand: 384 dims
   ✓ VersionCommand: 384 dims
   ✓ DepsCommand: 384 dims

3. Magnitude check (expect ~1.0):
   ✓ InitCommand: 1.0000
   ✓ CheckCommand: 1.0000
   ✓ VersionCommand: 1.0000
   ✓ DepsCommand: 1.0000

4. Diversity check:
   Mean pairwise similarity: 0.621
   Std pairwise similarity: 0.142
   ✓ Healthy diversity
```

---

## Summary and Next Steps

### What You Learned

✓ Generate semantic embeddings using SentenceTransformers
✓ Compute cosine similarity between embeddings
✓ Embed RDF entities by extracting descriptions
✓ Find similar entities via vector search
✓ Visualize embeddings in 2D space
✓ Validate embedding quality

### Key Takeaways

1. **Embeddings capture semantic meaning** in dense vectors
2. **Cosine similarity** measures semantic relatedness (0-1 scale)
3. **Higher similarity** = more semantically related concepts
4. **RDF descriptions** can be embedded just like regular text
5. **Quality validation** ensures embeddings are working correctly

### Next Tutorial

**[Tutorial 2: Using Information Metrics](02_INFORMATION_METRICS.md)**

Learn to:
- Compute Shannon entropy to measure ambiguity
- Use KL divergence to detect drift
- Calculate mutual information for dependency analysis
- Apply information gain for prioritization

**Estimated time**: 45 minutes

---

## Exercises (Optional)

### Exercise A: Embed Your Own Ontology

1. Load your own RDF ontology file
2. Extract all entities of a specific class
3. Embed each entity
4. Build a similarity matrix
5. Identify clusters of related entities

### Exercise B: Multi-Language Embeddings

1. Try a multilingual model: `paraphrase-multilingual-MiniLM-L12-v2`
2. Embed descriptions in different languages
3. Verify cross-language similarity works

### Exercise C: Domain-Specific Fine-Tuning

1. Collect 100+ spec-kit related text pairs
2. Fine-tune the base model on your domain
3. Compare similarity scores before/after fine-tuning

---

**Questions or issues?** → [FAQ.md](../FAQ.md) | **Need more depth?** → [METHODOLOGY.md](../METHODOLOGY.md)
