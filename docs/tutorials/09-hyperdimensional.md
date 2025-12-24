# Tutorial 9: Hyperdimensional Computing with Specify

Learn to use hyperdimensional computing (HDC) for semantic search, classification, and knowledge representation.

**Duration:** 30 minutes
**Prerequisites:** Tutorial 1 (getting-started)
**Difficulty:** Advanced

## Learning Goals

- Understand hypervectors and semantic spaces
- Create and query hyperdimensional spaces
- Perform semantic search and analogical reasoning
- Build a classification system with HDC

## Part 1: Create Your First Hyperdimensional Space

### Initialize Space

```bash
# Create a semantic space for fruit classification
specify hd init fruit-knowledge --dimensions 10000

✓ Created hyperdimensional space: fruit-knowledge
  Dimensions: 10,000
  Base vectors: 0
  Size on disk: 0 MB
```

### Define Concepts

```bash
# Define fruits
specify hd define fruit-knowledge fruit:apple \
  --properties "color=red,taste=sweet,texture=crisp"

✓ Defined: fruit:apple
  Properties: color, taste, texture

specify hd define fruit-knowledge fruit:banana \
  --properties "color=yellow,taste=sweet,texture=soft"

specify hd define fruit-knowledge fruit:lemon \
  --properties "color=yellow,taste=sour,texture=firm"

# Define colors as standalone concepts
specify hd define fruit-knowledge color:red
specify hd define fruit-knowledge color:yellow
specify hd define fruit-knowledge color:green
```

## Part 2: Create Relationships

### Add Associations

```bash
# Create "has color" relationships
specify hd relate fruit-knowledge fruit:apple HAS color:red
specify hd relate fruit-knowledge fruit:banana HAS color:yellow
specify hd relate fruit-knowledge fruit:lemon HAS color:yellow

# Create hypernym relationships (is-a)
specify hd relate fruit-knowledge fruit:apple IS_A category:fruit
specify hd relate fruit-knowledge fruit:banana IS_A category:fruit
specify hd relate fruit-knowledge fruit:lemon IS_A category:fruit
```

## Part 3: Semantic Search

### Simple Similarity Search

```bash
# Find fruits similar to apple
specify hd query fruit-knowledge "What is similar to apple?" \
  --limit 3

✓ Query: "What is similar to apple?"

Results (by similarity):
  1. fruit:apple (1.00 - exact match)
  2. fruit:banana (0.88 - also sweet)
  3. fruit:lemon (0.76 - also fruit)
```

### Property-Based Search

```bash
# Find red fruits
specify hd query fruit-knowledge "red fruits" --limit 5

✓ Query: "red fruits"

Results:
  1. fruit:apple (0.95)
     Properties: color=red, taste=sweet
  2. color:red (0.87)
  3. category:fruit (0.61)

Interpretation: apple matches "red fruits" best
because it has color:red property
```

### Multi-Criteria Search

```bash
# Find sweet yellow fruits
specify hd query fruit-knowledge "sweet yellow fruits"

Results (ranked):
  1. fruit:banana (0.92)
     ✓ sweet, ✓ yellow
  2. fruit:apple (0.68)
     ✓ sweet, ✗ not yellow
  3. fruit:lemon (0.64)
     ✓ yellow, ✗ not sweet
```

## Part 4: Analogical Reasoning

### Learn Patterns

```bash
# Fruit analogy: "Apple is to Red as Banana is to ?"
specify hd analogy fruit-knowledge \
  fruit:apple color:red fruit:banana --limit 1

✓ Analogy: apple:red :: banana:?

Most likely answer: color:yellow

Why? Because:
  - apple HAS color:red
  - banana HAS color:yellow
  - apple and banana are both fruits
  - Pattern: fruit IS HAS color
```

### Taste Analogy

```bash
# "Apple is to Sweet as Lemon is to ?"
specify hd analogy fruit-knowledge \
  fruit:apple taste:sweet fruit:lemon

✓ Result: taste:sour

Reasoning:
  - apple : sweet :: lemon : sour
  - Learned pattern: fruits paired with taste properties
  - Applied to new pair
```

## Part 5: Build a Classifier

### Compose Training Concepts

```bash
# Create a "sweet fruits" cluster
specify hd compose fruit-knowledge \
  fruit:apple fruit:banana \
  --name "sweet-fruits" \
  --save

✓ Composed: sweet-fruits
  Components: fruit:apple (0.5) + fruit:banana (0.5)

# Create a "yellow fruits" cluster
specify hd compose fruit-knowledge \
  fruit:banana fruit:lemon \
  --name "yellow-fruits" \
  --save

✓ Composed: yellow-fruits
```

