from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    department_id: Optional[int] = None
    joining_date: date
    salary: float

class EmployeeCreate(EmployeeBase):
    user_id: int

class EmployeeResponse(EmployeeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True