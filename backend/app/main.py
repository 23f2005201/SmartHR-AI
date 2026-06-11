from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router

app = FastAPI(
    title="SmartHR AI Platform API",
    description="Automated HRMS, Payroll, and Predictive Workforce Analytics Backend Engine",
    version="1.0.0"
)

# Configure cross-origin resource sharing for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Default Vite local dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the consolidated API router matrix
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "online", "system": "SmartHR AI Engine"}