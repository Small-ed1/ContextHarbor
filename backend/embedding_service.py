import numpy as np
from sentence_transformers import SentenceTransformer
import os
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

class EmbeddingService:
    def __init__(self, model_name: str = "nomic-embed-text"):
        self.model_name = model_name
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def load_model(self):
        """Load the embedding model asynchronously"""
        if self.model is None:
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(self.executor, self._load_model_sync)

    def _load_model_sync(self):
        """Load model synchronously"""
        return SentenceTransformer(self.model_name)

    async def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings"""
        if self.model is None:
            await self.load_model()

        if self.model is None:
            raise RuntimeError("Failed to load embedding model")

        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            self.executor,
            lambda: self.model.encode(texts, convert_to_numpy=True).tolist()
        )
        return embeddings

    async def encode_text(self, text: str) -> List[float]:
        """Encode single text to embedding"""
        embeddings = await self.encode_texts([text])
        return embeddings[0]

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(vec1)
        b = np.array(vec2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Ollama embedding alternative (for when local models are preferred)
class OllamaEmbeddingService:
    def __init__(self, host: str = "http://127.0.0.1:11434", model: str = "nomic-embed-text"):
        self.host = host.rstrip("/")
        self.model = model
        self.client = None

    async def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """Encode texts using Ollama API"""
        import httpx

        embeddings = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for text in texts:
                response = await client.post(
                    f"{self.host}/api/embeddings",
                    json={"model": self.model, "prompt": text}
                )
                if response.status_code == 200:
                    data = response.json()
                    embeddings.append(data["embedding"])
                else:
                    raise Exception(f"Ollama embedding failed: {response.text}")
        return embeddings

    async def encode_text(self, text: str) -> List[float]:
        embeddings = await self.encode_texts([text])
        return embeddings[0]

# Global instance
embedding_service = EmbeddingService()

if __name__ == "__main__":
    import asyncio

    async def test():
        await embedding_service.load_model()
        embedding = await embedding_service.encode_text("Hello world")
        print(f"Embedding dimension: {len(embedding)}")

    asyncio.run(test())