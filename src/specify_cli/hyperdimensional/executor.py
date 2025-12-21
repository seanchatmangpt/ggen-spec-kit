"""Query executor for HDQL.

This module executes compiled query plans against embedding databases.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from specify_cli.hyperdimensional.results import (
    Alternative,
    AnalysisResult,
    Entity,
    EntityMatch,
    ReasoningTrace,
    Recommendation,
    RecommendationResult,
    TradeOffAnalysis,
    VectorQueryResult,
)

if TYPE_CHECKING:
    from specify_cli.hyperdimensional.compiler import ExecutionPlan, VectorOperation
    from specify_cli.hyperdimensional.embeddings import EmbeddingDatabase


@dataclass
class ExecutionContext:
    """Runtime context for query execution."""

    variables: dict[str, Any] = field(default_factory=dict)
    reasoning_steps: list[str] = field(default_factory=list)
    intermediate_results: dict[str, Any] = field(default_factory=dict)

    def set(self, name: str, value: Any) -> None:
        """Set variable value."""
        self.variables[name] = value

    def get(self, name: str) -> Any:
        """Get variable value."""
        # Handle both $var and var syntax
        clean_name = name.lstrip("$")
        return self.variables.get(clean_name)

    def add_step(self, step: str) -> None:
        """Add reasoning step."""
        self.reasoning_steps.append(step)

    def save_intermediate(self, key: str, value: Any) -> None:
        """Save intermediate result for debugging."""
        self.intermediate_results[key] = value


class QueryExecutor:
    """Executes compiled query plans."""

    def __init__(self, embedding_db: EmbeddingDatabase) -> None:
        """Initialize executor.

        Args:
            embedding_db: Embedding database to query against
        """
        self.db = embedding_db

    def execute_plan(
        self, plan: ExecutionPlan, verbose: bool = False
    ) -> VectorQueryResult | RecommendationResult | AnalysisResult:
        """Execute query plan.

        Args:
            plan: Compiled execution plan
            verbose: Include reasoning trace

        Returns:
            Query results (type depends on query)
        """
        context = ExecutionContext()

        if verbose:
            context.add_step(f"Executing plan with {len(plan.operations)} operations")

        # Execute operations in sequence
        for i, operation in enumerate(plan.operations, 1):
            if verbose:
                context.add_step(f"Step {i}: {operation.op_type}")

            self._execute_operation(operation, context)

        # Extract final result
        result_var = context.get("result")

        # Build reasoning trace
        reasoning = ReasoningTrace(
            steps=tuple(context.reasoning_steps),
            intermediate_results=context.intermediate_results,
            execution_plan=plan.explain(),
        )

        # Return appropriate result type
        return self._build_result(result_var, reasoning, plan)

    def _execute_operation(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute single operation.

        Args:
            operation: Operation to execute
            context: Execution context
        """
        # Dispatch to operation handler
        handler = getattr(self, f"_execute_{operation.op_type}", None)
        if handler is None:
            msg = f"Unknown operation type: {operation.op_type}"
            raise ValueError(msg)

        handler(operation, context)

    def _execute_lookup(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute lookup operation."""
        entity_type = operation.parameters["entity_type"]
        identifier = operation.parameters["identifier"]

        context.add_step(f"Looking up {entity_type}({identifier!r})")

        # Handle wildcards
        if any(c in identifier for c in "*?~"):
            matches = self._wildcard_lookup(entity_type, identifier)
        else:
            matches = self.db.lookup(entity_type, identifier)

        context.set(operation.output, matches)
        context.save_intermediate(f"lookup_{entity_type}_{identifier}", len(matches))

    def _execute_bind_relation(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute relational binding (->)."""
        left_entities = context.get(operation.inputs[0])
        right_entities = context.get(operation.inputs[1])

        context.add_step(
            f"Finding relationships between {len(left_entities)} and {len(right_entities)} entities"
        )

        # Find semantically related entities
        matches = []
        for left in left_entities:
            for right in right_entities:
                similarity = self.db.compute_relation_similarity(left, right)
                if similarity > 0.5:  # Threshold
                    matches.append((left, right, similarity))

        # Sort by similarity
        matches.sort(key=lambda x: x[2], reverse=True)

        # Extract left entities that have relationships
        result = [left for left, _, _ in matches]
        context.set(operation.output, result)

    def _execute_logical(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute logical operation (AND/OR/NOT)."""
        operator = operation.parameters["operator"]
        operand_sets = [context.get(inp) for inp in operation.inputs]

        context.add_step(f"Applying {operator} to {len(operand_sets)} operand sets")

        if operator == "AND":
            # Intersection
            result = set(operand_sets[0])
            for operand in operand_sets[1:]:
                result &= set(operand)
            result = list(result)
        elif operator == "OR":
            # Union
            result = set()
            for operand in operand_sets:
                result |= set(operand)
            result = list(result)
        elif operator == "NOT":
            # Complement (relative to all entities)
            all_entities = self.db.get_all_entities()
            result = [e for e in all_entities if e not in operand_sets[0]]
        else:
            msg = f"Unknown logical operator: {operator}"
            raise ValueError(msg)

        context.set(operation.output, result)

    def _execute_filter(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute filter operation."""
        entities = context.get(operation.inputs[0])
        operator_symbol = operation.parameters["operator"]
        value = operation.parameters["value"]

        context.add_step(f"Filtering {len(entities)} entities with {operator_symbol} {value}")

        # Apply filter
        filtered = []
        for entity in entities:
            # Extract attribute value (assuming previous attribute_access)
            if hasattr(entity, "value"):
                entity_value = entity.value
            else:
                continue

            # Compare
            if self._compare(entity_value, operator_symbol, value):
                filtered.append(entity)

        context.set(operation.output, filtered)
        context.save_intermediate("filter_result_count", len(filtered))

    def _execute_similarity(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute similarity search."""
        reference_entities = context.get(operation.inputs[0])
        threshold = operation.parameters["threshold"]
        top_k = operation.parameters["top_k"]

        context.add_step(f"Finding similar entities (threshold={threshold}, top_k={top_k})")

        # Get reference vector
        if not reference_entities:
            context.set(operation.output, [])
            return

        reference = (
            reference_entities[0] if isinstance(reference_entities, list) else reference_entities
        )

        # Find similar entities
        similar = self.db.find_similar(reference, threshold=threshold, top_k=top_k)

        context.set(operation.output, similar)
        context.save_intermediate("similarity_matches", len(similar))

    def _execute_analogy(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute analogy operation (a:b::c:?)."""
        source_a = context.get(operation.inputs[0])[0]
        source_b = context.get(operation.inputs[1])[0]
        target_a = context.get(operation.inputs[2])[0]

        context.add_step(f"Solving analogy: {source_a.name}:{source_b.name}::{target_a.name}:?")

        # Vector arithmetic: ? ≈ target_a + (source_b - source_a)
        result = self.db.solve_analogy(source_a, source_b, target_a)

        context.set(operation.output, [result])

    def _execute_optimize(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute optimization operation."""
        objective_type = operation.parameters["objective_type"]

        context.add_step(f"Running {objective_type} optimization")

        # Get all entities as candidates
        candidates = self.db.get_all_entities()

        # Evaluate objective for each candidate
        scores = []
        for entity in candidates:
            score = self._evaluate_objective(entity, context)
            scores.append((entity, score))

        # Sort by objective
        reverse = objective_type == "maximize"
        scores.sort(key=lambda x: x[1], reverse=reverse)

        # Apply constraints (simplified)
        # For full implementation, filter based on constraint variables

        context.set(operation.output, [entity for entity, _ in scores[:10]])
        context.save_intermediate("optimization_scores", {e.name: s for e, s in scores[:10]})

    def _execute_function_call(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute function call."""
        function_name = operation.parameters["function_name"]

        context.add_step(f"Calling function: {function_name}")

        # Dispatch to function handler
        handler = getattr(self, f"_function_{function_name}", None)
        if handler is None:
            msg = f"Unknown function: {function_name}"
            raise ValueError(msg)

        result = handler(operation, context)
        context.set(operation.output, result)

    def _execute_attribute_access(
        self, operation: VectorOperation, context: ExecutionContext
    ) -> None:
        """Execute attribute access."""
        entities = context.get(operation.inputs[0])
        attribute = operation.parameters["attribute"]

        context.add_step(f"Accessing attribute: {attribute}")

        # Extract attribute values
        results = []
        for entity in entities:
            value = entity.attributes.get(attribute, 0.0)
            # Wrap in object with value field for filtering
            results.append(type("AttrValue", (), {"entity": entity, "value": value})())

        context.set(operation.output, results)

    def _execute_binary_op(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute binary operation."""
        left = context.get(operation.inputs[0])
        right = context.get(operation.inputs[1])
        operator_symbol = operation.parameters["operator"]

        # Perform operation
        if operator_symbol == "+":
            result = left + right
        elif operator_symbol == "-":
            result = left - right
        elif operator_symbol == "*":
            result = left * right
        elif operator_symbol == "/":
            result = left / right if right != 0 else 0.0
        else:
            msg = f"Unknown binary operator: {operator_symbol}"
            raise ValueError(msg)

        context.set(operation.output, result)

    def _execute_literal(self, operation: VectorOperation, context: ExecutionContext) -> None:
        """Execute literal value."""
        value = operation.parameters["value"]
        context.set(operation.output, value)

    def _execute_collect_results(
        self, operation: VectorOperation, context: ExecutionContext
    ) -> None:
        """Collect final results."""
        entities = context.get(operation.inputs[0])
        top_k = operation.parameters.get("top_k", 10)

        if isinstance(entities, list):
            context.set("result", entities[:top_k])
        else:
            context.set("result", entities)

    def _wildcard_lookup(self, entity_type: str, pattern: str) -> list[Entity]:
        """Lookup entities matching wildcard pattern."""
        all_entities = self.db.get_entities_by_type(entity_type)

        if pattern.endswith("~"):
            # Fuzzy match (edit distance)
            pattern_clean = pattern[:-1]
            return [e for e in all_entities if self._fuzzy_match(e.name, pattern_clean)]
        # Glob pattern
        return [e for e in all_entities if fnmatch.fnmatch(e.name, pattern)]

    def _fuzzy_match(self, text: str, pattern: str, max_distance: int = 2) -> bool:
        """Check if text matches pattern with fuzzy matching."""
        # Simple Levenshtein distance
        if len(text) == 0:
            return len(pattern) <= max_distance
        if len(pattern) == 0:
            return len(text) <= max_distance

        # Use numpy for efficiency
        distances = np.zeros((len(text) + 1, len(pattern) + 1))
        for i in range(len(text) + 1):
            distances[i][0] = i
        for j in range(len(pattern) + 1):
            distances[0][j] = j

        for i in range(1, len(text) + 1):
            for j in range(1, len(pattern) + 1):
                if text[i - 1] == pattern[j - 1]:
                    distances[i][j] = distances[i - 1][j - 1]
                else:
                    distances[i][j] = min(
                        distances[i - 1][j] + 1,  # deletion
                        distances[i][j - 1] + 1,  # insertion
                        distances[i - 1][j - 1] + 1,  # substitution
                    )

        return distances[len(text)][len(pattern)] <= max_distance

    def _compare(self, left: Any, operator: str, right: Any) -> bool:
        """Compare two values with operator."""
        if operator == "==":
            return left == right
        if operator == "!=":
            return left != right
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        return False

    def _evaluate_objective(self, entity: Entity, context: ExecutionContext) -> float:
        """Evaluate objective function for entity."""
        # Simplified: use weighted sum of attributes
        weights = {
            "outcome_coverage": 1.0,
            "job_frequency": 0.5,
            "implementation_effort": -0.3,
        }

        score = 0.0
        for attr, weight in weights.items():
            value = entity.attributes.get(attr, 0.0)
            score += weight * value

        return score

    def _build_result(
        self, result_data: Any, reasoning: ReasoningTrace, plan: ExecutionPlan
    ) -> VectorQueryResult | RecommendationResult | AnalysisResult:
        """Build appropriate result type from execution data."""
        # Detect result type based on plan operations
        has_optimize = any(op.op_type == "optimize" for op in plan.operations)

        if has_optimize:
            return self._build_recommendation_result(result_data, reasoning)
        return self._build_vector_result(result_data, reasoning)

    def _build_vector_result(
        self, entities: list[Entity], reasoning: ReasoningTrace
    ) -> VectorQueryResult:
        """Build vector query result."""
        matches = []
        confidences = []

        for entity in entities:
            # Calculate similarity/distance
            distance = 0.0  # Placeholder
            similarity = 1.0 - distance
            explanation = f"Matched {entity.entity_type}: {entity.description}"

            matches.append(
                EntityMatch(
                    entity=entity,
                    distance=distance,
                    similarity=similarity,
                    explanation=explanation,
                )
            )
            confidences.append(similarity)

        return VectorQueryResult(
            matching_entities=tuple(matches),
            confidence_scores=tuple(confidences),
            reasoning_trace=reasoning,
            execution_time_ms=0.0,  # Will be filled by query engine
        )

    def _build_recommendation_result(
        self, entities: list[Entity], reasoning: ReasoningTrace
    ) -> RecommendationResult:
        """Build recommendation result."""
        recommendations = []
        alternatives = []

        for i, entity in enumerate(entities[:10]):
            score = 1.0 - (i * 0.05)  # Decreasing scores
            rationale = "High score based on weighted objectives"

            recommendation = Recommendation(
                entity=entity,
                score=score,
                rationale=rationale,
                metrics={
                    "outcome_coverage": entity.attributes.get("outcome_coverage", 0.0),
                    "implementation_effort": entity.attributes.get("implementation_effort", 0.0),
                },
            )

            if i == 0:
                recommendations.append(recommendation)
            else:
                alternative = Alternative(
                    entity=entity,
                    score=score,
                    trade_offs="Lower priority alternative",
                )
                alternatives.append(alternative)

        trade_offs = TradeOffAnalysis(
            summary="Trade-off between coverage and effort",
            pareto_frontier=tuple(entities[:3]),
            dominated_options=tuple(entities[3:]),
        )

        return RecommendationResult(
            top_k_recommendations=tuple(recommendations),
            trade_offs=trade_offs,
            alternative_options=tuple(alternatives),
            objective_value=recommendations[0].score if recommendations else 0.0,
        )

    # Function implementations
    def _function_commands_for_job(
        self, operation: VectorOperation, context: ExecutionContext
    ) -> list[Entity]:
        """Find commands addressing a job."""
        # This would use the compiled arguments
        return []

    def _function_count(self, operation: VectorOperation, context: ExecutionContext) -> int:
        """Count entities."""
        input_entities = context.get(operation.inputs[0])
        return len(input_entities) if isinstance(input_entities, list) else 0
