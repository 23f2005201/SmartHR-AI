from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# --- 📋 REQUEST SCHEMAS ---

class AttritionRequest(BaseModel):
    # Pass Ellipsis (...) as the default first argument, and force all others as explicit keywords
    years_at_company: float = Field(..., ge=0.0, json_schema_extra={"example": 3.5})
    monthly_salary: float = Field(..., ge=0.0, json_schema_extra={"example": 45000.0})
    weekly_overtime_hours: float = Field(..., ge=0.0, json_schema_extra={"example": 12.0})
    satisfaction_score: int = Field(..., ge=1, le=5, json_schema_extra={"example": 2})

class LeaveAnalysisRequest(BaseModel):
    sick_leaves_taken: int = Field(..., ge=0, json_schema_extra={"example": 4})
    casual_leaves_taken: int = Field(..., ge=0, json_schema_extra={"example": 1})
    consecutive_days_requested: int = Field(..., ge=1, json_schema_extra={"example": 5})