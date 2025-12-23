# specify hdql

Hyperdimensional Query Language - semantic query execution on hypervector spaces.

## Usage

```bash
specify hdql [SUBCOMMAND] [OPTIONS]
```

## Description

HDQL (Hyperdimensional Query Language) is a specialized query language for semantic reasoning over hyperdimensional spaces. It enables:
- Semantic similarity searches
- Multi-criteria filtering
- Relationship traversal
- Analogical reasoning queries
- Composite concept queries

HDQL is to HDC what SQL is to relational databases.

## Subcommands

### execute

Run a HDQL query against a hyperdimensional space.

```bash
specify hdql execute SPACE_NAME QUERY [OPTIONS]
```

**Options:**
- `--query-file FILE` - Read query from file
- `--limit N` - Result limit (default: 10)
- `--threshold SIMILARITY` - Minimum similarity (0.0-1.0)
- `--format` - Output format (text, json, csv)
- `--explain` - Show query execution plan

**Example:**
```bash
specify hdql execute fruit-kb "SELECT ?fruit WHERE { ?fruit HAS color:red }"
✓ Query executed in 12ms

Results:
  1. fruit:apple (confidence: 0.94)
  2. fruit:strawberry (confidence: 0.91)
  3. fruit:cherry (confidence: 0.89)
```

### parse

Parse and validate HDQL syntax.

```bash
specify hdql parse QUERY
```

Shows query structure without executing:

```bash
$ specify hdql parse "SELECT ?fruit WHERE { ?fruit HAS color:red; IS_FRUIT true }"
✓ Valid HDQL query

Parsed structure:
  SELECT: ?fruit
  WHERE:
    Triple 1: ?fruit HAS color:red
    Triple 2: ?fruit IS_FRUIT true
  Semantics: AND (both conditions required)
```

### compile

Compile HDQL query to optimized form.

```bash
specify hdql compile QUERY [OPTIONS]
```

Shows optimization opportunities:

```bash
$ specify hdql compile "SELECT ?fruit WHERE { ?fruit IS_A fruit; HAS color:red }"
✓ Query compiled

Optimizations:
  - Reordered conditions (selectivity: ?fruit IS_A fruit before color filtering)
  - Index available for IS_A relation
  - Estimated results: 2-5 rows

Compiled form:
  FILTER(?fruit IS_A fruit) -> FILTER(HAS color:red)
```

### explain

Explain query execution plan.

```bash
specify hdql explain SPACE_NAME QUERY
```

Shows how query will be executed:

```bash
$ specify hdql explain fruit-kb "SELECT ?fruit WHERE { ?fruit HAS color:red }"
Query Execution Plan:

1. SIMILARITY_SEARCH
   Concept: color:red
   Range: [0.8, 1.0] similarity
   Estimated: 15 candidates

2. FILTER
   Condition: HAS relationship
   Estimated: 3 results

3. RANK
   Order by: Similarity DESC
   Limit: 10

Estimated execution time: 5-10ms
Estimated memory: 2 MB
```

## HDQL Syntax

### Basic Query Structure

```hdql
SELECT ?variable [, ?variable2, ...]
WHERE {
  ?variable RELATION ?target ;
  ?variable PROPERTY value ;
  ?variable SIMILARITY ?other_concept > threshold .
}
[ORDER BY ?variable [ASC | DESC]]
[LIMIT number]
```

### SELECT Clause

What to return from the query:

```hdql
SELECT ?fruit              # Single variable
SELECT ?fruit, ?color     # Multiple variables
SELECT DISTINCT ?fruit    # Remove duplicates
SELECT COUNT(?fruit)      # Count results
SELECT ?fruit AS result   # Alias
```

### WHERE Clause

Define search criteria using three patterns:

#### 1. Relationship Patterns
```hdql
?fruit HAS color:red           # Direct relationship
?fruit IS_A category:fruit     # Hypernymy (type hierarchy)
?fruit SIMILAR_TO fruit:apple  # Similarity match
?fruit OPPOSITE_OF fruit:bitter # Antonymy
```

#### 2. Property Filters
```hdql
?fruit taste = "sweet"              # Exact match
?fruit taste LIKE "sw%"             # Pattern match
?fruit similarity > 0.8             # Numeric comparison
?fruit count >= 5                   # Numeric range
```

#### 3. Similarity Criteria
```hdql
?fruit SIMILARITY fruit:apple > 0.8        # Similar to concept
?fruit SIMILARITY-DISTANCE < 2.5           # Distance-based
?fruit COMPOSITE orange, banana > 0.85     # Composition match
```

### Examples by Category

#### Simple Concept Search
```hdql
# Find all red fruits
SELECT ?fruit
WHERE {
  ?fruit HAS color:red ;
  ?fruit IS_A category:fruit .
}
```

