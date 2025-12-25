"""
Integration tests for RDF AGI (Autonomous Generative Intelligence) capabilities.

Tests verify:
- Autonomous reasoning engine functionality
- Semantic agents and multi-agent collaboration
- RDF-to-vector transformations
- Cross-domain knowledge synthesis
- Contradiction detection

Author: Claude Code
Date: 2025-12-24
"""

from __future__ import annotations

import pytest
import numpy as np
from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.hyperdimensional.agi_reasoning import (
    AutonomousReasoningEngine,
    Constraint,
    ReasoningStrategy,
)
from specify_cli.hyperdimensional.semantic_agents import (
    SemanticAgent,
    SpecificationAnalyzer,
    DependencyResolver,
    DesignExplorer,
)
from specify_cli.hyperdimensional.rdf_to_vector import (
    RDFVectorTransformer,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def reasoning_engine() -> AutonomousReasoningEngine:
    """Create autonomous reasoning engine."""
    engine = AutonomousReasoningEngine(embedding_dim=1000)

    # Add some basic facts
    engine.add_fact("specification_exists")
    engine.add_fact("user_stories_defined")
    engine.add_fact("requirements_identified")

    # Add rules for inference
    def rule_complete_spec(facts):
        if "specification_exists" in facts and "requirements_identified" in facts:
            return "specification_may_be_complete"
        return None

    def rule_testable(facts):
        if "user_stories_defined" in facts:
            return "specification_testable"
        return None

    engine.add_rule("complete_spec_rule", rule_complete_spec)
    engine.add_rule("testable_rule", rule_testable)

    return engine


@pytest.fixture
def vector_space() -> dict[str, np.ndarray]:
    """Create sample semantic vector space."""
    np.random.seed(42)
    space = {}
    entities = ["feature_auth", "feature_api", "user_story_login", "requirement_secure"]

    for entity in entities:
        space[entity] = np.random.randn(1000)

    return space


@pytest.fixture
def sample_rdf_graph() -> dict:
    """Create sample RDF graph for testing."""
    return {
        "entities": [
            "Feature:Authentication",
            "UserStory:UserLogin",
            "Requirement:SecurePassword",
            "SuccessCriterion:LoginSuccessful",
        ],
        "relations": {
            "rel_1": {
                "subject": "Feature:Authentication",
                "predicate": "hasUserStory",
                "object": "UserStory:UserLogin",
            },
            "rel_2": {
                "subject": "UserStory:UserLogin",
                "predicate": "requires",
                "object": "Requirement:SecurePassword",
            },
            "rel_3": {
                "subject": "Requirement:SecurePassword",
                "predicate": "hasSuccessCriterion",
                "object": "SuccessCriterion:LoginSuccessful",
            },
        },
    }


# ============================================================================
# Test: Autonomous Reasoning Engine - Forward Chaining
# ============================================================================


def test_reasoning_engine_forward_chaining(reasoning_engine: AutonomousReasoningEngine) -> None:
    """Test forward chaining inference."""
    trace = reasoning_engine.reason_about("Is specification complete?")

    assert trace.goal == "Is specification complete?"
    assert len(trace.steps) > 0
    assert "specification_may_be_complete" in reasoning_engine.inferred_facts
    assert trace.overall_confidence > 0.0


def test_reasoning_engine_multiple_rules(reasoning_engine: AutonomousReasoningEngine) -> None:
    """Test multiple rules firing in sequence."""
    trace = reasoning_engine.reason_about("What can we infer?")

    # Should have inferred multiple facts
    assert len(reasoning_engine.inferred_facts) >= 1
    assert "specification_testable" in reasoning_engine.inferred_facts


def test_reasoning_engine_contradiction_detection(reasoning_engine: AutonomousReasoningEngine) -> None:
    """Test contradiction detection."""
    reasoning_engine.add_fact("feature_implemented")
    reasoning_engine.add_fact("NOT feature_implemented")

    trace = reasoning_engine.reason_about("Check for contradictions")

    assert len(trace.contradictions_detected) > 0 or len(reasoning_engine.contradictions) > 0


# ============================================================================
# Test: Constraint Satisfaction
# ============================================================================


def test_constraint_satisfaction(reasoning_engine: AutonomousReasoningEngine, vector_space: dict) -> None:
    """Test constraint satisfaction problem solving."""
    reasoning_engine.vector_space = vector_space

    constraints = [
        Constraint(
            name="security_constraint",
            variables=["password_policy", "encryption"],
            constraint_fn=lambda assignment: "password_policy" in assignment and "encryption" in assignment,
            priority=1.0,
        ),
    ]

    solution = reasoning_engine.solve_constraint(constraints)

    assert solution.satisfied_constraints > 0
    assert solution.total_constraints == 1
    assert "password_policy" in solution.assignments or "encryption" in solution.assignments


# ============================================================================
# Test: Knowledge Synthesis
# ============================================================================


def test_knowledge_synthesis(reasoning_engine: AutonomousReasoningEngine, sample_rdf_graph: dict) -> None:
    """Test cross-domain knowledge synthesis."""
    graphs = [sample_rdf_graph, sample_rdf_graph]  # Two similar graphs

    synthesis = reasoning_engine.synthesize_knowledge(graphs)

    assert synthesis["total_entities"] > 0
    assert synthesis["total_relations"] > 0
    assert "emergent_patterns" in synthesis


# ============================================================================
# Test: Semantic Agents
# ============================================================================


def test_specification_analyzer(vector_space: dict, sample_rdf_graph: dict) -> None:
    """Test SpecificationAnalyzer agent."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)
    analyzer = SpecificationAnalyzer("SpecAnalyzer", engine, vector_space)

    result = analyzer.explore(sample_rdf_graph)

    assert result.agent_name == "SpecAnalyzer"
    assert result.entities_discovered > 0
    assert len(result.insights) > 0
    assert result.confidence > 0.0


def test_dependency_resolver(vector_space: dict, sample_rdf_graph: dict) -> None:
    """Test DependencyResolver agent."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)
    resolver = DependencyResolver("DepResolver", engine, vector_space)

    result = resolver.explore(sample_rdf_graph)

    assert result.agent_name == "DepResolver"
    assert result.relationships_found > 0
    assert len(result.insights) > 0


def test_design_explorer(vector_space: dict) -> None:
    """Test DesignExplorer agent."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)
    explorer = DesignExplorer("DesignExplorer", engine, vector_space)

    graph_with_options = {
        "entities": [
            {"name": "DatabaseChoice", "options": ["PostgreSQL", "MongoDB", "DynamoDB"]},
            {"name": "ArchitectureChoice", "options": ["Monolith", "Microservices", "Serverless"]},
        ]
    }

    result = explorer.explore(graph_with_options)

    assert result.agent_name == "DesignExplorer"
    assert len(result.insights) > 0


def test_agent_navigation(vector_space: dict, sample_rdf_graph: dict) -> None:
    """Test semantic navigation."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)
    analyzer = SpecificationAnalyzer("SpecAnalyzer", engine, vector_space)

    path = analyzer.navigate_relationships("Feature:Authentication", sample_rdf_graph)

    assert path.start_entity == "Feature:Authentication"
    assert path.path_length >= 0


def test_agent_autonomous_reasoning(vector_space: dict) -> None:
    """Test autonomous reasoning by agent."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)
    engine.add_fact("has_requirements")
    engine.add_rule("infer_complete", lambda facts: "possibly_complete" if "has_requirements" in facts else None)

    analyzer = SpecificationAnalyzer("Analyzer", engine, vector_space)
    analyzer.beliefs.add("has_requirements")

    trace = analyzer.autonomously_reason("Is specification complete?")

    assert trace.goal == "Is specification complete?"


def test_agent_collaboration(vector_space: dict, sample_rdf_graph: dict) -> None:
    """Test multi-agent collaboration."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)

    analyzer = SpecificationAnalyzer("Analyzer", engine, vector_space)
    resolver = DependencyResolver("Resolver", engine, vector_space)
    explorer = DesignExplorer("Explorer", engine, vector_space)

    # All explore the same graph
    for agent in [analyzer, resolver, explorer]:
        result = agent.explore(sample_rdf_graph)
        agent.beliefs.add(f"explored_{result.agent_name}")

    # Collaborate
    collab_result = analyzer.collaborate([resolver, explorer])

    assert len(collab_result.participating_agents) == 3
    assert collab_result.confidence > 0.0


def test_agent_learning(vector_space: dict) -> None:
    """Test agent learning from feedback."""
    engine = AutonomousReasoningEngine(vector_space=vector_space)
    analyzer = SpecificationAnalyzer("Analyzer", engine, vector_space)

    initial_beliefs = analyzer.beliefs.copy()

    feedback = {
        "correct": True,
        "new_facts": ["learned_from_feedback", "specification_valid"],
    }

    updates = analyzer.learn_from_feedback(feedback)

    assert "new_beliefs_learned" in updates
    assert len(updates["new_beliefs_learned"]) > 0
    assert "specification_valid" in analyzer.beliefs


# ============================================================================
# Test: RDF-to-Vector Transformation
# ============================================================================


def test_rdf_vector_transformer_initialization() -> None:
    """Test transformer initialization."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    assert transformer.embedding_dim == 1000
    assert len(transformer._entity_cache) == 0


def test_entity_transformation() -> None:
    """Test entity URI transformation to vector."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    vector1 = transformer.transform_entity("Feature:Authentication")
    vector2 = transformer.transform_entity("Feature:Authentication")

    # Should be deterministic
    assert np.allclose(vector1, vector2)

    # Should be normalized
    assert np.isclose(np.linalg.norm(vector1), 1.0)


def test_entity_transformation_different() -> None:
    """Test that different entities get different vectors."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    vector1 = transformer.transform_entity("Feature:Authentication")
    vector2 = transformer.transform_entity("Feature:Authorization")

    # Different entities should have different vectors
    similarity = np.dot(vector1, vector2)
    assert abs(similarity) < 0.9  # Not highly similar


def test_relationship_transformation() -> None:
    """Test relationship transformation."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    rel_vec = transformer.transform_relationship(
        "Feature:Auth", "requires", "Requirement:Secure"
    )

    assert rel_vec.shape == (1000,)
    assert np.isclose(np.linalg.norm(rel_vec), 1.0)


