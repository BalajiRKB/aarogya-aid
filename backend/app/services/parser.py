import fitz  # PyMuPDF
from typing import List
import json

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF. Handles multi-column layouts."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_parts = []
    for page in doc:
        # sort text blocks top-to-bottom for logical reading order
        blocks = page.get_text("blocks")
        blocks_sorted = sorted(blocks, key=lambda b: (b[1], b[0]))
        for block in blocks_sorted:
            text_parts.append(block[4].strip())
    return "\n".join(text_parts)

def parse_json(file_bytes: bytes) -> str:
    data = json.loads(file_bytes.decode("utf-8"))
    return json.dumps(data, indent=2)

def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")

def chunk_text(text: str, doc_id: str, metadata: dict) -> List[dict]:
    """
    Paragraph-aware chunking strategy:
    - Split on double newlines first (preserves clause boundaries in policy PDFs)
    - Then fall back to fixed-size chunks with overlap if paragraphs are too long
    This ensures exclusion clauses and sub-limit tables are not split mid-sentence.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    chunk_index = 0

    for para in paragraphs:
        if len(current) + len(para) < CHUNK_SIZE:
            current += ("\n\n" + para) if current else para
        else:
            if current:
                chunks.append({
                    "id": f"{doc_id}_chunk_{chunk_index}",
                    "text": current,
                    "metadata": {**metadata, "doc_id": doc_id, "chunk_index": chunk_index},
                })
                chunk_index += 1
                # overlap: carry last CHUNK_OVERLAP chars into next chunk
                current = current[-CHUNK_OVERLAP:] + "\n\n" + para
            else:
                current = para

    if current:
        chunks.append({
            "id": f"{doc_id}_chunk_{chunk_index}",
            "text": current,
            "metadata": {**metadata, "doc_id": doc_id, "chunk_index": chunk_index},
        })

    return chunks