#### Similarity-Based Search
```hdql
# Find fruits similar to apple
SELECT ?fruit, ?similarity
WHERE {
  ?fruit SIMILAR_TO fruit:apple ;
  ?fruit SIMILARITY > 0.8 .
}
ORDER BY ?similarity DESC
```

#### Multi-Criteria Filtering
```hdql
# Find red, sweet fruits
SELECT ?fruit
WHERE {
  ?fruit HAS color:red ;
  ?fruit HAS taste:sweet ;
  ?fruit IS_FRUIT true .
}
```

#### Relationship Traversal
```hdql
# Find all fruits and their colors
SELECT ?fruit, ?color
WHERE {
  ?fruit IS_A category:fruit ;
  ?fruit HAS ?color ;
  ?color IS_A category:color .
}
```

#### Analogical Reasoning
```hdql
# Apple is to Red as Orange is to ?
SELECT ?color
WHERE {
  fruit:apple HAS ?color1 ;
  fruit:orange HAS ?color ;
  fruit:apple ANALOGY fruit:banana :: ?color1 ANALOGY ?color .
}
```

#### Aggregation
```hdql
# Count fruits by color
SELECT ?color, COUNT(?fruit) AS count
WHERE {
  ?fruit HAS ?color ;
  ?fruit IS_A category:fruit .
}
GROUP BY ?color
ORDER BY count DESC
```

## Examples

### Query from Command Line
```bash
specify hdql execute fruit-kb \
  "SELECT ?fruit WHERE { ?fruit HAS color:red }"

Results:
  fruit:apple (0.94)
  fruit:strawberry (0.91)
```

### Query from File
```bash
# Create query file: fruit_query.hdql
SELECT ?fruit, ?color
WHERE {
  ?fruit HAS ?color ;
  ?fruit SIMILARITY fruit:apple > 0.8 .
}
ORDER BY ?similarity DESC
LIMIT 5

# Execute
specify hdql execute fruit-kb --query-file fruit_query.hdql
```

### Interactive Mode
```bash
specify hdql interactive fruit-kb
hdql> SELECT ?fruit WHERE { ?fruit HAS color:red }
(2 results in 3ms)
  fruit:apple, confidence: 0.94
  fruit:strawberry, confidence: 0.91

hdql> SELECT ?color WHERE { fruit:apple HAS ?color }
(2 results in 1ms)
  color:red
  color:sweet

hdql> exit
```

### JSON Output
```bash
specify hdql execute fruit-kb \
  "SELECT ?fruit WHERE { ?fruit HAS color:red }" \
  --format json

{
  "query": "SELECT ?fruit WHERE { ?fruit HAS color:red }",
  "execution_time_ms": 3,
  "results": [
    {"fruit": "fruit:apple", "confidence": 0.94},
    {"fruit": "fruit:strawberry", "confidence": 0.91}
  ],
  "result_count": 2
}
```

## Performance Tips

### Selectivity Ordering
Put most selective conditions first:

```hdql
# Good - filters early
SELECT ?fruit WHERE {
  ?fruit IS_A category:fruit ;      # Highly selective
  ?fruit HAS color:red ;             # Less selective
  ?fruit SIMILAR_TO fruit:apple .    # Least selective
}

# Less efficient - filters later
SELECT ?fruit WHERE {
  ?fruit SIMILAR_TO fruit:apple ;   # Least selective
  ?fruit HAS color:red ;            # Less selective
  ?fruit IS_A category:fruit .      # Highly selective
}
```

### Index Usage
```bash
# Check if query uses indexes
specify hdql explain space-name "SELECT ..."

# Create indexes for frequently used properties
specify hd index space-name --property IS_A
specify hd index space-name --property HAS
```

## Advanced Features

### User-Defined Functions
```hdql
DEFINE FUNCTION is_sweet(?fruit) AS
  ?fruit HAS taste:sweet ;

SELECT ?fruit
WHERE {
  is_sweet(?fruit) ;
  ?fruit HAS color:red .
}
```

### Recursive Queries
```hdql
# Find all categories (recursive IS_A)
SELECT ?category
WHERE {
  fruit:apple IS_A* ?category .  # * = recursive
}
```

### Machine Learning Integration
```hdql
# Use learned classifier
SELECT ?category
WHERE {
  ?fruit CLASSIFY-WITH model:fruit-classifier ;
  ?fruit PREDICTED_CLASS ?category ;
  ?fruit CONFIDENCE > 0.8 .
}
```

## See Also

- [hd.md](./hd.md) - Hyperdimensional computing commands
- `/docs/explanation/hyperdimensional-theory.md` - HDC theory
- `/docs/guides/hyperdimensional/` - HDQL how-to guides
- `/docs/reference/hdql-syntax.md` - Complete syntax reference
