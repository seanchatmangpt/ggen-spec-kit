"""
specify_cli.hyperdimensional.embedding_store
--------------------------------------------
RDF-based persistent storage for hyperdimensional embeddings.

This module provides RDF persistence for embeddings, allowing:
- Storage of embeddings in Turtle (TTL) format
- Semantic traceability via RDF relationships
- Version management and integrity verification
- Efficient batch operations

The RDF schema maps embeddings to the spec-kit ontology, enabling
SPARQL queries over the embedding space and integration with ggen
transformation pipelines.

Classes
-------
EmbeddingStore
    RDF-based storage with save/load operations
EmbeddingMetadata
    Metadata for embedding versioning and checksums

Example
-------
    >>> from specify_cli.hyperdimensional import HyperdimensionalEmbedding, EmbeddingStore
    >>> hde = HyperdimensionalEmbedding(dimensions=10000)
    >>> store = EmbeddingStore()
    >>>
    >>> # Create embeddings
    >>> init_cmd = hde.embed_command("init")
    >>> store.save_embedding("command:init", init_cmd, metadata={"version": "0.0.25"})
    >>>
    >>> # Save to RDF
    >>> store.save_to_rdf("memory/embeddings.ttl")
    >>>
    >>> # Load from RDF
    >>> loaded_store = EmbeddingStore.load_from_rdf("memory/embeddings.ttl")
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from specify_cli.hyperdimensional.embeddings import Vector, VectorDict

# Optional RDF support (graceful degradation)
try:
    from rdflib import RDF, Graph, Literal, Namespace, URIRef
    from rdflib.namespace import XSD

    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False


@dataclass
class EmbeddingMetadata:
    """Metadata for an embedding.

    Attributes
    ----------
    entity_name : str
        Full entity name (e.g., "command:init")
    dimensions : int
        Vector dimensionality
    created : datetime
        Creation timestamp
    checksum : str
        SHA256 checksum of vector data
    version : str
        Version tag (e.g., "0.0.25")
    tags : list[str]
        Semantic tags for categorization
    """

    entity_name: str
    dimensions: int
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    checksum: str = ""
    version: str = "0.0.1"
    tags: list[str] = field(default_factory=list)


class EmbeddingStore:
    """RDF-based persistent storage for embeddings.

    This class manages the storage and retrieval of hyperdimensional embeddings
    in RDF/Turtle format, providing semantic traceability and version control.

    Parameters
    ----------
    namespace : str, optional
        RDF namespace URI (default: spec-kit namespace)

    Attributes
    ----------
    embeddings : VectorDict
        Mapping of entity_name → vector
    metadata : dict[str, EmbeddingMetadata]
        Metadata for each embedding
    graph : Graph | None
        RDF graph (if rdflib available)

    Example
    -------
    >>> store = EmbeddingStore()
    >>> store.save_embedding("command:init", init_vector)
    >>> store.save_to_rdf("memory/embeddings.ttl")
    """

    def __init__(self, namespace: str = "http://github.com/github/spec-kit#") -> None:
        """Initialize embedding store."""
        self.embeddings: VectorDict = {}
        self.metadata: dict[str, EmbeddingMetadata] = {}
        self.namespace = namespace

        if RDFLIB_AVAILABLE:
            self.graph = Graph()
            self.ns = Namespace(namespace)
        else:
            self.graph = None
            self.ns = None

    def _compute_checksum(self, vector: Vector) -> str:
        """Compute SHA256 checksum of vector.

        Parameters
        ----------
        vector : Vector
            Input vector

        Returns
        -------
        str
            Hexadecimal checksum
        """
        vector_bytes = vector.tobytes()
        return hashlib.sha256(vector_bytes).hexdigest()

    def save_embedding(
        self,
        entity_name: str,
        vector: Vector,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save embedding with metadata.

        Parameters
        ----------
        entity_name : str
            Full entity name (e.g., "command:init")
        vector : Vector
            Embedding vector
        metadata : dict[str, Any], optional
            Additional metadata fields

        Example
        -------
        >>> store.save_embedding(
        ...     "command:init",
        ...     init_vector,
        ...     metadata={"version": "0.0.25", "tags": ["setup"]}
        ... )
        """
        # Store vector
        self.embeddings[entity_name] = vector

        # Create metadata
        meta = EmbeddingMetadata(
            entity_name=entity_name,
            dimensions=len(vector),
            checksum=self._compute_checksum(vector),
        )

        # Apply additional metadata
        if metadata:
            if "version" in metadata:
                meta.version = metadata["version"]
            if "tags" in metadata:
                meta.tags = metadata["tags"]

        self.metadata[entity_name] = meta

    def get_embedding(self, entity_name: str) -> Vector | None:
        """Retrieve embedding by entity name.

        Parameters
        ----------
        entity_name : str
            Full entity name

        Returns
        -------
        Vector | None
            Embedding vector if found, None otherwise
        """
        return self.embeddings.get(entity_name)

    def get_metadata(self, entity_name: str) -> EmbeddingMetadata | None:
        """Retrieve metadata for entity.

        Parameters
        ----------
        entity_name : str
            Full entity name

        Returns
        -------
        EmbeddingMetadata | None
            Metadata if found, None otherwise
        """
        return self.metadata.get(entity_name)

    def save_to_rdf(self, filepath: Path | str) -> None:
        """Save embeddings to RDF/Turtle file.

        Parameters
        ----------
        filepath : Path | str
            Output file path

        Raises
        ------
        ImportError
            If rdflib is not available
        """
        if not RDFLIB_AVAILABLE:
            raise ImportError("rdflib required for RDF persistence. Install with: uv add rdflib")

        if self.graph is None or self.ns is None:
            raise RuntimeError("RDF graph not initialized")

        # Clear existing graph
        self.graph = Graph()
        self.ns = Namespace(self.namespace)

        # Bind namespaces
        self.graph.bind("sk", self.ns)
        self.graph.bind("xsd", XSD)

        # Add embeddings to graph
        for entity_name, vector in self.embeddings.items():
            entity_uri = URIRef(self.ns[entity_name.replace(":", "_")])
            meta = self.metadata.get(entity_name)

            # Add type
            self.graph.add((entity_uri, RDF.type, self.ns.Embedding))

            # Add entity name
            self.graph.add((entity_uri, self.ns.entityName, Literal(entity_name)))

            # Add dimensions
            self.graph.add(
                (entity_uri, self.ns.dimensions, Literal(len(vector), datatype=XSD.integer))
            )

            # Add vector data (as JSON array literal)
            vector_json = "[" + ",".join(f"{x:.6f}" for x in vector) + "]"
            self.graph.add((entity_uri, self.ns.vectorData, Literal(vector_json)))

            # Add metadata if available
            if meta:
                self.graph.add((entity_uri, self.ns.checksum, Literal(meta.checksum)))
                self.graph.add((entity_uri, self.ns.version, Literal(meta.version)))
                self.graph.add(
                    (
                        entity_uri,
                        self.ns.created,
                        Literal(meta.created.isoformat(), datatype=XSD.dateTime),
                    )
                )

                # Add tags
                for tag in meta.tags:
                    self.graph.add((entity_uri, self.ns.tag, Literal(tag)))

        # Serialize to Turtle
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        self.graph.serialize(destination=str(filepath), format="turtle")

    @classmethod
    def load_from_rdf(cls, filepath: Path | str) -> EmbeddingStore:
        """Load embeddings from RDF/Turtle file.

        Parameters
        ----------
        filepath : Path | str
            Input file path

        Returns
        -------
        EmbeddingStore
            Loaded embedding store

        Raises
        ------
        ImportError
            If rdflib is not available
        FileNotFoundError
            If file doesn't exist
        """
        if not RDFLIB_AVAILABLE:
            raise ImportError("rdflib required for RDF persistence. Install with: uv add rdflib")

        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Embedding file not found: {filepath}")

        # Create store
        store = cls()
        if store.graph is None or store.ns is None:
            raise RuntimeError("RDF graph not initialized")

        # Parse RDF file
        store.graph.parse(str(filepath), format="turtle")

        # Extract embeddings
        for subj in store.graph.subjects(RDF.type, store.ns.Embedding):
            # Get entity name
            entity_name_literal = store.graph.value(subj, store.ns.entityName)
            if entity_name_literal is None:
                continue
            entity_name = str(entity_name_literal)

            # Get vector data
            vector_json_literal = store.graph.value(subj, store.ns.vectorData)
            if vector_json_literal is None:
                continue
            vector_json = str(vector_json_literal)

            # Parse vector JSON
            vector_list = json.loads(vector_json)
            vector = np.array(vector_list, dtype=np.float64)

            # Get metadata
            checksum_literal = store.graph.value(subj, store.ns.checksum)
            version_literal = store.graph.value(subj, store.ns.version)
            created_literal = store.graph.value(subj, store.ns.created)
            dimensions_literal = store.graph.value(subj, store.ns.dimensions)

            meta = EmbeddingMetadata(
                entity_name=entity_name,
                dimensions=int(dimensions_literal) if dimensions_literal else len(vector),
                checksum=str(checksum_literal) if checksum_literal else "",
                version=str(version_literal) if version_literal else "0.0.1",
            )

            if created_literal:
                meta.created = datetime.fromisoformat(str(created_literal))

            # Get tags
            for tag_literal in store.graph.objects(subj, store.ns.tag):
                meta.tags.append(str(tag_literal))

            # Store
            store.embeddings[entity_name] = vector
            store.metadata[entity_name] = meta

        return store

    def verify_checksums(self) -> dict[str, bool]:
        """Verify checksums for all embeddings.

        Returns
        -------
        dict[str, bool]
            Mapping of entity_name → checksum_valid
        """
        results: dict[str, bool] = {}
        for entity_name, vector in self.embeddings.items():
            meta = self.metadata.get(entity_name)
            if meta is None:
                results[entity_name] = False
                continue

            computed = self._compute_checksum(vector)
            results[entity_name] = computed == meta.checksum

        return results

    def filter_by_prefix(self, prefix: str) -> VectorDict:
        """Filter embeddings by entity name prefix.

        Parameters
        ----------
        prefix : str
            Entity name prefix (e.g., "command:", "job:")

        Returns
        -------
        VectorDict
            Filtered embeddings
        """
        return {name: vec for name, vec in self.embeddings.items() if name.startswith(prefix)}

    def get_all_commands(self) -> VectorDict:
        """Get all command embeddings.

        Returns
        -------
        VectorDict
            Command embeddings
        """
        return self.filter_by_prefix("command:")

    def get_all_jobs(self) -> VectorDict:
        """Get all job embeddings.

        Returns
        -------
        VectorDict
            Job embeddings
        """
        return self.filter_by_prefix("job:")

    def get_all_outcomes(self) -> VectorDict:
        """Get all outcome embeddings.

        Returns
        -------
        VectorDict
            Outcome embeddings
        """
        return self.filter_by_prefix("outcome:")

    def get_all_features(self) -> VectorDict:
        """Get all feature embeddings.

        Returns
        -------
        VectorDict
            Feature embeddings
        """
        return self.filter_by_prefix("feature:")

    def get_all_constraints(self) -> VectorDict:
        """Get all constraint embeddings.

        Returns
        -------
        VectorDict
            Constraint embeddings
        """
        return self.filter_by_prefix("constraint:")

    def clear(self) -> None:
        """Clear all embeddings and metadata."""
        self.embeddings.clear()
        self.metadata.clear()

    def __len__(self) -> int:
        """Return number of stored embeddings."""
        return len(self.embeddings)

    def __contains__(self, entity_name: str) -> bool:
        """Check if entity embedding exists."""
        return entity_name in self.embeddings


__all__ = [
    "RDFLIB_AVAILABLE",
    "EmbeddingMetadata",
    "EmbeddingStore",
]
