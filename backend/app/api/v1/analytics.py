from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.payroll import PayrollRecord
from app.schemas.analytics import DashboardSummaryResponse
from app.app import RoleChecker

router = APIRouter()
allow_hr_admin = RoleChecker(["Admin", "HR"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_aggregations(db: Session = Depends(get_db), current_user = Depends(allow_hr_admin)):
    try:
        # 1. Total Active Global Headcount
        total_headcount = db.query(Employee).count()

        # 2. Total Pending Leave Requests requiring immediate operational review
        pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "Pending").count()

        # 3. Aggregated Financial Net Salary Spend across all processed payroll records
        total_spend = db.query(func.sum(PayrollRecord.net_salary)).scalar() or 0.0

        # 4. Department Distribution Array Generation
        # (Assuming your Employee model contains a department_id field)
        dept_counts = db.query(
            Employee.department_id, 
            func.count(Employee.id)
        ).group_by(Employee.department_id).all()
        
        # Format the distribution data into a readable object map
        distribution_map = {f"Dept-{str(dept_id)}": count for dept_id, count in dept_counts if dept_id is not None}
        if not distribution_map:
            distribution_map = {"Core Operations": total_headcount}

        return {
            "total_headcount": total_headcount,
            "active_leave_claims": pending_leaves,
            "total_monthly_spend": round(total_spend, 2),
            "department_distribution": distribution_map
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database aggregation computation error: {str(e)}")