from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.leave import LeaveRequest
from app.models.employee import Employee
from app.schemas.leave import LeaveRequestCreate, LeaveRequestResponse, LeaveRequestUpdate
from app.api.deps import RoleChecker
from app.api.v1.attendance import get_current_employee

router = APIRouter()
allow_hr_admin = RoleChecker(["Admin", "HR"])

@router.post("/", response_model=LeaveRequestResponse)
def submit_leave_request(
    payload: LeaveRequestCreate, 
    db: Session = Depends(get_db), 
    employee: Employee = Depends(get_current_employee)
):
    # Ensure the payload maps securely to the current user's employee ID
    new_leave = LeaveRequest(
        employee_id=employee.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status="Pending"
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave

@router.get("/me", response_model=list[LeaveRequestResponse])
def get_my_leave_requests(db: Session = Depends(get_db), employee: Employee = Depends(get_current_employee)):
    return db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee.id).all()

@router.put("/{leave_id}/status", response_model=LeaveRequestResponse)
def update_leave_status(
    leave_id: int, 
    payload: LeaveRequestUpdate, 
    db: Session = Depends(get_db), 
    current_operator = Depends(allow_hr_admin) # Guarded: Only HR/Admin can approve
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    
    leave.status = payload.status  # type: ignore
    db.commit()
    db.refresh(leave)
    return leave