from pydantic import BaseModel, Field
from typing import List, Literal

class UserProfile(BaseModel):
    full_name: str = Field(..., description="User's full name")
    age: int = Field(..., ge=1, le=99, description="Age in years")
    lifestyle: Literal["Sedentary", "Moderate", "Active", "Athlete"]
    pre_existing_conditions: List[Literal["Diabetes", "Hypertension", "Asthma", "Cardiac", "None", "Other"]]
    income_band: Literal["under_3L", "3-8L", "8-15L", "15L+"]
    city_tier: Literal["Metro", "Tier-2", "Tier-3"]
