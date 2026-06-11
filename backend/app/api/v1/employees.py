from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.api.deps import RoleChecker, get_current_user

router = APIRouter()

# Instantiate the RBAC dependency rule
allow_hr_and_admin = RoleChecker(["Admin", "HR"])

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    db: Session = Depends(get_db),
    current_operator = Depends(allow_hr_and_admin) # Guarding the endpoint
):
    # Verify if the user account mapping exists
    employee_exists = db.query(Employee).filter(Employee.user_id == employee.user_id).first()
    if employee_exists:
        raise HTTPException(status_code=400, detail="An employee profile is already mapped to this user account.")

    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee