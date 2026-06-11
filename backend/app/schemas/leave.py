from pydantic import BaseModel
from datetime import date
from typing import Optional

class LeaveRequestBase(BaseModel):
    employee_id: int
    leave_type: str  # Casual, Sick, Annual
    start_date: date
    end_date: date

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequestUpdate(BaseModel):
    status: str  # Approved, Rejected

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    status: str  # Pending, Approved, Rejected

    class Config:
        from_attributes = True