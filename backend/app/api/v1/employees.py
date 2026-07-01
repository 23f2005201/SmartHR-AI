from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import RoleChecker
from app.core.database import get_db
from app.models.employee import Employee


router = APIRouter()

allow_hr_admin = RoleChecker(["Admin", "HR"])


@router.get("/")
def get_employees(
    db: Session = Depends(get_db),
    current_user: Any = Depends(allow_hr_admin),
):
    employees = db.query(Employee).all()
    return employees


@router.get("/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(allow_hr_admin),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(allow_hr_admin),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    db.delete(employee)
    db.commit()

    return {
        "message": "Employee deleted successfully",
        "employee_id": employee_id,
    }