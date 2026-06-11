from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class AttendanceBase(BaseModel):
    employee_id: int
    date: date
    clock_in: Optional[time] = None
    clock_out: Optional[time] = None
    status: Optional[str] = "Present"  # Present, Absent, Late, Half-day

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    clock_out: Optional[time] = None
    status: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        from_attributes = True