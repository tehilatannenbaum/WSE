import os
import re
import httpx
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.app.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)

# Constants
KB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "knowledge_base",
    "travel_info.txt"
)

# Global variables for simple search
KB_CHUNKS = []
EMBEDDING_MODEL = None
CHUNK_EMBEDDINGS = None

def init_rag():
    global KB_CHUNKS, EMBEDDING_MODEL, CHUNK_EMBEDDINGS
    
    # 1. Load Knowledge Base
    if not os.path.exists(KB_PATH):
        logger.warning(f"Knowledge base file not found at {KB_PATH}. AI Advisor will run with empty KB.")
        return
        
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Split content by sections
        sections = re.split(r"\[SECTION:", content)
        chunks = []
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
            # Reconstruct section text
            chunks.append("[SECTION: " + sec)
            
        KB_CHUNKS = chunks
        logger.info(f"Loaded {len(KB_CHUNKS)} knowledge base chunks from {KB_PATH}")
    except Exception as e:
        logger.error(f"Failed to read knowledge base file: {e}")
        KB_CHUNKS = []
        return
        
    # 2. Try loading SentenceTransformers for semantic search
    try:
        from sentence_transformers import SentenceTransformer
        # Use a very small and fast model: all-MiniLM-L6-v2 (approx 80MB)
        logger.info("Initializing SentenceTransformer model (all-MiniLM-L6-v2)...")
        EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        # Precompute chunk embeddings
        if KB_CHUNKS:
            CHUNK_EMBEDDINGS = EMBEDDING_MODEL.encode(KB_CHUNKS)
            logger.info("Semantic RAG embeddings successfully indexed.")
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformers: {e}. Falling back to TF-IDF keyword search.")
        EMBEDDING_MODEL = None
        CHUNK_EMBEDDINGS = None

# Fallback basic keyword search
def keyword_search(query: str, top_k: int = 2) -> list[str]:
    if not KB_CHUNKS:
        return []
    
    # Simple term overlap scoring
    query_words = set(re.findall(r"\w+", query.lower()))
    scores = []
    
    for i, chunk in enumerate(KB_CHUNKS):
        chunk_words = set(re.findall(r"\w+", chunk.lower()))
        overlap = len(query_words.intersection(chunk_words))
        scores.append((overlap, i))
        
    scores.sort(key=lambda x: x[0], reverse=True)
    top_indices = [idx for score, idx in scores[:top_k]]
    return [KB_CHUNKS[idx] for idx in top_indices]

# Semantic search using embeddings
def semantic_search(query: str, top_k: int = 2) -> list[str]:
    global EMBEDDING_MODEL, CHUNK_EMBEDDINGS
    
    if not KB_CHUNKS:
        return []
        
    if EMBEDDING_MODEL is None or CHUNK_EMBEDDINGS is None:
        return keyword_search(query, top_k)
        
    try:
        import numpy as np
        query_emb = EMBEDDING_MODEL.encode(query)
        # Compute cosine similarity
        dot_product = np.dot(CHUNK_EMBEDDINGS, query_emb)
        norms = np.linalg.norm(CHUNK_EMBEDDINGS, axis=1) * np.linalg.norm(query_emb)
        similarities = dot_product / (norms + 1e-8)
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [KB_CHUNKS[idx] for idx in top_indices]
    except Exception as e:
        logger.error(f"Semantic search failed, falling back to keyword: {e}")
        return keyword_search(query, top_k)

# API Schema
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str
    context: list[str]
    mode: str  # "Ollama" or "Offline fallback"

@router.post("/ask", response_model=QueryResponse)
async def ask_advisor(request: QueryRequest):
    query = request.query
    
    # 1. Retrieve relevant context
    context_chunks = semantic_search(query, top_k=2)
    context_text = "\n\n".join(context_chunks)
    
    # 2. Setup prompt
    system_prompt = (
        "You are an expert AI Travel Advisor. Answer the user's travel query using ONLY "
        "the provided travel policies and guide context. Be friendly, polite and helpful. "
        "If the answer cannot be found in the context, answer based on general knowledge but "
        "prefix that part of the answer with a note stating it is not in the official guidelines."
    )
    
    prompt = f"CONTEXT:\n{context_text}\n\nUSER QUERY:\n{query}\n\nADVISOR RESPONSE:"
    
    # 3. Call local Ollama REST API
    url = f"{settings.OLLAMA_HOST}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                advisor_response = data.get("response", "").strip()
                return QueryResponse(
                    query=query,
                    response=advisor_response,
                    context=context_chunks,
                    mode="Ollama"
                )
            else:
                logger.error(f"Ollama returned status code {response.status_code}")
    except (httpx.RequestError, Exception) as e:
        logger.warning(f"Failed to communicate with Ollama service: {e}")
        
    # 4. Fallback: Parse matched sections directly into a message if Ollama is offline
    offline_msg = (
        "⚠️ [Ollama is offline or model is pulling. Showing retrieved documents directly]\n\n"
        "Here is what I found in our travel databases matching your query:\n\n"
    )
    for i, chunk in enumerate(context_chunks):
        # Format the sections for reading
        offline_msg += f"📄 **Doc {i+1}**:\n{chunk}\n\n"
        
    if not context_chunks:
        offline_msg += "I could not find any official documents matching your query. Please try searching for keywords like 'baggage', 'refund', 'cancellation', or destinations like 'Paris' or 'Tokyo'."
        
    return QueryResponse(
        query=query,
        response=offline_msg,
        context=context_chunks,
        mode="Offline fallback"
    )