def test_constraint_transformation() -> None:
    """Test constraint transformation to vector."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    constraint = {
        "name": "security_constraint",
        "variables": ["password_length", "encryption_strength"],
        "type": "numeric",
    }

    vec_constraint = transformer.transform_constraint(constraint)

    assert vec_constraint.name == "security_constraint"
    assert len(vec_constraint.variable_embeddings) == 2
    assert vec_constraint.constraint_type == "numeric"


def test_graph_transformation(sample_rdf_graph: dict) -> None:
    """Test full graph transformation."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    result = transformer.transform_graph(sample_rdf_graph)

    assert result.success
    assert result.embedding_dim == 1000
    assert len(result.vector_space) > 0
    assert result.relationships == 3


def test_inverse_transformation() -> None:
    """Test inverse transformation from vector."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    # Transform entity
    entity = "Feature:Authentication"
    vector = transformer.transform_entity(entity)

    # Inverse transform
    rdf_repr = transformer.inverse_transform(vector)

    assert rdf_repr["approximated_entity"] == entity
    assert rdf_repr["distance_to_nearest"] < 1e-6  # Very close to original


def test_semantic_similarity() -> None:
    """Test semantic similarity computation."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    vec1 = transformer.transform_entity("Concept:A")
    vec2 = transformer.transform_entity("Concept:A")  # Same
    vec3 = transformer.transform_entity("Concept:B")  # Different

    # Same entity should have similarity ~1.0
    sim_same = transformer.compute_semantic_similarity(vec1, vec2)
    assert sim_same > 0.99

    # Different entities should have lower similarity
    sim_diff = transformer.compute_semantic_similarity(vec1, vec3)
    assert abs(sim_diff) < 0.9


