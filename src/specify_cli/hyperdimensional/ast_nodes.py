"""Abstract Syntax Tree (AST) node definitions for HDQL.

This module defines the AST node types used by the HDQL parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ASTNode:
    """Base AST node."""

    node_type: str
    location: tuple[int, int]  # (start, end) in source


@dataclass(frozen=True)
class AtomicNode(ASTNode):
    """Atomic query: entity("identifier")."""

    entity_type: str  # command, job, feature, outcome, constraint
    identifier: str  # Entity identifier (may include wildcards)

    def __init__(
        self, entity_type: str, identifier: str, location: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize atomic node."""
        object.__setattr__(self, "node_type", "atomic")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "entity_type", entity_type)
        object.__setattr__(self, "identifier", identifier)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.entity_type}({self.identifier!r})"


@dataclass(frozen=True)
class RelationalNode(ASTNode):
    """Relational query: entity1 -> entity2."""

    left: ASTNode
    right: ASTNode
    relation_type: str  # -> (arrow)

    def __init__(
        self,
        left: ASTNode,
        right: ASTNode,
        relation_type: str = "->",
        location: tuple[int, int] = (0, 0),
    ) -> None:
        """Initialize relational node."""
        object.__setattr__(self, "node_type", "relational")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "left", left)
        object.__setattr__(self, "right", right)
        object.__setattr__(self, "relation_type", relation_type)

    def __repr__(self) -> str:
        """String representation."""
        return f"({self.left} {self.relation_type} {self.right})"


@dataclass(frozen=True)
class LogicalNode(ASTNode):
    """Logical query: query1 AND query2."""

    operator: str  # AND, OR, NOT
    operands: tuple[ASTNode, ...]

    def __init__(
        self, operator: str, operands: list[ASTNode], location: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize logical node."""
        object.__setattr__(self, "node_type", "logical")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "operands", tuple(operands))

    def __repr__(self) -> str:
        """String representation."""
        if self.operator == "NOT":
            return f"NOT {self.operands[0]}"
        return f"({' '.join(f'{op}' for op in self.operands[::2])} {self.operator})"


@dataclass(frozen=True)
class ComparisonNode(ASTNode):
    """Comparison query: entity.attribute >= value."""

    left: ASTNode
    operator: str  # ==, !=, >, >=, <, <=
    right: Any  # Value to compare against

    def __init__(
        self, left: ASTNode, operator: str, right: Any, location: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize comparison node."""
        object.__setattr__(self, "node_type", "comparison")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "left", left)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "right", right)

    def __repr__(self) -> str:
        """String representation."""
        return f"({self.left} {self.operator} {self.right})"


@dataclass(frozen=True)
class AttributeNode(ASTNode):
    """Attribute access: entity.attribute."""

    entity: ASTNode
    attribute: str

    def __init__(self, entity: ASTNode, attribute: str, location: tuple[int, int] = (0, 0)) -> None:
        """Initialize attribute node."""
        object.__setattr__(self, "node_type", "attribute")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "entity", entity)
        object.__setattr__(self, "attribute", attribute)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.entity}.{self.attribute}"


@dataclass(frozen=True)
class SimilarityNode(ASTNode):
    """Similarity query: similar_to(entity, distance=0.2)."""

    reference: ASTNode
    parameters: dict[str, Any]

    def __init__(
        self,
        reference: ASTNode,
        parameters: dict[str, Any] | None = None,
        location: tuple[int, int] = (0, 0),
    ) -> None:
        """Initialize similarity node."""
        object.__setattr__(self, "node_type", "similarity")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "parameters", parameters or {})

    @property
    def threshold(self) -> float:
        """Get distance threshold."""
        return self.parameters.get("distance", self.parameters.get("within_distance", 0.3))

    @property
    def top_k(self) -> int | None:
        """Get top_k parameter."""
        return self.parameters.get("top_k")

    @property
    def metric(self) -> str:
        """Get similarity metric."""
        return self.parameters.get("metric", "cosine")

    def __repr__(self) -> str:
        """String representation."""
        params = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"similar_to({self.reference}, {params})"


