import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

_client = None
_collection = None

def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client

def get_collection():
    global _collection
    client = get_chroma_client()
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.EMBEDDING_MODEL,
    )
    _collection = client.get_or_create_collection(
        name="policies",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection

def delete_document_chunks(doc_id: str):
    """Immediately removes all chunks for a given document from the vector store."""
    collection = get_collection()
    results = collection.get(where={"doc_id": doc_id})
    if results and results["ids"]:
        collection.delete(ids=results["ids"])
    return len(results["ids"]) if results and results["ids"] else 0
