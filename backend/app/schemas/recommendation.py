from pydantic import BaseModel
from typing import List, Optional

class PolicyComparison(BaseModel):
    policy_name: str
    insurer: str
    premium_per_year: str
    cover_amount: str
    waiting_period: str
    key_benefit: str
    suitability_score: str

class CoverageDetail(BaseModel):
    inclusions: str
    exclusions: str
    sub_limits: str
    copay_percent: str
    claim_type: str

class RecommendationResponse(BaseModel):
    session_id: str
    peer_comparison: List[PolicyComparison]
    coverage_detail: CoverageDetail
    why_this_policy: str
    recommended_policy_name: str
    source_documents: List[str]
