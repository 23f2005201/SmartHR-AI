from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.models.payroll import PayrollRecord
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.api.deps import RoleChecker

router = APIRouter()
allow_hr_admin = RoleChecker(["Admin", "HR"])

@router.post("/process/{employee_id}")
def calculate_salary(employee_id: int, start_date: date, end_date: date, db: Session = Depends(get_db), current_user = Depends(allow_hr_admin)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Count actual days present within pay period bounds
    days_present = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date,
        Attendance.status == "Present"
    ).count()

    # Core processing rules engine logic
    base_monthly_salary = employee.salary or 50000.00
    daily_rate = base_monthly_salary / 22.0 # Standard business work month layout
    
    gross_pay = round(daily_rate * max(days_present, 1), 2)
    tax_rate = 0.15 # Baseline statutory income tax deduction tier (15%)
    tax_deductions = round(gross_pay * tax_rate, 2)
    net_salary = round(gross_pay - tax_deductions, 2)

    new_payroll = PayrollRecord(
        employee_id=employee_id,
        pay_period_start=start_date,
        pay_period_end=end_date,
        gross_salary=gross_pay,
        tax_deductions=tax_deductions,
        net_salary=net_salary,
        status="Processed"
    )
    db.add(new_payroll)
    db.commit()
    db.refresh(new_payroll)
    return new_payroll