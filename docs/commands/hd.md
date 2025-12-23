# specify hd

Hyperdimensional computing operations for semantic reasoning and knowledge representation.

## Usage

```bash
specify hd [SUBCOMMAND] [OPTIONS]
```

## Description

The `hd` command provides hyperdimensional computing (HDC) operations for:
- Creating semantic hypervector spaces
- Defining and composing concepts
- Querying semantic similarity
- Performing analogical reasoning
- Building knowledge bases

HDC represents knowledge as high-dimensional vectors (10,000+ dimensions), enabling robust semantic operations.

## Subcommands

### init

Initialize a new hyperdimensional space.

```bash
specify hd init SPACE_NAME [OPTIONS]
```

**Options:**
- `--dimensions N` - Vector dimensions (default: 10000)
- `--seed N` - Random seed for reproducibility
- `--format` - Output format (python, json, binary)

**Example:**
```bash
specify hd init semantic-kb --dimensions 10000
✓ Created hyperdimensional space: semantic-kb
  Dimensions: 10,000
  Base vectors: 0
  Total size: 0 MB
```

### define

Define a new concept in the hypervector space.

```bash
specify hd define SPACE_NAME CONCEPT [OPTIONS]
```

**Arguments:**
- `SPACE_NAME` - Target hyperdimensional space
- `CONCEPT` - Concept identifier (e.g., `fruit:apple`, `color:red`)

**Options:**
- `--properties KEY=VALUE` - Semantic properties
- `--hypervector FILE` - Load from file
- `--related CONCEPT` - Associate with related concept
- `--description TEXT` - Concept description

**Example:**
```bash
specify hd define semantic-kb fruit:apple \
  --properties "color=red,taste=sweet,texture=crisp" \
  --description "A red, sweet apple"

✓ Defined concept: fruit:apple
  Properties: 3 (color, taste, texture)
  Related to: fruit (hypernym)
```

### query

Find semantically similar concepts.

```bash
specify hd query SPACE_NAME QUERY [OPTIONS]
```

**Options:**
- `--limit N` - Return top N results (default: 5)
- `--threshold SIMILARITY` - Minimum similarity (0.0-1.0)
- `--filter CONDITION` - Filter results (e.g., `type=fruit`)

**Example:**
```bash
specify hd query semantic-kb "What is red and sweet?" --limit 3
✓ fruit:apple (similarity: 0.92)
  color: red, taste: sweet
✓ fruit:strawberry (similarity: 0.88)
  color: red, taste: sweet
✓ color:red (similarity: 0.45)
  category: color
```

### compose

Create a composite concept from multiple concepts.

```bash
specify hd compose SPACE_NAME CONCEPT1 CONCEPT2 [CONCEPT3...] [OPTIONS]
```

**Options:**
- `--name RESULT_NAME` - Name the composite concept
- `--save` - Save composite to space
- `--weight W1,W2,...` - Weights for each concept

**Example:**
```bash
specify hd compose semantic-kb fruit:apple color:red --name "red_apple" --save
✓ Composed concept: red_apple
  Components: fruit:apple (0.5) + color:red (0.5)
  Similarity to fruit:apple: 0.94
  Similarity to color:red: 0.92
  Saved to space
```

### analogy

Perform analogical reasoning (A is to B as C is to ?).

```bash
specify hd analogy SPACE_NAME A B C [OPTIONS]
```

**Format:** A:B::C:?

**Options:**
- `--limit N` - Top N candidate answers (default: 1)
- `--threshold SIMILARITY` - Minimum threshold

**Example:**
```bash
specify hd analogy semantic-kb fruit:apple color:red fruit:banana --limit 3
✓ fruit:banana is to color:yellow as fruit:apple is to color:red

Candidates:
  1. color:yellow (similarity: 0.91)
  2. color:gold (similarity: 0.87)
  3. color:amber (similarity: 0.84)
```

### relate

Create explicit relationships between concepts.

```bash
specify hd relate SPACE_NAME CONCEPT1 RELATION CONCEPT2
```

**Common relations:**
- `IS_A` - Hypernymy (e.g., apple IS_A fruit)
- `HAS` - Attribute (e.g., apple HAS color:red)
- `SIMILAR_TO` - Similarity (e.g., apple SIMILAR_TO orange)
- `OPPOSITE_OF` - Antonymy
- `PART_OF` - Meronymy

