"""HDQL query parser.

This module implements a recursive descent parser for the Hyperdimensional Query Language.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from specify_cli.hyperdimensional.ast_nodes import (
    AnalogyNode,
    ASTNode,
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


class TokenType(Enum):
    """Token types for HDQL lexer."""

    # Entity types
    COMMAND = "command"
    JOB = "job"
    FEATURE = "feature"
    OUTCOME = "outcome"
    CONSTRAINT = "constraint"

    # Operators
    ARROW = "->"
    DOT = "."
    LPAREN = "("
    RPAREN = ")"
    COMMA = ","
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"

    # Keywords
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IS_TO = "is_to"
    AS = "as"
    SIMILAR_TO = "similar_to"
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    SUBJECT_TO = "subject_to"

    # Function names
    COMMANDS_FOR_JOB = "commands_for_job"
    FEATURES_FOR_JOB = "features_for_job"
    OUTCOMES_FOR_JOB = "outcomes_for_job"
    COMMANDS_SIMILAR_TO = "commands_similar_to"
    FEATURES_SATISFYING = "features_satisfying"
    OUTCOMES_MATCHING = "outcomes_matching"
    COUNT = "count"
    AVG = "avg"
    SUM = "sum"
    MAX = "max"
    MIN = "min"

    # Literals
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    IDENTIFIER = "IDENTIFIER"
    WILDCARD = "WILDCARD"

    # Special
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Token:
    """Lexical token."""

    token_type: TokenType
    value: Any
    position: int
    line: int = 1
    column: int = 1

    def __repr__(self) -> str:
        """String representation."""
        return f"Token({self.token_type.name}, {self.value!r}, pos={self.position})"


class ParseError(Exception):
    """Query parsing error."""

    def __init__(self, message: str, position: int = 0, token: Token | None = None) -> None:
        """Initialize parse error."""
        super().__init__(message)
        self.position = position
        self.token = token


class Lexer:
    """Lexical analyzer for HDQL."""

    # Token patterns (order matters!)
    PATTERNS = [
        # Keywords (must come before identifiers)
        (r"\bcommands_similar_to\b", TokenType.COMMANDS_SIMILAR_TO),
        (r"\bfeatures_satisfying\b", TokenType.FEATURES_SATISFYING),
        (r"\boutcomes_matching\b", TokenType.OUTCOMES_MATCHING),
        (r"\bcommands_for_job\b", TokenType.COMMANDS_FOR_JOB),
        (r"\bfeatures_for_job\b", TokenType.FEATURES_FOR_JOB),
        (r"\boutcomes_for_job\b", TokenType.OUTCOMES_FOR_JOB),
        (r"\bsimilar_to\b", TokenType.SIMILAR_TO),
        (r"\bmaximize\b", TokenType.MAXIMIZE),
        (r"\bminimize\b", TokenType.MINIMIZE),
        (r"\bsubject_to\b", TokenType.SUBJECT_TO),
        (r"\bis_to\b", TokenType.IS_TO),
        (r"\bcommand\b", TokenType.COMMAND),
        (r"\bjob\b", TokenType.JOB),
        (r"\bfeature\b", TokenType.FEATURE),
        (r"\boutcome\b", TokenType.OUTCOME),
        (r"\bconstraint\b", TokenType.CONSTRAINT),
        (r"\bAND\b", TokenType.AND),
        (r"\bOR\b", TokenType.OR),
        (r"\bNOT\b", TokenType.NOT),
        (r"\bas\b", TokenType.AS),
        (r"\bcount\b", TokenType.COUNT),
        (r"\bavg\b", TokenType.AVG),
        (r"\bsum\b", TokenType.SUM),
        (r"\bmax\b", TokenType.MAX),
        (r"\bmin\b", TokenType.MIN),
        (r"\btrue\b", lambda m: Token(TokenType.BOOLEAN, True, m.start())),
        (r"\bfalse\b", lambda m: Token(TokenType.BOOLEAN, False, m.start())),
        # Operators
        (r"->", TokenType.ARROW),
        (r"==", TokenType.EQ),
        (r"!=", TokenType.NE),
        (r">=", TokenType.GE),
        (r"<=", TokenType.LE),
        (r">", TokenType.GT),
        (r"<", TokenType.LT),
        (r"=", TokenType.ASSIGN),
        (r"\+", TokenType.PLUS),
        (r"-", TokenType.MINUS),
        (r"\*", TokenType.STAR),
        (r"/", TokenType.SLASH),
        (r"\.", TokenType.DOT),
        (r"\(", TokenType.LPAREN),
        (r"\)", TokenType.RPAREN),
        (r",", TokenType.COMMA),
        # Literals
        (r'"([^"]*)"', lambda m: Token(TokenType.STRING, m.group(1), m.start())),
        (r"'([^']*)'", lambda m: Token(TokenType.STRING, m.group(1), m.start())),
        (
            r"\d+\.\d+",
            lambda m: Token(TokenType.FLOAT, float(m.group()), m.start()),
        ),
        (
            r"\d+",
            lambda m: Token(TokenType.INTEGER, int(m.group()), m.start()),
        ),
        # Identifiers with wildcards
        (
            r"[a-zA-Z_][a-zA-Z0-9_-]*[*?~]?",
            lambda m: Token(
                TokenType.WILDCARD if any(c in m.group() for c in "*?~") else TokenType.IDENTIFIER,
                m.group(),
                m.start(),
            ),
        ),
        # Whitespace (skip)
        (r"\s+", None),
    ]

    def __init__(self, text: str) -> None:
        """Initialize lexer with input text."""
        self.text = text
        self.position = 0
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """Tokenize input text."""
        while self.position < len(self.text):
            matched = False

            for pattern, token_type in self.PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.text, self.position)

                if match:
                    if token_type is not None:  # Skip whitespace
                        if callable(token_type):
                            token = token_type(match)
                        else:
                            token = Token(token_type, match.group(), self.position)
                        self.tokens.append(token)

                    self.position = match.end()
                    matched = True
                    break

            if not matched:
                msg = f"Unknown character: {self.text[self.position]!r}"
                raise ParseError(msg, self.position)

        self.tokens.append(Token(TokenType.EOF, None, self.position))
        return self.tokens


class Parser:
    """Recursive descent parser for HDQL."""

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize parser with token stream."""
        self.tokens = tokens
        self.position = 0

    @property
    def current_token(self) -> Token:
        """Get current token."""
        return self.tokens[self.position] if self.position < len(self.tokens) else self.tokens[-1]

    def peek(self, offset: int = 1) -> Token:
        """Peek ahead at token."""
        pos = self.position + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current_token
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error."""
        if self.current_token.token_type != token_type:
            msg = f"Expected {token_type.name}, got {self.current_token.token_type.name}"
            raise ParseError(msg, self.current_token.position, self.current_token)
        return self.advance()

    def parse(self) -> ASTNode:
        """Parse query and return AST."""
        ast = self.parse_expr()
        self.expect(TokenType.EOF)
        return ast

    def parse_expr(self) -> ASTNode:
        """Parse expression (top-level)."""
        return self.parse_or_expr()

    def parse_or_expr(self) -> ASTNode:
        """Parse OR expression."""
        left = self.parse_and_expr()

        while self.current_token.token_type == TokenType.OR:
            self.advance()
            right = self.parse_and_expr()
            left = LogicalNode("OR", [left, right])

        return left

    def parse_and_expr(self) -> ASTNode:
        """Parse AND expression."""
        left = self.parse_not_expr()

        while self.current_token.token_type == TokenType.AND:
            self.advance()
            right = self.parse_not_expr()
            left = LogicalNode("AND", [left, right])

        return left

    def parse_not_expr(self) -> ASTNode:
        """Parse NOT expression."""
        if self.current_token.token_type == TokenType.NOT:
            self.advance()
            operand = self.parse_not_expr()
            return LogicalNode("NOT", [operand])

        return self.parse_comparison_expr()

    def parse_comparison_expr(self) -> ASTNode:
        """Parse comparison expression."""
        left = self.parse_relational_expr()

        comparison_ops = {
            TokenType.EQ: "==",
            TokenType.NE: "!=",
            TokenType.GT: ">",
            TokenType.GE: ">=",
            TokenType.LT: "<",
            TokenType.LE: "<=",
        }

        if self.current_token.token_type in comparison_ops:
            operator = comparison_ops[self.current_token.token_type]
            self.advance()
            right = self.parse_relational_expr()
            return ComparisonNode(left, operator, right)

        return left

    def parse_relational_expr(self) -> ASTNode:
        """Parse relational expression (->)."""
        left = self.parse_additive_expr()

        if self.current_token.token_type == TokenType.ARROW:
            self.advance()
            right = self.parse_relational_expr()
            return RelationalNode(left, right)

        return left

    def parse_additive_expr(self) -> ASTNode:
        """Parse additive expression (+ -)."""
        left = self.parse_multiplicative_expr()

        while self.current_token.token_type in (TokenType.PLUS, TokenType.MINUS):
            operator = "+" if self.current_token.token_type == TokenType.PLUS else "-"
            self.advance()
            right = self.parse_multiplicative_expr()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_multiplicative_expr(self) -> ASTNode:
        """Parse multiplicative expression (* /)."""
        left = self.parse_primary_expr()

        while self.current_token.token_type in (TokenType.STAR, TokenType.SLASH):
            operator = "*" if self.current_token.token_type == TokenType.STAR else "/"
            self.advance()
            right = self.parse_primary_expr()
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_primary_expr(self) -> ASTNode:
        """Parse primary expression."""
        # Parenthesized expression
        if self.current_token.token_type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr

        # Atomic entity query
        entity_types = {
            TokenType.COMMAND,
            TokenType.JOB,
            TokenType.FEATURE,
            TokenType.OUTCOME,
            TokenType.CONSTRAINT,
        }
        if self.current_token.token_type in entity_types:
            return self.parse_atomic_query()

        # Function calls
        if self.current_token.token_type == TokenType.SIMILAR_TO:
            return self.parse_similarity_query()

        if self.current_token.token_type in (TokenType.MAXIMIZE, TokenType.MINIMIZE):
            return self.parse_optimization_query()

        if self.current_token.token_type in (
            TokenType.COMMANDS_SIMILAR_TO,
            TokenType.FEATURES_SATISFYING,
            TokenType.OUTCOMES_MATCHING,
            TokenType.COMMANDS_FOR_JOB,
            TokenType.FEATURES_FOR_JOB,
            TokenType.OUTCOMES_FOR_JOB,
            TokenType.COUNT,
            TokenType.AVG,
            TokenType.SUM,
            TokenType.MAX,
            TokenType.MIN,
        ):
            return self.parse_function_call()

        # Literals
        if self.current_token.token_type in (
            TokenType.STRING,
            TokenType.INTEGER,
            TokenType.FLOAT,
            TokenType.BOOLEAN,
        ):
            return self.parse_literal()

        # Identifier
        if self.current_token.token_type == TokenType.IDENTIFIER:
            identifier = self.parse_identifier()

            # Check for attribute access
            if self.current_token.token_type == TokenType.DOT:
                self.advance()
                attribute = self.expect(TokenType.IDENTIFIER).value
                return AttributeNode(identifier, attribute)

            return identifier

        msg = f"Unexpected token: {self.current_token}"
        raise ParseError(msg, self.current_token.position, self.current_token)

    def parse_atomic_query(self) -> AtomicNode | AttributeNode:
        """Parse atomic entity query: entity("identifier")."""
        entity_type = self.current_token.value
        start_pos = self.current_token.position
        self.advance()

        self.expect(TokenType.LPAREN)
        identifier_token = self.current_token

        if identifier_token.token_type not in (
            TokenType.STRING,
            TokenType.IDENTIFIER,
            TokenType.WILDCARD,
        ):
            msg = f"Expected string or identifier, got {identifier_token.token_type.name}"
            raise ParseError(msg, identifier_token.position, identifier_token)

        identifier = identifier_token.value
        self.advance()
        end_pos = self.current_token.position
        self.expect(TokenType.RPAREN)

        # Create atomic node
        node: AtomicNode | AttributeNode = AtomicNode(entity_type, identifier, (start_pos, end_pos))

        # Check for attribute access (.)
        if self.current_token.token_type == TokenType.DOT:
            self.advance()
            attribute = self.expect(TokenType.IDENTIFIER).value
            node = AttributeNode(node, attribute)

        # Check for analogy (is_to)
        if self.current_token.token_type == TokenType.IS_TO:
            return self.parse_analogy(node)

        return node

    def parse_analogy(self, source_a: ASTNode) -> AnalogyNode:
        """Parse analogy query: a is_to b as c is_to ?"""
        self.expect(TokenType.IS_TO)
        source_b = self.parse_primary_expr()

        self.expect(TokenType.AS)
        target_a = self.parse_primary_expr()

        self.expect(TokenType.IS_TO)

        # Check for wildcard (?)
        if (
            self.current_token.token_type == TokenType.IDENTIFIER
            and self.current_token.value == "?"
        ):
            self.advance()
            target_b = None
        else:
            target_b = self.parse_primary_expr()

        return AnalogyNode(source_a, source_b, target_a, target_b)

    def parse_similarity_query(self) -> SimilarityNode:
        """Parse similarity query: similar_to(entity, params)."""
        self.expect(TokenType.SIMILAR_TO)
        self.expect(TokenType.LPAREN)

        reference = self.parse_expr()

        parameters: dict[str, Any] = {}
        if self.current_token.token_type == TokenType.COMMA:
            self.advance()
            parameters = self.parse_parameters()

        self.expect(TokenType.RPAREN)

        return SimilarityNode(reference, parameters)

    def parse_optimization_query(self) -> OptimizationNode:
        """Parse optimization query: maximize(obj) subject_to(constraints)."""
        objective_type = self.current_token.value
        self.advance()

        self.expect(TokenType.LPAREN)
        objective = self.parse_expr()
        self.expect(TokenType.RPAREN)

        constraints: list[ASTNode] = []
        if self.current_token.token_type == TokenType.SUBJECT_TO:
            self.advance()
            self.expect(TokenType.LPAREN)

            # Parse constraint list
            constraints.append(self.parse_expr())
            while self.current_token.token_type == TokenType.COMMA:
                self.advance()
                constraints.append(self.parse_expr())

            self.expect(TokenType.RPAREN)

        return OptimizationNode(objective_type, objective, constraints)

    def parse_function_call(self) -> FunctionCallNode:
        """Parse function call: func(args, kwargs)."""
        function_name = self.current_token.value
        self.advance()

        self.expect(TokenType.LPAREN)

        args: list[ASTNode] = []
        kwargs: dict[str, ASTNode] = {}

        if self.current_token.token_type != TokenType.RPAREN:
            # Parse arguments
            while True:
                # Check for keyword argument
                if (
                    self.current_token.token_type == TokenType.IDENTIFIER
                    and self.peek().token_type == TokenType.ASSIGN
                ):
                    key = self.current_token.value
                    self.advance()
                    self.expect(TokenType.ASSIGN)
                    value = self.parse_expr()
                    kwargs[key] = value
                else:
                    args.append(self.parse_expr())

                if self.current_token.token_type != TokenType.COMMA:
                    break
                self.advance()

        self.expect(TokenType.RPAREN)

        return FunctionCallNode(function_name, args, kwargs)

    def parse_parameters(self) -> dict[str, Any]:
        """Parse parameter list: key=value, key=value."""
        parameters: dict[str, Any] = {}

        while True:
            if self.current_token.token_type != TokenType.IDENTIFIER:
                break

            key = self.current_token.value
            self.advance()

            self.expect(TokenType.ASSIGN)

            value_token = self.current_token
            if value_token.token_type in (
                TokenType.STRING,
                TokenType.INTEGER,
                TokenType.FLOAT,
                TokenType.BOOLEAN,
            ):
                parameters[key] = value_token.value
                self.advance()
            else:
                msg = f"Expected literal value, got {value_token.token_type.name}"
                raise ParseError(msg, value_token.position, value_token)

            if self.current_token.token_type != TokenType.COMMA:
                break
            self.advance()

        return parameters

    def parse_literal(self) -> LiteralNode:
        """Parse literal value."""
        token = self.current_token
        self.advance()

        type_map = {
            TokenType.STRING: "string",
            TokenType.INTEGER: "integer",
            TokenType.FLOAT: "float",
            TokenType.BOOLEAN: "boolean",
        }

        return LiteralNode(token.value, type_map[token.token_type])

    def parse_identifier(self) -> IdentifierNode:
        """Parse identifier."""
        token = self.current_token
        self.advance()
        return IdentifierNode(token.value)


def parse_query(query_string: str) -> ASTNode:
    """Parse HDQL query string and return AST.

    Args:
        query_string: HDQL query string

    Returns:
        AST root node

    Raises:
        ParseError: If query is malformed
    """
    lexer = Lexer(query_string)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
