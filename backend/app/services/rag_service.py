import os
import numpy as np
import logging
import requests
import json
from typing import List, Dict, Any

logger = logging.getLogger("uvicorn.error")

# Configure target local Ollama service URL running inside your docker network mesh
OLLAMA_EMBED_URL = "http://ollama:11434/api/embeddings"
EMBED_MODEL = "all-minilm" # Or whichever light embedding model you pulled in Ollama

class RAGKnowledgeService:
    def __init__(self):
        # In-memory document vector registry matrix store
        self.vector_index: List[Dict[str, Any]] = []

    def _get_embedding(self, text: str) -> List[float]:
        """Calls the local Ollama container network to get vector text embeddings."""
        try:
            response = requests.post(
                OLLAMA_EMBED_URL,
                json={"model": EMBED_MODEL, "prompt": text},
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
            return [0.0] * 384 # Fallback zero vector baseline
        except Exception as e:
            logger.warning(f"⚠️ Ollama embedding extraction timed out or failed: {str(e)}")
            return [0.0] * 384

    def ingest_document_text(self, filename: str, full_text: str):
        """Splits documents into clean semantic blocks and computes their vector weights."""
        logger.info(f"📄 RAG Engine: Ingesting text content matrix from {filename}")
        
        # Simple text chunking by paragraph or length bounds (approx 500 chars)
        chunks = [full_text[i:i+500] for i in range(0, len(full_text), 400)]
        
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            embedding = self._get_embedding(chunk)
            self.vector_index.append({
                "filename": filename,
                "chunk_id": idx,
                "text": chunk,
                "vector": embedding
            })
        logger.info(f"✅ Successfully registered {len(chunks)} text chunk vector maps.")

    def query_relevant_context(self, user_query: str, limit: int = 3) -> str:
        """Computes cosine similarity against the database to fetch matches."""
        if not self.vector_index:
            return "No company handbook documents have been uploaded to system storage yet."

        query_vector = np.array(self._get_embedding(user_query))
        scores = []

        for item in self.vector_index:
            item_vector = np.array(item["vector"])
            # Calculate cosine similarity formula dot(A, B) / (norm(A) * norm(B)) cleanly
            if np.linalg.norm(query_vector) == 0 or np.linalg.norm(item_vector) == 0:
                similarity = 0.0
            else:
                similarity = np.dot(query_vector, item_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(item_vector))
            scores.append((similarity, item["text"]))

        # Sort matches descending by rank score
        scores.sort(key=lambda x: x[0], reverse=True)
        top_matches = [text for score, text in scores[:limit] if score > 0.1]
        
        if not top_matches:
            return "No text records matched the contextual profile signature."
            
        return "\n---\n".join(top_matches)

# Instantiate the singleton vector manager service
rag_knowledge_service = RAGKnowledgeService()