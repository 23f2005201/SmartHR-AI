from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.employees import router as employee_router
from app.api.v1.users import router as user_router # Add this import

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(user_router, prefix="/users", tags=["User Credentials"]) # Mount users
api_v1_router.include_router(employee_router, prefix="/employees", tags=["Employee Profiles"])