### Classify New Items

```bash
# New unknown fruit with these properties:
# color=yellow, taste=sweet, texture=soft

specify hd classify fruit-knowledge \
  "yellow sweet soft fruit" \
  --against "sweet-fruits,yellow-fruits,category:fruit"

✓ Classification results:

  sweet-fruits: 0.89 (HIGH - similar to apple & banana)
  yellow-fruits: 0.91 (HIGH - similar to banana & lemon)
  category:fruit: 0.94 (HIGH - is definitely a fruit)

Prediction: Likely fruit:banana or fruit:pineapple
(both are yellow, sweet, soft)

Confidence: 91% (very high)
```

## Part 6: Export Space for Use in Code

### Generate Python Module

```bash
# Export the knowledge base
specify hd export fruit-knowledge \
  --format python \
  --output spaces/fruit_kb.py

✓ Exported to spaces/fruit_kb.py

# Generated code (snippet):
from specify_cli.hd import HDSpace

fruit_knowledge = HDSpace(dimensions=10000)
fruit_knowledge.vectors = {
    "fruit:apple": Vector([...10000 values...]),
    "fruit:banana": Vector([...10000 values...]),
    "color:red": Vector([...10000 values...]),
    # ... more vectors
}
```

### Use in Application

```python
# In your code
from spaces.fruit_kb import fruit_knowledge

def find_similar_fruits(name: str):
    """Find fruits similar to query"""
    results = fruit_knowledge.find_similar(name, count=5)
    return results

def classify_fruit(properties: dict):
    """Classify unknown fruit"""
    query = compose_query(properties)
    classification = fruit_knowledge.classify(query)
    return classification

# Usage
results = find_similar_fruits("apple")
print(results)  # [banana, orange, peach, ...]

fruit_class = classify_fruit({
    "color": "orange",
    "taste": "sweet",
    "texture": "firm"
})
print(fruit_class)  # Likely: orange or peach
```

## Part 7: Advanced: Analogy-Based Reasoning

### Solve Analogies Automatically

```bash
# Setup: Given three items, find the fourth
# A:B :: C:D

# Example 1
specify hd solve-analogy fruit-knowledge \
  "apple:red::banana:?"

✓ Solution: banana:yellow

# Example 2
specify hd solve-analogy fruit-knowledge \
  "apple:sweet::lemon:?"

✓ Solution: lemon:sour

# Example 3 (complex)
specify hd solve-analogy fruit-knowledge \
  "apple:crisp::banana:?"

✓ Solution: banana:soft

# These are learned patterns, working perfectly!
```

### Multiple Solutions

```bash
# Find multiple possible analogy solutions
specify hd solve-analogy fruit-knowledge \
  "fruit:apple::category:?" \
  --limit 5

✓ Possible solutions (ranked):

  1. category:fruit (0.98)
     apple is strongly associated with fruit category
  2. category:healthy (0.82)
     apples are often healthy
  3. category:red (0.71)
     apples are often red
  4. category:sweet (0.68)
     apples are often sweet
```

## Part 8: Interactive Exploration

### Start Interactive Mode

```bash
specify hd interactive fruit-knowledge

hdql> define fruit:orange color=orange taste=sweet
✓ Defined fruit:orange

hdql> query "sweet orange fruits"
✓ Results:
   fruit:orange (0.98)
   fruit:apple (0.85)
   fruit:banana (0.84)

hdql> analogy fruit:apple color:red fruit:orange:?
✓ color:orange

hdql> classify "round yellow soft tropical"
Likely: fruit:banana (0.93) or fruit:mango (0.89)

hdql> export --format json
✓ Exported knowledge base

hdql> exit
```

## Summary

**Hypervectors:** 10,000-dimensional vectors representing concepts
**Spaces:** Collections of related hypervectors
**Relationships:** Semantic associations (HAS, IS_A, similar, etc.)
**Queries:** Find similar concepts by meaning
**Analogies:** Solve A:B :: C:D patterns
**Classification:** Classify new items by similarity
**Export:** Use HDC in your own code

## Key Insights

1. **Semantic similarity** works without explicit rules
2. **Analogical reasoning** emerges from patterns
3. **Compositionality** - combine vectors for complex concepts
4. **Robustness** - works with incomplete or noisy data
5. **Interpretability** - can inspect why matching works

## See Also

- `/docs/explanation/hyperdimensional-theory.md` - HD theory
- `/docs/commands/hd.md` - hd command reference
- `/docs/commands/hdql.md` - HDQL query language
- `/docs/reference/hd-ontology.md` - HD ontology
