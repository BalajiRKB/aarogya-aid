from pydantic import BaseModel
from typing import Optional

class PolicyDocumentMeta(BaseModel):
    doc_id: str
    file_name: str
    upload_date: str
    file_type: str
    policy_name: str
    insurer: str

class MetadataUpdateRequest(BaseModel):
    policy_name: Optional[str] = None
    insurer: Optional[str] = None
