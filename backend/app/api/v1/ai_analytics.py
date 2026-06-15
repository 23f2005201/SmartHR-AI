from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.ai_analytics import AttritionInput, LeavePatternInput, PayrollVarianceInput
from app.services.analytics import ai_analytics_service
from app.services.anomaly_detector import CorporateInsightsService
from app.app import RoleChecker

router = APIRouter()
allow_operator = RoleChecker(["Admin", "HR", "Employee"])
allow_hr_only = RoleChecker(["Admin", "HR"])

@router.post("/predict-attrition")
def predict_staff_attrition(payload: AttritionInput, current_user = Depends(allow_hr_only)):
    return ai_analytics_service.predict_attrition(
        payload.years_at_company,
        payload.monthly_salary,
        payload.weekly_overtime_hours,
        payload.satisfaction_score
    )

@router.post("/analyze-leave")
def verify_leave_burnout_patterns(payload: LeavePatternInput, current_user = Depends(allow_operator)):
    return ai_analytics_service.analyze_leave_pattern(
        payload.sick_leaves_taken,
        payload.casual_leaves_taken,
        payload.consecutive_days_requested
    )

@router.post("/payroll-anomaly")
def inspect_payroll_variance(payload: PayrollVarianceInput, db: Session = Depends(get_db), current_user = Depends(allow_hr_only)):
    return CorporateInsightsService.inspect_payroll_variance(
        db, 
        payload.employee_id, 
        payload.incoming_net_payout
    )

@router.get("/productivity-insights/{employee_id}")
def get_employee_productivity(employee_id: int, db: Session = Depends(get_db), current_user = Depends(allow_operator)):
    return CorporateInsightsService.process_productivity_insights(db, employee_id)