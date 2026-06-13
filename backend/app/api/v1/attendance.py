from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.schemas.attendance import AttendanceResponse
from app.api.deps import get_current_user

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
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already clocked in today.")
    
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
    if record.clock_out: # type: ignore
        raise HTTPException(status_code=400, detail="You have already clocked out today.")
        
    record.clock_out = datetime.now().time() # type: ignore
    db.commit()
    db.refresh(record)
    return record

from app.api.deps import RoleChecker
allow_hr_admin = RoleChecker(["Admin", "HR"])

@router.get("/", response_model=list[AttendanceResponse])
def get_todays_attendance(
    db: Session = Depends(get_db), 
    current_operator = Depends(allow_hr_admin) # Guarded: Only HR/Admin
):
    today = date.today()
    return db.query(Attendance).filter(Attendance.date == today).all()