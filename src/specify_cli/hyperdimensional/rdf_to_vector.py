"""
RDF to vector transformation pipeline for semantic reasoning.

This module provides transformation between RDF representations and
high-dimensional semantic vectors for autonomous reasoning.

Author: Claude Code
Date: 2025-12-24
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

Vector = NDArray[np.float64]


@dataclass
class TransformationResult:
    """Result of RDF to vector transformation."""

    success: bool
    vector_space: dict[str, Vector]
    entities: list[str]
    relationships: int
    embedding_dim: int


@dataclass
class VectorizedConstraint:
    """Constraint represented in vector space."""

    name: str
    vector_representation: Vector
    variable_embeddings: dict[str, Vector]
    constraint_type: str


class RDFVectorTransformer:
    """Transform RDF graphs to semantic vector spaces.

    Converts RDF entities, relationships, and constraints to high-dimensional
    vectors suitable for autonomous reasoning and inference.

    Attributes
    ----------
    embedding_dim : int
        Dimensionality of semantic space
    seed : int
        Random seed for reproducibility
    """

    def __init__(self, embedding_dim: int = 10000, seed: int = 42) -> None:
        """Initialize transformer.

        Parameters
        ----------
        embedding_dim : int
            Dimensionality of embedding space
        seed : int
            Random seed for reproducibility
        """
        self.embedding_dim = embedding_dim
        self.seed = seed
        np.random.seed(seed)
        self._entity_cache: dict[str, Vector] = {}

    def transform_graph(
        self, rdf_graph: dict[str, Any]
    ) -> TransformationResult:
        """Transform entire RDF graph to vector space.

        Parameters
        ----------
        rdf_graph : dict[str, Any]
            RDF graph with entities and relations

        Returns
        -------
        TransformationResult
            Vector space and transformation metadata
        """
        vector_space: dict[str, Vector] = {}
        entities = rdf_graph.get("entities", [])
        relations = rdf_graph.get("relations", {})

        # Transform each entity to vector
        for entity in entities:
            entity_name = str(entity)
            vector = self.transform_entity(entity_name)
            vector_space[entity_name] = vector

        # Transform relationships
        for rel_name, rel_data in relations.items():
            if isinstance(rel_data, dict):
                subject = rel_data.get("subject", "")
                predicate = rel_data.get("predicate", "")
                obj = rel_data.get("object", "")

                # Create relationship vector
                rel_vec = self.transform_relationship(subject, predicate, obj)
                vector_space[f"{subject}--{predicate}--{obj}"] = rel_vec

        result = TransformationResult(
            success=True,
            vector_space=vector_space,
            entities=list(vector_space.keys()),
            relationships=len(relations),
            embedding_dim=self.embedding_dim,
        )

        logger.info(
            f"Transformed {len(entities)} entities and "
            f"{len(relations)} relationships to vector space"
        )
        return result

    def transform_entity(self, entity_uri: str) -> Vector:
        """Transform RDF entity URI to semantic vector.

        Parameters
        ----------
        entity_uri : str
            URI of entity to transform

        Returns
        -------
        Vector
            Semantic vector representation
        """
        if entity_uri in self._entity_cache:
            return self._entity_cache[entity_uri]

        # Hash-based deterministic embedding
        hash_obj = hashlib.sha256(entity_uri.encode())
        hash_bytes = hash_obj.digest()

        # Create vector from hash
        np.random.seed(int.from_bytes(hash_bytes[:4], "big") % (2**31))
        vector = np.random.randn(self.embedding_dim).astype(np.float64)

        # Normalize to unit vector
        vector = vector / np.linalg.norm(vector)

        self._entity_cache[entity_uri] = vector
        return vector

    def transform_relationship(
        self, subject: str, predicate: str, obj: str
    ) -> Vector:
        """Transform RDF relationship to vector.

        In semantic space, relationships are encoded as vector operations:
        If subject ≈ s and object ≈ o, then relation ≈ s ⊙ predicate ⊙ o

        Parameters
        ----------
        subject : str
            Subject entity URI
        predicate : str
            Relationship predicate
        obj : str
            Object entity URI

        Returns
        -------
        Vector
            Vector representation of relationship
        """
        subject_vec = self.transform_entity(subject)
        object_vec = self.transform_entity(obj)
        predicate_vec = self.transform_entity(f"predicate:{predicate}")

        # Relationship encoded as: subject + predicate + object
        # (simplified binding operation)
        relationship = (subject_vec + predicate_vec + object_vec) / 3
        relationship = relationship / (np.linalg.norm(relationship) + 1e-8)

        return relationship

    def transform_constraint(self, constraint: dict[str, Any]) -> VectorizedConstraint:
        """Transform constraint to vector space representation.

        Parameters
        ----------
        constraint : dict[str, Any]
            Constraint specification with variables

        Returns
        -------
        VectorizedConstraint
            Constraint represented in vector space
        """
        name = constraint.get("name", "unknown")
        variables = constraint.get("variables", [])
        constraint_type = constraint.get("type", "generic")

        # Transform variables to vectors
        variable_embeddings: dict[str, Vector] = {}
        for var in variables:
            variable_embeddings[var] = self.transform_entity(f"var:{var}")

        # Create constraint vector (embedding of the constraint itself)
        constraint_str = f"constraint:{name}"
        constraint_vec = self.transform_entity(constraint_str)

        # Modify constraint vector based on variables
        for var_vec in variable_embeddings.values():
            constraint_vec = constraint_vec + 0.1 * var_vec

        constraint_vec = constraint_vec / (np.linalg.norm(constraint_vec) + 1e-8)

        return VectorizedConstraint(
            name=name,
            vector_representation=constraint_vec,
            variable_embeddings=variable_embeddings,
            constraint_type=constraint_type,
        )

    def inverse_transform(self, vector: Vector) -> dict[str, Any]:
        """Approximate inverse transformation from vector to RDF representation.

        Note: This is an approximation since semantic information is lossy.

        Parameters
        ----------
        vector : Vector
            Vector to inverse transform

        Returns
        -------
        dict[str, Any]
            Approximated RDF representation
        """
        # Find nearest entity in cache
        nearest_entity = None
        nearest_distance = float("inf")

        for entity, cached_vec in self._entity_cache.items():
            distance = np.linalg.norm(vector - cached_vec)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_entity = entity

        # Also compute semantic similarity of vector to itself
        similarity = float(np.dot(vector, vector) / (np.linalg.norm(vector) + 1e-8))

        rdf_repr = {
            "approximated_entity": nearest_entity,
            "distance_to_nearest": float(nearest_distance),
            "semantic_signature": float(similarity),
            "confidence": max(0.0, 1.0 - nearest_distance) if nearest_entity else 0.0,
        }

        return rdf_repr

    def compute_semantic_similarity(
        self, vector1: Vector, vector2: Vector
    ) -> float:
        """Compute cosine similarity between two vectors.

        Parameters
        ----------
        vector1 : Vector
            First vector
        vector2 : Vector
            Second vector

        Returns
        -------
        float
            Cosine similarity (-1 to 1)
        """
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        if norm1 < 1e-8 or norm2 < 1e-8:
            return 0.0

        return float(np.dot(vector1, vector2) / (norm1 * norm2))

    def find_similar_entities(
        self, vector: Vector, vector_space: dict[str, Vector], k: int = 5
    ) -> list[tuple[str, float]]:
        """Find k most similar entities to a given vector.

        Parameters
        ----------
        vector : Vector
            Query vector
        vector_space : dict[str, Vector]
            Space of entity vectors
        k : int
            Number of results to return

        Returns
        -------
        list[tuple[str, float]]
            List of (entity, similarity) pairs
        """
        similarities: list[tuple[str, float]] = []

        for entity_name, entity_vec in vector_space.items():
            sim = self.compute_semantic_similarity(vector, entity_vec)
            similarities.append((entity_name, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:k]
