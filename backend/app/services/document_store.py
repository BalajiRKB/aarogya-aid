import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from app.schemas.admin import PolicyDocumentMeta

META_FILE = Path("./chroma_db/doc_metadata.json")

def _load() -> Dict[str, dict]:
    if META_FILE.exists():
        return json.loads(META_FILE.read_text())
    return {}

def _save(data: dict):
    META_FILE.parent.mkdir(parents=True, exist_ok=True)
    META_FILE.write_text(json.dumps(data, indent=2))

def save_document_meta(doc_id: str, file_name: str, file_type: str, policy_name: str, insurer: str):
    data = _load()
    data[doc_id] = {
        "doc_id": doc_id,
        "file_name": file_name,
        "upload_date": datetime.utcnow().isoformat(),
        "file_type": file_type,
        "policy_name": policy_name,
        "insurer": insurer,
    }
    _save(data)

def list_documents() -> List[PolicyDocumentMeta]:
    data = _load()
    return [PolicyDocumentMeta(**v) for v in data.values()]

def get_document(doc_id: str) -> PolicyDocumentMeta | None:
    data = _load()
    entry = data.get(doc_id)
    return PolicyDocumentMeta(**entry) if entry else None

def update_document_meta(doc_id: str, policy_name: str | None, insurer: str | None):
    data = _load()
    if doc_id not in data:
        return False
    if policy_name:
        data[doc_id]["policy_name"] = policy_name
    if insurer:
        data[doc_id]["insurer"] = insurer
    _save(data)
    return True

def delete_document_meta(doc_id: str) -> bool:
    data = _load()
    if doc_id not in data:
        return False
    del data[doc_id]
    _save(data)
    return True
