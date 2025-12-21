"""Query compiler for HDQL.

This module compiles AST to executable query plans.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from specify_cli.hyperdimensional.ast_nodes import ASTNode


@dataclass
class VectorOperation:
    """Single vector operation in execution plan."""

    op_type: str  # lookup, bind, bundle, similarity, filter, optimize
    inputs: list[str]
    output: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """String representation."""
        params = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.op_type}({', '.join(self.inputs)}) -> {self.output} [{params}]"


@dataclass
class ExecutionPlan:
    """Compiled query execution plan."""

    operations: list[VectorOperation]
    index_hints: list[str] = field(default_factory=list)
    optimization_flags: dict[str, bool] = field(default_factory=dict)
    estimated_cost: float = 0.0
    ast: ASTNode | None = None

    def explain(self) -> str:
        """Generate human-readable explanation of execution plan."""
        lines = [
            "Query Execution Plan",
            "=" * 80,
            "",
            f"Estimated Cost: {self.estimated_cost:.2f}",
            f"Operations: {len(self.operations)}",
            "",
            "Execution Steps:",
        ]

        for i, op in enumerate(self.operations, 1):
            lines.append(f"{i}. {op}")

        if self.index_hints:
            lines.extend(["", "Index Hints:", *[f"  - {hint}" for hint in self.index_hints]])

        if self.optimization_flags:
            lines.extend(
                [
                    "",
                    "Optimizations:",
                    *[
                        f"  - {flag}: {enabled}"
                        for flag, enabled in self.optimization_flags.items()
                    ],
                ]
            )

        return "\n".join(lines)


class QueryCompiler:
    """Compiles AST to executable query plan."""

    def __init__(self) -> None:
        """Initialize compiler."""
        self.operation_counter = 0

    def compile(self, ast: ASTNode, top_k: int = 10) -> ExecutionPlan:
        """Compile AST to execution plan.

        Args:
            ast: Abstract syntax tree
            top_k: Maximum results to return

        Returns:
            Executable query plan
        """
        operations: list[VectorOperation] = []
        self.operation_counter = 0

        # Compile AST to operations
        output_var = self._compile_node(ast, operations, top_k=top_k)

        # Add final result collection
        operations.append(
            VectorOperation(
                op_type="collect_results",
                inputs=[output_var],
                output="$result",
                parameters={"top_k": top_k},
            )
        )

        # Estimate cost
        cost = sum(self._estimate_operation_cost(op) for op in operations)

        # Create execution plan
        return ExecutionPlan(
            operations=operations,
            index_hints=self._select_indexes(operations),
            optimization_flags={"parallel_execution": len(operations) > 3},
            estimated_cost=cost,
            ast=ast,
        )

    def _compile_node(
        self, node: ASTNode, operations: list[VectorOperation], top_k: int = 10
    ) -> str:
        """Compile single AST node to operations.

        Args:
            node: AST node to compile
            operations: List to append operations to
            top_k: Maximum results

        Returns:
            Variable name containing result
        """
        from specify_cli.hyperdimensional.ast_nodes import (
            AnalogyNode,
            AtomicNode,
            AttributeNode,
            BinaryOpNode,
            ComparisonNode,
            FunctionCallNode,
            IdentifierNode,
            LiteralNode,
            LogicalNode,
            OptimizationNode,
            RelationalNode,
            SimilarityNode,
        )

        if isinstance(node, AtomicNode):
            return self._compile_atomic(node, operations)
        if isinstance(node, RelationalNode):
            return self._compile_relational(node, operations, top_k)
        if isinstance(node, LogicalNode):
            return self._compile_logical(node, operations, top_k)
        if isinstance(node, ComparisonNode):
            return self._compile_comparison(node, operations, top_k)
        if isinstance(node, SimilarityNode):
            return self._compile_similarity(node, operations, top_k)
        if isinstance(node, AnalogyNode):
            return self._compile_analogy(node, operations)
        if isinstance(node, OptimizationNode):
            return self._compile_optimization(node, operations)
        if isinstance(node, FunctionCallNode):
            return self._compile_function_call(node, operations, top_k)
        if isinstance(node, AttributeNode):
            return self._compile_attribute(node, operations)
        if isinstance(node, BinaryOpNode):
            return self._compile_binary_op(node, operations, top_k)
        if isinstance(node, LiteralNode):
            return self._compile_literal(node, operations)
        if isinstance(node, IdentifierNode):
            return self._compile_identifier(node, operations)
        msg = f"Unsupported node type: {type(node).__name__}"
        raise ValueError(msg)

    def _compile_atomic(self, node: Any, operations: list[VectorOperation]) -> str:
        """Compile atomic query."""
        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="lookup",
                inputs=[],
                output=output_var,
                parameters={
                    "entity_type": node.entity_type,
                    "identifier": node.identifier,
                },
            )
        )
        return output_var

    def _compile_relational(self, node: Any, operations: list[VectorOperation], top_k: int) -> str:
        """Compile relational query (->)."""
        left_var = self._compile_node(node.left, operations, top_k)
        right_var = self._compile_node(node.right, operations, top_k)

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="bind_relation",
                inputs=[left_var, right_var],
                output=output_var,
                parameters={"relation_type": node.relation_type},
            )
        )
        return output_var

    def _compile_logical(self, node: Any, operations: list[VectorOperation], top_k: int) -> str:
        """Compile logical query (AND/OR/NOT)."""
        operand_vars = [self._compile_node(op, operations, top_k) for op in node.operands]

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="logical",
                inputs=operand_vars,
                output=output_var,
                parameters={"operator": node.operator},
            )
        )
        return output_var

    def _compile_comparison(self, node: Any, operations: list[VectorOperation], top_k: int) -> str:
        """Compile comparison query."""
        left_var = self._compile_node(node.left, operations, top_k)

        # Right side might be literal
        from specify_cli.hyperdimensional.ast_nodes import LiteralNode

        if isinstance(node.right, LiteralNode):
            right_value = node.right.value
        else:
            right_var = self._compile_node(node.right, operations, top_k)
            # For now, treat as variable reference
            right_value = f"${right_var}"

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="filter",
                inputs=[left_var],
                output=output_var,
                parameters={
                    "operator": node.operator,
                    "value": right_value,
                },
            )
        )
        return output_var

    def _compile_similarity(self, node: Any, operations: list[VectorOperation], top_k: int) -> str:
        """Compile similarity query."""
        ref_var = self._compile_node(node.reference, operations, top_k)

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="similarity",
                inputs=[ref_var],
                output=output_var,
                parameters={
                    "threshold": node.threshold,
                    "top_k": node.top_k or top_k,
                    "metric": node.metric,
                },
            )
        )
        return output_var

    def _compile_analogy(self, node: Any, operations: list[VectorOperation]) -> str:
        """Compile analogy query."""
        source_a_var = self._compile_node(node.source_a, operations)
        source_b_var = self._compile_node(node.source_b, operations)
        target_a_var = self._compile_node(node.target_a, operations)

        target_b_var = None
        if node.target_b is not None:
            target_b_var = self._compile_node(node.target_b, operations)

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="analogy",
                inputs=[source_a_var, source_b_var, target_a_var]
                + ([target_b_var] if target_b_var else []),
                output=output_var,
                parameters={},
            )
        )
        return output_var

    def _compile_optimization(self, node: Any, operations: list[VectorOperation]) -> str:
        """Compile optimization query."""
        objective_var = self._compile_node(node.objective, operations)

        constraint_vars = [self._compile_node(c, operations) for c in node.constraints]

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="optimize",
                inputs=[objective_var, *constraint_vars],
                output=output_var,
                parameters={
                    "objective_type": node.objective_type,
                },
            )
        )
        return output_var

    def _compile_function_call(
        self, node: Any, operations: list[VectorOperation], top_k: int
    ) -> str:
        """Compile function call."""
        arg_vars = [self._compile_node(arg, operations, top_k) for arg in node.args]
        kwarg_vars = {k: self._compile_node(v, operations, top_k) for k, v in node.kwargs.items()}

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="function_call",
                inputs=arg_vars,
                output=output_var,
                parameters={
                    "function_name": node.function_name,
                    "kwargs": kwarg_vars,
                },
            )
        )
        return output_var

    def _compile_attribute(self, node: Any, operations: list[VectorOperation]) -> str:
        """Compile attribute access."""
        entity_var = self._compile_node(node.entity, operations)

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="attribute_access",
                inputs=[entity_var],
                output=output_var,
                parameters={"attribute": node.attribute},
            )
        )
        return output_var

    def _compile_binary_op(self, node: Any, operations: list[VectorOperation], top_k: int) -> str:
        """Compile binary operation."""
        left_var = self._compile_node(node.left, operations, top_k)
        right_var = self._compile_node(node.right, operations, top_k)

        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="binary_op",
                inputs=[left_var, right_var],
                output=output_var,
                parameters={"operator": node.operator},
            )
        )
        return output_var

    def _compile_literal(self, node: Any, operations: list[VectorOperation]) -> str:
        """Compile literal value."""
        output_var = self._next_var()
        operations.append(
            VectorOperation(
                op_type="literal",
                inputs=[],
                output=output_var,
                parameters={
                    "value": node.value,
                    "value_type": node.value_type,
                },
            )
        )
        return output_var

    def _compile_identifier(self, node: Any, operations: list[VectorOperation]) -> str:
        """Compile identifier."""
        # Identifiers reference variables or metrics
        return f"${node.name}"

    def _next_var(self) -> str:
        """Generate next variable name."""
        self.operation_counter += 1
        return f"$v{self.operation_counter}"

    def _estimate_operation_cost(self, operation: VectorOperation) -> float:
        """Estimate cost of single operation."""
        cost_map = {
            "lookup": 1.0,
            "bind_relation": 5.0,
            "similarity": 10.0,
            "filter": 2.0,
            "logical": 3.0,
            "analogy": 8.0,
            "optimize": 50.0,
            "function_call": 5.0,
            "collect_results": 1.0,
        }
        return cost_map.get(operation.op_type, 1.0)

    def _select_indexes(self, operations: list[VectorOperation]) -> list[str]:
        """Select indexes based on operations."""
        hints = []

        # Check for similarity operations
        if any(op.op_type == "similarity" for op in operations):
            hints.append("Use HNSW index for similarity search")

        # Check for exact lookups
        if any(op.op_type == "lookup" for op in operations):
            hints.append("Use hash index for exact lookups")

        return hints


def compile_query(ast: ASTNode, top_k: int = 10) -> ExecutionPlan:
    """Compile AST to execution plan (convenience function).

    Args:
        ast: Abstract syntax tree
        top_k: Maximum results to return

    Returns:
        Executable query plan
    """
    compiler = QueryCompiler()
    return compiler.compile(ast, top_k=top_k)
