from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.core.database import get_db
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.payroll import PayrollRecord
from app.schemas.analytics import DashboardSummaryResponse
from app.app import RoleChecker

logger = logging.getLogger("uvicorn.error")
router = APIRouter()
allow_hr_admin = RoleChecker(["Admin", "HR"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_aggregations(db: Session = Depends(get_db), current_user = Depends(allow_hr_admin)):
    try:
        # 1. Total Active Global Headcount (Fallback safe integer handling)
        total_headcount = db.query(Employee).count() or 0

        # 2. Total Pending Leave Requests requiring immediate operational review
        pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == "Pending").count() or 0

        # 3. Aggregated Financial Net Salary Spend (Force float type conversion instantly)
        spend_query = db.query(func.sum(PayrollRecord.net_salary)).scalar()
        total_spend = float(spend_query) if spend_query is not None else 0.0

        # 4. Department Distribution Array Generation with safety nets
        try:
            dept_counts = db.query(
                Employee.department_id, 
                func.count(Employee.id)
            ).group_by(Employee.department_id).all()
            
            distribution_map = {f"Dept-{str(dept_id)}": count for dept_id, count in dept_counts if dept_id is not None}
        except Exception as inner_e:
            logger.warning(f"⚠️ Department aggregation skipped: {str(inner_e)}")
            distribution_map = {}

        if not distribution_map:
            distribution_map = {"Core Operations": total_headcount}

        # Return a perfectly type-mapped response dictionary matching the schema expectations
        return {
            "total_headcount": total_headcount,
            "active_leave_claims": pending_leaves,
            "total_monthly_spend": round(total_spend, 2),
            "department_distribution": distribution_map
        }

    except Exception as e:
        logger.error(f"❌ Core Analytics endpoint failure: {str(e)}")
        # Ultimate structural safety net to keep the server alive if a database table drops
        raise HTTPException(
            status_code=500, 
            detail=f"Database aggregation computation error: {str(e)}"
        )