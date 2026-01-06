import sqlite3
import json
from typing import List, Dict, Any, Optional, Tuple
from backend.database import Database
from backend.embedding_service import embedding_service
import numpy as np

class RAGService:
    def __init__(self, db: Database):
        self.db = db

    async def add_knowledge(self, content: str, source: str = "", metadata: Optional[Dict[str, Any]] = None, chunk_id: str = "") -> Optional[int]:
        """Add knowledge content to the database"""
        metadata_json = json.dumps(metadata or {})

        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (content, source, chunk_id, metadata)
                VALUES (?, ?, ?, ?)
            """, (content, source, chunk_id, metadata_json))
            knowledge_id = cursor.lastrowid

            # Generate and store embedding
            embedding = await embedding_service.encode_text(content)
            embedding_blob = np.array(embedding, dtype=np.float32).tobytes()

            cursor.execute("""
                INSERT INTO embeddings (knowledge_id, embedding, model)
                VALUES (?, ?, ?)
            """, (knowledge_id, embedding_blob, embedding_service.model_name))

            conn.commit()
            return knowledge_id if knowledge_id else None

    async def search_knowledge(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search knowledge using semantic similarity"""
        query_embedding = await embedding_service.encode_text(query)
        query_vec = np.array(query_embedding, dtype=np.float32)

        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT k.id, k.content, k.source, k.metadata, e.embedding
                FROM knowledge k
                JOIN embeddings e ON k.id = e.knowledge_id
                WHERE e.model = ?
            """, (embedding_service.model_name,))

            results = []
            for row in cursor.fetchall():
                knowledge_id, content, source, metadata_json, embedding_blob = row
                stored_vec = np.frombuffer(embedding_blob, dtype=np.float32)
                similarity = embedding_service.cosine_similarity(query_vec.tolist(), stored_vec.tolist())

                if similarity >= threshold:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    results.append({
                        "id": knowledge_id,
                        "content": content,
                        "source": source,
                        "metadata": metadata,
                        "similarity": similarity
                    })

            # Sort by similarity and limit
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]

    def search_knowledge_fts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback search using FTS5"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT k.id, k.content, k.source, k.metadata, bm25(knowledge_fts)
                FROM knowledge_fts
                JOIN knowledge k ON knowledge_fts.rowid = k.id
                WHERE knowledge_fts MATCH ?
                ORDER BY bm25(knowledge_fts)
                LIMIT ?
            """, (query, limit))

            results = []
            for row in cursor.fetchall():
                knowledge_id, content, source, metadata_json, score = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                results.append({
                    "id": knowledge_id,
                    "content": content,
                    "source": source,
                    "metadata": metadata,
                    "score": score
                })
            return results

    def export_knowledge(self) -> List[Dict[str, Any]]:
        """Export all knowledge for backup"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, source, chunk_id, metadata, created_at FROM knowledge")
            rows = cursor.fetchall()

            knowledge = []
            for row in rows:
                knowledge_id, content, source, chunk_id, metadata_json, created_at = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                knowledge.append({
                    "id": knowledge_id,
                    "content": content,
                    "source": source,
                    "chunk_id": chunk_id,
                    "metadata": metadata,
                    "created_at": created_at
                })
            return knowledge

    def import_knowledge(self, knowledge_data: List[Dict[str, Any]]):
        """Import knowledge from backup"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            for item in knowledge_data:
                metadata_json = json.dumps(item.get("metadata", {}))
                cursor.execute("""
                    INSERT OR REPLACE INTO knowledge (id, content, source, chunk_id, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item["id"],
                    item["content"],
                    item["source"],
                    item.get("chunk_id", ""),
                    metadata_json,
                    item.get("created_at")
                ))
            conn.commit()

    def maintenance_cleanup(self, days_old: int = 30):
        """Remove old, unused knowledge entries"""
        # This is a skeleton - implement based on usage tracking
        pass

# Content chunking utility
class ContentChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source: str = "") -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            chunks.append({
                "content": chunk_text,
                "source": source,
                "chunk_id": f"{source}_{i//(self.chunk_size - self.overlap)}",
                "metadata": {
                    "chunk_start": i,
                    "chunk_end": min(i + self.chunk_size, len(words)),
                    "total_words": len(words)
                }
            })

        return chunks

# Global instance
from backend.database import db
rag_service = RAGService(db)
chunker = ContentChunker()