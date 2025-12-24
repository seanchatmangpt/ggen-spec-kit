"""AGI system exception hierarchy.

Auto-generated from: ontology/agi-agent-schema.ttl
Constitutional equation: exceptions.py = μ(agi-agent-schema.ttl)
DO NOT EDIT MANUALLY - Edit the RDF source instead.
"""

from __future__ import annotations

from typing import Any, Optional


class AGIError(Exception):
    """Base exception for all AGI errors."""

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize AGI error.

        Parameters
        ----------
        message : str
            Error message
        context : dict[str, Any], optional
            Contextual information
        cause : Exception, optional
            Underlying exception
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.cause = cause


class PlanningError(AGIError):
    """Error in task planning."""

    pass


class PlanValidationError(PlanningError):
    """Error validating execution plan."""

    pass


class GoalDecompositionError(PlanningError):
    """Error decomposing goal into tasks."""

    pass


class ReasoningError(AGIError):
    """Error in reasoning operation."""

    pass


class PremiseValidationError(ReasoningError):
    """Error validating premise."""

    pass


class InferenceError(ReasoningError):
    """Error in inference step."""

    pass


class SynthesisError(AGIError):
    """Error in code synthesis."""

    pass


class SpecificationError(SynthesisError):
    """Error in specification."""

    pass


class CodeGenerationError(SynthesisError):
    """Error generating code."""

    pass


class CodeValidationError(SynthesisError):
    """Error validating generated code."""

    pass


class AgentError(AGIError):
    """Error related to agents."""

    pass


class AgentInitializationError(AgentError):
    """Error initializing agent."""

    pass


class TaskExecutionError(AgentError):
    """Error executing task."""

    pass


class AgentCommunicationError(AgentError):
    """Error in agent communication."""

    pass


class OrchestrationError(AGIError):
    """Error in orchestration."""

    pass


class WorkflowError(OrchestrationError):
    """Error in workflow execution."""

    pass


class ResourceAllocationError(OrchestrationError):
    """Error allocating resources."""

    pass


class DecisionError(AGIError):
    """Error in decision making."""

    pass


class CriterionError(DecisionError):
    """Error with decision criterion."""

    pass


class OptionEvaluationError(DecisionError):
    """Error evaluating option."""

    pass


class ConfigurationError(AGIError):
    """Configuration error."""

    pass


class ValidationError(AGIError):
    """General validation error."""

    pass


class TimeoutError(AGIError):
    """Operation timeout."""

    pass


def format_exception_chain(exc: Exception, indent: int = 0) -> str:
    """Format exception chain for display.

    Parameters
    ----------
    exc : Exception
        Exception to format
    indent : int, optional
        Indentation level

    Returns
    -------
    str
        Formatted exception chain
    """
    lines = []
    prefix = "  " * indent

    if isinstance(exc, AGIError):
        lines.append(f"{prefix}{type(exc).__name__}: {exc.message}")
        if exc.context:
            lines.append(f"{prefix}  Context: {exc.context}")
        if exc.cause:
            lines.append(f"{prefix}  Caused by:")
            lines.append(format_exception_chain(exc.cause, indent + 2))
    else:
        lines.append(f"{prefix}{type(exc).__name__}: {str(exc)}")

    return "\n".join(lines)
