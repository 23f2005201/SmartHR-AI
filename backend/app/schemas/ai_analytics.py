from pydantic import BaseModel

class AttritionInput(BaseModel):
    years_at_company: float
    monthly_salary: float
    weekly_overtime_hours: float
    satisfaction_score: float # 1 to 5 scale

class LeavePatternInput(BaseModel):
    sick_leaves_taken: int
    casual_leaves_taken: int
    consecutive_days_requested: int

class PayrollVarianceInput(BaseModel):
    employee_id: int
    incoming_net_payout: float