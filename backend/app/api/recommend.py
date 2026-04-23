from fastapi import APIRouter, HTTPException
from app.schemas.profile import UserProfile
from app.schemas.recommendation import RecommendationResponse
from app.services.agent import get_recommendation
from app.core.sessions import create_session
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/recommend", response_model=RecommendationResponse)
def recommend(profile: UserProfile):
    try:
        result = get_recommendation(profile)
        session_id = create_session(
            profile=profile.model_dump(),
            recommendation=result,
        )
        return RecommendationResponse(
            session_id=session_id,
            peer_comparison=result.get("peer_comparison", []),
            coverage_detail=result.get("coverage_detail", {}),
            why_this_policy=result.get("why_this_policy", ""),
            recommended_policy_name=result.get("recommended_policy_name", ""),
            source_documents=result.get("source_documents", []),
        )
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
