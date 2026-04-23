import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chromadb import Documents, EmbeddingFunction, Embeddings
from app.core.config import settings

_client = None
_collection = None


class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Wraps LangChain's GoogleGenerativeAIEmbeddings so Chroma can call it.
    Uses Gemini text-embedding-004 — free tier, 768-dim, no OpenAI needed.
    """
    def __init__(self):
        self._model = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )

    def __call__(self, input: Documents) -> Embeddings:
        return self._model.embed_documents(list(input))


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection():
    global _collection
    client = get_chroma_client()
    ef = GeminiEmbeddingFunction()
    _collection = client.get_or_create_collection(
        name="policies",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def delete_document_chunks(doc_id: str):
    collection = get_collection()
    results = collection.get(where={"doc_id": doc_id})
    if results and results["ids"]:
        collection.delete(ids=results["ids"])
    return len(results["ids"]) if results and results["ids"] else 0
