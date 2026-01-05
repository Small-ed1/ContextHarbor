"""
Vector Store Module for Document Q&A System
Provides FAISS-based vector storage and retrieval for document embeddings.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import faiss

logger = logging.getLogger(__name__)


class VectorStoreConfig:
    """Configuration for vector store."""

    def __init__(
        self,
        dimension: int = 768,  # Default for sentence-transformers
        index_type: str = "IndexFlatIP",  # Inner product (cosine similarity)
        persist_directory: str = "data/vector_store",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.dimension = dimension
        self.index_type = index_type
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


class VectorStore:
    """FAISS-based vector store for document embeddings."""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self.persist_directory = Path(config.persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize index
        self._initialize_index()

        # Load existing data if available
        self._load_persisted_data()

    def _initialize_index(self):
        """Initialize the FAISS index."""
        if self.config.index_type == "IndexFlatIP":
            # Inner product for cosine similarity (normalized vectors)
            self.index = faiss.IndexFlatIP(self.config.dimension)
        elif self.config.index_type == "IndexIVFFlat":
            # IVF with flat quantization for larger datasets
            quantizer = faiss.IndexFlatIP(self.config.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.config.dimension, 100)
        else:
            raise ValueError(f"Unsupported index type: {self.config.index_type}")

        logger.info(f"Initialized FAISS index: {self.config.index_type}")

    def _load_persisted_data(self):
        """Load persisted index and metadata."""
        index_path = self.persist_directory / "vector_index.faiss"
        metadata_path = self.persist_directory / "metadata.json"

        if index_path.exists():
            try:
                self.index = faiss.read_index(str(index_path))
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
                # Reinitialize empty index
                self._initialize_index()

        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.metadata)} documents")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                self.metadata = []

    def _save_persisted_data(self):
        """Save index and metadata to disk."""
        try:
            # Save index
            index_path = self.persist_directory / "vector_index.faiss"
            faiss.write_index(self.index, str(index_path))

            # Save metadata
            metadata_path = self.persist_directory / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)

            logger.debug("Persisted vector store data")
        except Exception as e:
            logger.error(f"Failed to persist data: {e}")

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add vectors and their metadata to the store.

        Args:
            vectors: Numpy array of shape (n, dimension)
            metadata: List of metadata dictionaries for each vector
        """
        if vectors.shape[0] != len(metadata):
            raise ValueError("Number of vectors must match number of metadata entries")

        if vectors.shape[1] != self.config.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.config.dimension}")

        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        vectors_normalized = vectors / norms

        # Add to index
        self.index.add(vectors_normalized.astype(np.float32))
        self.metadata.extend(metadata)

        # Persist changes
        self._save_persisted_data()

        logger.info(f"Added {len(vectors)} vectors to index")

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors with advanced options.

        Args:
            query_vector: Query vector of shape (dimension,)
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            filters: Optional metadata filters

        Returns:
            List of (metadata, score) tuples, sorted by relevance
        """
        if self.index.ntotal == 0:
            return []

        # Normalize query vector
        norm = np.linalg.norm(query_vector)
        if norm == 0:
            return []
        query_normalized = query_vector / norm

        # Search with expanded k to account for filtering
        search_k = min(k * 3, self.index.ntotal)  # Get more results for filtering
        scores, indices = self.index.search(
            query_normalized.reshape(1, -1).astype(np.float32),
            search_k
        )

        # Process results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= len(self.metadata):
                continue

            metadata = self.metadata[idx]
            similarity_score = float(score)

            # Apply filters
            if filters:
                if not self._matches_filters(metadata, filters):
                    continue

            # Apply score threshold
            if similarity_score < score_threshold:
                continue

            results.append((metadata, similarity_score))

        # Sort by score (descending) and take top k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the given filters."""
        for key, value in filters.items():
            if key not in metadata:
                return False

            metadata_value = metadata[key]

            # Handle different filter types
            if isinstance(value, list):
                # OR condition - metadata value must be in the list
                if metadata_value not in value:
                    return False
            elif isinstance(value, dict):
                # Range or complex conditions
                if "min" in value and metadata_value < value["min"]:
                    return False
                if "max" in value and metadata_value > value["max"]:
                    return False
                if "in" in value and metadata_value not in value["in"]:
                    return False
            else:
                # Exact match
                if metadata_value != value:
                    return False

        return True

    def search_with_expansion(
        self,
        query_vector: np.ndarray,
        expansion_terms: List[np.ndarray],
        k: int = 5,
        expansion_weight: float = 0.3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search with query expansion for better results.

        Args:
            query_vector: Main query vector
            expansion_terms: Additional related vectors
            k: Number of results to return
            expansion_weight: Weight for expansion terms (0-1)

        Returns:
            Combined search results
        """
        if not expansion_terms:
            return self.search(query_vector, k)

        # Search with main query
        main_results = self.search(query_vector, k * 2)

        # Search with expansion terms
        expansion_results = []
        for expansion_vector in expansion_terms[:3]:  # Limit expansion terms
            results = self.search(expansion_vector, k)
            expansion_results.extend(results)

        # Combine and rerank results
        combined_scores = {}

        # Add main query scores
        for metadata, score in main_results:
            doc_id = metadata.get("document_id", metadata.get("id", str(id(metadata))))
            combined_scores[doc_id] = {
                "metadata": metadata,
                "score": score * (1 - expansion_weight)
            }

        # Add expansion scores
        for metadata, score in expansion_results:
            doc_id = metadata.get("document_id", metadata.get("id", str(id(metadata))))
            if doc_id in combined_scores:
                combined_scores[doc_id]["score"] += score * expansion_weight
            else:
                combined_scores[doc_id] = {
                    "metadata": metadata,
                    "score": score * expansion_weight
                }

        # Sort and return top k
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return [(item["metadata"], item["score"]) for item in sorted_results[:k]]

    def get_relevance_score(self, query_vector: np.ndarray, doc_vector: np.ndarray) -> float:
        """Calculate relevance score between query and document vectors."""
        if not NUMPY_AVAILABLE:
            return 0.0

        # Cosine similarity
        dot_product = np.dot(query_vector, doc_vector)
        query_norm = np.linalg.norm(query_vector)
        doc_norm = np.linalg.norm(doc_vector)

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot_product / (query_norm * doc_norm)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        total_vectors = self.index.ntotal if self.index else 0
        total_documents = len(set(m.get("document_id") for m in self.metadata if m.get("document_id")))

        return {
            "total_vectors": total_vectors,
            "dimension": self.config.dimension,
            "index_type": self.config.index_type,
            "total_documents": total_documents,
            "is_trained": getattr(self.index, 'is_trained', lambda: True)() if hasattr(self.index, 'is_trained') else True,
            "index_size_mb": self._estimate_index_size(),
        }

    def _estimate_index_size(self) -> float:
        """Estimate the memory size of the index in MB."""
        if not self.index:
            return 0.0

        # Rough estimation based on FAISS index types
        if hasattr(self.index, 'ntotal') and hasattr(self.index, 'd'):
            # For flat indices, roughly ntotal * d * 4 bytes (float32)
            size_bytes = self.index.ntotal * self.index.d * 4
        else:
            size_bytes = 0

        return size_bytes / (1024 * 1024)

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the vector store."""
        issues = []
        status = "healthy"

        try:
            # Check if index exists
            if not self.index:
                issues.append("Index not initialized")
                status = "unhealthy"
                return {"status": status, "issues": issues}

            # Check index integrity
            if self.index.ntotal < 0:
                issues.append("Invalid index state")
                status = "unhealthy"

            # Check metadata consistency
            if len(self.metadata) != self.index.ntotal:
                issues.append(f"Metadata count ({len(self.metadata)}) doesn't match index size ({self.index.ntotal})")
                status = "warning"

            # Check persistence directory
            if not self.persist_directory.exists():
                issues.append("Persistence directory missing")
                status = "warning"

            # Check if we can perform a basic search
            if self.index.ntotal > 0:
                try:
                    # Create a test query vector
                    test_vector = np.random.rand(self.config.dimension).astype(np.float32)
                    self.index.search(test_vector.reshape(1, -1), min(1, self.index.ntotal))
                except Exception as e:
                    issues.append(f"Search test failed: {str(e)}")
                    status = "unhealthy"

        except Exception as e:
            issues.append(f"Health check failed: {str(e)}")
            status = "error"

        return {
            "status": status,
            "issues": issues,
            "stats": self.get_stats(),
            "timestamp": str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else None,
        }

    def clear(self):
        """Clear all vectors and metadata."""
        self._initialize_index()
        self.metadata = []
        self._save_persisted_data()
        logger.info("Cleared vector store")


class VectorStoreManager:
    """Manager for multiple vector stores."""

    def __init__(self, base_directory: str = "data/vector_stores"):
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)
        self.stores: Dict[str, VectorStore] = {}

    def get_or_create_store(self, store_name: str, config: Optional[VectorStoreConfig] = None) -> VectorStore:
        """Get or create a vector store by name."""
        if store_name not in self.stores:
            if config is None:
                config = VectorStoreConfig(persist_directory=str(self.base_directory / store_name))
            else:
                config.persist_directory = str(self.base_directory / store_name)

            self.stores[store_name] = VectorStore(config)

        return self.stores[store_name]

    def list_stores(self) -> List[str]:
        """List all available stores."""
        return list(self.stores.keys())

    def save_all(self):
        """Save all stores."""
        for store in self.stores.values():
            store._save_persisted_data()