import chromadb
from google import genai
from google.genai import types as genai_types
from chromadb import Documents, EmbeddingFunction, Embeddings
from app.core.config import settings

_client = None
_collection = None


class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Uses the new google-genai SDK (v1 API) for embeddings.
    Avoids the deprecated google.generativeai / v1beta route used by
    langchain-google-genai, which has no working embedding model.
    """
    def __init__(self):
        self._genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def __call__(self, input: Documents) -> Embeddings:
        result = self._genai_client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=list(input),
            config=genai_types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
            ),
        )
        return [e.values for e in result.embeddings]


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
