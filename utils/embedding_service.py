"""
Embedding Service for Document Q&A System
Handles text embedding generation using sentence-transformers.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import pickle
from dataclasses import dataclass

# Import embedding libraries
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    torch = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "multi-qa-mpnet-base-dot-v1"  # Good for semantic search
    device: str = "auto"  # auto, cpu, cuda
    cache_directory: str = "data/embedding_cache"
    max_seq_length: int = 512
    normalize_embeddings: bool = True


class EmbeddingCache:
    """Cache for embeddings to avoid recomputation."""

    def __init__(self, cache_dir: str = "data/embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding for text."""
        if not NUMPY_AVAILABLE:
            return None

        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {e}")
                return None
        return None

    def set(self, text: str, embedding: np.ndarray):
        """Cache embedding for text."""
        if not NUMPY_AVAILABLE:
            return

        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.model = None
        self.cache = EmbeddingCache(config.cache_directory)
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
            return

        try:
            # Determine device
            device = self.config.device
            if device == "auto":
                device = "cuda" if torch and torch.cuda.is_available() else "cpu"

            logger.info(f"Loading embedding model: {self.config.model_name} on {device}")

            self.model = SentenceTransformer(self.config.model_name, device=device)

            # Set max sequence length
            if hasattr(self.model, 'max_seq_length'):
                self.model.max_seq_length = self.config.max_seq_length

            logger.info(f"Model loaded successfully. Dimension: {self.model.get_sentence_embedding_dimension()}")

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None

    def is_available(self) -> bool:
        """Check if the embedding service is available."""
        return self.model is not None

    def encode_text(self, text: str, use_cache: bool = True) -> Optional[np.ndarray]:
        """Encode a single text into an embedding vector."""
        if not self.is_available() or not NUMPY_AVAILABLE:
            return None

        # Check cache first
        if use_cache:
            cached = self.cache.get(text)
            if cached is not None:
                return cached

        try:
            # Generate embedding
            embedding = self.model.encode(text, normalize_embeddings=self.config.normalize_embeddings)

            # Cache the result
            if use_cache:
                self.cache.set(text, embedding)

            return embedding

        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            return None

    def encode_batch(self, texts: List[str], batch_size: int = 32, use_cache: bool = True) -> List[Optional[np.ndarray]]:
        """Encode multiple texts into embeddings."""
        if not self.is_available() or not NUMPY_AVAILABLE:
            return [None] * len(texts)

        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # Check cache for each text
        if use_cache:
            for i, text in enumerate(texts):
                cached = self.cache.get(text)
                if cached is not None:
                    embeddings.append(cached)
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)

        # Encode uncached texts in batches
        if uncached_texts:
            try:
                logger.info(f"Encoding {len(uncached_texts)} texts in batches of {batch_size}")

                # Process in batches
                for i in range(0, len(uncached_texts), batch_size):
                    batch_texts = uncached_texts[i:i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch_texts,
                        normalize_embeddings=self.config.normalize_embeddings,
                        batch_size=batch_size
                    )

                    # Store results and cache
                    for j, embedding in enumerate(batch_embeddings):
                        text_idx = i + j
                        global_idx = uncached_indices[text_idx]
                        embeddings[global_idx] = embedding

                        if use_cache:
                            self.cache.set(uncached_texts[text_idx], embedding)

                logger.info(f"Successfully encoded {len(uncached_texts)} texts")

            except Exception as e:
                logger.error(f"Failed to encode batch: {e}")
                # Fill failed embeddings with None
                for idx in uncached_indices:
                    if embeddings[idx] is None:
                        embeddings[idx] = None

        return embeddings

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.is_available():
            return {"available": False}

        return {
            "available": True,
            "model_name": self.config.model_name,
            "dimension": self.model.get_sentence_embedding_dimension(),
            "max_seq_length": self.config.max_seq_length,
            "device": str(self.model.device),
            "normalize_embeddings": self.config.normalize_embeddings,
        }


class DocumentEmbeddingService:
    """Service for embedding document chunks."""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def embed_chunks(self, chunks: List[Any], batch_size: int = 32) -> List[Dict[str, Any]]:
        """Embed document chunks and return with embeddings."""
        if not chunks:
            return []

        # Extract texts from chunks
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings
        embeddings = self.embedding_service.encode_batch(texts, batch_size=batch_size)

        # Combine chunks with embeddings
        result = []
        for chunk, embedding in zip(chunks, embeddings):
            if embedding is not None:
                result.append({
                    "chunk": chunk,
                    "embedding": embedding,
                    "embedding_available": True,
                })
            else:
                result.append({
                    "chunk": chunk,
                    "embedding": None,
                    "embedding_available": False,
                })

        successful_embeddings = sum(1 for r in result if r["embedding_available"])
        logger.info(f"Embedded {successful_embeddings}/{len(chunks)} chunks")

        return result

    def embed_query(self, query: str) -> Optional[np.ndarray]:
        """Embed a search query."""
        return self.embedding_service.encode_text(query, use_cache=True)


# Global embedding service instance
_embedding_service = None

def get_embedding_service(config: Optional[EmbeddingConfig] = None) -> EmbeddingService:
    """Get or create global embedding service instance."""
    global _embedding_service

    if _embedding_service is None:
        if config is None:
            config = EmbeddingConfig()
        _embedding_service = EmbeddingService(config)

    return _embedding_service