**Example:**
```bash
specify hd relate semantic-kb fruit:apple IS_A fruit
specify hd relate semantic-kb fruit:apple HAS color:red
specify hd relate semantic-kb fruit:apple HAS taste:sweet

✓ Created relationships for fruit:apple
  apple IS_A fruit
  apple HAS color:red
  apple HAS taste:sweet
```

### export

Export hypervector space for use in code.

```bash
specify hd export SPACE_NAME [OPTIONS]
```

**Options:**
- `--format FORMAT` - Output format (python, json, binary, sql)
- `--output FILE` - Save to file
- `--language LANG` - Target language (python, javascript, rust)

**Example:**
```bash
specify hd export semantic-kb --format python --output spaces.py
✓ Exported space to spaces.py

# Python code generated:
from specify_cli.hd import HDSpace, Vector
import numpy as np

semantic_kb = HDSpace(dimensions=10000)
semantic_kb.vectors = {
    "fruit:apple": Vector([...10000 values...]),
    "color:red": Vector([...10000 values...]),
    ...
}
```

### stat

Show statistics about a hyperdimensional space.

```bash
specify hd stat SPACE_NAME
```

**Example:**
```bash
$ specify hd stat semantic-kb
Hyperdimensional Space: semantic-kb

Dimensions: 10,000
Concepts: 48
Relationships: 156
Composite vectors: 12

Memory usage: 1.8 MB
Vector size: 40 KB each

Performance:
  Query avg: 2.3ms
  Compose avg: 5.1ms
  Similarity check: 1.2ms
```

## Examples

### Building a Semantic Knowledge Base

```bash
# Initialize space
specify hd init fruit-kb --dimensions 10000

# Define base concepts
specify hd define fruit-kb fruit:apple --properties "color=red,taste=sweet"
specify hd define fruit-kb fruit:orange --properties "color=orange,taste=sweet"
specify hd define fruit-kb fruit:lemon --properties "color=yellow,taste=sour"

# Define colors
specify hd define fruit-kb color:red
specify hd define fruit-kb color:orange
specify hd define fruit-kb color:yellow

# Create relationships
specify hd relate fruit-kb fruit:apple HAS color:red
specify hd relate fruit-kb fruit:orange HAS color:orange
specify hd relate fruit-kb fruit:lemon HAS color:yellow

# Query semantic relationships
specify hd query fruit-kb "What is red and sweet?"
# Returns: fruit:apple (0.94 similarity)

# Analogical reasoning
specify hd analogy fruit-kb fruit:apple color:red fruit:orange
# Returns: color:orange

# Save space for later use
specify hd export fruit-kb --format python --output fruit_kb.py
```

### Classification System

```bash
# Create classification space
specify hd init classifiers --dimensions 5000

# Define categories
specify hd define classifiers category:fruit
specify hd define classifiers category:vegetable
specify hd define classifiers category:meat

# Define examples
specify hd define classifiers apple --related category:fruit
specify hd define classifiers carrot --related category:vegetable
specify hd define classifiers chicken --related category:meat

# Classify new item
specify hd compose classifiers apple orange banana --name "fruit_cluster"
specify hd query classifiers "fruit_cluster" --limit 1
# Returns: category:fruit (high similarity)
```

## Advanced Options

### Custom Similarity Metrics
```bash
specify hd query fruit-kb "red apple" \
  --similarity cosine     # Default
  --similarity euclidean  # Alternative
  --similarity hamming    # For binary vectors
```

### Batch Operations
```bash
# Define multiple concepts from file
specify hd define-batch fruit-kb concepts.csv
# CSV format: concept_id, properties, description
```

### Visualization
```bash
specify hd visualize fruit-kb --output visualization.html
# Opens interactive 2D/3D visualization
# (dimensionality reduction for visualization)
```

## Configuration

Hyperdimensional spaces are stored in `.hd/` directory:

```
.hd/
├── spaces/
│   ├── semantic-kb.hdspace
│   ├── fruit-kb.hdspace
│   └── classifiers.hdspace
├── metadata.json
└── config.toml
```

## Performance Considerations

| Operation | Time | Dimensions |
|-----------|------|-----------|
| Define concept | <1ms | N/A |
| Simple query | 2-5ms | 10K |
| Composition | 5-10ms | 10K |
| Analogy | 10-20ms | 10K |
| Similarity check | 1-2ms | 10K |

More dimensions = slower but more accurate.

## See Also

- `/docs/explanation/hyperdimensional-theory.md` - HDC theory and concepts
- [hdql.md](./hdql.md) - HDQL query language
- `/docs/guides/hyperdimensional/` - How-to guides
- `/docs/reference/hd-ontology.md` - HD ontology reference
