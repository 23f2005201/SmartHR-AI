from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.employees import router as employee_router
from app.api.v1.users import router as user_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.leave import router as leave_router
from app.api.v1.payroll import router as payroll_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(user_router, prefix="/users", tags=["User Credentials"])
api_v1_router.include_router(employee_router, prefix="/employees", tags=["Employee Profiles"])
api_v1_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance Tracking"])
api_v1_router.include_router(leave_router, prefix="/leave", tags=["Leave Management"])
api_v1_router.include_router(payroll_router, prefix="/payroll", tags=["Payroll Automation"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["Reporting Analytics"])