@dataclass(frozen=True)
class AnalogyNode(ASTNode):
    """Analogy query: a is_to b as c is_to ?"""

    source_a: ASTNode  # First source entity
    source_b: ASTNode  # Second source entity
    target_a: ASTNode  # First target entity
    target_b: ASTNode | None  # Second target entity (None for ?)

    def __init__(
        self,
        source_a: ASTNode,
        source_b: ASTNode,
        target_a: ASTNode,
        target_b: ASTNode | None = None,
        location: tuple[int, int] = (0, 0),
    ) -> None:
        """Initialize analogy node."""
        object.__setattr__(self, "node_type", "analogy")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "source_a", source_a)
        object.__setattr__(self, "source_b", source_b)
        object.__setattr__(self, "target_a", target_a)
        object.__setattr__(self, "target_b", target_b)

    def __repr__(self) -> str:
        """String representation."""
        target_b_str = str(self.target_b) if self.target_b else "?"
        return f"({self.source_a} is_to {self.source_b} as {self.target_a} is_to {target_b_str})"


@dataclass(frozen=True)
class OptimizationNode(ASTNode):
    """Optimization query: maximize(objective) subject_to(constraints)."""

    objective_type: str  # maximize | minimize
    objective: ASTNode  # Objective expression
    constraints: tuple[ASTNode, ...]  # Constraint expressions

    def __init__(
        self,
        objective_type: str,
        objective: ASTNode,
        constraints: list[ASTNode] | None = None,
        location: tuple[int, int] = (0, 0),
    ) -> None:
        """Initialize optimization node."""
        object.__setattr__(self, "node_type", "optimization")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "objective_type", objective_type)
        object.__setattr__(self, "objective", objective)
        object.__setattr__(self, "constraints", tuple(constraints or []))

    def __repr__(self) -> str:
        """String representation."""
        if self.constraints:
            constraints_str = ", ".join(str(c) for c in self.constraints)
            return f"{self.objective_type}({self.objective}) subject_to({constraints_str})"
        return f"{self.objective_type}({self.objective})"


@dataclass(frozen=True)
class FunctionCallNode(ASTNode):
    """Function call: function_name(arg1, arg2, kwarg=value)."""

    function_name: str
    args: tuple[ASTNode, ...]
    kwargs: dict[str, ASTNode]

    def __init__(
        self,
        function_name: str,
        args: list[ASTNode] | None = None,
        kwargs: dict[str, ASTNode] | None = None,
        location: tuple[int, int] = (0, 0),
    ) -> None:
        """Initialize function call node."""
        object.__setattr__(self, "node_type", "function_call")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "function_name", function_name)
        object.__setattr__(self, "args", tuple(args or []))
        object.__setattr__(self, "kwargs", kwargs or {})

    def __repr__(self) -> str:
        """String representation."""
        args_str = ", ".join(str(a) for a in self.args)
        kwargs_str = ", ".join(f"{k}={v}" for k, v in self.kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        return f"{self.function_name}({all_args})"


@dataclass(frozen=True)
class BinaryOpNode(ASTNode):
    """Binary operation: left op right."""

    operator: str  # +, -, *, /
    left: ASTNode
    right: ASTNode

    def __init__(
        self, operator: str, left: ASTNode, right: ASTNode, location: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize binary operation node."""
        object.__setattr__(self, "node_type", "binary_op")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "left", left)
        object.__setattr__(self, "right", right)

    def __repr__(self) -> str:
        """String representation."""
        return f"({self.left} {self.operator} {self.right})"


@dataclass(frozen=True)
class LiteralNode(ASTNode):
    """Literal value: string, number, boolean."""

    value: Any
    value_type: str  # string, integer, float, boolean

    def __init__(self, value: Any, value_type: str, location: tuple[int, int] = (0, 0)) -> None:
        """Initialize literal node."""
        object.__setattr__(self, "node_type", "literal")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "value_type", value_type)

    def __repr__(self) -> str:
        """String representation."""
        if self.value_type == "string":
            return f'"{self.value}"'
        return str(self.value)


@dataclass(frozen=True)
class IdentifierNode(ASTNode):
    """Identifier: variable or metric name."""

    name: str

    def __init__(self, name: str, location: tuple[int, int] = (0, 0)) -> None:
        """Initialize identifier node."""
        object.__setattr__(self, "node_type", "identifier")
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "name", name)

    def __repr__(self) -> str:
        """String representation."""
        return self.name
