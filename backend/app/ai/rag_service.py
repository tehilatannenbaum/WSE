import os
import re
import httpx
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.app.config import settings
from backend.app.auth.service import get_current_user, UserRead

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)

KB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "knowledge_base",
    "travel_info.txt"
)

# Global variables for simple search
KB_CHUNKS = [] # list of dicts: {"section": str, "text": str}
EMBEDDING_MODEL = None
CHUNK_EMBEDDINGS = None

def init_rag():
    global KB_CHUNKS, EMBEDDING_MODEL, CHUNK_EMBEDDINGS
    
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
            parts = sec.split("]", 1)
            sec_name = parts[0].strip() if len(parts) > 0 else "General"
            chunks.append({
                "section": sec_name,
                "text": "[SECTION: " + sec
            })
            
        KB_CHUNKS = chunks
        logger.info(f"Loaded {len(KB_CHUNKS)} knowledge base chunks from {KB_PATH}")
    except Exception as e:
        logger.error(f"Failed to read knowledge base file: {e}")
        KB_CHUNKS = []
        return
        
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Initializing SentenceTransformer model (all-MiniLM-L6-v2)...")
        EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        if KB_CHUNKS:
            texts = [c["text"] for c in KB_CHUNKS]
            CHUNK_EMBEDDINGS = EMBEDDING_MODEL.encode(texts)
            logger.info("Semantic RAG embeddings successfully indexed.")
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformers: {e}. Falling back to keyword search.")
        EMBEDDING_MODEL = None
        CHUNK_EMBEDDINGS = None

def keyword_search(query: str, top_k: int = 2) -> list[dict]:
    if not KB_CHUNKS:
        return []
    
    query_words = set(re.findall(r"\w+", query.lower()))
    scores = []
    
    for i, chunk in enumerate(KB_CHUNKS):
        chunk_words = set(re.findall(r"\w+", chunk["text"].lower()))
        overlap = len(query_words.intersection(chunk_words))
        scores.append((overlap, i))
        
    scores.sort(key=lambda x: x[0], reverse=True)
    top_indices = [idx for score, idx in scores[:top_k]]
    return [KB_CHUNKS[idx] for idx in top_indices]

def semantic_search(query: str, top_k: int = 2) -> list[dict]:
    global EMBEDDING_MODEL, CHUNK_EMBEDDINGS
    
    if not KB_CHUNKS:
        return []
        
    if EMBEDDING_MODEL is None or CHUNK_EMBEDDINGS is None:
        return keyword_search(query, top_k)
        
    try:
        import numpy as np
        query_emb = EMBEDDING_MODEL.encode(query)
        dot_product = np.dot(CHUNK_EMBEDDINGS, query_emb)
        norms = np.linalg.norm(CHUNK_EMBEDDINGS, axis=1) * np.linalg.norm(query_emb)
        similarities = dot_product / (norms + 1e-8)
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [KB_CHUNKS[idx] for idx in top_indices]
    except Exception as e:
        logger.error(f"Semantic search failed, falling back to keyword: {e}")
        return keyword_search(query, top_k)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str
    context: list[str]
    sources: list[str]
    mode: str  # "Ollama" or "Offline fallback"

@router.get("/status")
def check_ollama_status():
    """
    Verify connectivity to the local Ollama daemon.
    """
    url = f"{settings.OLLAMA_HOST}/api/tags"
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                return {"status": "Online", "model": settings.OLLAMA_MODEL}
            return {"status": "Error", "detail": f"Ollama returned status {response.status_code}"}
    except Exception as e:
        return {"status": "Offline", "detail": str(e)}

@router.post("/ask", response_model=QueryResponse)
async def ask_advisor(
    request: QueryRequest,
    current_user: UserRead = Depends(get_current_user)
):
    query = request.query
    
    # 1. Retrieve relevant context
    context_chunks = semantic_search(query, top_k=2)
    context_text = "\n\n".join([c["text"] for c in context_chunks])
    sources = [c["section"] for c in context_chunks]
    
    # 2. Setup prompt strictly mapping constraints
    system_prompt = (
        "You are an expert AI Travel Advisor. Answer the user's travel query using ONLY "
        "the provided travel policies and guide context. "
        "If the answer cannot be found in the provided context, you MUST state: "
        "'The available documents do not contain enough information to answer this question.' "
        "Do NOT make up answers or provide general information not in the text."
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
            "temperature": 0.0
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                advisor_response = data.get("response", "").strip()
                
                # Append sources details
                source_suffix = "\n\n(Sources: " + ", ".join(sources) + ")" if sources else ""
                
                return QueryResponse(
                    query=query,
                    response=advisor_response + source_suffix,
                    context=[c["text"] for c in context_chunks],
                    sources=sources,
                    mode="Ollama"
                )
            else:
                logger.error(f"Ollama returned status code {response.status_code}")
    except (httpx.RequestError, Exception) as e:
        logger.warning(f"Failed to communicate with Ollama service: {e}")
        
    # 4. Fallback: Parse matched sections directly into a message if Ollama is offline
    offline_msg = (
        "[Ollama is offline or model is pulling. Showing retrieved documents directly]\n\n"
        "Here is what I found in our travel databases matching your query:\n\n"
    )
    for chunk in context_chunks:
        offline_msg += f"Doc section: **{chunk['section']}**\n{chunk['text']}\n\n"
        
    if not context_chunks:
        offline_msg += "The available documents do not contain enough information to answer this question."
        
    return QueryResponse(
        query=query,
        response=offline_msg,
        context=[c["text"] for c in context_chunks],
        sources=sources,
        mode="Offline fallback"
    )