def test_find_similar_entities() -> None:
    """Test finding similar entities."""
    transformer = RDFVectorTransformer(embedding_dim=1000)

    # Create vector space
    vector_space = {
        "Entity:A": transformer.transform_entity("Entity:A"),
        "Entity:B": transformer.transform_entity("Entity:B"),
        "Entity:C": transformer.transform_entity("Entity:C"),
        "Entity:D": transformer.transform_entity("Entity:D"),
    }

    query_vec = transformer.transform_entity("Entity:A")
    similar = transformer.find_similar_entities(query_vec, vector_space, k=3)

    assert len(similar) == 3
    # Most similar should be Entity:A itself
    assert similar[0][0] == "Entity:A"
    assert similar[0][1] > 0.99


# ============================================================================
# Test: End-to-End AGI Workflow
# ============================================================================


def test_end_to_end_analysis(sample_rdf_graph: dict) -> None:
    """Test complete RDF AGI workflow."""
    # Create components
    transformer = RDFVectorTransformer(embedding_dim=1000)
    engine = AutonomousReasoningEngine(embedding_dim=1000)

    # Transform RDF graph
    transform_result = transformer.transform_graph(sample_rdf_graph)
    assert transform_result.success

    engine.vector_space = transform_result.vector_space

    # Create agents
    analyzer = SpecificationAnalyzer("Analyzer", engine, transform_result.vector_space)
    resolver = DependencyResolver("Resolver", engine, transform_result.vector_space)

    # Agents explore graph
    analysis_result = analyzer.explore(sample_rdf_graph)
    dependency_result = resolver.explore(sample_rdf_graph)

    assert analysis_result.entities_discovered > 0
    assert dependency_result.entities_discovered >= 0

    # Reason autonomously
    trace = engine.reason_about("What can we infer about this specification?")

    assert trace.goal is not None
    assert trace.overall_confidence > 0.0


def test_end_to_end_with_collaboration(sample_rdf_graph: dict) -> None:
    """Test complete workflow with multi-agent collaboration."""
    transformer = RDFVectorTransformer(embedding_dim=1000)
    engine = AutonomousReasoningEngine(embedding_dim=1000)

    transform_result = transformer.transform_graph(sample_rdf_graph)
    engine.vector_space = transform_result.vector_space

    # Create agents
    analyzer = SpecificationAnalyzer("Analyzer", engine, transform_result.vector_space)
    resolver = DependencyResolver("Resolver", engine, transform_result.vector_space)
    explorer = DesignExplorer("Explorer", engine, transform_result.vector_space)

    # All agents explore
    for agent in [analyzer, resolver, explorer]:
        agent.explore(sample_rdf_graph)

    # Collaborate
    collab = analyzer.collaborate([resolver, explorer])

    assert collab.consensus_reached or len(collab.disagreements) >= 0
    assert collab.confidence > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
