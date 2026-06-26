from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
import logging

from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.schemas.attendance import AttendanceResponse
from app.api.deps import get_current_user, RoleChecker

logger = logging.getLogger("uvicorn.error")
router = APIRouter()

# Dependency to fetch the Employee profile of the active user
def get_current_employee(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="No employee profile mapped to this account.")
    return employee


@router.post("/clock-in", response_model=AttendanceResponse)
def clock_in(db: Session = Depends(get_db), employee: Employee = Depends(get_current_employee)):
    today = date.today()
    existing = db.query(Attendance).filter(Attendance.employee_id == employee.id, Attendance.date == today).first()
    
    # 🌟 SAFE MULTI-CLICK OVERRIDE: Instead of hard crashing, return the active session cleanly
    if existing:
        logger.warning(f"⚠️ User Profile #{employee.id} requested duplicate clock-in validation framework.")
        return existing
    
    new_record = Attendance(
        employee_id=employee.id, 
        date=today, 
        clock_in=datetime.now().time(), 
        status="Present"
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.put("/clock-out", response_model=AttendanceResponse)
def clock_out(db: Session = Depends(get_db), employee: Employee = Depends(get_current_employee)):
    today = date.today()
    record = db.query(Attendance).filter(Attendance.employee_id == employee.id, Attendance.date == today).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="No active clock-in record found for today.")
    
    # 🌟 SAFE OVERWRITE OPTION: If user clicks clock-out again, update it with the latest time stamp cleanly
    record.clock_out = datetime.now().time() # type: ignore
    db.commit()
    db.refresh(record)
    return record


allow_hr_admin = RoleChecker(["Admin", "HR"])

@router.get("/", response_model=list[AttendanceResponse])
def get_todays_attendance(
    db: Session = Depends(get_db), 
    current_operator = Depends(allow_hr_admin)
):
    today = date.today()
    return db.query(Attendance).filter(Attendance.date == today).all()