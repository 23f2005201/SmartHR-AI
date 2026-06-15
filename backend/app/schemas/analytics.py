from pydantic import BaseModel
from typing import Dict, List

class DashboardSummaryResponse(BaseModel):
    total_headcount: int
    active_leave_claims: int
    total_monthly_spend: float
    department_distribution: Dict[str, int]

    class Config:
        from_attributes = True
