from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.core.security import verify_admin
from app.core.vector_store import get_collection, delete_document_chunks
from app.services.parser import parse_pdf, parse_json, parse_txt, chunk_text
from app.services.document_store import (
    save_document_meta, list_documents, update_document_meta, delete_document_meta, get_document
)
from app.schemas.admin import MetadataUpdateRequest
from uuid import uuid4
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"application/pdf", "application/json", "text/plain"}

@router.get("/documents", dependencies=[Depends(verify_admin)])
def list_policy_documents():
    return list_documents()

@router.post("/documents", dependencies=[Depends(verify_admin)])
async def upload_policy_document(
    file: UploadFile = File(...),
    policy_name: str = Form(...),
    insurer: str = Form(...),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, JSON, and TXT files are supported.")
    
    file_bytes = await file.read()
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext == "pdf":
        text = parse_pdf(file_bytes)
    elif file_ext == "json":
        text = parse_json(file_bytes)
    else:
        text = parse_txt(file_bytes)
    
    if not text.strip():
        raise HTTPException(status_code=422, detail="Document appears to be empty or unreadable.")
    
    doc_id = str(uuid4())
    metadata = {"policy_name": policy_name, "insurer": insurer, "file_name": file.filename}
    chunks = chunk_text(text, doc_id, metadata)
    
    collection = get_collection()
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    
    save_document_meta(
        doc_id=doc_id,
        file_name=file.filename,
        file_type=file_ext,
        policy_name=policy_name,
        insurer=insurer,
    )
    
    logger.info(f"Uploaded document {file.filename} as {doc_id} ({len(chunks)} chunks)")
    return {"doc_id": doc_id, "chunks_indexed": len(chunks), "policy_name": policy_name}

@router.patch("/documents/{doc_id}", dependencies=[Depends(verify_admin)])
def update_policy_metadata(doc_id: str, body: MetadataUpdateRequest):
    updated = update_document_meta(doc_id, body.policy_name, body.insurer)
    if not updated:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Metadata updated successfully."}

@router.delete("/documents/{doc_id}", dependencies=[Depends(verify_admin)])
def delete_policy_document(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    chunks_removed = delete_document_chunks(doc_id)
    delete_document_meta(doc_id)
    
    logger.info(f"Deleted document {doc_id} ({chunks_removed} chunks removed from vector store)")
    return {"message": f"Document deleted. {chunks_removed} chunks removed from vector store immediately."}
